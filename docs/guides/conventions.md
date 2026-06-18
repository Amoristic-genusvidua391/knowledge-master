# Convention Enforcement

Knowledge Master learns your team's patterns and can verify new code follows them.

## Auto-detection

When you index a repo, these conventions are detected automatically:

| Convention | How detected |
|---|---|
| `snake_case files` | >50% of code files use underscores |
| `kebab-case files` | >30% of code files use hyphens |
| `src/ directory` | src/ exists at root |
| `separate test directory` | tests/ or test/ exists |
| `docs/ directory` | docs/ exists |
| `infra as code` | infra/, deploy/, or k8s/ exists |
| `Repository pattern` | Classes named *Repository in code |
| `Route decorators` | @app.route or @router found |

## Checking conventions

```bash
km check-conventions ~/my-project
```

## Using via MCP (AI agent enforces conventions)

Your AI agent can call `check_conventions` before suggesting code changes, ensuring new code matches existing patterns.
