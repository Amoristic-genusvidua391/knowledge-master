# ⚡ Knowledge Master

**Your codebase's memory.** A local knowledge graph that gives AI agents real understanding of your architecture — not just text search.

## What you get

| Capability | Description |
|---|---|
| 🔍 **Semantic Search** | Find code, docs, emails by meaning — not just keywords |
| 🕸️ **Knowledge Graph** | Relationships between services, people, repos, technologies |
| 💥 **Blast Radius** | "What breaks if I change X?" — instant dependency analysis |
| 📏 **Convention Enforcement** | Detects your team's patterns and enforces them |
| 🤖 **MCP Server** | Plugs directly into AI agents (Claude, Cursor, Kiro) |
| 🖥️ **Web UI** | Visual graph, search, file browser |
| 🔒 **100% Local** | Nothing leaves your machine. Ever. |

## How it works

```
Your repos + docs + emails
        ↓ index
  ┌─────────────────────────┐
  │   Knowledge Graph        │
  │   (FalkorDB)            │
  │                         │
  │   Repo → Tech           │
  │   Repo → Service        │
  │   Person → Document     │
  │   Chunk + Embedding     │
  └─────────────────────────┘
        ↓ query
  AI Agent gets precise,
  grounded answers with
  full context
```

## Performance

| Metric | Value |
|---|---|
| Search latency | ~100ms (with re-ranking) |
| Token savings | 60-80% fewer tokens for codebase questions |
| Accuracy | ~85-90% precision (vs ~50% without RAG) |
| Indexing speed | ~100 files/minute |
| Storage overhead | ~3x raw data size |
| RAM usage (idle) | ~400MB total |

## Get started

```bash
pip install knowledge-master
km start
km index ~/your-project
km search "how does auth work"
```

→ [Full installation guide](getting-started/installation.md)
