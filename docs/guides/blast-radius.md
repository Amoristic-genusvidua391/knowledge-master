# Blast Radius Analysis

The killer feature that flat RAG tools can't do. Knowledge Master traverses the **graph** to answer "what depends on X?"

## Usage

```bash
km blast-radius <target>
```

Target can be:
- A **service name** (from docker-compose or K8s)
- A **technology** (Python, FastAPI, Redis)
- A **file path** (partial match)

## How it works

The graph stores explicit relationships:

```
Service A --DEPENDS_ON--> Service B
Repo --USES_TECH--> Technology
Repo --DEFINES_SERVICE--> Service
Person --AUTHORED--> Document
```

Blast radius walks these edges up to 3 hops deep, collecting all affected entities.

## Examples

```bash
$ km blast-radius postgres
💥 Blast radius: postgres
├── ⚙️ auth-service (Service, via DEPENDS_ON)
├── ⚙️ analytics (Service, via DEPENDS_ON)
├── 📦 backend (Repo, via DEFINES_SERVICE)
└── 👤 Alex (Person, via AUTHORED)

$ km blast-radius FastAPI
💥 Blast radius: FastAPI
├── 📦 auth-api (Repo, via USES_TECH)
├── 📦 data-service (Repo, via USES_TECH)
└── 📦 knowledge-master (Repo, via USES_TECH)
```
