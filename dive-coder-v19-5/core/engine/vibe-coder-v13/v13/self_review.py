from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from advanced_searching.api import AdvancedSearch
from v13.preflight import preflight
from tools.skills_reindex import write as skills_reindex



@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "ok": self.ok, **self.detail}


def _py_compile_repo(rr: Path) -> Tuple[bool, Dict[str, Any]]:
    py_files = [
        str(p)
        for p in rr.rglob('*.py')
        if p.is_file()
        and '.venv' not in p.parts
        and 'venv' not in p.parts
        and '__pycache__' not in p.parts
    ]
    if not py_files:
        return True, {"files": 0}
    try:
        # python -m py_compile <files...>
        cmd = ['python3', '-m', 'py_compile'] + py_files
        subprocess.check_output(cmd, cwd=str(rr), stderr=subprocess.STDOUT)
        return True, {"files": len(py_files)}
    except subprocess.CalledProcessError as e:
        out = (e.output or b'').decode('utf-8', errors='ignore') if isinstance(e.output, (bytes, bytearray)) else str(e.output)
        return False, {"files": len(py_files), "error": out[-1500:]}


def _advanced_search_smoke(rr: Path) -> Tuple[bool, Dict[str, Any]]:
    s = AdvancedSearch(str(rr))
    idx = s.index_repo()
    loc = s.locate('vibe.py', limit=5)
    fac = s.facets()
    hints = s.hints('vibe', limit=5)
    ok = bool(idx) and isinstance(loc, list) and isinstance(fac, dict) and isinstance(hints, list)
    return ok, {"index": idx, "locate_sample": loc[:2], "facets": {"by_ext": list((fac.get('by_ext') or {}).items())[:5]}}


def _skills_connectivity(rr: Path) -> Tuple[bool, Dict[str, Any]]:
    # Reindex to refresh automap after adding skills
    audit_path = skills_reindex(str(rr))
    core_automap = rr / '.shared' / 'vibe-coder-v13' / 'core' / 'skill_automap.json'
    ok = core_automap.exists()
    skills = []
    if ok:
        try:
            obj = json.loads(core_automap.read_text(encoding='utf-8', errors='ignore'))
            skills = obj.get('skills') or []
        except Exception:
            skills = []
    # assert key skills exist
    ids = {s.get('skill_id') for s in skills if isinstance(s, dict)}
    required = {'vibe-agent-scope', 'vibe-advanced-searching', 'vibe-advanced-rag'}
    missing = sorted([x for x in required if x not in ids])
    # verify base_score for agent-scope is 100
    agent_scope_score = None
    for s in skills:
        if isinstance(s, dict) and s.get('skill_id') == 'vibe-agent-scope':
            agent_scope_score = s.get('base_score')
            break
    ok = ok and not missing and int(agent_scope_score or 0) >= 100
    return ok, {
        'skills_audit_md': audit_path,
        'automap_path': str(core_automap),
        'missing': missing,
        'vibe-agent-scope.base_score': agent_scope_score,
        'total_skills': len(skills) if isinstance(skills, list) else 0,
    }


def run(repo_root: str, kind: str = 'nextjs', spec_path: Optional[str] = None) -> Dict[str, Any]:
    rr = Path(repo_root).resolve()

    results: List[CheckResult] = []

    ok_pf, pf = preflight(str(rr), kind=kind, spec_path=spec_path)
    results.append(CheckResult('v13_preflight', ok_pf, pf))

    ok_py, py = _py_compile_repo(rr)
    results.append(CheckResult('python_compile', ok_py, py))

    ok_as, asr = _advanced_search_smoke(rr)
    results.append(CheckResult('advanced_searching_smoke', ok_as, asr))

    ok_sk, sk = _skills_connectivity(rr)
    results.append(CheckResult('base_skills_connectivity', ok_sk, sk))

    overall = all(r.ok for r in results)
    return {
        "version": "13.0",
        "ok": overall,
        "checks": [r.to_dict() for r in results],
    }


def to_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Vibe Coder v{report.get('version')} — Self-Review\n")
    lines.append(f"- Overall: **{'PASS' if report.get('ok') else 'FAIL'}**\n")
    lines.append("\n## Checks\n")
    for c in report.get('checks') or []:
        lines.append(f"- **{c.get('name')}**: {'✅' if c.get('ok') else '❌'}")
        if not c.get('ok'):
            # show short error
            err = c.get('error') or ''
            if err:
                lines.append(f"  - error: `{str(err)[:200]}`")
    lines.append("\n")
    return "\n".join(lines)


def to_sarif(report: Dict[str, Any]) -> Dict[str, Any]:
    # minimal SARIF 2.1.0
    rules = []
    results = []
    for c in report.get('checks') or []:
        rid = str(c.get('name') or 'CHECK').upper().replace('-', '_')
        rules.append({"id": rid, "shortDescription": {"text": str(c.get('name') or '')}})
        level = 'note' if c.get('ok') else 'warning'
        msg = f"{c.get('name')}: {'PASS' if c.get('ok') else 'FAIL'}"
        res: Dict[str, Any] = {"ruleId": rid, "level": level, "message": {"text": msg}}
        # if path exists in details, attach
        path = c.get('path') or (c.get('spec') if isinstance(c.get('spec'), str) else None)
        if isinstance(path, str) and path:
            res["locations"] = [{"physicalLocation": {"artifactLocation": {"uri": path}}}]
        results.append(res)

    return {
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Vibe Coder V13 Self-Review", "version": str(report.get('version') or '13.0'), "rules": rules}},
                "results": results,
            }
        ],
    }
