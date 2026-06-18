"""FalkorDB graph store - nodes, edges, vector search, and graph traversal."""

import hashlib

from falkordb import FalkorDB

GRAPH_NAME = "knowledge"

# Vector dimension for nomic-embed-text
VECTOR_DIM = 768

_graph_instance = None


def get_graph(host: str = "localhost", port: int = 6379):
    """Get FalkorDB graph instance with schema version check."""
    global _graph_instance
    if _graph_instance is not None:
        return _graph_instance

    db = FalkorDB(host=host, port=port)
    graph = db.select_graph(GRAPH_NAME)

    # Check and auto-migrate schema
    from .migrations import check_and_migrate
    check_and_migrate(graph, auto_migrate=True)

    _graph_instance = graph
    return graph


def reset_graph_instance():
    """Reset cached graph instance (for testing)."""
    global _graph_instance
    _graph_instance = None


def content_hash(text: str) -> str:
    """Compute content hash for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def init_schema(graph):
    """Create indexes and constraints."""
    commands = [
        # Vector indexes
        "CREATE VECTOR INDEX FOR (c:Chunk) ON (c.embedding) OPTIONS {dimension: 768, similarityFunction: 'cosine'}",
        # Fulltext indexes
        "CREATE FULLTEXT INDEX FOR (c:Chunk) ON (c.text)",
        # Regular indexes for lookups
        "CREATE INDEX FOR (d:Document) ON (d.path)",
        "CREATE INDEX FOR (r:Repo) ON (r.name)",
        "CREATE INDEX FOR (p:Person) ON (p.email)",
        "CREATE INDEX FOR (f:File) ON (f.path)",
    ]
    for cmd in commands:
        try:
            graph.query(cmd)
        except Exception:
            pass  # index may already exist


def upsert_chunk(graph, chunk_id: str, text: str, embedding: list[float], metadata: dict):
    """Insert or update a chunk node with embedding. Skips if content unchanged (dedup)."""
    chash = content_hash(text)

    # Check if chunk exists with same content hash — skip if unchanged
    existing = graph.query(
        "MATCH (c:Chunk {id: $id}) RETURN c.content_hash",
        params={"id": chunk_id},
    )
    if existing.result_set and existing.result_set[0][0] == chash:
        return False  # skip — content unchanged

    graph.query(
        """MERGE (c:Chunk {id: $id})
           SET c.text = $text, c.embedding = vecf32($embedding),
               c.source = $source, c.source_type = $source_type,
               c.content_hash = $hash, c.indexed_at = timestamp()""",
        params={
            "id": chunk_id,
            "text": text,
            "embedding": embedding,
            "source": metadata.get("source", ""),
            "source_type": metadata.get("source_type", ""),
            "hash": chash,
        },
    )
    return True  # inserted/updated


def upsert_document(graph, path: str, doc_type: str, metadata: dict):
    """Insert or update a document node."""
    graph.query(
        """MERGE (d:Document {path: $path})
           SET d.type = $type, d.title = $title, d.indexed_at = timestamp()""",
        params={"path": path, "type": doc_type, "title": metadata.get("title", "")},
    )


def upsert_repo(graph, name: str, path: str):
    """Insert or update a repo node."""
    graph.query(
        "MERGE (r:Repo {name: $name}) SET r.path = $path",
        params={"name": name, "path": path},
    )


def upsert_person(graph, name: str, email: str):
    """Insert or update a person node."""
    graph.query(
        "MERGE (p:Person {email: $email}) SET p.name = $name",
        params={"name": name, "email": email},
    )


def link_chunk_to_document(graph, chunk_id: str, doc_path: str):
    """Create PART_OF edge from chunk to document."""
    graph.query(
        """MATCH (c:Chunk {id: $chunk_id}), (d:Document {path: $doc_path})
           MERGE (c)-[:PART_OF]->(d)""",
        params={"chunk_id": chunk_id, "doc_path": doc_path},
    )


def link_document_to_repo(graph, doc_path: str, repo_name: str):
    """Create IN_REPO edge."""
    graph.query(
        """MATCH (d:Document {path: $doc_path}), (r:Repo {name: $repo_name})
           MERGE (d)-[:IN_REPO]->(r)""",
        params={"doc_path": doc_path, "repo_name": repo_name},
    )


def link_person_authored(graph, email: str, doc_path: str):
    """Create AUTHORED edge."""
    graph.query(
        """MATCH (p:Person {email: $email}), (d:Document {path: $doc_path})
           MERGE (p)-[:AUTHORED]->(d)""",
        params={"email": email, "doc_path": doc_path},
    )


def vector_search(graph, query_embedding: list[float], top_k: int = 10, filters: dict = None):
    """Semantic vector search across chunks."""
    filter_clause = ""
    params = {"embedding": query_embedding, "top_k": top_k}

    if filters and filters.get("source_type"):
        filter_clause = "WHERE c.source_type = $source_type"
        params["source_type"] = filters["source_type"]

    result = graph.query(
        f"""CALL db.idx.vector.queryNodes('Chunk', 'embedding', $top_k, vecf32($embedding))
            YIELD node AS c, score
            {filter_clause}
            RETURN c.id AS id, c.text AS text, c.source AS source,
                   c.source_type AS source_type, score
            ORDER BY score DESC""",
        params=params,
    )
    return [
        {"id": r[0], "text": r[1], "source": r[2], "source_type": r[3], "score": r[4]}
        for r in result.result_set
    ]


def graph_context_search(graph, query_embedding: list[float], top_k: int = 5, query: str = None):
    """Hybrid search: vector find + graph traversal for related context."""
    # Fetch more candidates for re-ranking
    fetch_k = top_k * 3 if query else top_k

    result = graph.query(
        """CALL db.idx.vector.queryNodes('Chunk', 'embedding', $top_k, vecf32($embedding))
           YIELD node AS c, score
           OPTIONAL MATCH (c)-[:PART_OF]->(d:Document)-[:IN_REPO]->(r:Repo)
           OPTIONAL MATCH (p:Person)-[:AUTHORED]->(d)
           RETURN c.text AS text, c.source AS source, score,
                  d.path AS doc_path, r.name AS repo, p.name AS author
           ORDER BY score DESC""",
        params={"embedding": query_embedding, "top_k": fetch_k},
    )
    results = [
        {
            "text": r[0],
            "source": r[1],
            "score": r[2],
            "doc_path": r[3],
            "repo": r[4],
            "author": r[5],
        }
        for r in result.result_set
    ]

    # Apply re-ranking if query text is available
    if query and results:
        from .rerank import rerank
        results = rerank(query, results, top_k)
    else:
        results = results[:top_k]

    return results


def get_stats(graph):
    """Get graph statistics."""
    result = graph.query(
        """MATCH (c:Chunk) WITH count(c) AS chunks
           MATCH (d:Document) WITH chunks, count(d) AS docs
           MATCH (r:Repo) WITH chunks, docs, count(r) AS repos
           RETURN chunks, docs, repos"""
    )
    row = result.result_set[0] if result.result_set else [0, 0, 0]
    return {"chunks": row[0], "documents": row[1], "repos": row[2]}
