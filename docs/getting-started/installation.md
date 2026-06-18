# Installation

## Prerequisites

| Dependency | macOS | Ubuntu/Debian | Windows |
|---|---|---|---|
| **Docker** | `brew install colima && colima start` | `sudo apt install docker.io docker-compose-plugin` | [Docker Desktop](https://docker.com/products/docker-desktop/) |
| **Ollama** | `brew install ollama && ollama serve` | `curl -fsSL https://ollama.com/install.sh \| sh` | [Ollama installer](https://ollama.com/download) |
| **Python 3.11+** | `brew install python@3.12` | `sudo apt install python3.12 python3.12-venv` | [python.org](https://python.org/downloads/) |

## Install Knowledge Master

### From PyPI (recommended)

```bash
pip install knowledge-master
```

Or with pipx for isolated install:

```bash
pipx install knowledge-master
```

### From source

```bash
git clone https://github.com/subzone/knowledge-master.git
cd knowledge-master
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Verify installation

```bash
km --help
```

You should see the list of available commands.

## First run

```bash
km start
```

This will:

1. Start FalkorDB and Postgres containers (Docker)
2. Pull the `nomic-embed-text` embedding model (Ollama, ~274MB one-time download)
3. Initialize the graph schema

!!! success "You're ready"
    If you see "Knowledge Master is ready!", proceed to [Quick Start](quickstart.md).

## Troubleshooting

| Issue | Fix |
|---|---|
| `km: command not found` | Ensure your Python bin is in PATH, or use `python -m knowledge_master` |
| Docker not running | macOS: `colima start` · Linux: `sudo systemctl start docker` |
| Ollama not found | Install from https://ollama.com |
| Port 6379 already in use | Another Redis/FalkorDB is running. Stop it or change port in docker-compose.yml |
