from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from utils.hash_utils import sha256_text


def load_skills_lock(repo_root: str) -> Dict[str, Any]:
    """Load skills.lock.json (if present)."""
    root = Path(repo_root)
    candidates = [root / 'skills.lock.json', root / '.vibe' / 'skills.lock.json']
    for p in candidates:
        if p.exists() and p.is_file():
            try:
                data = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
    return {}


def file_sha256(path: str) -> str:
    p = Path(path)
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        text = ''
    return sha256_text(text)


def verify_skill_pinned(*, rel_path: str, abs_path: str, lock: Dict[str, Any]) -> Tuple[bool, str]:
    """Return (ok, reason)."""
    entries = lock.get('skills')
    if not isinstance(entries, list):
        return False, 'missing_lock_entries'

    expected = None
    for e in entries:
        if not isinstance(e, dict):
            continue
        if str(e.get('path') or '') == rel_path:
            expected = e
            break

    if expected is None:
        return False, 'not_listed'

    for k in ('source_repo', 'source_commit', 'sha256'):
        if not str(expected.get(k) or '').strip():
            return False, f'missing_{k}'

    actual = file_sha256(abs_path)
    if actual != str(expected.get('sha256')):
        return False, 'sha_mismatch'

    return True, 'ok'
