from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from builder.specs import REQUIRED_INPUTS, validate_spec
from utils.yaml_lite import load_yaml_file
from v13.templates import make_spec_template, write_yaml_like


def init_repo(repo_root: str, kinds: Optional[List[str]] = None) -> Dict[str, Any]:
    """Initialize V13 inputs templates and folders.

    Creates:
      - .vibe/inputs/v13/<kind>.yml templates
      - .vibe/hooks (empty)
      - .vibe/commands (empty)
      - .vibe/index, .vibe/reports
    """
    rr = Path(repo_root).resolve()
    kinds = kinds or sorted(REQUIRED_INPUTS.keys())
    created: List[str] = []

    # folders
    for d in [rr / '.vibe' / 'inputs' / 'v13', rr / '.vibe' / 'hooks', rr / '.vibe' / 'commands', rr / '.vibe' / 'index', rr / '.vibe' / 'reports']:
        d.mkdir(parents=True, exist_ok=True)

    # templates
    for k in kinds:
        req = REQUIRED_INPUTS.get(k)
        if not req:
            continue
        tpl = make_spec_template(req)
        p = rr / '.vibe' / 'inputs' / 'v13' / f'{k}.yml'
        if not p.exists():
            write_yaml_like(p, tpl)
            created.append(str(p.relative_to(rr)).replace('\\', '/'))

    return {"ok": True, "repo": str(rr), "created": created}


def _load_spec(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    if path.suffix.lower() == '.json':
        try:
            return json.loads(path.read_text(encoding='utf-8', errors='ignore'))
        except Exception:
            return {}
    return load_yaml_file(str(path))


def preflight(repo_root: str, kind: str, spec_path: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    """V13 preflight: validate required inputs + repo folders."""
    rr = Path(repo_root).resolve()
    kind = (kind or '').strip().lower()

    if not kind:
        return False, {"ok": False, "error": "MISSING_KIND"}

    default_spec = rr / '.vibe' / 'inputs' / 'v13' / f'{kind}.yml'
    sp = Path(spec_path).resolve() if spec_path else default_spec
    spec = _load_spec(sp)
    ok, missing = validate_spec(kind, spec)

    checks: List[Dict[str, Any]] = []
    checks.append({"check": "spec_exists", "ok": sp.exists(), "path": str(sp)})
    checks.append({"check": "spec_required_keys", "ok": ok, "missing": missing})

    # semgrep local config hint
    semgrep_local = (rr / '.semgrep' / 'vibe.yml')
    checks.append({"check": "semgrep_config_present", "ok": semgrep_local.exists(), "path": str(semgrep_local)})

    # folders expected
    for d in ['.vibe/index', '.vibe/reports', '.vibe/hooks', '.vibe/commands']:
        checks.append({"check": f"dir:{d}", "ok": (rr / d).exists()})

    overall = all(bool(c.get('ok')) for c in checks if c.get('check') != 'semgrep_config_present')
    return overall, {"ok": overall, "kind": kind, "spec": str(sp), "checks": checks}
