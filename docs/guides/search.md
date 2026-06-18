# Search & Re-ranking

Knowledge Master uses a two-pass search strategy:

1. **Vector search** — finds top 30 semantically similar chunks (fast, ~5ms)
2. **Re-ranking** — scores each candidate against your query (precise, ~50ms)
3. **Graph enrichment** — adds author, repo, and relationship context

## How re-ranking works

Raw cosine similarity finds "topically related" text. The re-ranker finds text that **actually answers your question**.

```bash
# Without re-ranking: score 0.3-0.5 (everything feels equally relevant)
# With re-ranking: score 0.85-0.95 (clear best answers surface)
```

## Filtering by source type

```bash
km search "deployment config" --type code    # only code files
km search "auth migration" --type email      # only emails
km search "architecture" --type docs         # only markdown/docs
```

## Tips for better results

- Be specific: "JWT token validation in auth service" > "how does auth work"
- Index more repos: cross-repo results emerge with more data
- Re-index after major refactors: `km index ~/project` updates existing chunks
