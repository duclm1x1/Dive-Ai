from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.claims import Claim, ClaimsLedger, write_claims_ledger
from evidencepack.runtime import collect_run_evidencepack
from flows.doctor import run_doctor
from flows.explain import run_explain
from flows.cache_design import init_cache_design, validate_cache_design, report_cache_design
from v13.preflight import preflight as v13_preflight
from utils.hash_utils import sha256_file
from utils.policy import Policy
from gates.runner import run_gate
from gates.semgrep import run_semgrep_sarif_gate
from plugins.registry import default_plugins


@dataclass
class ModeRunResult:
    mode: str
    run_id: str
    repo: str
    run_dir: str
    started_at: str
    finished_at: str
    ok: bool
    steps: List[Dict[str, Any]]
    artifacts: Dict[str, str]
    evidencepack: Optional[str] = None
    claims: Optional[str] = None
    scorecard: Optional[str] = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _render_template_text(text: str, mapping: Dict[str, str]) -> str:
    out = text
    for k, v in mapping.items():
        out = out.replace(f'{{{{{k}}}}}', v)
    return out


def list_modes(repo_root: Path) -> List[str]:
    modes_dir = repo_root / '.vibe' / 'templates' / 'modes'
    if not modes_dir.exists():
        return []
    return sorted([p.name for p in modes_dir.iterdir() if p.is_dir()])


def apply_mode(repo_root: Path, mode: str, outdir: Optional[Path] = None, run_id: Optional[str] = None, force: bool = False) -> Path:
    modes_dir = repo_root / '.vibe' / 'templates' / 'modes'
    src = modes_dir / mode
    if not src.exists():
        raise FileNotFoundError(f'Unknown mode template: {mode}')

    rid = run_id or f"{mode}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    base = outdir or (repo_root / '.vibe' / 'runs' / rid)
    if base.exists() and not force:
        raise FileExistsError(f'Run dir already exists: {base}. Use --force to overwrite.')
    base.mkdir(parents=True, exist_ok=True)

    # Copy template files
    for item in src.iterdir():
        dst = base / item.name
        if item.is_dir():
            if dst.exists() and force:
                shutil.rmtree(dst)
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)

    # Render PROMPT.md to PROMPT_RENDERED.md with placeholders
    mapping = {
        'REPO_ROOT': str(repo_root),
        'RUN_DIR': str(base),
        'MODE': mode,
        'RUN_ID': rid,
        'DATE_UTC': _utc_now(),
    }
    prompt = base / 'PROMPT.md'
    if prompt.exists():
        rendered = _render_template_text(prompt.read_text(encoding='utf-8', errors='ignore'), mapping)
        (base / 'PROMPT_RENDERED.md').write_text(rendered, encoding='utf-8')

    # Write run context
    ctx = {
        'mode': mode,
        'run_id': rid,
        'repo': str(repo_root),
        'run_dir': str(base),
        'created_at': _utc_now(),
    }
    (base / 'run_context.json').write_text(json.dumps(ctx, indent=2, ensure_ascii=False), encoding='utf-8')
    return base


def _parse_mode_yml(path: Path) -> List[Dict[str, Any]]:
    """Parse a minimal subset of YAML used by mode.yml.

    Supported:
      version: <int>
      steps:
        - id: <str>
          type: <str>
          gate: <str> (optional)
          evidence: <E0|E1|E2|E3>
          optional: true|false (optional)

    This avoids a hard dependency on PyYAML.
    """
    if not path.exists():
        return []

    lines = [ln.rstrip('\n') for ln in path.read_text(encoding='utf-8', errors='ignore').splitlines()]
    steps: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    in_steps = False

    def _commit():
        nonlocal cur
        if cur is not None and cur.get('id') and cur.get('type'):
            steps.append(cur)
        cur = None

    for raw in lines:
        ln = raw.strip()
        if not ln or ln.startswith('#'):
            continue
        if ln.startswith('steps:'):
            in_steps = True
            continue
        if not in_steps:
            continue

        if ln.startswith('- '):
            _commit()
            cur = {}
            ln = ln[2:].strip()
            if ln.startswith('id:'):
                cur['id'] = ln.split(':', 1)[1].strip()
            continue

        if cur is None:
            continue

        if ':' in ln:
            k, v = ln.split(':', 1)
            k = k.strip()
            v = v.strip()
            if v.lower() in {'true', 'false'}:
                cur[k] = (v.lower() == 'true')
            else:
                cur[k] = v
    _commit()
    return steps


def _detect_gate_specs(repo_root: Path) -> Dict[str, List[List[str]]]:
    specs: Dict[str, List[List[str]]] = {}
    for plugin in default_plugins():
        try:
            if not plugin.detect(str(repo_root)):
                continue
            for g in plugin.suggested_gates(str(repo_root)):
                specs.setdefault(g.name, []).append(g.cmd)
        except Exception:
            continue
    return specs


def _pick_gate_cmd(gate_specs: Dict[str, List[List[str]]], gate: str) -> Optional[List[str]]:
    g = (gate or '').lower()
    # match by intent
    def _match(pred):
        for name, cmds in gate_specs.items():
            if pred(name.lower()):
                return cmds[0]
        return None

    if g == 'lint':
        return _match(lambda n: 'lint' in n) or _match(lambda n: 'typecheck' in n)
    if g == 'test':
        return _match(lambda n: 'test' in n)
    if g == 'build':
        return _match(lambda n: 'build' in n)
    if g == 'benchmark':
        # best-effort: use go test -bench or npm script benchmark if exists
        return _match(lambda n: 'bench' in n) or _match(lambda n: 'benchmark' in n)
    # no match
    return None


def _compare_sarif(baseline_path: Path, current_path: Path) -> Dict[str, Any]:
    def _load(p: Path) -> Dict[str, Any]:
        return json.loads(p.read_text(encoding='utf-8', errors='ignore'))

    base = _load(baseline_path)
    cur = _load(current_path)

    def _keys(doc: Dict[str, Any]) -> List[Tuple[str, str, int]]:
        keys: List[Tuple[str, str, int]] = []
        for run in (doc.get('runs') or []):
            results = ((run.get('results') or []) if isinstance(run, dict) else [])
            for r in results:
                rid = str(r.get('ruleId') or r.get('rule') or '')
                locs = r.get('locations') or []
                if not locs:
                    keys.append((rid, '', 0))
                    continue
                for loc in locs:
                    phys = ((loc.get('physicalLocation') or {}) if isinstance(loc, dict) else {})
                    art = ((phys.get('artifactLocation') or {}) if isinstance(phys, dict) else {})
                    uri = str(art.get('uri') or '')
                    reg = ((phys.get('region') or {}) if isinstance(phys, dict) else {})
                    start = int(reg.get('startLine') or 0)
                    keys.append((rid, uri, start))
        return keys

    base_keys = set(_keys(base))
    cur_keys = set(_keys(cur))
    new = sorted(list(cur_keys - base_keys))
    return {
        'baseline': str(baseline_path),
        'current': str(current_path),
        'new_count': len(new),
        'new': [{'ruleId': k[0], 'uri': k[1], 'startLine': k[2]} for k in new[:200]],
    }


def _write_json(p: Path, obj: Any) -> str:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)


def _scorecard(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len([s for s in steps if not s.get('skipped')])
    passed = len([s for s in steps if s.get('ok') is True])
    failed = len([s for s in steps if s.get('ok') is False and not s.get('skipped')])
    skipped = len([s for s in steps if s.get('skipped')])
    score = 0 if total == 0 else int(round((passed / max(total, 1)) * 100))
    blockers = [s for s in steps if s.get('blocking') and s.get('ok') is False]
    return {
        'score': score,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'blockers': [{'step': b.get('step'), 'reason': b.get('reason')} for b in blockers],
    }


def run_mode(
    repo_root: Path,
    mode: str,
    run_dir: Path,
    *,
    query: Optional[str] = None,
    full: bool = False,
    kind: Optional[str] = None,
    spec: Optional[str] = None,
) -> ModeRunResult:
    started = _utc_now()
    steps_out: List[Dict[str, Any]] = []
    artifacts: Dict[str, str] = {}
    policy = Policy.load(None)

    # Ensure run_dir exists with template content
    if not run_dir.exists():
        run_dir = apply_mode(repo_root, mode, outdir=run_dir, force=True)

    # Load manifest
    manifest_path = run_dir / 'mode.yml'
    manifest = _parse_mode_yml(manifest_path)
    if not manifest:
        # Backward compatibility: run a minimal default pipeline
        manifest = [
            {'id': 'doctor', 'type': 'doctor', 'evidence': 'E2'},
            {'id': 'cache-design', 'type': 'cache-design', 'evidence': 'E3'},
        ]

    gate_specs = _detect_gate_specs(repo_root)

    def _record(step: str, ok: Optional[bool], *, output: Optional[str] = None, artifacts_map: Optional[Dict[str, str]] = None,
                evidence: str = 'E0', skipped: bool = False, reason: Optional[str] = None, blocking: bool = False):
        entry = {'step': step, 'ok': ok, 'evidence': evidence}
        if skipped:
            entry['skipped'] = True
        if reason:
            entry['reason'] = reason
        if blocking:
            entry['blocking'] = True
        if output:
            entry['output'] = output
        if artifacts_map:
            entry['artifacts'] = artifacts_map
        steps_out.append(entry)

    # Execute steps from manifest
    for s in manifest:
        sid = str(s.get('id') or '')
        stype = str(s.get('type') or '')
        evidence = str(s.get('evidence') or 'E0')
        optional = bool(s.get('optional') is True)

        if stype == 'doctor':
            doc = run_doctor(str(repo_root), kind=kind, spec_path=spec, full=full)
            p = run_dir / 'doctor.json'
            _write_json(p, doc.to_dict())
            artifacts['doctor'] = str(p)
            _record('doctor', doc.overall != 'BLOCKED', output=str(p), evidence='E2', blocking=True)

        elif stype == 'v13-preflight':
            inferred = kind
            if not inferred:
                if mode == 'build-n8n':
                    inferred = 'n8n'
                elif mode == 'website':
                    inferred = 'website'
                elif mode == 'build-app':
                    inferred = 'nextjs'
            if not inferred:
                _record('v13-preflight', True, skipped=True, reason='No kind inferred', evidence='E0')
                continue
            ok_pf, pf_report = v13_preflight(str(repo_root), inferred, spec_path=spec)
            p = run_dir / 'preflight.json'
            _write_json(p, pf_report)
            artifacts['preflight'] = str(p)
            _record('v13-preflight', bool(ok_pf), output=str(p), evidence='E1', blocking=not optional)

        elif stype == 'cache-design':
            cache_root = repo_root / '.cache' / 'cache-design'
            if not cache_root.exists():
                init_cache_design(repo_root, force=False)
            val_path, val_report = validate_cache_design(repo_root)
            artifacts['cache_design_validate'] = str(val_path)
            _record('cache-design-validate', bool(val_report.get('ok')), output=str(val_path), evidence='E2', blocking=not optional)
            ep_path, claims_path = report_cache_design(repo_root, out_path=None)
            artifacts['cache_design_evidencepack'] = str(ep_path)
            artifacts['cache_design_claims'] = str(claims_path)
            _record('cache-design-report', True, output=str(ep_path), evidence='E3')

        elif stype == 'gate':
            gate = str(s.get('gate') or '')
            cmd = _pick_gate_cmd(gate_specs, gate)
            if cmd is None:
                _record(f'gate:{gate}', True, skipped=True, reason='No matching gate command found for this stack', evidence='E0')
                continue
            gr = run_gate(name=f'gate:{gate}', cmd=cmd, cwd=str(repo_root), policy=policy)
            p = run_dir / f'gate_{gate}.json'
            _write_json(p, gr.__dict__)
            artifacts[f'gate_{gate}'] = str(p)
            _record(f'gate:{gate}', (gr.exit_code == 0) if gr.exit_code is not None else False, output=str(p), evidence=gr.evidence_level or 'E2',
                    skipped=(gr.allowed is False and gr.exit_code is None), reason=None if gr.allowed else 'Command blocked/missing', blocking=not optional)

        elif stype == 'baseline-compare':
            # Compare semgrep SARIF vs baseline SARIF
            # 1) Run semgrep SARIF if available
            sarif_out = repo_root / '.vibe' / 'reports' / 'semgrep.sarif.json'
            sg = run_semgrep_sarif_gate(str(repo_root), policy=policy, config='auto', out_path=str(sarif_out))
            psg = run_dir / 'semgrep_gate.json'
            _write_json(psg, sg.__dict__)
            artifacts['semgrep_gate'] = str(psg)

            if not sarif_out.exists():
                _record('baseline-compare', True, skipped=True, reason='semgrep SARIF missing (semgrep not installed or blocked)', evidence='E0')
                continue

            baseline = repo_root / '.vibe' / 'baseline' / 'semgrep.sarif.json'
            if not baseline.exists():
                # optional baseline compare can be skipped, required one blocks
                if optional:
                    _record('baseline-compare', True, skipped=True, reason='baseline missing (.vibe/baseline/semgrep.sarif.json)', evidence='E0')
                else:
                    outp = run_dir / 'baseline_compare.json'
                    _write_json(outp, {'ok': False, 'reason': 'baseline missing', 'expected': str(baseline)})
                    artifacts['baseline_compare'] = str(outp)
                    _record('baseline-compare', False, output=str(outp), evidence='E3', blocking=True, reason='baseline missing')
                continue

            comp = _compare_sarif(baseline, sarif_out)
            comp['ok'] = (comp.get('new_count', 0) == 0)
            outp = run_dir / 'baseline_compare.json'
            _write_json(outp, comp)
            artifacts['baseline_compare'] = str(outp)
            _record('baseline-compare', bool(comp['ok']), output=str(outp), evidence='E3', blocking=True)

        elif stype == 'debug-repro':
            # placeholder artifact: user should paste logs/steps; we still make a structured stub
            stub = {
                'issue': 'Describe the bug and exact reproduction steps',
                'expected': '',
                'actual': '',
                'environment': {'os': '', 'node': '', 'expo': '', 'device': ''},
                'logs': [],
            }
            p = run_dir / 'repro.json'
            _write_json(p, stub)
            artifacts['repro'] = str(p)
            _record('debug-repro', True, output=str(p), evidence='E1')

        elif stype == 'perf-compare':
            _record('perf-compare', True, skipped=True, reason='Perf compare is repo/tool-specific; implement project benchmark harness', evidence='E0')

        else:
            _record(sid or stype, True, skipped=True, reason=f'Unknown step type: {stype}', evidence='E0')

    # Optional explain
    if query:
        exp = run_explain(str(repo_root), query=query, topk=8)
        p = run_dir / 'explain.json'
        _write_json(p, exp)
        artifacts['explain'] = str(p)
        _record('explain', True, output=str(p), evidence='E1')

    # Compute overall status
    blockers = [s for s in steps_out if s.get('blocking') and s.get('ok') is False]
    ok = len(blockers) == 0

    # Write mode run report
    run_report = {
        'mode': mode,
        'repo': str(repo_root),
        'run_dir': str(run_dir),
        'ok': ok,
        'steps': steps_out,
        'artifacts': artifacts,
        'started_at': started,
        'finished_at': _utc_now(),
        'sha256': sha256_file(str(repo_root / 'vibe.config.yml')) if (repo_root / 'vibe.config.yml').exists() else None,
    }
    mode_run_path = run_dir / 'mode_run.json'
    _write_json(mode_run_path, run_report)
    artifacts['mode_run'] = str(mode_run_path)

    # Scorecard
    sc = _scorecard(steps_out)
    score_path = run_dir / 'scorecard.json'
    _write_json(score_path, sc)
    artifacts['scorecard'] = str(score_path)

    # EvidencePack (E3 bundle)
    ep = collect_run_evidencepack(str(repo_root), str(run_dir))
    evidencepack_path = run_dir / 'evidencepack.json'
    _write_json(evidencepack_path, ep)
    artifacts['evidencepack'] = str(evidencepack_path)

    # Claims ledger for the run
    ledger = ClaimsLedger(claims=[
        Claim(
            claim=f'mode:{mode}:run_completed',
            evidence_level='E3' if full else 'E1',
            tool='vibe mode run',
            artifact=str(mode_run_path),
        ),
        Claim(
            claim='mode:scorecard_present',
            evidence_level='E3',
            tool='vibe mode run',
            artifact=str(score_path),
        ),
        Claim(
            claim='evidencepack_present',
            evidence_level='E3',
            tool='vibe mode run',
            artifact=str(evidencepack_path),
        ),
    ])
    claims_path = run_dir / 'claims.ledger.jsonl'
    write_claims_ledger(ledger, str(claims_path))
    artifacts['claims'] = str(claims_path)

    finished = _utc_now()
    return ModeRunResult(
        mode=mode,
        run_id=str(run_dir.name),
        repo=str(repo_root),
        run_dir=str(run_dir),
        started_at=started,
        finished_at=finished,
        ok=bool(ok),
        steps=steps_out,
        artifacts=artifacts,
        evidencepack=str(evidencepack_path),
        claims=str(claims_path),
        scorecard=str(score_path),
    )
