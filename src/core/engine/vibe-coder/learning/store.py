from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from core.models import Report, utc_now_iso


@dataclass
class LearningEvent:
    """Append-only run telemetry for local learning loops.

    This is NOT chat memory. It's repo-local operational data to improve routing,
    prioritization, and regression prevention.
    """
    event_id: str
    ts: str
    task: str
    mode: str
    outcome: str  # ok|fail
    evidence_level: str
    findings_count: int
    gates_failed: int
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def append_event(repo_root: str, report: Report, *, outcome: str, meta: Optional[Dict[str, Any]] = None) -> str:
    rr = Path(repo_root).resolve()
    out = rr / '.vibe' / 'learning' / 'events.jsonl'
    out.parent.mkdir(parents=True, exist_ok=True)

    eid = f"{utc_now_iso()}-{abs(hash(report.task)) % 10_000_000}"
    gates_failed = 0
    try:
        for g in report.gates or []:
            if g.exit_code and int(g.exit_code) != 0:
                gates_failed += 1
    except Exception:
        pass

    ev = LearningEvent(
        event_id=eid,
        ts=utc_now_iso(),
        task=report.task or '',
        mode=report.mode or '',
        outcome=str(outcome),
        evidence_level=str(getattr(report, 'evidence_level', 'E0')),
        findings_count=len(report.findings or []),
        gates_failed=int(gates_failed),
        meta=dict(meta or {}),
    )
    with out.open('a', encoding='utf-8') as f:
        f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + '\n')
    return str(out)
