"""YAML utilities.

PyYAML is available in the runtime, so we use it for correctness.
This module exists to keep YAML parsing centralized.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def load_yaml_text(text: str) -> Dict[str, Any]:
    """Parse YAML text into a dict. Returns {} on error."""
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    try:
        data = yaml.safe_load(text) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_yaml_file(path: str) -> Dict[str, Any]:
    try:
        p = Path(path)
        if not p.exists():
            return {}
        return load_yaml_text(p.read_text(encoding='utf-8', errors='ignore'))
    except Exception:
        return {}
