from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from iko.models import IKO


def _safe_id(s: str) -> str:
    s = (s or '').strip()
    if not s:
        return 'UNKNOWN'
    return ''.join(ch for ch in s if ch.isalnum() or ch in ('-', '_', '.'))


def iko_dir(repo_root: str) -> Path:
    return Path(repo_root) / '.vibe' / 'iko'


def iko_path(repo_root: str, issue_id: str) -> Path:
    return iko_dir(repo_root) / f"{_safe_id(issue_id)}.json"


def save(repo_root: str, iko: IKO) -> str:
    d = iko_dir(repo_root)
    d.mkdir(parents=True, exist_ok=True)
    p = iko_path(repo_root, iko.id)
    p.write_text(json.dumps(iko.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)


def load(repo_root: str, issue_id: str) -> Optional[IKO]:
    p = iko_path(repo_root, issue_id)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
        if not isinstance(data, dict):
            return None
        return IKO.from_dict(data)
    except Exception:
        return None


def list_ids(repo_root: str) -> List[str]:
    d = iko_dir(repo_root)
    if not d.exists():
        return []
    return [fp.stem for fp in sorted(d.glob('*.json'))]
