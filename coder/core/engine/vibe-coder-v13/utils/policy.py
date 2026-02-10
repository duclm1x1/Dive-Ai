from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_POLICY: Dict[str, Any] = {
    "allow_shell": True,
    "allow_network": False,
    "allow_write": False,
    "allow_autofix": False,
    "allowed_commands": [
        "python",
        "python3",
        "node",
        "npm",
        "pnpm",
        "yarn",
        "bun",
        "git",
        "pytest",
        "ruff",
        "bandit",
        "semgrep",
    ],
}


@dataclass
class Policy:
    allow_shell: bool
    allow_network: bool
    allow_write: bool
    allow_autofix: bool
    allowed_commands: List[str]

    @staticmethod
    def load(path: str | Path | None) -> 'Policy':
        if path is None:
            return Policy(**DEFAULT_POLICY)

        p = Path(path)
        if not p.exists():
            return Policy(**DEFAULT_POLICY)

        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            data = {}

        merged: Dict[str, Any] = dict(DEFAULT_POLICY)
        merged.update({k: v for k, v in data.items() if v is not None})
        return Policy(
            allow_shell=bool(merged.get('allow_shell', True)),
            allow_network=bool(merged.get('allow_network', False)),
            allow_write=bool(merged.get('allow_write', False)),
            allow_autofix=bool(merged.get('allow_autofix', False)),
            allowed_commands=list(merged.get('allowed_commands', [])),
        )

    def check_command(self, cmd: List[str]) -> bool:
        if not self.allow_shell:
            return False
        if not cmd:
            return False
        exe = cmd[0]
        return exe in set(self.allowed_commands)
