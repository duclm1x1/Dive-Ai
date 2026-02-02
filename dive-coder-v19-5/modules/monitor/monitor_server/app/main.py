from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from fastapi import Body, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .store import load_store


def _repo_root() -> Path:
    # monitor_server/app/main.py -> monitor_server -> repo root
    return Path(__file__).resolve().parents[2]


def _data_dir(repo_root: Path) -> Path:
    # keeps persistent data inside repo (safe for local dev)
    return repo_root / ".dive_monitor"


def _ui_dist_dir(repo_root: Path) -> Path:
    # Option A: serve dist-lite or real dist if built
    return repo_root / "ui" / "dive-monitor" / "dist"


REPO_ROOT = _repo_root()
DATA_DIR = Path(os.environ.get("DIVE_MON_DATA_DIR", str(_data_dir(REPO_ROOT))))
UI_DIST_DIR = Path(os.environ.get("DIVE_MON_UI_DIST_DIR", str(_ui_dist_dir(REPO_ROOT))))

store = load_store(DATA_DIR)

app = FastAPI(title="Dive Monitor Server", version="15.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "version": "15.0.0",
        "ui_dist_present": UI_DIST_DIR.exists(),
    }


@app.post("/v1/ingest")
def ingest(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    # supports {events:[...]}, {event:{...}}, or a single event envelope
    events = None
    if isinstance(payload.get("events"), list):
        events = payload["events"]
    elif isinstance(payload.get("event"), dict):
        events = [payload["event"]]
    else:
        # assume payload itself is an envelope
        events = [payload]

    res = store.ingest_events(events)
    return {
        "ok": True,
        "inserted": len(res),
        "seq": [r["seq"] for r in res],
    }


@app.get("/v1/runs")
def list_runs(limit: int = 50, offset: int = 0):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    return {"runs": store.list_runs(limit=limit, offset=offset)}


@app.get("/v1/runs/{run_id}/snapshot")
def run_snapshot(run_id: str):
    snap = store.build_snapshot(run_id)
    if not snap:
        raise HTTPException(status_code=404, detail="run not found")
    return snap


@app.get("/v1/runs/{run_id}/evidencepack")
def run_evidencepack(run_id: str):
    ep = store.get_latest_evidencepack(run_id)
    if not ep:
        raise HTTPException(status_code=404, detail="evidencepack not found")
    return ep


@app.get("/v1/stream/events")
def stream_events(request: Request, run_id: Optional[str] = None, after_seq: int = 0):
    # SSE endpoint. Supports Last-Event-ID resume.
    last_event_id = request.headers.get("last-event-id")
    if last_event_id and str(last_event_id).isdigit():
        after_seq = max(after_seq, int(last_event_id))

    def gen():
        nonlocal after_seq
        # initial backlog
        heartbeat_every = 10.0
        last_hb = 0.0

        while True:
            if request.client is None:
                break
            if request.is_disconnected():
                break

            events = store.list_events_after(after_seq=after_seq, run_id=run_id, limit=500)
            if events:
                for ev in events:
                    after_seq = max(after_seq, int(ev.get("seq", after_seq)))
                    data = json.dumps(ev, ensure_ascii=False)
                    # event name fixed to "dive" to match UI provider
                    yield f"event: dive\nid: {ev['seq']}\ndata: {data}\n\n"

            now = os.times()[4]
            if now - last_hb >= heartbeat_every:
                last_hb = now
                yield ": hb\n\n"

            # short sleep
            import time as _t

            _t.sleep(0.5)

    return StreamingResponse(gen(), media_type="text/event-stream")


# -------------------------
# OpenAPI (YAML)
# -------------------------

@app.get("/openapi.yaml")
def openapi_yaml() -> Response:
    spec = app.openapi()
    y = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
    return PlainTextResponse(y, media_type="application/yaml")


# -------------------------
# Static UI (Option A)
# -------------------------

if UI_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(UI_DIST_DIR), html=True), name="ui")


@app.get("/{path:path}")
def spa_fallback(path: str):
    # If UI is mounted, StaticFiles handles existing files.
    # This fallback serves index.html for client-side routing.
    idx = UI_DIST_DIR / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return JSONResponse(
        {
            "error": "UI dist not found",
            "hint": "Expected ui/dive-monitor/dist. Use dist-lite (already provided) or build UI.",
        },
        status_code=404,
    )
