# Quick Start

## 1. Start the system

```bash
km start
```

## 2. Index your first repository

```bash
km index ~/path/to/your/project
```

Knowledge Master will:

- Parse all code files (Python, TypeScript, Rust, Go, etc.)
- Split them into smart chunks (by function/class boundaries)
- Generate embeddings locally (nomic-embed-text via Ollama)
- Store in the knowledge graph with relationships
- Auto-detect tech stack, services, and conventions

## 3. Search

```bash
km search "how does authentication work"
```

Results include graph context: which repo, who authored it, related services.

## 4. Check blast radius

```bash
km blast-radius postgres
```

Shows everything that depends on postgres — repos, services, people.

## 5. Start the web UI

```bash
km serve
```

Open http://127.0.0.1:9999 for:

- Visual search with results
- Interactive knowledge graph visualization
- File browser for adding new sources
- Source management (add/remove)

## 6. Connect to AI agents

Knowledge Master works as an MCP server. Your AI agent can search, check blast radius, and enforce conventions directly.

See [MCP Integration](../guides/mcp-integration.md) for setup with Claude, Cursor, or Kiro.

## What's next?

- [Index emails from Outlook/Slack](../guides/connectors.md)
- [Understand search & re-ranking](../guides/search.md)
- [Set up convention enforcement](../guides/conventions.md)
