from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set


def _read_json(path: Path) -> Dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def detect_stacks(repo_root: str) -> List[str]:
    root = Path(repo_root)
    stacks: Set[str] = set()

    # Node / web stacks
    pkg = root / 'package.json'
    if pkg.exists():
        data = _read_json(pkg)
        deps: Dict[str, str] = {}
        for key in ('dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies'):
            v = data.get(key)
            if isinstance(v, dict):
                deps.update({str(k): str(vv) for k, vv in v.items()})

        # Next.js
        if 'next' in deps:
            stacks.add('nextjs')

        # NestJS
        if '@nestjs/core' in deps or '@nestjs/common' in deps:
            stacks.add('nestjs')

        # Tailwind
        if 'tailwindcss' in deps:
            stacks.add('tailwind')

        # React
        if 'react' in deps:
            stacks.add('react')

        # TypeScript
        if 'typescript' in deps:
            stacks.add('typescript')

    # Python
    if (root / 'pyproject.toml').exists() or (root / 'requirements.txt').exists():
        stacks.add('python')

    return sorted(stacks)
