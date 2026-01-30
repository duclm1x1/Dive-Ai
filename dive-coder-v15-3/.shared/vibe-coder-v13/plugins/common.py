from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def read_package_json(repo_root: str) -> Dict:
    pkg = Path(repo_root) / 'package.json'
    if not pkg.exists():
        return {}
    try:
        return json.loads(pkg.read_text(encoding='utf-8'))
    except Exception:
        return {}


def merged_deps(pkg_json: Dict) -> Dict[str, str]:
    deps: Dict[str, str] = {}
    for k in ('dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies'):
        v = pkg_json.get(k)
        if isinstance(v, dict):
            deps.update({str(n): str(ver) for n, ver in v.items()})
    return deps


def scripts(pkg_json: Dict) -> Dict[str, str]:
    sc = pkg_json.get('scripts')
    return dict(sc) if isinstance(sc, dict) else {}


def detect_package_manager(repo_root: str) -> str:
    root = Path(repo_root)
    if (root / 'pnpm-lock.yaml').exists():
        return 'pnpm'
    if (root / 'yarn.lock').exists():
        return 'yarn'
    if (root / 'bun.lockb').exists():
        return 'bun'
    # default
    return 'npm'


def run_script_cmd(pm: str, script_name: str) -> list[str]:
    pm = (pm or 'npm').lower()
    if pm == 'yarn':
        return ['yarn', 'run', script_name]
    if pm == 'pnpm':
        return ['pnpm', 'run', script_name]
    if pm == 'bun':
        return ['bun', 'run', script_name]
    return ['npm', 'run', script_name]
