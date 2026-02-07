from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.yaml_lite import load_yaml_file


DEFAULT_CONFIG: Dict[str, Any] = {
    'enable_p0': True,
    'enable_p1': False,
    'gates': {
        # If empty, fall back to stack plugins.
        'p0': [],
        # Security/polish gates; if empty, only optional semgrep SARIF gate may run.
        'p1': [],
    },
    'skills': {
        'enforce_lock': False,
        'max_selected': 12,
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(repo_root: str) -> Dict[str, Any]:
    """Load `vibe.config.yml` if present, else return defaults."""
    root = Path(repo_root)
    candidates = [
        root / 'vibe.config.yml',
        root / '.vibe' / 'vibe.config.yml',
    ]
    cfg: Dict[str, Any] = {}
    for p in candidates:
        if p.exists() and p.is_file():
            cfg = load_yaml_file(str(p))
            break

    if not isinstance(cfg, dict):
        cfg = {}

    merged = _deep_merge(DEFAULT_CONFIG, cfg)

    # Normalize expected shapes
    if not isinstance(merged.get('gates'), dict):
        merged['gates'] = dict(DEFAULT_CONFIG['gates'])
    for key in ('p0', 'p1'):
        if not isinstance(merged['gates'].get(key), list):
            merged['gates'][key] = []

    if not isinstance(merged.get('skills'), dict):
        merged['skills'] = dict(DEFAULT_CONFIG['skills'])

    return merged


def gate_cmds(cfg: Dict[str, Any], tier: str) -> List[List[str]]:
    gates = (cfg.get('gates') or {}).get(tier) or []
    out: List[List[str]] = []
    for g in gates:
        if isinstance(g, list) and all(isinstance(x, str) for x in g):
            out.append([str(x) for x in g])
        elif isinstance(g, str) and g.strip():
            out.append([g.strip()])
    return out
