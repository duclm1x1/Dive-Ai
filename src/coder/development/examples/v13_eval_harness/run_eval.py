#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure we can import the v13 package from the demo tree.
THIS = Path(__file__).resolve()
ROOT = THIS.parents[2] / '.shared' / 'vibe-coder-v13'
sys.path.insert(0, str(ROOT))

from search.hybrid import search as hybrid_search  # noqa: E402


def _ok_hit(hit: Dict[str, Any], expect: Dict[str, Any]) -> bool:
    pc = str(expect.get('path_contains') or '')
    sym = str(expect.get('symbol') or '')
    if pc and pc not in str(hit.get('path') or ''):
        return False
    if sym and sym.lower() != str(hit.get('symbol') or '').lower():
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description='Vibe v13 eval harness (offline).')
    ap.add_argument('--repo', default='.', help='Repo root')
    ap.add_argument('--tasks', default=str(Path(__file__).parent / 'tasks.json'), help='Tasks JSON')
    ap.add_argument('--limit', type=int, default=8)
    args = ap.parse_args()

    repo = str(Path(args.repo).resolve())
    data = json.loads(Path(args.tasks).read_text(encoding='utf-8', errors='ignore'))
    tasks: List[Dict[str, Any]] = list(data.get('tasks') or [])

    results = []
    passed = 0
    for t in tasks:
        hits = hybrid_search(repo, str(t.get('query') or ''), limit=int(args.limit))
        expect = dict(t.get('expect') or {})
        ok = any(_ok_hit(h, expect) for h in hits)
        results.append({'id': t.get('id'), 'ok': ok, 'top_hit': hits[0] if hits else None})
        passed += 1 if ok else 0

    summary = {'ok': passed == len(tasks), 'passed': passed, 'total': len(tasks), 'results': results}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary['ok'] else 3


if __name__ == '__main__':
    raise SystemExit(main())