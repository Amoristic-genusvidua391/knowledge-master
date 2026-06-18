"""Git repository parser - indexes files and extracts graph relationships."""

import os
import sys
from pathlib import Path

from git import Repo
from rich.progress import Progress

from .. import chunking, embeddings, store
from ..intelligence import extract_all
from ..static_analysis import build_import_graph

INDEXABLE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".rs", ".go", ".java",
    ".md", ".markdown", ".txt", ".yaml", ".yml", ".json",
    ".toml", ".cfg", ".ini", ".sh", ".bash", ".dockerfile",
}

SKIP_DIRS = {".git", "node_modules", "target", "dist", "build", "__pycache__", ".venv", "venv"}

MAX_FILE_SIZE = 512_000  # 500KB


def index_repo(repo_path: str, graph=None, branch: str = "HEAD", on_progress=None):
    """Index an entire git repository into the knowledge graph."""
    repo_path = os.path.expanduser(repo_path)
    repo = Repo(repo_path)
    repo_name = Path(repo_path).name

    if graph is None:
        graph = store.get_graph()

    store.init_schema(graph)
    store.upsert_repo(graph, repo_name, repo_path)

    # Extract authors from recent commits
    authors = set()
    for commit in repo.iter_commits(branch, max_count=100):
        authors.add((commit.author.name, commit.author.email))

    for name, email in authors:
        store.upsert_person(graph, name, email)

    # Get tracked files
    tracked = repo.git.ls_files().splitlines()
    indexable = [f for f in tracked if _should_index(f)]
    total = len(indexable)

    with Progress(disable=not sys.stdout.isatty()) as progress:
        task = progress.add_task(f"Indexing {repo_name}", total=total)
        for i, filepath in enumerate(indexable):
            full_path = os.path.join(repo_path, filepath)
            try:
                _index_file(graph, full_path, filepath, repo_name, repo)
            except Exception as e:
                progress.console.print(f"  [yellow]skip {filepath}: {e}[/]")
            progress.advance(task)
            if on_progress:
                on_progress(i + 1, total, filepath)

    # Run intelligence extraction
    intel = extract_all(repo_path, graph)

    # Run static analysis (import graph, symbols)
    static = build_import_graph(repo_path, graph)

    return {"repo": repo_name, "files_indexed": total, "intelligence": intel, "static_analysis": static}


def _should_index(filepath: str) -> bool:
    """Check if file should be indexed."""
    ext = Path(filepath).suffix.lower()
    parts = Path(filepath).parts
    if any(d in SKIP_DIRS for d in parts):
        return False
    if ext not in INDEXABLE_EXTENSIONS:
        return False
    return True


def _index_file(graph, full_path: str, relative_path: str, repo_name: str, repo: Repo):
    """Index a single file: chunk, embed, store with relationships."""
    if os.path.getsize(full_path) > MAX_FILE_SIZE:
        return

    with open(full_path, "r", errors="ignore") as f:
        content = f.read()

    if not content.strip():
        return

    ext = Path(full_path).suffix.lower()
    chunks = chunking.chunk_file(content, ext)
    if not chunks:
        return

    # Embed all chunks
    vectors = embeddings.embed_batch(chunks)

    # Store document node
    store.upsert_document(graph, relative_path, ext.lstrip("."), {"title": relative_path})
    store.link_document_to_repo(graph, relative_path, repo_name)

    # Get last author for this file
    try:
        last_commit = next(repo.iter_commits(paths=relative_path, max_count=1))
        store.link_person_authored(graph, last_commit.author.email, relative_path)
    except StopIteration:
        pass

    # Store chunks with embeddings
    for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
        cid = chunking.chunk_id(relative_path, i)
        store.upsert_chunk(
            graph, cid, chunk_text, vector,
            {"source": relative_path, "source_type": "code" if ext != ".md" else "docs"},
        )
        store.link_chunk_to_document(graph, cid, relative_path)
