from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .cache import DiskCache
from .external_tools import run_bandit, run_ruff, run_semgrep, tool_versions
from .models import Finding, Report, RunManifest, utc_now_iso
from .python_ast import analyze_python_file
from .repo_scanner import find_repo_root, git_changed_files, iter_source_files
from .rules_engine import load_rule_files, run_regex_rules
from .stack_detector import detect_stacks
from .vibe_config import load_config, gate_cmds
from .skill_router import route_skills
from .cruel_runner import run_cruel, select_cruel_files
from .dependency_graph import DependencyAnalyzer
from .n8n import analyze_n8n_text
from gates.runner import run_gate
from plugins.registry import default_plugins
from utils.hash_utils import sha256_text
from utils.policy import Policy
from utils.sanitize import sanitize_untrusted_text
from utils.tracing import Tracer


V13_VERSION = '13.0.0-antigravity-enterprise'


def _severity_rank(sev: str) -> int:
    sev = (sev or '').lower()
    order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    return order.get(sev, 9)


def _score_from_findings(findings: List[Finding]) -> Dict[str, Any]:
    """Conservative score model with per-severity caps.

    Why: avoid "death by 1,000 lows" while still punishing criticals.
    """

    base = 100
    weights = {'critical': 15, 'high': 8, 'medium': 3, 'low': 1, 'info': 0}
    caps = {'critical': 45, 'high': 40, 'medium': 30, 'low': 15, 'info': 0}

    counts = {k: 0 for k in weights.keys()}
    for f in findings:
        sev = (f.severity or 'medium').lower()
        if sev not in counts:
            sev = 'medium'
        counts[sev] += 1

    penalty = 0
    for sev, n in counts.items():
        penalty += min(n * weights[sev], caps[sev])

    score = max(0, min(100, base - penalty))
    grade = (
        'A' if score >= 90 else
        'B' if score >= 80 else
        'C' if score >= 70 else
        'D' if score >= 60 else
        'F'
    )

    return {'overall': score, 'grade': grade, 'penalty': penalty, 'counts': counts}


def _action_plan(findings: List[Finding], limit: int = 20) -> List[Dict[str, Any]]:
    fs = sorted(findings, key=lambda f: (_severity_rank(f.severity), -int(f.confidence)))
    out: List[Dict[str, Any]] = []
    for f in fs[:limit]:
        out.append({
            'priority': f.severity,
            'category': f.category,
            'title': f.title,
            'confidence': f.confidence,
            'location': f"{f.evidence.file}:{f.evidence.start_line}" if f.evidence else '',
            'recommendation': f.recommendation,
        })
    return out


def _config_hash(*, mode: str, stacks: List[str], diff_base: Optional[str], seed: int, min_confidence: int) -> str:
    payload = json.dumps({'mode': mode, 'stacks': stacks, 'diff_base': diff_base, 'seed': seed, 'min_confidence': int(min_confidence)}, sort_keys=True)
    return sha256_text(payload)[:16]


def _default_extensions() -> Set[str]:
    return {'.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.md', '.yml', '.yaml'}


def _mode_caps(mode: str) -> int:
    if mode == 'fast':
        return 200
    if mode == 'accuracy':
        return 1200
    return 600


def _collect_files(repo_root: str, *, diff_base: Optional[str], mode: str, extensions: Set[str]) -> List[str]:
    if diff_base:
        changed = [p for p in git_changed_files(repo_root, base=diff_base) if Path(p).suffix.lower() in extensions]
        files = sorted(set(changed))
    else:
        files = sorted(set(iter_source_files(repo_root, extensions=extensions)))

    return files[: _mode_caps(mode)]


def _load_regex_rules(repo_root: str) -> List[Dict[str, Any]]:
    shared_rules_dir = str(Path(__file__).resolve().parents[1] / 'rules' / 'custom')
    repo_rules_dir = str(Path(repo_root) / '.vibe' / 'rules')
    return load_rule_files([shared_rules_dir, repo_rules_dir])


def _analyze_single_file(path: str, text: str, regex_rules: List[Dict[str, Any]]) -> List[Finding]:
    p = Path(path)
    local: List[Finding] = []
    if p.suffix.lower() == '.py':
        local.extend(analyze_python_file(str(p), text))

    if p.suffix.lower() == ".json":
        local.extend(analyze_n8n_text(str(p), text))

    # Regex rules are multi-language
    local.extend(run_regex_rules(regex_rules, str(p), text))
    return local


def _rehydrate_cached_findings(arr: Any) -> List[Finding]:
    if not isinstance(arr, list):
        return []
    out: List[Finding] = []
    for d in arr:
        if not isinstance(d, dict):
            continue
        try:
            out.append(Finding.from_dict(d))
        except Exception:
            continue
    return out


def _dedupe_findings(findings: List[Finding]) -> List[Finding]:
    seen = set()
    uniq: List[Finding] = []
    for f in findings:
        key = (
            f.id,
            f.evidence.file if f.evidence else '',
            f.evidence.start_line if f.evidence else 0,
        )
        if key in seen:
            continue
        seen.add(key)
        uniq.append(f)
    return uniq


def _maybe_run_external_tools(repo_root: str, mode: str) -> List[Finding]:
    out: List[Finding] = []
    if mode in {'balanced', 'accuracy'}:
        out.extend(run_ruff(repo_root))
    if mode == 'accuracy':
        out.extend(run_bandit(repo_root))
        out.extend(run_semgrep(repo_root, config='auto'))
    return out


def _normalize_optional_path(p: Optional[str]) -> Optional[str]:
    if p is None:
        return None
    if isinstance(p, str) and p.strip() == '':
        return None
    return p


def analyze_repo(
    target_path: str,
    mode: str = 'balanced',
    task: str = '',
    diff_base: Optional[str] = None,
    run_gates: bool = False,
    gates: Optional[List[List[str]]] = None,
    policy_path: Optional[str] = None,
    seed: int = 0,
    min_confidence: int = 80,
) -> Report:
    """Repo-level analysis orchestration.

    This is intentionally deterministic (given the same inputs) and produces a run manifest.
    """

    started_at = utc_now_iso()

    tracer = Tracer()
    policy_path = _normalize_optional_path(policy_path)

    internal: Dict[str, int] = {
        'file_read_errors': 0,
        'cache_read_errors': 0,
        'cache_write_errors': 0,
    }

    with tracer.span('repo_root'):
        repo_root = find_repo_root(target_path)

    with tracer.span('detect_stacks'):
        stacks = detect_stacks(repo_root)

    with tracer.span('config'):
        cfg = load_config(repo_root)
        enforce_lock = bool((cfg.get('skills') or {}).get('enforce_lock'))
        max_selected = int((cfg.get('skills') or {}).get('max_selected') or 12)

    cfg_hash = _config_hash(mode=mode, stacks=stacks, diff_base=diff_base, seed=seed, min_confidence=min_confidence)

    with tracer.span('collect_files', meta={'diff_base': diff_base, 'mode': mode}):
        files = _collect_files(repo_root, diff_base=diff_base, mode=mode, extensions=_default_extensions())

    cache_dir = str(Path(repo_root) / '.vibe' / 'cache')
    cache = DiskCache(cache_dir)

    with tracer.span('load_rules'):
        regex_rules = _load_regex_rules(repo_root)

    with tracer.span('dependency_analysis'):
        dep_analyzer = DependencyAnalyzer(repo_root)
        dep_analyzer.analyze(files)

    findings: List[Finding] = []
    file_hashes: Dict[str, str] = {}

    with tracer.span('analyze_files', meta={'file_count': len(files)}):
        for fp in files:
            p = Path(fp)
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                internal['file_read_errors'] += 1
                continue

            fhash = sha256_text(text)
            file_hashes[str(p)] = fhash

            cache_key = sha256_text(f"{V13_VERSION}:{cfg_hash}:{fhash}")[:24]

            cached = cache.get(cache_key)
            if cached and isinstance(cached.get('findings'), list):
                try:
                    findings.extend(_rehydrate_cached_findings(cached.get('findings')))
                    continue
                except Exception:
                    internal['cache_read_errors'] += 1

            local = _analyze_single_file(str(p), text, regex_rules)
            findings.extend(local)

            try:
                cache.set(cache_key, {'findings': [f.to_dict() for f in local]})
            except Exception:
                internal['cache_write_errors'] += 1

    with tracer.span('external_tools', meta={'mode': mode}):
        findings.extend(_maybe_run_external_tools(repo_root, mode))

    with tracer.span('dedupe'):
        findings = _dedupe_findings(findings)

    with tracer.span('confidence_filter', meta={'min_confidence': int(min_confidence)}):
        findings = [f for f in findings if int(f.confidence or 0) >= int(min_confidence)]

    gate_results = []
    policy = Policy.load(policy_path)

    with tracer.span('gates', meta={'run_gates': run_gates}):
        if run_gates:
            enable_p0 = bool(cfg.get('enable_p0'))
            enable_p1 = bool(cfg.get('enable_p1'))

            configured_gates = []
            if enable_p0:
                configured_gates.extend(gate_cmds(cfg, 'p0'))
            if enable_p1:
                configured_gates.extend(gate_cmds(cfg, 'p1'))

            # If vibe.config.yml provides gates, use them; otherwise fall back to stack plugins.
            if configured_gates:
                gates_to_run = configured_gates
            else:
                gates_to_run = gates
                if gates_to_run is None:
                    gates_to_run = []
                    for pl in default_plugins():
                        try:
                            if pl.detect(repo_root):
                                for gs in pl.suggested_gates(repo_root):
                                    gates_to_run.append(gs.cmd)
                        except Exception:
                            continue
            
            # Breakthrough: Auto-add verification gates if not present
            if 'python' in stacks and not any('pytest' in ' '.join(c) for c in gates_to_run):
                if (Path(repo_root) / 'tests').exists() or (Path(repo_root) / 'test').exists():
                    gates_to_run.append(['pytest', '--maxfail=3', '--durations=5'])
            
            if 'nextjs' in stacks and not any('lint' in ' '.join(c) for c in gates_to_run):
                gates_to_run.append(['npm', 'run', 'lint'])

            # Optional security gate: semgrep SARIF (P1)
            if enable_p1:
                try:
                    from gates.semgrep import run_semgrep_sarif_gate
                    gate_results.append(run_semgrep_sarif_gate(repo_root, policy))
                except Exception:
                    pass

            # de-dup
            seen_cmds = set()
            for idx, cmd in enumerate(gates_to_run or []):
                tcmd = tuple(cmd)
                if tcmd in seen_cmds:
                    continue
                seen_cmds.add(tcmd)
                gate_results.append(run_gate(name=f'gate-{idx+1}', cmd=cmd, cwd=repo_root, policy=policy))

    with tracer.span('score_and_plan'):
        scores = _score_from_findings(findings)
        scores['internal'] = dict(internal)
        plan = _action_plan(findings)

    with tracer.span('skills_router'):
        gates_meta = []
        for g in gate_results:
            try:
                code = g.exit_code
                status = 'pass' if (code is None or int(code) == 0) else 'fail'
            except Exception:
                status = 'unknown'
            gates_meta.append({'name': getattr(g, 'name', ''), 'status': status})

        skills_info = route_skills(
            repo_root,
            stacks=stacks,
            findings=findings,
            gates=gates_meta,
            task=task,
            enforce_lock=enforce_lock,
            max_selected=max_selected,
        )

        # Cruel System (Mode A) – always-on
        cruel_info = {}
        try:
            with tracer.span('cruel'):
                rel_files = select_cruel_files(repo_root)
                cruel_info = run_cruel(repo_root, rel_files=rel_files)
        except Exception:
            cruel_info = {'enabled': False, 'mode': 'A', 'error': 'cruel_failed'}

    finished_at = utc_now_iso()

    manifest = RunManifest(
        version=V13_VERSION,
        started_at=started_at,
        finished_at=finished_at,
        seed=int(seed),
        repo_root=repo_root,
        mode=mode,
        diff_base=diff_base,
        file_count=len(files),
        file_hashes=file_hashes,
        config_hash=cfg_hash,
        tool_versions=tool_versions(),
    )

    report = Report(
        version=V13_VERSION,
        started_at=started_at,
        finished_at=finished_at,
        repo_root=repo_root,
        mode=mode,
        task=sanitize_untrusted_text(task or ''),
        detected_stacks=stacks,
        analyzed_files=files,
        findings=findings,
        scores=scores,
        action_plan=plan,
        gates=gate_results,
        traces=tracer.spans,
        manifest=manifest,
        skills=skills_info,
        cruel=cruel_info,
    )

    return report
