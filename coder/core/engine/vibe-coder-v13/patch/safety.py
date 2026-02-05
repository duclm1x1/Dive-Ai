from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


_DIFF_FILE_RE = re.compile(r'^\+\+\+ b/(.+)$', re.MULTILINE)


@dataclass
class PatchConstraints:
    """Safety constraints for automated patches.

    This is a guardrail layer: even if a patch is syntactically valid, it should
    remain reviewable and refactor-safe.
    """
    max_files_touched: int = 5
    forbid_whitespace_only: bool = True
    forbid_generated: bool = True


def touched_files(unified_diff_text: str) -> List[str]:
    return sorted(set(_DIFF_FILE_RE.findall(unified_diff_text or '')))


def is_whitespace_only_change(unified_diff_text: str) -> bool:
    """Best-effort heuristic: if all added/removed lines differ only by whitespace."""
    adds: List[str] = []
    dels: List[str] = []
    for ln in (unified_diff_text or '').splitlines():
        if ln.startswith('+++') or ln.startswith('---') or ln.startswith('@@'):
            continue
        if ln.startswith('+'):
            adds.append(ln[1:])
        elif ln.startswith('-'):
            dels.append(ln[1:])
    if not adds and not dels:
        return False
    # Compare normalized
    norm_add = [a.strip() for a in adds if a.strip() != '']
    norm_del = [d.strip() for d in dels if d.strip() != '']
    return sorted(norm_add) == sorted(norm_del)


def validate_patch(unified_diff_text: str, constraints: Optional[PatchConstraints] = None) -> Tuple[bool, List[str]]:
    c = constraints or PatchConstraints()
    reasons: List[str] = []

    files = touched_files(unified_diff_text)
    if len(files) > int(c.max_files_touched):
        reasons.append(f'Patch touches {len(files)} files (limit {c.max_files_touched}).')

    if c.forbid_whitespace_only and is_whitespace_only_change(unified_diff_text):
        reasons.append('Patch appears to be whitespace-only (forbidden by policy).')

    if c.forbid_generated:
        for f in files:
            lf = f.lower()
            if 'dist/' in lf or 'build/' in lf or lf.endswith('.min.js'):
                reasons.append(f'Patch touches likely-generated output: {f}')

    return (len(reasons) == 0), reasons
