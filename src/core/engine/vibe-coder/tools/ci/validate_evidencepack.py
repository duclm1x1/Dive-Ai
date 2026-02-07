#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from utils.hash_utils import sha256_file


def _load(p: str) -> Dict[str, Any]:
    return json.loads(Path(p).read_text(encoding='utf-8', errors='ignore'))


def _iter_artifacts(pack: Dict[str, Any]) -> List[Tuple[str, str]]:
    artifacts = []
    for a in pack.get('artifacts') or []:
        if isinstance(a, dict) and a.get('path') and a.get('sha256'):
            artifacts.append((str(a['path']), str(a['sha256'])))
    return artifacts


def validate(pack_path: str) -> int:
    pack = _load(pack_path)
    failures: List[str] = []

    for path, expected in _iter_artifacts(pack):
        p = Path(path)
        if not p.exists() or not p.is_file():
            failures.append(f"MISSING {path}")
            continue
        got = sha256_file(p)
        if got != expected:
            failures.append(f"HASH_MISMATCH {path} expected={expected} got={got}")

    if failures:
        print(json.dumps({'ok': False, 'failures': failures, 'count': len(failures)}, indent=2))
        return 2

    print(json.dumps({'ok': True, 'artifacts_validated': len(_iter_artifacts(pack))}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate a Vibe EvidencePack (hash + existence).')
    ap.add_argument('evidencepack', help='Path to evidencepack.json')
    args = ap.parse_args()
    return validate(args.evidencepack)


if __name__ == '__main__':
    raise SystemExit(main())
