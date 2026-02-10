from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.policy import Policy
from gates.runner import run_gate
from graph.test_selection import select_tests
from search.hybrid import search as hybrid_search
from core.claims import Claim, ClaimsLedger, write_claims_ledger


_STACK_FILE_RE = re.compile(r'File "([^"]+)"')
_TOKEN_RE = re.compile(r'[A-Za-z0-9_]{2,}')


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def _extract_repo_paths(repo: Path, text: str) -> List[str]:
    paths: List[str] = []
    for m in _STACK_FILE_RE.finditer(text or ''):
        fp = m.group(1)
        try:
            p = Path(fp)
            if not p.is_absolute():
                p = (repo / p).resolve()
            else:
                p = p.resolve()
            if repo in p.parents or p == repo:
                rel = str(p.relative_to(repo))
                # Skip venv/node_modules/.vibe
                if rel.startswith('.vibe/') or 'node_modules/' in rel or rel.startswith('.venv/'):
                    continue
                paths.append(rel)
        except Exception:
            continue
    return sorted(set(paths))


def _summarize_query(failing_test: Optional[str], stacktrace_text: Optional[str]) -> str:
    parts: List[str] = []
    if failing_test:
        parts.append(failing_test)
    if stacktrace_text:
        toks = [m.group(0) for m in _TOKEN_RE.finditer(stacktrace_text)]
        parts.append(' '.join(toks[:80]))
    return ' '.join(parts).strip() or (failing_test or 'bug')


@dataclass
class FixReport:
    repo: str
    failing_test: Optional[str]
    stacktrace_path: Optional[str]
    evidence_level: str
    query: str
    grounded_hits: List[Dict[str, Any]]
    selected_tests: List[str]
    gates: List[Dict[str, Any]]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_fix(
    repo_root: str,
    *,
    failing_test: Optional[str] = None,
    stacktrace: Optional[str] = None,
    outdir: Optional[str] = None,
    verify: bool = False,
    full: bool = False,
    max_tests: int = 20,
    policy_path: Optional[str] = None,
) -> Tuple[FixReport, Dict[str, str], str]:
    """A–Z bugfix flow (scaffolding + optional verification).

    This command does NOT magically invent a code patch. It produces a grounded investigation bundle:
      - grounded pointers/snippets relevant to the failure
      - hypothesis template
      - optional test selection + execution (pytest only by default)
      - claims ledger and artifact bundle paths

    Returns (report, artifacts_map, claims_path).
    """
    repo = Path(repo_root).resolve()
    od = Path(outdir) if outdir else (repo / '.vibe' / 'fix' / 'latest')
    od.mkdir(parents=True, exist_ok=True)

    notes: List[str] = []
    if not failing_test and not stacktrace:
        raise ValueError('vibe fix requires --failing-test and/or --stacktrace')

    stack_text = None
    stack_path = None
    if stacktrace:
        sp = Path(stacktrace)
        if not sp.is_absolute():
            sp = (repo / sp).resolve()
        stack_path = str(sp) if sp.exists() else None
        stack_text = _read_text(sp) if sp.exists() else stacktrace
        if not sp.exists():
            notes.append('Stacktrace path not found; treated as inline text.')

    # Grounded retrieval
    query = _summarize_query(failing_test, stack_text)
    hits = hybrid_search(str(repo), query, limit=12)

    # Changed/impacted seeds from stacktrace paths
    changed_files: List[str] = []
    if stack_text:
        changed_files = _extract_repo_paths(repo, stack_text)

    sel = select_tests(str(repo), changed_files=changed_files, max_tests=max_tests) if changed_files else None
    selected_tests = (sel.selected_tests if sel else [])[: int(max_tests)]

    gates: List[Dict[str, Any]] = []
    gate_artifacts: Dict[str, str] = {}

    # Policy
    policy = Policy.load(policy_path)

    # Optional verification: run pytest on selected tests when python tests exist
    if verify:
        if selected_tests:
            # If selection includes JS tests, only run python ones here.
            py_tests = [t for t in selected_tests if t.endswith('.py')]
            if py_tests:
                cmd = ['pytest', '-q'] + py_tests[: min(len(py_tests), 10)]
                gr = run_gate('pytest', cmd, cwd=str(repo), policy=policy, timeout_s=1200)
                gates.append(gr.to_dict())
                # Write gate outputs as artifacts (E3)
                gp = od / 'gates' / 'pytest.json'
                gp.parent.mkdir(parents=True, exist_ok=True)
                gp.write_text(json.dumps(gr.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
                gate_artifacts['pytest'] = str(gp)
            else:
                notes.append('No python tests selected; skipping pytest execution.')
        else:
            notes.append('No tests discovered/selected; skipping verification.')

    evidence_level = 'E2' if gates else 'E1' if (stacktrace is not None) else 'E0'
    if full and gates:
        evidence_level = 'E3'

    # Write investigation bundle
    report = FixReport(
        repo=str(repo),
        failing_test=failing_test,
        stacktrace_path=stack_path,
        evidence_level=evidence_level,
        query=query,
        grounded_hits=hits,
        selected_tests=selected_tests,
        gates=gates,
        notes=notes,
    )

    report_path = od / 'fix_report.json'
    report_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')

    # Hypothesis template
    hyp_md = od / 'hypotheses.md'
    hyp_md.write_text(_hypothesis_template(report), encoding='utf-8')

    artifacts = {
        'report': str(report_path),
        'hypotheses': str(hyp_md),
    }
    if stack_path:
        artifacts['stacktrace'] = stack_path
    for k, v in gate_artifacts.items():
        artifacts[f'gate:{k}'] = v

    # Claims ledger (anti governance-theater)
    ledger = ClaimsLedger(version='v13', run_id=str(od.name), claims=[])
    # Claim: grounded retrieval performed (E0)
    ledger.claims.append(Claim(claim='grounded_retrieval', evidence_level='E0', tool='v13-hybrid-search', artifact=str(report_path)))
    # Claim: verification gate if any
    for g in gates:
        name = g.get('name') or 'gate'
        ev = g.get('evidence_level') or 'E2'
        art = gate_artifacts.get(name) or ''
        ledger.claims.append(Claim(claim=f'gate:{name}', evidence_level=ev, tool=name, artifact=art))

    claims_path = od / 'claims.json'
    write_claims_ledger(str(repo), ledger, str(claims_path))

    artifacts['claims'] = str(claims_path)

    return report, artifacts, str(claims_path)


def _hypothesis_template(r: FixReport) -> str:
    lines: List[str] = []
    lines.append('# Bugfix Hypotheses\n')
    lines.append(f'- Evidence Level: **{r.evidence_level}**')
    if r.failing_test:
        lines.append(f'- Failing test: `{r.failing_test}`')
    if r.stacktrace_path:
        lines.append(f'- Stacktrace: `{r.stacktrace_path}`')
    lines.append('\n## Grounded Code Pointers (top hits)\n')
    if not r.grounded_hits:
        lines.append('_No grounded hits. Consider refining query._\n')
    for h in r.grounded_hits[:8]:
        path = h.get('path') or ''
        sym = h.get('symbol') or ''
        pid = h.get('pointer_id') or ''
        sn = h.get('snippet') or {}
        sl = sn.get('start_line') or ''
        el = sn.get('end_line') or ''
        lines.append(f'- `{path}` {f"({sym})" if sym else ""} {f"[id:{pid}]" if pid else ""} lines {sl}-{el}')
    lines.append('\n## Hypothesis Matrix\n')
    lines.append('List 3-5 hypotheses. For each: evidence needed to confirm/refute.\n')
    lines.append('1. **Hypothesis:** ...\n   - Evidence needed: ...\n   - How to test: ...\n   - Fix strategy: ...\n')
    lines.append('2. **Hypothesis:** ...\n   - Evidence needed: ...\n   - How to test: ...\n   - Fix strategy: ...\n')
    lines.append('3. **Hypothesis:** ...\n   - Evidence needed: ...\n   - How to test: ...\n   - Fix strategy: ...\n')
    lines.append('\n## Candidate Fix Plan\n')
    lines.append('- Minimal patch scope: ...\n- Tests to run: ...\n- Risk assessment: ...\n')
    return '\n'.join(lines)
