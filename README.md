# ⚡ Knowledge Master

**Your codebase's memory.** A local knowledge graph that gives AI agents real understanding of your architecture — not just text search.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Why

Every time you start a new AI chat, it forgets everything. You re-explain your architecture, conventions, dependencies. Knowledge Master gives your AI **permanent, structured memory** about your entire system.

Unlike flat RAG tools that return "chunks about X", Knowledge Master builds a **graph** — so it can answer "what breaks if I change X?" by traversing actual relationships.

## What it does

- 🔍 **Semantic search** across all your code, docs, and configs
- 🕸️ **Knowledge graph** — relationships between services, people, repos, technologies
- 💥 **Blast radius** — "what depends on this service/file/technology?"
- 📏 **Convention enforcement** — detects and enforces your team's patterns
- 🤖 **MCP server** — plugs directly into AI agents (Kiro, Claude, Cursor)
- 🖥️ **Web UI** — search, browse, visualize your knowledge graph
- 🔒 **Local-first** — nothing leaves your machine

## Prerequisites

| Dependency | macOS | Ubuntu/Debian | Windows |
|---|---|---|---|
| **Docker** | `brew install colima && colima start` or Docker Desktop | `sudo apt install docker.io docker-compose-plugin` | [Docker Desktop](https://docker.com/products/docker-desktop/) |
| **Ollama** | `brew install ollama && ollama serve` | `curl -fsSL https://ollama.com/install.sh \| sh` | [Ollama installer](https://ollama.com/download) |
| **Python 3.11+** | `brew install python@3.12` | `sudo apt install python3.12 python3.12-venv` | [python.org](https://python.org/downloads/) |

## Quick Start

```bash
# Clone
git clone https://github.com/subzone/knowledge-master.git
cd knowledge-master

# One command setup
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
km start

# Index your first repo
km index ~/path/to/your/project

# Search
km search "authentication flow"

# Check blast radius
km blast-radius postgres

# Start web UI with graph visualization
km serve
```

**Requirements:** Docker, Ollama, Python 3.11+

## Features

### Semantic Search with Graph Context
```bash
$ km search "how does auth work"
┌────────┬──────────────────────┬─────────────────────┬──────────────────────┐
│ Score  │ Source               │ Context             │ Preview              │
├────────┼──────────────────────┼─────────────────────┼──────────────────────┤
│ 0.847  │ src/auth/service.py  │ repo:myapp, by:Alex │ JWT token validat... │
│ 0.791  │ docs/auth.md         │ repo:myapp          │ Authentication f...  │
└────────┴──────────────────────┴─────────────────────┴──────────────────────┘
```

### Blast Radius Analysis
```bash
$ km blast-radius auth-service
💥 Blast radius: auth-service
├── ⚙️ user-service (Service, via DEPENDS_ON)
├── ⚙️ payment-service (Service, via DEPENDS_ON)
├── 📦 frontend (Repo, via USES_SERVICE)
└── 👤 Alex (Person, via AUTHORED)

4 entities affected
```

### Convention Enforcement
```bash
$ km check-conventions ~/my-project
  ✓ src/ directory (structure)
  ✓ separate test directory (testing)
  ✗ snake_case files (file-naming)
  ✓ Repository pattern (design-pattern)

1 convention(s) violated
```

### Web UI & Graph Visualization

```bash
$ km serve
Knowledge Master UI → http://127.0.0.1:9999
```

Interactive force-directed graph showing your entire knowledge topology:
- 📦 Repos (blue) → 🔧 Technologies (red)
- ⚙️ Services (orange) → Dependencies
- 👤 People → Authorship
- 📏 Conventions (purple)

### MCP Integration (AI Agents)

Add to your Kiro/Claude agent config:

```json
{
  "mcpServers": {
    "knowledge": {
      "command": "km-server"
    }
  }
}
```

Your AI agent gets these tools:
- `search` — semantic search with graph context
- `blast_radius` — dependency analysis
- `check_conventions` — verify code follows team patterns
- `index_repo` — add new repos to the knowledge base

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Your AI Agent                    │
│              (Kiro / Claude / Cursor)             │
└────────────────────┬────────────────────────────┘
                     │ MCP Protocol
┌────────────────────▼────────────────────────────┐
│              Knowledge Master                    │
│                                                  │
│  ┌──────────┐  ┌────────────┐  ┌────────────┐  │
│  │  Search  │  │Blast Radius│  │ Conventions│  │
│  └────┬─────┘  └─────┬──────┘  └─────┬──────┘  │
│       │               │               │         │
│  ┌────▼───────────────▼───────────────▼──────┐  │
│  │            FalkorDB (Graph + Vector)       │  │
│  │                                           │  │
│  │  [Repo]──USES_TECH──▶[Tech]              │  │
│  │    │                                      │  │
│  │    ├──DEFINES_SERVICE──▶[Service]         │  │
│  │    │                      │               │  │
│  │    ├──FOLLOWS──▶[Convention]              │  │
│  │    │                                      │  │
│  │  [Person]──AUTHORED──▶[Document]          │  │
│  │                          │                │  │
│  │                    [Chunk + Embedding]     │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │         Ollama (nomic-embed-text)          │  │
│  └───────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Commands

| Command | Description |
|---|---|
| `km start` | Boot Docker containers + pull embedding model |
| `km stop` | Stop containers |
| `km index <path>` | Index a git repo or docs directory |
| `km search <query>` | Semantic search with graph context |
| `km blast-radius <target>` | Show dependencies and affected entities |
| `km check-conventions <path>` | Verify code follows detected patterns |
| `km list` | Show indexed repos, techs, stats |
| `km remove <name>` | Remove a source from the knowledge base |
| `km serve` | Start web UI at http://127.0.0.1:9999 |
| `km status` | Check system health |

## What gets extracted automatically

When you index a repo, Knowledge Master detects:

| Category | Examples |
|---|---|
| **Tech stack** | Languages, frameworks, packages from dependency files |
| **Services** | From docker-compose.yml and K8s manifests |
| **Dependencies** | Service-to-service relationships |
| **Conventions** | File naming (snake_case/kebab-case), folder structure, design patterns |
| **People** | Git commit authors and file ownership |
| **Code structure** | Functions, classes, chunked by AST-aware boundaries |

## Comparison

| Feature | Knowledge Master | Generic RAG | GitHub Copilot | Glean |
|---|---|---|---|---|
| Graph relationships | ✅ | ❌ | ❌ | Partial |
| Blast radius analysis | ✅ | ❌ | ❌ | ❌ |
| Convention enforcement | ✅ | ❌ | ❌ | ❌ |
| Local-first (no cloud) | ✅ | ✅ | ❌ | ❌ |
| MCP integration | ✅ | ❌ | ❌ | ❌ |
| Multi-repo intelligence | ✅ | Partial | ❌ | ✅ |
| Cost | Free | Free | $19/mo | $15-30/mo |

## Development

```bash
# Run tests
pytest

# Lint
ruff check src/

# Run MCP server directly
python -m src.server
```

## Troubleshooting

| Issue | Fix |
|---|---|
| `km start` fails with "Docker not running" | Start Docker: `colima start` (macOS) or `sudo systemctl start docker` (Linux) |
| `km start` fails with "Ollama not found" | Install Ollama from https://ollama.com and run `ollama serve` |
| `km index` is slow | First run downloads the embedding model (~274MB). Subsequent runs are fast. |
| Web UI shows "Connection refused" | Make sure containers are running: `km start` |
| Search returns poor results | Index more content. Quality improves with more context in the graph. |
| Port 9999 already in use | Use `km serve --port 8888` |

## License

MIT
