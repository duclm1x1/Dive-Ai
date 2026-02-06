# Dive Monitor Server (v15)

FastAPI observability server for **Dive Monitor** (UI) and Antigravity ingestion.

## Run (Option A: server serves UI)

```bash
pip install -r monitor_server/requirements.txt
uvicorn monitor_server.app.main:app --host 0.0.0.0 --port 8787
```

Open:
- `http://localhost:8787/` (Dive Monitor dist-lite)
- `http://localhost:8787/openapi.yaml`

## Ingest

POST events:

```http
POST /v1/ingest
{
  "events": [ {"run_id":"...","type":"run_start","payload":{...}} ]
}
```

## Stream

```http
GET /v1/stream/events?after_seq=0
```

SSE frames:
- `event: dive`
- `id: <seq>`
- `data: <event envelope json>`
