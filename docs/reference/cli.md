# CLI Reference

## Commands

| Command | Description |
|---|---|
| `km start` | Start Docker containers + pull Ollama model |
| `km stop` | Stop containers |
| `km index <path>` | Index a git repo or docs directory |
| `km search <query>` | Semantic search with re-ranking |
| `km blast-radius <target>` | Multi-layer dependency/impact analysis |
| `km who-owns <file>` | Show file ownership (git blame weighted by recency) |
| `km check-conventions <path>` | Verify conventions |
| `km connect <source>` | Pull from external MCP (email, Slack) |
| `km list` | Show indexed repos, tech stack, stats |
| `km remove <name>` | Remove a source |
| `km serve` | Start web UI (http://127.0.0.1:9999) |
| `km status` | System health check |

## Global options

All commands support `--help` for detailed usage.

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `KM_API_KEY` | API key for REST endpoint auth | None (disabled) |

## Examples

### Blast radius with multi-layer traversal

```bash
$ km blast-radius store.py
💥 Blast radius: store.py
├── Definite impact
│   ├── 📄 cli.py (Document, IMPORTS)
│   ├── 📄 server.py (Document, IMPORTS)
│   ├── 📄 web.py (Document, IMPORTS)
│   └── 📄 api.py (Document, IMPORTS)
├── Likely affected
│   └── ⚙️ falkordb (Service, owns affected file)
└── Possibly affected
    └── 👤 Alex (Person, AUTHORED affected file)
```

### File ownership

```bash
$ km who-owns auth/service.py
auth/service.py
  Owner: Alex (weight: 0.85)
```

Weight is computed from git blame, weighted by recency (recent changes count more).
