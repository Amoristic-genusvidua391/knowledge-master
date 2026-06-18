"""Re-ranking — improve search quality with a second-pass scoring model.

Uses Ollama's embedding model to compute query-document relevance via
cosine similarity of concatenated query+document vs query alone.
This is a lightweight approximation of cross-encoder re-ranking.
"""

from .embeddings import _client, MODEL


def rerank(query: str, results: list[dict], top_k: int = 5) -> list[dict]:
    """Re-rank search results by computing more precise relevance scores.

    Takes top candidates from vector search and re-scores them using
    query-document pair embedding similarity.
    """
    if not results:
        return results

    # Build query-document pairs for scoring
    pairs = []
    for r in results:
        text = r.get("text", "")[:512]  # limit to avoid context overflow
        # Prefix the text with the query for better semantic matching
        pairs.append(f"search_query: {query}\nsearch_document: {text}")

    # Embed all pairs + the query reference
    query_ref = f"search_query: {query}\nsearch_document: {query}"
    all_texts = [query_ref] + pairs

    response = _client.embed(model=MODEL, input=all_texts)
    vectors = response["embeddings"]

    query_vec = vectors[0]
    pair_vecs = vectors[1:]

    # Score each pair against the query reference vector
    scored = []
    for i, (pair_vec, result) in enumerate(zip(pair_vecs, results)):
        score = _cosine_sim(query_vec, pair_vec)
        scored.append({**result, "rerank_score": score, "original_score": result.get("score", 0)})

    # Sort by rerank score descending
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)

    # Update the "score" field to the rerank score for display
    for item in scored[:top_k]:
        item["score"] = item["rerank_score"]

    return scored[:top_k]


def _cosine_sim(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
