# Blast Radius Analysis

Multi-layer dependency analysis that traces through code imports, services, and people.

## How it works

Knowledge Master traverses **4 layers**:

```
Layer 1: File imports (AST-resolved)     → Definite impact
Layer 2: Service ownership               → Likely affected
Layer 3: Service dependencies            → Likely affected
Layer 4: People (git blame ownership)    → Possibly affected
```

### Static analysis (Python)

For Python repos, Knowledge Master parses the AST to build a real import graph:
- Resolves relative imports (`from . import store`)
- Resolves package imports (`from .parsers import git_repo`)
- Extracts top-level functions and classes as symbols

### Confidence levels

| Level | Meaning | Example |
|---|---|---|
| **Definite** | Direct import dependency | `cli.py` imports `store.py` |
| **Likely** | Service that owns affected files | `auth-service` contains `store.py` |
| **Possible** | Transitive or ownership relationship | `Alex` owns `auth-service` |

## Usage

```bash
# File-level blast radius
km blast-radius store.py

# Function name
km blast-radius validate_token

# Service
km blast-radius postgres

# Technology
km blast-radius FastAPI
```

## MCP tool

AI agents can call `blast_radius` with any target:

```json
{"name": "blast_radius", "arguments": {"target": "store.py"}}
```

Returns structured JSON with definite/likely/possible groupings.

## Ownership

Use `km who-owns` to check file ownership:

```bash
km who-owns src/auth/service.py
```

Ownership is computed from git blame, weighted by recency:
- Lines changed in last 30 days: **3x weight**
- Lines changed 30-90 days ago: **2x weight**  
- Older lines: **1x weight**

This means the person who *recently* worked on a file is considered the owner, not someone who wrote it years ago.
