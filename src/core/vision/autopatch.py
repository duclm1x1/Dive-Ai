from __future__ import annotations

import difflib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Patch:
    file: str
    description: str
    diff: str
    applied: bool = False


_HUNK_RE = re.compile(r'^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,(\d+))?\s+@@')


def _strip_trailing_ws_preserve_newline(ln: str) -> str:
    if ln.endswith('\r\n'):
        body, newline = ln[:-2], '\r\n'
    elif ln.endswith('\n'):
        body, newline = ln[:-1], '\n'
    else:
        body, newline = ln, ''
    body = body.rstrip(' \t')
    return body + newline


def _parse_changed_line_ranges(diff_text: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    for line in diff_text.splitlines():
        m = _HUNK_RE.match(line)
        if not m:
            continue
        start = int(m.group(1))
        length = int(m.group(2) or '1')
        if length <= 0:
            continue
        ranges.append((start, start + length - 1))

    ranges.sort()
    merged: List[List[int]] = []
    for s, e in ranges:
        if not merged or s > merged[-1][1] + 1:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    return [(a, b) for a, b in merged]


def _git_diff_u0(repo_root: str, base: str, rel_path: str) -> str:
    try:
        cmd = ['git', 'diff', '-U0', f'{base}...HEAD', '--', rel_path]
        return subprocess.check_output(cmd, cwd=repo_root, stderr=subprocess.STDOUT, text=True)
    except Exception:
        return ''


def _diff_ranges_for_files(repo_root: str, base: str, files: List[str]) -> Dict[str, List[Tuple[int, int]]]:
    out: Dict[str, List[Tuple[int, int]]] = {}
    root = Path(repo_root).resolve()
    for fp in files:
        p = Path(fp).resolve()
        try:
            rel = str(p.relative_to(root)).replace('\\', '/')
        except Exception:
            rel = p.name
        diff_text = _git_diff_u0(repo_root, base, rel)
        ranges = _parse_changed_line_ranges(diff_text)
        if ranges:
            out[str(p)] = ranges
    return out


def _normalize_text_full(text: str) -> str:
    lines = [ln.rstrip(' \t') for ln in text.splitlines()]
    out = '\n'.join(lines)
    if out and not out.endswith('\n'):
        out += '\n'
    return out


def _normalize_text_in_ranges(text: str, ranges: List[Tuple[int, int]]) -> str:
    if not ranges:
        return text

    lines = text.splitlines(keepends=True)

    def in_any(i: int) -> bool:
        for s, e in ranges:
            if s <= i <= e:
                return True
        return False

    new_lines: List[str] = []
    for idx, ln in enumerate(lines, start=1):
        if in_any(idx):
            new_lines.append(_strip_trailing_ws_preserve_newline(ln))
        else:
            new_lines.append(ln)

    out = ''.join(new_lines)
    if out and not out.endswith('\n'):
        out += '\n'
    return out


def generate_whitespace_patches(repo_root: str, files: List[str], diff_base: Optional[str] = None) -> List[Patch]:
    patches: List[Patch] = []

    diff_map: Dict[str, List[Tuple[int, int]]] = {}
    if diff_base:
        diff_map = _diff_ranges_for_files(repo_root, diff_base, files)

    for f in files:
        p = Path(f)
        try:
            orig = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        if diff_base:
            ranges = diff_map.get(str(p.resolve()))
            if not ranges:
                continue
            fixed = _normalize_text_in_ranges(orig, ranges)
            desc = f'Diff-aware whitespace cleanup (base {diff_base})'
        else:
            fixed = _normalize_text_full(orig)
            desc = 'Trim trailing whitespace and ensure newline at EOF'

        if fixed == orig:
            continue

        diff = ''.join(difflib.unified_diff(
            orig.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile=str(p),
            tofile=str(p),
        ))

        patches.append(Patch(
            file=str(p),
            description=desc,
            diff=diff,
            applied=False,
        ))

    return patches


def render_combined_patch(patches: List[Patch]) -> str:
    text = '\n'.join([p.diff.rstrip('\n') for p in patches if p.diff]).rstrip('\n')
    return (text + '\n') if text else ''


def apply_patches(patches: List[Patch]) -> List[Patch]:
    """Apply safe patches.

    Enterprise safety note:
      - Diff-aware patches are intended to be applied via `git apply` or reviewdog suggestions.
      - This method only applies full-file whitespace normalization patches.
    """

    for patch in patches:
        if patch.description.startswith('Diff-aware'):
            patch.applied = False
            continue

        p = Path(patch.file)
        try:
            orig = p.read_text(encoding='utf-8', errors='ignore')
            fixed = _normalize_text_full(orig)
            if fixed != orig:
                p.write_text(fixed, encoding='utf-8')
                patch.applied = True
        except Exception:
            patch.applied = False

    return patches
