# REST API Reference

Base URL: `http://127.0.0.1:9999/api/v1`

OpenAPI docs: `http://127.0.0.1:9999/docs`

## Authentication

Optional. Set `KM_API_KEY` env var to enable:

```bash
curl -H "X-API-Key: your-key" http://127.0.0.1:9999/api/v1/search?q=test
```

## Endpoints

### GET /api/v1/search

```
?q=your+query&top_k=10&source_type=code
```

### GET /api/v1/blast-radius/{target}

```
/api/v1/blast-radius/postgres
```

### GET /api/v1/conventions/check

```
?path=/home/user/project
```

### POST /api/v1/index

```
?path=/home/user/repo&type=auto
```

### GET /api/v1/status

Returns: `{"chunks": N, "documents": N, "repos": N}`
