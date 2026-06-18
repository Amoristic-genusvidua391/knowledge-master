# Your First Index

## What happens when you index a repo

```bash
km index ~/my-project
```

Knowledge Master performs these steps:

1. **Discovers files** — walks git-tracked files, skips node_modules/.venv/build
2. **Parses by type** — code files split by function, markdown by heading
3. **Embeds chunks** — generates 768-dim vectors via Ollama (local)
4. **Extracts intelligence** — detects tech stack, services, conventions
5. **Builds graph** — creates nodes and relationships

## What gets created in the graph

```
📦 Repo (my-project)
├── 🔧 USES_TECH → Python, FastAPI, Docker, ...
├── ⚙️ DEFINES_SERVICE → api, postgres, redis
├── 📏 FOLLOWS → snake_case, src/ directory, separate tests
├── 📄 Documents (your files)
│   ├── 🧩 Chunks (with embeddings)
│   └── 👤 AUTHORED_BY → Person (from git history)
└── ⚙️ Service DEPENDS_ON → other services
```

## Supported file types

| Extension | Chunking strategy |
|---|---|
| `.py` | By function/class definition |
| `.ts`, `.tsx`, `.js` | By export/function/class |
| `.rs` | By fn/impl/struct |
| `.go` | By func |
| `.md`, `.markdown` | By heading section |
| `.yaml`, `.yml` | Full file (configs) |
| `.json`, `.toml` | Full file |
| `.txt` | By paragraph |

## Intelligence auto-detection

| What | How it's detected |
|---|---|
| **Languages** | Presence of pyproject.toml, package.json, Cargo.toml, go.mod |
| **Packages** | Parsed from dependency files |
| **Services** | docker-compose.yml service definitions, K8s Deployments |
| **Dependencies** | depends_on in docker-compose |
| **Conventions** | File naming patterns, folder structure, design patterns in code |
| **Authors** | Git commit history (last 100 commits) |

## Tips for best results

- **Index at the repo root** — ensures git history and docker-compose are found
- **Index multiple repos** — cross-repo intelligence emerges (shared tech, shared authors)
- **Re-index after major changes** — `km index ~/project` is idempotent (updates existing)
