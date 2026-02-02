from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.models import Finding, Report
from patch.autopatch import Patch, generate_whitespace_patches
from utils.n8n_sanitize import sanitize_n8n_text


def _is_n8n_finding(f: Finding) -> bool:
    return str(getattr(f, 'id', '') or '').startswith('N8N.')


def generate_resolve_patches(repo_root: str, report: Report, *, diff_base: Optional[str] = None) -> Dict[str, Any]:
    """Generate a combined patch set that addresses the highest-confidence, safest findings.

    Current fixers (safe-by-default):
    - whitespace normalization (existing v11 autopatch)
    - n8n workflow JSON sanitizer (strip credential names/ids and replace likely secret literals)

    Returns dict with {patches: List[Patch], fixed_findings: List[str], notes: Dict}
    """

    patches: List[Patch] = []
    fixed_findings: List[str] = []
    notes: Dict[str, Any] = {}

    # Whitespace patches (diff-aware if diff_base set)
    ws_patches = generate_whitespace_patches(repo_root, report.analyzed_files, diff_base=diff_base)
    if ws_patches:
        patches.extend(ws_patches)

    # n8n sanitizer patches
    n8n_targets = {}
    for f in report.findings:
        if not _is_n8n_finding(f):
            continue
        if not f.evidence or not f.evidence.file:
            continue
        n8n_targets[f.evidence.file] = True

    n8n_patch_count = 0
    for fp in sorted(n8n_targets.keys()):
        p = Path(fp)
        if not p.exists() or not p.is_file():
            continue
        try:
            orig = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        fixed, changed, info = sanitize_n8n_text(orig)
        if not changed:
            continue

        diff = ''.join(difflib.unified_diff(
            orig.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile=str(p),
            tofile=str(p),
        ))
        patches.append(Patch(
            file=str(p),
            description='Sanitize n8n workflow JSON (strip credential ids/names; replace secret literals with placeholders)',
            diff=diff,
            applied=False,
        ))
        n8n_patch_count += 1
        notes.setdefault('n8n_sanitize', []).append({'file': str(p), **info})

    if n8n_patch_count:
        for f in report.findings:
            if _is_n8n_finding(f):
                fixed_findings.append(f.id)

    return {
        'patches': patches,
        'fixed_findings': sorted(set(fixed_findings)),
        'notes': notes,
    }
