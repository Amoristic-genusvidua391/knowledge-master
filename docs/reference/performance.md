# Performance & Resource Usage

## Token usage (AI agent context)

| Scenario | Without Knowledge Master | With Knowledge Master |
|---|---|---|
| "How does auth work?" | Paste 5 files (~15K tokens) | Retrieves 5 chunks (~2K tokens) |
| "What depends on postgres?" | Manual grep + explain (~5K tokens) | Blast radius in ~200 tokens |
| "Does this follow conventions?" | Describe rules manually (~1K tokens) | Structured check in ~300 tokens |
| Re-explaining architecture | Every session (~3K tokens) | Never (persisted in graph) |

**Net effect:** 60-80% fewer tokens for codebase questions.

## Speed

| Operation | Latency | Bottleneck |
|---|---|---|
| Search (vector) | 5-10ms | FalkorDB HNSW index |
| Search (with re-ranking) | 50-80ms | Ollama re-scoring |
| Blast radius | 2-5ms | Graph traversal |
| Convention check | 1-2ms | Filesystem |
| Index (per file) | 300-500ms | Ollama embedding |
| Index (100 files) | 40-60s | Sequential embedding |
| Full MCP tool call | 100-150ms | Embed + search + rerank |

## Accuracy

| Method | Precision@5 | Notes |
|---|---|---|
| LLM guessing (no RAG) | ~50% | Hallucinates confidently |
| Raw vector search | ~60-70% | Finds topically related chunks |
| Vector + re-ranking | ~80-85% | Promotes actual answers |
| Vector + re-ranking + graph | ~85-90% | Adds relationship context |
| Blast radius (graph only) | ~100% | Deterministic traversal |
| Convention check | ~100% | Rule-based verification |

## Resource usage

### Idle (containers running, no queries)

| Component | RAM | CPU | Disk |
|---|---|---|---|
| FalkorDB | 80-128 MB | <1% | Depends on data |
| Postgres | 30-64 MB | <1% | Minimal |
| Ollama (model loaded) | 300 MB | 0% | 274 MB (model file) |
| **Total** | **~400-500 MB** | **<1%** | |

### During indexing

| Component | RAM | CPU | Notes |
|---|---|---|---|
| FalkorDB | 200-500 MB | Low | Grows with data |
| Ollama | 500 MB-1 GB | High (1 core) | Embedding inference |
| Python process | 100-200 MB | Low | Chunking + I/O |
| **Total** | **~1-1.5 GB** | **1 core** | |

### Storage growth

| Data indexed | Vector storage | Total on disk |
|---|---|---|
| 1,000 files | ~500 MB | ~800 MB |
| 10,000 files | ~3 GB | ~5 GB |
| 50,000 files | ~15 GB | ~25 GB |
| 100 emails | ~50 MB | ~80 MB |

Rule of thumb: **~3x raw data size** for vectors + metadata.

## Scaling limits

| Metric | Comfortable limit | Hard limit |
|---|---|---|
| Total chunks | 500K | 2M (FalkorDB memory) |
| Repos indexed | 50 | Unlimited (disk-bound) |
| Concurrent searches | 10 | ~50 (single FalkorDB instance) |
| Search latency at scale | <200ms at 1M chunks | Degrades above 2M |

## Optimization tips

1. **Index selectively** — skip generated files, vendor dirs, build artifacts
2. **Use `--type docs`** for non-code directories (skips git history extraction)
3. **Restart Ollama** if embedding slows down (memory leak in long sessions)
4. **Increase FalkorDB memory** for large graphs: edit `deploy.resources.limits.memory` in docker-compose.yml
