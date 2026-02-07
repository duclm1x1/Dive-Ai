from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set


DEFAULT_EXCLUDES = {
    '.git',
    '.hg',
    '.svn',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    'dist',
    'build',
    '.next',
    '.turbo',
    '.idea',
    '.vscode',
    '.vibe',
    '.shared',
    '.agent',
}


@dataclass
class RepoScan:
    repo_root: str
    files: List[str]


def _is_excluded(part: str) -> bool:
    return part in DEFAULT_EXCLUDES


def find_repo_root(start: str) -> str:
    p = Path(start).resolve()
    if p.is_file():
        p = p.parent

    # Walk up until we hit a git root or filesystem root
    cur = p
    while True:
        if (cur / '.git').exists():
            return str(cur)
        parent = cur.parent
        if parent == cur:
            return str(p)
        cur = parent


def iter_source_files(repo_root: str, extensions: Set[str], extra_excludes: Optional[Set[str]] = None) -> Iterable[str]:
    ex = set(DEFAULT_EXCLUDES)
    # Allow opt-in scanning of vendor/agent directories (disabled by default for signal/noise).
    if os.environ.get('VIBE_INCLUDE_SHARED', '').lower() in {'1','true','yes'}:
        ex.discard('.shared')
    if os.environ.get('VIBE_INCLUDE_AGENT', '').lower() in {'1','true','yes'}:
        ex.discard('.agent')
    if extra_excludes:
        ex |= set(extra_excludes)

    root = Path(repo_root)
    for dirpath, dirnames, filenames in os.walk(root):
        # mutate dirnames to prune traversal
        dirnames[:] = [d for d in dirnames if d not in ex]
        for fn in filenames:
            if any(part in ex for part in Path(dirpath).parts):
                continue
            if not extensions:
                yield str(Path(dirpath) / fn)
                continue
            ext = Path(fn).suffix.lower()
            if ext in extensions:
                yield str(Path(dirpath) / fn)


def git_changed_files(repo_root: str, base: str = 'HEAD') -> List[str]:
    """Return changed files (name-only) vs base.

    Uses `git diff --name-only <base>...HEAD` when possible.

    If git isn't available or repo isn't git, returns []
    """
    try:
        cmd = ['git', '-C', repo_root, 'diff', '--name-only', f'{base}...HEAD']
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        files = [str(Path(repo_root) / line.strip()) for line in out.splitlines() if line.strip()]
        return files
    except Exception:
        return []
