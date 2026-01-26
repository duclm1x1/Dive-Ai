from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .models import Finding, Report


def _key(f: Finding) -> Tuple[str, str, int]:
    return (
        f.id,
        f.evidence.file if f.evidence else '',
        int(f.evidence.start_line) if f.evidence else 0,
    )


def write_baseline(repo_root: str, report: Report, filename: str = 'baseline.json') -> str:
    p = Path(repo_root) / '.vibe' / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)


def load_report(path: str) -> Dict[str, Any]:
    p = Path(path)
    return json.loads(p.read_text(encoding='utf-8'))


def new_findings(baseline: Dict[str, Any], current: Report) -> List[Finding]:
    base = baseline.get('findings') if isinstance(baseline, dict) else []
    base_keys = set()
    if isinstance(base, list):
        for f in base:
            if not isinstance(f, dict):
                continue
            ev = f.get('evidence') or {}
            base_keys.add((
                str(f.get('id') or ''),
                str(ev.get('file') or ''),
                int(ev.get('start_line') or 0),
            ))

    out: List[Finding] = []
    for f in current.findings:
        if _key(f) not in base_keys:
            out.append(f)
    return out
