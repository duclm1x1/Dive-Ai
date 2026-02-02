from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from builder.specs import validate_spec
from core.external_tools import tool_versions
from core.stack_detector import detect_stacks


@dataclass
class DoctorCheck:
    name: str
    status: str  # OK|WARN|FAIL
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class DoctorReport:
    repo: str
    overall: str  # READY|WARN|BLOCKED
    checks: List[DoctorCheck]
    stacks: List[str]
    tool_versions: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo": self.repo,
            "overall": self.overall,
            "checks": [asdict(c) for c in self.checks],
            "stacks": self.stacks,
            "tool_versions": self.tool_versions,
        }


def _has_file(repo: Path, rel: str) -> bool:
    p = repo / rel
    return p.exists()


def _check_templates(repo: Path) -> DoctorCheck:
    tpl_dir = repo / ".vibe" / "inputs" / "v13"
    if not tpl_dir.exists():
        return DoctorCheck(
            name="v13_templates",
            status="WARN",
            message="Missing .vibe/inputs/v13 templates directory (v13-init can create it).",
        )
    ymls = sorted([p.name for p in tpl_dir.glob("*.yml")])
    if not ymls:
        return DoctorCheck(
            name="v13_templates",
            status="WARN",
            message="No templates found under .vibe/inputs/v13/*.yml",
        )
    return DoctorCheck(
        name="v13_templates",
        status="OK",
        message=f"Found {len(ymls)} templates.",
        details={"templates": ymls},
    )


def _check_spec(repo: Path, spec_path: Optional[str], kind: Optional[str]) -> DoctorCheck:
    if not spec_path:
        return DoctorCheck(
            name="spec",
            status="WARN",
            message="No --spec provided. Skipping spec validation.",
        )
    sp = Path(spec_path)
    if not sp.is_absolute():
        sp = (repo / sp).resolve()
    if not sp.exists():
        return DoctorCheck(
            name="spec",
            status="FAIL",
            message=f"Spec file not found: {sp}",
        )
    try:
        validate_spec(str(sp), kind=kind)
        return DoctorCheck(name="spec", status="OK", message="Spec validation passed.", details={"spec": str(sp)})
    except Exception as e:
        return DoctorCheck(name="spec", status="FAIL", message=f"Spec validation failed: {e}", details={"spec": str(sp)})


def _check_repo_basics(repo: Path) -> List[DoctorCheck]:
    checks: List[DoctorCheck] = []
    # Basic signals
    if _has_file(repo, "package.json") or _has_file(repo, "pnpm-lock.yaml") or _has_file(repo, "bun.lockb"):
        checks.append(DoctorCheck(name="node_project", status="OK", message="Node project signals found."))
    else:
        checks.append(DoctorCheck(name="node_project", status="WARN", message="No Node signals found (package.json/lock)."))

    if _has_file(repo, "pyproject.toml") or _has_file(repo, "requirements.txt") or _has_file(repo, "setup.py"):
        checks.append(DoctorCheck(name="python_project", status="OK", message="Python project signals found."))
    else:
        checks.append(DoctorCheck(name="python_project", status="WARN", message="No Python signals found (pyproject/reqs)."))

    # Index presence
    db = repo / ".vibe" / "index" / "vibe_index.db"
    if db.exists():
        checks.append(DoctorCheck(name="index_db", status="OK", message="Index DB present.", details={"path": str(db)}))
    else:
        checks.append(DoctorCheck(name="index_db", status="WARN", message="Index DB missing (run v13-search index)."))

    return checks


def _check_baseline(repo: Path, baseline_path: Optional[str], require: bool) -> DoctorCheck:
    bp = Path(baseline_path) if baseline_path else (repo / ".vibe" / "baseline.json")
    if not bp.is_absolute():
        bp = (repo / bp).resolve()
    if bp.exists():
        return DoctorCheck(name="baseline", status="OK", message="Baseline present.", details={"path": str(bp)})
    if require:
        return DoctorCheck(name="baseline", status="FAIL", message="Baseline required but missing.", details={"path": str(bp)})
    return DoctorCheck(
        name="baseline",
        status="WARN",
        message="Baseline missing (build can auto-init unless --require-baseline).",
        details={"path": str(bp)},
    )


def run_doctor(
    repo_root: str,
    *,
    kind: Optional[str] = None,
    spec: Optional[str] = None,
    full: bool = False,
    baseline: Optional[str] = None,
    require_baseline: bool = False,
) -> DoctorReport:
    repo = Path(repo_root).resolve()
    stacks = detect_stacks(str(repo))
    vers = tool_versions()

    checks: List[DoctorCheck] = []
    checks.extend(_check_repo_basics(repo))
    checks.append(_check_templates(repo))
    checks.append(_check_spec(repo, spec, kind))
    checks.append(_check_baseline(repo, baseline, require=require_baseline or full))

    # Tool presence quick check for common stacks
    want = []
    if any(s in ("python", "django", "fastapi") for s in stacks):
        want += ["python", "python3", "pytest", "ruff"]
    if any(s in ("node", "nextjs", "react", "nestjs") for s in stacks):
        want += ["node", "npm", "pnpm", "bun"]

    missing = [c for c in sorted(set(want)) if shutil.which(c) is None]
    if missing:
        checks.append(DoctorCheck(name="tools", status="WARN", message=f"Missing tools on PATH: {', '.join(missing)}"))
    else:
        checks.append(DoctorCheck(name="tools", status="OK", message="Common tools look available."))

    # Overall status
    has_fail = any(c.status == "FAIL" for c in checks)
    has_warn = any(c.status == "WARN" for c in checks)
    overall = "BLOCKED" if has_fail else ("WARN" if has_warn else "READY")

    return DoctorReport(repo=str(repo), overall=overall, checks=checks, stacks=stacks, tool_versions=vers)
