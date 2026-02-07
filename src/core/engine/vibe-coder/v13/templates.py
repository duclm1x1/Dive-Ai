from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _nest_set(root: Dict[str, Any], dotted: str, value: Any) -> None:
    cur: Dict[str, Any] = root
    parts = [p for p in (dotted or '').split('.') if p]
    for p in parts[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[p] = nxt
        cur = nxt
    if parts:
        cur[parts[-1]] = value


def make_spec_template(required_keys: List[str]) -> Dict[str, Any]:
    """Build a nested dict template from REQUIRED_INPUTS dotted paths."""
    out: Dict[str, Any] = {}
    for k in required_keys:
        # heuristic placeholders
        if k.endswith('.pages') or k.endswith('.core_flows') or k.endswith('.endpoints') or k.endswith('.steps'):
            v: Any = ["TODO"]
        elif k.endswith('.users') or k.endswith('.sources'):
            v = ["TODO"]
        elif k.endswith('.slo'):
            v = {"availability": "99.9%", "latency_p95_ms": 300}
        elif k.endswith('.security'):
            v = {"auth": "TODO", "secrets": "TODO", "threat_model": "TODO"}
        elif k.endswith('.observability'):
            v = {"logging": "TODO", "tracing": "TODO", "metrics": "TODO"}
        elif k.endswith('.placeholders'):
            v = {"EXAMPLE_SECRET": "${{REPLACE_ME}}"}
        else:
            v = "TODO"
        _nest_set(out, k, v)
    return out


def write_yaml_like(path: Path, obj: Dict[str, Any], indent: int = 0) -> None:
    """Write a minimal YAML (no external deps)."""
    lines: List[str] = []

    def emit(o: Any, level: int) -> None:
        pad = "  " * level
        if isinstance(o, dict):
            for kk, vv in o.items():
                if isinstance(vv, (dict, list)):
                    lines.append(f"{pad}{kk}:")
                    emit(vv, level + 1)
                else:
                    s = str(vv)
                    if ':' in s or s.strip() == '':
                        s = f"'{s}'"
                    lines.append(f"{pad}{kk}: {s}")
        elif isinstance(o, list):
            for vv in o:
                if isinstance(vv, (dict, list)):
                    lines.append(f"{pad}-")
                    emit(vv, level + 1)
                else:
                    s = str(vv)
                    if ':' in s or s.strip() == '':
                        s = f"'{s}'"
                    lines.append(f"{pad}- {s}")
        else:
            lines.append(f"{pad}{o}")

    emit(obj, indent)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
