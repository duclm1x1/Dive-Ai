from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class RunRow:
    run_id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    last_seq: int


class MonitorStore:
    """
    Small, dependency-free (sqlite3) store.

    - Append-only events table (seq AUTOINCREMENT)
    - Runs table for list view
    - JSONL append for easy file tail/debug

    Designed for:
      - POST /v1/ingest
      - GET /v1/stream/events (SSE)
      - GET /v1/runs
      - GET /v1/runs/{run_id}/snapshot
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "monitor.db"
        self.jsonl_path = self.data_dir / "events.jsonl"

        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  ts TEXT NOT NULL,
                  run_id TEXT NOT NULL,
                  type TEXT NOT NULL,
                  step_id TEXT,
                  trace_id TEXT,
                  span_id TEXT,
                  parent_span_id TEXT,
                  data_json TEXT NOT NULL
                );
                """
            )
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_events_run_seq ON events(run_id, seq);")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_events_seq ON events(seq);")

            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                  run_id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  last_seq INTEGER NOT NULL DEFAULT 0
                );
                """
            )

    def ingest_events(self, events: Iterable[Dict[str, Any]]) -> List[int]:
        """Insert envelopes; returns assigned seqs."""
        seqs: List[int] = []
        for env in events:
            seqs.append(self.ingest_event(env))
        return seqs

    def ingest_event(self, env: Dict[str, Any]) -> int:
        # Normalize envelope
        run_id = str(env.get("run_id") or "").strip()
        if not run_id:
            raise ValueError("run_id is required")

        ev_type = str(env.get("type") or "").strip()
        if not ev_type:
            raise ValueError("type is required")

        ts = str(env.get("ts") or "").strip() or _utc_now_iso()

        step_id = env.get("step_id")
        trace_id = env.get("trace_id")
        span_id = env.get("span_id")
        parent_span_id = env.get("parent_span_id")

        # keep payload flexible
        payload = env.get("payload") if isinstance(env.get("payload"), dict) else env.get("payload")
        normalized: Dict[str, Any] = {
            "v": int(env.get("v") or 1),
            "ts": ts,
            "run_id": run_id,
            "type": ev_type,
            "step_id": step_id,
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "payload": payload,
        }

        data_json = _safe_json_dumps(normalized)

        with self._lock:
            with self._conn:
                cur = self._conn.execute(
                    """
                    INSERT INTO events(ts, run_id, type, step_id, trace_id, span_id, parent_span_id, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ts,
                        run_id,
                        ev_type,
                        str(step_id) if step_id is not None else None,
                        str(trace_id) if trace_id is not None else None,
                        str(span_id) if span_id is not None else None,
                        str(parent_span_id) if parent_span_id is not None else None,
                        data_json,
                    ),
                )
                seq = int(cur.lastrowid)

                # Update runs
                title, status = self._derive_run_fields(run_id, ev_type, payload)
                now = ts

                row = self._conn.execute("SELECT run_id,title,status,created_at,updated_at,last_seq FROM runs WHERE run_id=?", (run_id,)).fetchone()
                if row is None:
                    self._conn.execute(
                        "INSERT INTO runs(run_id,title,status,created_at,updated_at,last_seq) VALUES (?,?,?,?,?,?)",
                        (run_id, title or run_id, status or "running", now, now, seq),
                    )
                else:
                    new_title = title or row["title"]
                    new_status = status or row["status"]
                    self._conn.execute(
                        "UPDATE runs SET title=?, status=?, updated_at=?, last_seq=? WHERE run_id=?",
                        (new_title, new_status, now, seq, run_id),
                    )

                # Append JSONL (best-effort)
                try:
                    with self.jsonl_path.open("a", encoding="utf-8") as f:
                        f.write(_safe_json_dumps({"seq": seq, **normalized}) + "\n")
                except Exception:
                    pass

        return seq

    def _derive_run_fields(self, run_id: str, ev_type: str, payload: Any) -> Tuple[Optional[str], Optional[str]]:
        title = None
        status = None
        if ev_type == "run_start":
            if isinstance(payload, dict):
                title = payload.get("title") or payload.get("name")
                status = payload.get("status") or "running"
            else:
                status = "running"
        elif ev_type == "run_update":
            if isinstance(payload, dict):
                title = payload.get("title")
                status = payload.get("status")
        elif ev_type == "run_end":
            if isinstance(payload, dict):
                status = payload.get("status") or "completed"
            else:
                status = "completed"
        return title, status

    def list_runs(self, limit: int = 50, offset: int = 0) -> List[RunRow]:
        limit = max(1, min(int(limit), 200))
        offset = max(0, int(offset))
        rows = self._conn.execute(
            "SELECT run_id,title,status,created_at,updated_at,last_seq FROM runs ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [
            RunRow(
                run_id=r["run_id"],
                title=r["title"],
                status=r["status"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                last_seq=int(r["last_seq"]),
            )
            for r in rows
        ]

    def get_run(self, run_id: str) -> Optional[RunRow]:
        r = self._conn.execute(
            "SELECT run_id,title,status,created_at,updated_at,last_seq FROM runs WHERE run_id=?",
            (run_id,),
        ).fetchone()
        if not r:
            return None
        return RunRow(
            run_id=r["run_id"],
            title=r["title"],
            status=r["status"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            last_seq=int(r["last_seq"]),
        )

    def list_events_after(
        self,
        after_seq: int = 0,
        run_id: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        after_seq = max(0, int(after_seq))
        limit = max(1, min(int(limit), 5000))

        if run_id:
            rows = self._conn.execute(
                "SELECT seq, data_json FROM events WHERE run_id=? AND seq>? ORDER BY seq ASC LIMIT ?",
                (run_id, after_seq, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT seq, data_json FROM events WHERE seq>? ORDER BY seq ASC LIMIT ?",
                (after_seq, limit),
            ).fetchall()

        out: List[Dict[str, Any]] = []
        for r in rows:
            env = json.loads(r["data_json"])
            env["seq"] = int(r["seq"])
            out.append(env)
        return out

    def build_snapshot(self, run_id: str, max_events: int = 5000) -> Dict[str, Any]:
        """Derive minimal UI snapshot (steps, metrics, rag, evidence) from events."""
        max_events = max(100, min(int(max_events), 20000))
        rows = self._conn.execute(
            "SELECT seq, data_json FROM events WHERE run_id=? ORDER BY seq ASC LIMIT ?",
            (run_id, max_events),
        ).fetchall()
        events: List[Dict[str, Any]] = []
        for r in rows:
            env = json.loads(r["data_json"])
            env["seq"] = int(r["seq"])
            events.append(env)

        run = self.get_run(run_id)
        if not run:
            raise KeyError(run_id)

        # Reduce events into a UI-friendly structure
        steps: Dict[str, Dict[str, Any]] = {}
        metrics: Dict[str, Any] = {}
        rag: Dict[str, Any] = {"queries": [], "results": []}
        evidencepack: Optional[Dict[str, Any]] = None

        for ev in events:
            t = ev.get("type")
            payload = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
            step_id = ev.get("step_id")

            if t in {"step_start", "step_update", "step_end"} and step_id:
                s = steps.setdefault(
                    str(step_id),
                    {
                        "step_id": str(step_id),
                        "step_type": payload.get("step_type") or payload.get("type") or "",
                        "title": payload.get("title") or str(step_id),
                        "status": payload.get("status") or "running",
                        "started_at": None,
                        "ended_at": None,
                        "stats": {},
                    },
                )
                if t == "step_start":
                    s["status"] = payload.get("status") or "running"
                    s["started_at"] = ev.get("ts")
                elif t == "step_update":
                    if payload.get("status"):
                        s["status"] = payload.get("status")
                    if payload.get("stats"):
                        s["stats"] = payload.get("stats")
                elif t == "step_end":
                    s["status"] = payload.get("status") or "completed"
                    s["ended_at"] = ev.get("ts")
                    if payload.get("stats"):
                        s["stats"] = payload.get("stats")

            if t == "metrics_update":
                if isinstance(payload, dict):
                    metrics = payload

            if t in {"rag_query", "rag_results"}:
                if t == "rag_query":
                    rag["queries"].append({"seq": ev.get("seq"), **payload})
                else:
                    rag["results"].append({"seq": ev.get("seq"), **payload})

            if t in {"evidence_pack_ready", "evidencepack_ready"}:
                if isinstance(payload, dict):
                    evidencepack = payload

        # Timeline is raw events (cap for UI)
        timeline = events[-2000:]

        return {
            "run": {
                "run_id": run.run_id,
                "title": run.title,
                "status": run.status,
                "created_at": run.created_at,
                "updated_at": run.updated_at,
            },
            "steps": list(steps.values()),
            "metrics": metrics,
            "rag": rag,
            "evidencepack": evidencepack,
            "timeline": timeline,
        }


def load_store(data_dir: Path) -> MonitorStore:
    return MonitorStore(data_dir=data_dir)
