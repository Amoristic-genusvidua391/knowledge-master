# CLI Reference

## Commands

| Command | Description |
|---|---|
| `km start` | Start Docker containers + pull Ollama model |
| `km stop` | Stop containers |
| `km index <path>` | Index a git repo or docs directory |
| `km search <query>` | Semantic search with re-ranking |
| `km blast-radius <target>` | Dependency/impact analysis |
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
| `KM_PG_PASSWORD` | Postgres password | `km_local_dev` |
