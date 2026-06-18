# MCP Integration

Knowledge Master exposes an MCP server that any compatible AI agent can use.

## Start the MCP server

```bash
km-server
```

This runs on stdio (standard input/output) — the way MCP clients expect.

## Available tools

| Tool | Description |
|---|---|
| `search` | Semantic search with graph context |
| `blast_radius` | Dependency analysis |
| `check_conventions` | Convention verification |
| `index_repo` | Index a git repository |
| `index_directory` | Index a docs folder |
| `get_status` | Knowledge base stats |

## Setup guides

- [Claude Desktop](../integrations/claude-desktop.md)
- [Cursor](../integrations/cursor.md)
- [Kiro](../integrations/kiro.md)
