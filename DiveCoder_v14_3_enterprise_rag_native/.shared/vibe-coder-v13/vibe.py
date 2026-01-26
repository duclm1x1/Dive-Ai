#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from builder.scaffold import scaffold
from builder.specs import validate_spec
from core.baseline import load_report, new_findings, write_baseline
from core.external_tools import tool_versions
from core.models import Report, GateResult
from core.claims import Claim, ClaimsLedger, write_claims_ledger
from learning.store import append_event
from graph.test_selection import select_tests
from graph.store import build_graph, impacted_files
from tools.skills_reindex import write as reindex_skills
from core.orchestrator import analyze_repo
from core.stack_detector import detect_stacks
from exporters.markdown import write_findings_markdown, write_report_markdown
from exporters.sarif import write_sarif
from patch.autopatch import apply_patches, generate_whitespace_patches, render_combined_patch
from patch.golden_config import apply_golden_patches, generate_golden_config_patches
from patch.resolve_engine import generate_resolve_patches
from patch.safety import validate_patch, PatchConstraints
from utils.yaml_lite import load_yaml_file

# v12.1 infra add-ons
from index.indexer import build as build_repo_index, save_stats as save_index_stats
from search.semantic import search as semantic_search
from kb.updater import update_github_raw, update_reddit_search
from dag.engine import run_dag, to_dict as dag_to_dict
from debate.runtime import generate_debate, to_dict as debate_to_dict, to_markdown as debate_to_markdown
from utils.policy import Policy


# IKO / EvidencePack / Gatekeeper / RLM investigator
from iko.models import IKO
from iko.store import save as save_iko, load as load_iko, list_ids as list_iko_ids
from evidencepack.collector import collect_evidencepack
from evidencepack.runtime import collect_run_evidencepack
# V13 init / preflight / self-review
from v13.preflight import init_repo as v13_init_repo, preflight as v13_preflight
from v13.self_review import run as v13_self_review, to_markdown as v13_self_review_md, to_sarif as v13_self_review_sarif

from gatekeeper.runner import transition_iko
from rlm.investigator import investigate as rlm_investigate

from flows.doctor import run_doctor
from flows.explain import run_explain, to_markdown as explain_to_markdown
from flows.fix import run_fix
from flows.cache_design import init_cache_design, validate_cache_design, report_cache_design
from flows.mode_runner import list_modes as mode_list, apply_mode as mode_apply, run_mode as mode_run

# V13 Breakthrough Add-ons
from advanced_searching.api import AdvancedSearch
from rag.engine import AdvancedRAG
from rag.report import run_rag_eval


def _severity_rank(sev: str) -> int:
    sev = (sev or '').lower()
    order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    return order.get(sev, 9)


def _norm_opt(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    if isinstance(s, str) and s.strip() == '':
        return None
    return s


def _write_json(path: str, obj: Any) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)


def _write_text(path: str, text: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return str(p)




def cmd_skills_reindex(args: argparse.Namespace) -> int:
    paths = reindex_skills(args.repo)
    print(json.dumps(paths, indent=2))
    return 0

def cmd_status(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    stacks = detect_stacks(str(repo_root))
    vers = tool_versions()
    print(json.dumps({'stacks': stacks, 'tool_versions': vers}, indent=2, ensure_ascii=False))
    return 0



def cmd_doctor(args: argparse.Namespace) -> int:
    rep = run_doctor(
        args.repo,
        kind=_norm_opt(args.kind),
        spec=_norm_opt(args.spec),
        full=bool(args.full),
        baseline=_norm_opt(args.baseline),
        require_baseline=bool(args.require_baseline),
    )
    out_p = args.out or str(Path(args.repo).resolve() / '.vibe' / 'reports' / 'doctor.json')
    _write_json(out_p, rep.to_dict())
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.overall != 'BLOCKED' else 2


def cmd_explain(args: argparse.Namespace) -> int:
    res = run_explain(args.repo, args.query, topk=int(args.topk))
    out_p = args.out or str(Path(args.repo).resolve() / '.vibe' / 'reports' / 'explain.json')
    _write_json(out_p, res.to_dict())
    if args.md_out:
        _write_text(args.md_out, explain_to_markdown(res, max_hits=int(args.topk)))
    print(json.dumps(res.to_dict(), indent=2, ensure_ascii=False))
    return 0


def cmd_fix(args: argparse.Namespace) -> int:
    report, artifacts, claims_path = run_fix(
        args.repo,
        failing_test=_norm_opt(args.failing_test),
        stacktrace=_norm_opt(args.stacktrace),
        outdir=_norm_opt(args.outdir),
        verify=bool(args.verify),
        full=bool(args.full),
        max_tests=int(args.max_tests),
        policy_path=_norm_opt(args.policy),
    )

    # Optionally emit a run-level evidencepack in FULL mode.
    ep_path = None
    if args.full:
        pack_id = args.pack_id or 'vibe-fix'
        ep_path = collect_run_evidencepack(
            repo_root=args.repo,
            pack_id=pack_id,
            report_path=artifacts.get('report'),
            claims_path=claims_path,
            gate_artifacts={k.split(':', 1)[1]: v for k, v in artifacts.items() if k.startswith('gate:')},
            out_path=args.evidencepack_out,
        )
        print(json.dumps({'evidencepack': ep_path}, indent=2, ensure_ascii=False))

    # Print primary report
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    return 0



def cmd_cache_design_init(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    root = init_cache_design(repo, force=bool(args.force))
    out = {"cache_root": str(root.relative_to(repo))}
    print(json.dumps(out, indent=2))
    return 0


def cmd_cache_design_validate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    report_path, report = validate_cache_design(repo)
    # print full report for CI friendliness
    print(json.dumps(report, indent=2))
    return 0 if bool(report.get("ok")) else 2
def cmd_cache_design_report(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    out_path = Path(args.out).resolve() if args.out else None
    out, claims = report_cache_design(repo, out_path=out_path)
    print(json.dumps({"evidencepack": str(out), "claims": str(claims)}, indent=2))
    return 0




def cmd_mode_list(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    print(json.dumps({"modes": mode_list(repo)}, indent=2, ensure_ascii=False))
    return 0


def cmd_mode_apply(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    outdir = Path(args.outdir).resolve() if args.outdir else None
    run_dir = mode_apply(repo, args.mode, outdir=outdir, run_id=args.run_id, force=bool(args.force))
    print(json.dumps({"run_dir": str(run_dir)}, indent=2, ensure_ascii=False))
    return 0


def cmd_mode_run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if args.run_dir:
        run_dir = Path(args.run_dir).resolve()
    else:
        # auto-create run workspace from template
        run_dir = mode_apply(repo, args.mode, outdir=None, run_id=args.run_id, force=False)

    res = mode_run(
        repo,
        args.mode,
        run_dir,
        query=args.query,
        full=bool(args.full),
        kind=args.kind,
        spec=args.spec,
    )
    print(json.dumps(res.__dict__, indent=2, ensure_ascii=False))
    return 0 if res.ok else 2


def cmd_graph_build(args: argparse.Namespace) -> int:
    res = build_graph(args.repo, files=args.files, db_path=_norm_opt(args.db))
    print(json.dumps(res.__dict__, indent=2, ensure_ascii=False))
    return 0


def cmd_graph_impact(args: argparse.Namespace) -> int:
    changed = args.changed or []
    if not changed:
        raise ValueError('graph-impact requires at least one --changed <file>')
    res = impacted_files(args.repo, changed_files=changed, db_path=_norm_opt(args.db), depth=int(args.depth))
    print(json.dumps({'changed': changed, 'impacted': res, 'count': len(res)}, indent=2, ensure_ascii=False))
    return 0


def cmd_patch_check(args: argparse.Namespace) -> int:
    p = Path(args.patch)
    if not p.exists():
        raise ValueError(f'Patch file not found: {p}')
    diff = p.read_text(encoding='utf-8', errors='ignore')
    ok, reasons = validate_patch(diff, PatchConstraints(max_files_touched=int(args.max_files)))
    out = {'ok': ok, 'reasons': reasons, 'patch': str(p)}
    if args.out:
        _write_json(args.out, out)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if ok else 2

def cmd_review(args: argparse.Namespace) -> int:
    report = analyze_repo(
        target_path=args.repo,
        mode=args.mode,
        task=args.task or '',
        diff_base=_norm_opt(args.diff_base),
        run_gates=bool(args.run_gates),
        gates=None,
        policy_path=_norm_opt(args.policy),
        seed=int(args.seed or 0),
        min_confidence=int(args.confidence),
    )

    # Default evidence level: E2 if any gates executed, else E0.
    report.evidence_level = 'E2' if bool(args.run_gates) else 'E0'

    out_path = args.out or str(Path(report.repo_root) / '.vibe' / 'reports' / 'vibe-report.json')
    _write_json(out_path, report.to_dict())

    sarif_path = None
    if args.sarif_out:
        sarif_path = write_sarif(args.sarif_out, report)

    # CI helpers / policy enforcement
    rc = 0
    if args.min_score is not None:
        try:
            overall = int((report.scores or {}).get('overall') or 0)
            if overall < int(args.min_score):
                rc = max(rc, 3)
        except Exception:
            pass

    if args.fail_on is not None:
        thr = str(args.fail_on).lower().strip()
        if thr:
            t_rank = _severity_rank(thr)
            if any(_severity_rank(f.severity) <= t_rank for f in report.findings):
                rc = max(rc, 4)

    # Claims ledger (prevents governance theater): always emit for review runs.
    claims_out = str(Path(report.repo_root) / '.vibe' / 'reports' / 'vibe-review.claims.json')
    claims: List[Claim] = [
        Claim(claim='review:report', evidence_level='E3', tool='vibe', artifact=out_path),
    ]
    if sarif_path:
        claims.append(Claim(claim='review:sarif', evidence_level='E3', tool='vibe', artifact=sarif_path))

    for g in report.gates or []:
        claims.append(Claim(
            claim=f'gate:{g.name}',
            evidence_level=str(getattr(g, 'evidence_level', 'E0')),
            tool='gate',
            artifact=(g.artifacts or {}).get('sarif') if isinstance(g.artifacts, dict) else None,
            meta={'exit_code': g.exit_code, 'command': g.command},
        ))

    ledger = ClaimsLedger(version=report.version, run_id='vibe-review', claims=claims)
    claims_path = write_claims_ledger(report.repo_root, ledger, claims_out)

    # Learning loop: append outcome telemetry
    learning_path = append_event(report.repo_root, report, outcome='ok' if rc == 0 else 'fail', meta={'rc': rc})

    # Optional: generate an EvidencePack for this run (E3).
    if bool(getattr(args, 'evidencepack', False)) or getattr(args, 'evidencepack_out', None):
        ep_path = collect_run_evidencepack(
            repo_root=report.repo_root,
            pack_id='vibe-review',
            report_path=out_path,
            sarif_path=sarif_path,
            claims_path=claims_path,
            learning_path=learning_path,
            out_path=str(args.evidencepack_out) if args.evidencepack_out else None,
        )
        report.evidence_level = 'E3'
        report.evidencepack_path = ep_path
        _write_json(out_path, report.to_dict())

    if args.md_out:
        write_report_markdown(args.md_out, report)

    print(out_path)
    return rc


def cmd_sarif(args: argparse.Namespace) -> int:
    data = load_report(args.report)
    report = Report.from_dict(data)
    out = write_sarif(args.out, report)
    print(out)
    return 0


def cmd_baseline_set(args: argparse.Namespace) -> int:
    report = analyze_repo(
        target_path=args.repo,
        mode=args.mode,
        task=args.task or '',
        diff_base=_norm_opt(args.diff_base),
        run_gates=False,
        policy_path=_norm_opt(args.policy),
        seed=int(args.seed or 0),
        min_confidence=int(args.confidence),
    )
    path = write_baseline(report.repo_root, report, filename=args.filename)
    print(path)
    return 0


def cmd_baseline_compare(args: argparse.Namespace) -> int:
    baseline = load_report(args.baseline)
    report = analyze_repo(
        target_path=args.repo,
        mode=args.mode,
        task=args.task or '',
        diff_base=_norm_opt(args.diff_base),
        run_gates=False,
        policy_path=_norm_opt(args.policy),
        seed=int(args.seed or 0),
        min_confidence=int(args.confidence),
    )
    nf = new_findings(baseline, report)

    out_json = args.out or str(Path(report.repo_root) / '.vibe' / 'reports' / 'vibe-new-findings.json')
    _write_json(out_json, {
        'version': report.version,
        'baseline': args.baseline,
        'new_findings': [f.to_dict() for f in nf],
    })

    if args.md_out:
        write_findings_markdown(args.md_out, nf, title='New Findings (since baseline)')

    print(out_json)
    return 3 if baseline_failed else 0


def cmd_autopatch(args: argparse.Namespace) -> int:
    report = analyze_repo(
        target_path=args.repo,
        mode=args.mode,
        task=args.task or '',
        diff_base=_norm_opt(args.diff_base),
        run_gates=False,
        policy_path=_norm_opt(args.policy),
        seed=int(args.seed or 0),
        min_confidence=int(args.confidence),
    )

    patches = generate_whitespace_patches(report.repo_root, report.analyzed_files, diff_base=_norm_opt(args.diff_base))
    if not patches:
        print('NO_PATCHES')
        return 0

    combined = render_combined_patch(patches)
    out_patch = args.out or str(Path(report.repo_root) / '.vibe' / 'patches' / 'vibe-whitespace.patch')
    _write_text(out_patch, combined)

    if args.apply:
        apply_patches(patches)

    print(out_patch)
    return 0


def cmd_golden(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    stacks = detect_stacks(repo_root)
    patches = generate_golden_config_patches(repo_root, stacks)
    if not patches:
        print('NO_PATCHES')
        return 0

    combined = render_combined_patch(patches)
    out_patch = args.out or str(Path(repo_root) / '.vibe' / 'patches' / 'vibe-golden.patch')
    _write_text(out_patch, combined)

    if args.apply:
        apply_golden_patches(patches)

    print(out_patch)
    return 0


def _load_spec(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    if p.suffix.lower() == '.json':
        try:
            return json.loads(p.read_text(encoding='utf-8', errors='ignore'))
        except Exception:
            return {}
    return load_yaml_file(str(p))


def cmd_build(args: argparse.Namespace) -> int:
    kind = str(args.kind).strip().lower()
    spec = _load_spec(args.spec)

    ok, missing = validate_spec(kind, spec)
    if not ok:
        out = {
            'ok': False,
            'kind': kind,
            'missing_required': missing,
            'required_hint': f"Provide keys: {', '.join(missing)}",
        }
        out_path = args.out or str(Path(args.outdir) / 'vibe-build-missing.json')
        _write_json(out_path, out)
        print(out_path)
        return 2

    outdir = str(Path(args.outdir).resolve())
    scaffold(kind, outdir, spec)

    # Run verification loop by default: review -> (optional gates) -> sarif -> summary
    report = analyze_repo(
        target_path=outdir,
        mode=args.mode,
        task=f'build:{kind}',
        diff_base=None,
        run_gates=bool(args.run_gates),
        policy_path=_norm_opt(args.policy),
        seed=int(args.seed or 0),
        min_confidence=int(args.confidence),
    )

    report.evidence_level = 'E2' if bool(args.run_gates) else 'E0'

    sarif_path = None
    if args.sarif_out:
        sarif_path = write_sarif(args.sarif_out, report)

    out_json = args.out or str(Path(outdir) / '.vibe' / 'reports' / 'vibe-build-report.json')
    _write_json(out_json, report.to_dict())

    # Baseline compare gate (E3) — enforced in build pipeline.
    # Policy: if a baseline exists, fail build on new findings unless explicitly allowed.
    # If baseline is missing, initialize it (unless --require-baseline is set).
    baseline_failed = False
    gate_artifacts: Dict[str, str] = {}

    baseline_path = _norm_opt(getattr(args, 'baseline', None))
    if baseline_path is None:
        baseline_path = str(Path(outdir) / '.vibe' / 'baseline.json')
    require_baseline = bool(getattr(args, 'require_baseline', False))
    allow_regressions = bool(getattr(args, 'allow_baseline_regressions', False))

    base_fp = Path(baseline_path)
    compare_out = str(Path(outdir) / '.vibe' / 'reports' / 'baseline-compare.json')

    if base_fp.exists() and base_fp.is_file():
        baseline = load_report(str(base_fp))
        nf = new_findings(baseline, report)
        _write_json(compare_out, {
            'ok': len(nf) == 0,
            'baseline': str(base_fp),
            'new_findings_count': len(nf),
            'new_findings': [f.to_dict() for f in nf],
        })
        gate_artifacts['baseline-compare'] = compare_out
        gate_artifacts['baseline'] = str(base_fp)

        ok_baseline = len(nf) == 0
        report.gates.append(GateResult(
            name='baseline-compare',
            command=f'baseline-compare {base_fp}',
            allowed=ok_baseline or allow_regressions,
            evidence_level='E3',
            exit_code=0 if (ok_baseline or allow_regressions) else 3,
            stdout=f'New findings since baseline: {len(nf)}',
            stderr='' if (ok_baseline or allow_regressions) else 'Baseline regression detected',
            artifacts={'baseline': str(base_fp), 'compare': compare_out},
        ))
        baseline_failed = (not ok_baseline) and (not allow_regressions)
    else:
        if require_baseline:
            report.gates.append(GateResult(
                name='baseline-missing',
                command=f'baseline-required {base_fp}',
                allowed=False,
                evidence_level='E0',
                exit_code=2,
                stdout='',
                stderr='Baseline file is required but was not found.',
                artifacts=None,
            ))
            baseline_failed = True
        else:
            # Initialize baseline on first run (E3 artifact).
            base_fp.parent.mkdir(parents=True, exist_ok=True)
            _write_json(str(base_fp), report.to_dict())
            gate_artifacts['baseline'] = str(base_fp)
            report.gates.append(GateResult(
                name='baseline-init',
                command=f'baseline-init {base_fp}',
                allowed=True,
                evidence_level='E3',
                exit_code=0,
                stdout=f'Baseline initialized at {base_fp}',
                stderr='',
                artifacts={'baseline': str(base_fp)},
            ))

    # Persist build report with baseline gate results before packaging evidence.
    _write_json(out_json, report.to_dict())

    # Claims ledger (E3): build mode must be machine-verifiable.
    claims_out = str(Path(outdir) / '.vibe' / 'reports' / 'vibe-build.claims.json')
    claims: List[Claim] = [
        Claim(claim='build:report', evidence_level='E3', tool='vibe', artifact=out_json),
    ]
    if sarif_path:
        claims.append(Claim(claim='build:sarif', evidence_level='E3', tool='vibe', artifact=sarif_path))

    # Include baseline artifacts as explicit claims.
    if base_fp.exists() and base_fp.is_file():
        claims.append(Claim(claim='build:baseline', evidence_level='E3', tool='vibe', artifact=str(base_fp)))
        if Path(compare_out).exists():
            claims.append(Claim(claim='build:baseline-compare', evidence_level='E3', tool='vibe', artifact=compare_out))

    # Gate claims (stdout/stderr is E2; artifacts are E3).
    for g in report.gates or []:
        ev = str(getattr(g, 'evidence_level', 'E0'))
        claims.append(Claim(
            claim=f'gate:{g.name}',
            evidence_level=ev,
            tool='gate',
            artifact=None,
            meta={'exit_code': g.exit_code, 'command': g.command},
        ))
        if isinstance(g.artifacts, dict):
            for k, p in g.artifacts.items():
                if p:
                    claims.append(Claim(
                        claim=f'gate:{g.name}:artifact:{k}',
                        evidence_level='E3',
                        tool='gate',
                        artifact=str(p),
                    ))

    ledger = ClaimsLedger(version=report.version, run_id='vibe-build', claims=claims)
    claims_path = write_claims_ledger(outdir, ledger, claims_out)

    # Learning loop: append outcome telemetry
    learning_path = append_event(outdir, report, outcome='ok' if not baseline_failed else 'fail', meta={'baseline_failed': baseline_failed})

    # Build mode always emits a run EvidencePack for CI use.
    ep_out = str(Path(outdir) / '.vibe' / 'reports' / 'vibe-build.evidencepack.json')
    ep_path = collect_run_evidencepack(
        repo_root=outdir,
        pack_id='vibe-build',
        report_path=out_json,
        sarif_path=sarif_path,
        baseline_path=baseline_path,
        claims_path=claims_path,
        learning_path=learning_path,
        gate_artifacts=gate_artifacts,
        out_path=ep_out,
    )
    report.evidence_level = 'E3'
    report.evidencepack_path = ep_path
    _write_json(out_json, report.to_dict())

    if args.md_out:
        write_report_markdown(args.md_out, report)

    print(out_json)
    return 3 if baseline_failed else 0


def cmd_resolve(args: argparse.Namespace) -> int:
    if args.report:
        data = load_report(args.report)
        report = Report.from_dict(data)
        repo_root = report.repo_root
    else:
        report = analyze_repo(
            target_path=args.repo,
            mode=args.mode,
            task=args.task or '',
            diff_base=_norm_opt(args.diff_base),
            run_gates=False,
            policy_path=_norm_opt(args.policy),
            seed=int(args.seed or 0),
            min_confidence=int(args.confidence),
        )
        repo_root = report.repo_root

    res = generate_resolve_patches(repo_root, report, diff_base=_norm_opt(args.diff_base))
    patches = res.get('patches') or []
    if not patches:
        print('NO_PATCHES')
        return 0

    combined = render_combined_patch(patches)
    out_patch = args.out or str(Path(repo_root) / '.vibe' / 'patches' / 'vibe-resolve.patch')
    _write_text(out_patch, combined)

    if args.apply:
        # Apply whitespace patches via existing engine; apply in-file transformations via resolve_engine outputs.
        ws = [p for p in patches if 'whitespace' in ((p.description or '').lower())]
        if ws:
            apply_patches(ws)
        apply_files = res.get('apply_files') or {}
        if isinstance(apply_files, dict):
            for fp, txt in apply_files.items():
                try:
                    Path(fp).write_text(str(txt), encoding='utf-8')
                except Exception:
                    continue

    print(out_patch)
    return 0


def cmd_sarif_merge(args: argparse.Namespace) -> int:
    # Merge multiple SARIF docs by concatenating runs.
    def load_doc(p: str) -> Optional[Dict[str, Any]]:
        try:
            d = json.loads(Path(p).read_text(encoding='utf-8', errors='ignore'))
            return d if isinstance(d, dict) and isinstance(d.get('runs'), list) else None
        except Exception:
            return None

    base = load_doc(args.base)
    if not base:
        raise SystemExit(f'Invalid SARIF: {args.base}')

    out_runs = list(base.get('runs') or [])
    for ex in args.extra or []:
        doc = load_doc(ex)
        if not doc:
            continue
        for run in doc.get('runs') or []:
            out_runs.append(run)

    merged = dict(base)
    merged['runs'] = out_runs

    out_path = args.out
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
    print(out_path)
    return 0




def cmd_index_build(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    db_path = args.db or str(Path(repo_root) / '.vibe' / 'index' / 'vibe_index.db')
    payload = build_repo_index(repo_root, db_path, vector=not bool(getattr(args, "no_vector", False)), vector_dim=int(getattr(args, "vec_dim", 256)))
    stats_path = save_index_stats(repo_root, payload)
    if args.out:
        _write_json(args.out, payload)
        print(args.out)
    else:
        print(stats_path)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    db_path = args.db or str(Path(repo_root) / '.vibe' / 'index' / 'vibe_index.db')
    results = semantic_search(repo_root, args.query, db_path=db_path, mode=args.mode, limit=int(args.limit))
    out = {'repo': repo_root, 'query': args.query, 'mode': args.mode, 'results': results}
    if args.out:
        _write_json(args.out, out)
        print(args.out)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_select_tests(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    changed: List[str] = []
    if args.changed:
        changed = [c.strip() for c in args.changed if str(c).strip()]
    elif args.diff_base:
        # Use git diff to determine changed files.
        try:
            from core.repo_scanner import git_changed_files
            changed = [str(p) for p in git_changed_files(repo_root, base=_norm_opt(args.diff_base))]
        except Exception:
            changed = []

    sel = select_tests(repo_root, changed_files=changed, max_tests=int(args.max_tests))
    out = {
        'repo': repo_root,
        'changed_files': sel.changed_files,
        'impacted_files': sel.impacted_files,
        'selected_tests': sel.selected_tests,
        'all_tests_count': sel.all_tests_count,
    }
    if args.out:
        _write_json(args.out, out)
        print(args.out)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_kb_update(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    policy = Policy.load(_norm_opt(args.policy))
    out_dir = args.outdir or str(Path(repo_root) / '.vibe' / 'kb')
    res: Dict[str, Any] = {'ok': True, 'runs': []}

    if args.github_repo:
        ref = args.github_ref or 'main'
        paths = [p.strip() for p in (args.github_paths or '').split(',') if p.strip()]
        if not paths:
            paths = ['README.md']
        r = update_github_raw(args.github_repo, ref, paths, out_dir, policy)
        res['runs'].append({'type': 'github', **r.__dict__})

    if args.reddit_sub and args.reddit_query:
        r = update_reddit_search(args.reddit_sub, args.reddit_query, out_dir, policy, limit=int(args.reddit_limit))
        res['runs'].append({'type': 'reddit', **r.__dict__})

    res['ok'] = all((run.get('ok') for run in res['runs'])) if res['runs'] else False

    out_path = args.out or str(Path(repo_root) / '.vibe' / 'kb' / 'kb-update.json')
    _write_json(out_path, res)
    print(out_path)
    return 0


def cmd_dag_run(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    policy = Policy.load(_norm_opt(args.policy))
    result = run_dag(args.spec, repo_root, policy)
    out = dag_to_dict(result)
    out_path = args.out or str(Path(repo_root) / '.vibe' / 'dag' / 'dag-run.json')
    _write_json(out_path, out)
    print(out_path)
    return 0


def cmd_debate(args: argparse.Namespace) -> int:
    report = None
    if args.report:
        data = load_report(args.report)
        report = Report.from_dict(data)
    d = generate_debate(args.question, report=report)
    out_json = args.out or (str(Path(report.repo_root) / '.vibe' / 'debate' / 'debate.json') if report else '.vibe/debate.json')
    _write_json(out_json, debate_to_dict(d))

    if args.md_out:
        _write_text(args.md_out, debate_to_markdown(d))

    print(out_json)
    return 0



# --- IKO / EvidencePack / Gatekeeper / RLM commands ---

def cmd_iko_new(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    iko = IKO(id=str(args.id), title=str(args.title), description=str(args.description or ''))
    iko.add_event(actor=str(args.actor or 'user'), action='IKO_CREATED')
    path = save_iko(repo_root, iko)
    print(path)
    return 0


def cmd_iko_show(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    iko = load_iko(repo_root, str(args.id))
    if not iko:
        raise SystemExit('IKO_NOT_FOUND')
    print(json.dumps(iko.to_dict(), indent=2, ensure_ascii=False))
    return 0


def cmd_iko_list(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    print(json.dumps({'ids': list_iko_ids(repo_root)}, indent=2, ensure_ascii=False))
    return 0


def cmd_evidencepack(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    out_dir = args.outdir or str(Path(repo_root) / '.vibe' / 'evidence')
    path = collect_evidencepack(repo_root, str(args.issue_id), out_dir, ci_run_id=_norm_opt(args.ci_run_id))
    print(path)
    return 0


def cmd_gatekeeper(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    res = transition_iko(
        repo_root=repo_root,
        issue_id=str(args.issue_id),
        to_state=str(args.to),
        actor=str(args.actor or 'gatekeeper'),
        reason=str(args.reason or ''),
        evidencepack_path=_norm_opt(args.evidencepack),
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get('ok') else 2


def cmd_investigate(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    db = _norm_opt(args.db)
    path = rlm_investigate(repo_root, str(args.issue_id), str(args.question), db_path=db, limit=int(args.limit))
    print(path)
    return 0


def cmd_v13_search(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    searcher = AdvancedSearch(repo_root)

    if args.action == 'index':
        files = [str(p) for p in Path(repo_root).rglob('*') if p.is_file()]
        path = searcher.index(files)
        print(f"Index created at: {path}")
        return 0

    if args.action == 'facets':
        print(json.dumps(searcher.facets(), indent=2, ensure_ascii=False))
        return 0

    if args.action == 'hints':
        print(json.dumps(searcher.hints(args.query), indent=2, ensure_ascii=False))
        return 0

    if args.action == 'pointer':
        pid = str(getattr(args, 'id', '') or '')
        if not pid:
            pid = str(getattr(args, 'symbol_id', '') or '')
        if not pid:
            print(json.dumps({"error": "missing --id/--symbol-id"}, indent=2))
            return 2
        print(json.dumps(searcher.pointer(pid), indent=2, ensure_ascii=False))
        return 0

    # default: locate
    results = searcher.locate(args.query, limit=getattr(args, 'limit', 20))
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def cmd_v13_rag(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    rag = AdvancedRAG(repo_root)
    if args.action == 'ingest':
        # Load sources + settings
        settings = {}
        if _norm_opt(getattr(args, 'spec', None)):
            spec = load_yaml_file(str(args.spec)) or {}
            sources = spec.get('sources') or spec.get('kb') or []
            if isinstance(spec, dict):
                settings = dict(spec.get('settings') or {}) if isinstance(spec.get('settings') or {}, dict) else {}
        else:
            sources = json.loads(args.sources)

        # Dense index build happens during ingest only if enabled.
        enable_dense = bool(settings.get('enable_dense', False))
        dense_provider = str(settings.get('dense_provider') or (settings.get('dense') or {}).get('provider') or 'stub_hash')
        dense_model = str(settings.get('dense_model') or (settings.get('dense') or {}).get('model') or 'hash-256')
        dense_dim = int(settings.get('dense_dim') or (settings.get('dense') or {}).get('dim') or 256)
        dense_backend = str(settings.get('dense_backend') or (settings.get('dense') or {}).get('backend') or 'scan')

        # CLI overrides (optional)
        if getattr(args, 'enable_dense', None) is not None:
            enable_dense = bool(getattr(args, 'enable_dense'))
        if getattr(args, 'dense_provider', None) is not None:
            dense_provider = str(getattr(args, 'dense_provider'))
        if getattr(args, 'dense_model', None) is not None:
            dense_model = str(getattr(args, 'dense_model'))
        if getattr(args, 'dense_dim', None) is not None:
            dense_dim = int(getattr(args, 'dense_dim'))
        if getattr(args, 'dense_backend', None) is not None:
            dense_backend = str(getattr(args, 'dense_backend'))

        path = rag.ingest(
            sources,
            chunk_size_chars=int(getattr(args, 'chunk_chars', 900)),
            chunk_overlap_chars=int(getattr(args, 'chunk_overlap', 120)),
            enable_dense=bool(enable_dense),
            dense_provider=str(dense_provider),
            dense_model=str(dense_model),
            dense_dim=int(dense_dim),
        )
        print(json.dumps({'kb': path}, indent=2, ensure_ascii=False))

    elif args.action == 'query':
        # Optional settings from spec (if provided)
        settings = {}
        if _norm_opt(getattr(args, 'spec', None)):
            spec = load_yaml_file(str(args.spec)) or {}
            if isinstance(spec, dict):
                settings = dict(spec.get('settings') or {}) if isinstance(spec.get('settings') or {}, dict) else {}

        preset = int(getattr(args, 'preset', None) or settings.get('preset') or 1)
        # Preset defaults (still offline-first)
        enable_graphrag = settings.get('enable_graphrag', True)
        enable_raptor = settings.get('enable_raptor', True)
        enable_crag = settings.get('enable_crag', True)
        crag_max_passes = settings.get('crag_max_passes', 1)
        graphrag_expand_k = settings.get('graphrag_expand_k', 6)
        raptor_summary_k = settings.get('raptor_summary_k', 4)
        include_summaries = bool(settings.get('include_summaries', False))

        # Adapter-based dense + fusion + rerank defaults (off unless enabled)
        enable_dense = bool(settings.get('enable_dense', False))
        dense_provider = str(settings.get('dense_provider') or (settings.get('dense') or {}).get('provider') or 'stub_hash')
        dense_model = str(settings.get('dense_model') or (settings.get('dense') or {}).get('model') or 'hash-256')
        dense_dim = int(settings.get('dense_dim') or (settings.get('dense') or {}).get('dim') or 256)
        dense_backend = str(settings.get('dense_backend') or (settings.get('dense') or {}).get('backend') or 'scan')
        dense_topk = int(settings.get('dense_topk') or (settings.get('dense') or {}).get('topk') or 24)
        dense_backend = str(settings.get('dense_backend') or (settings.get('dense') or {}).get('backend') or 'scan')

        fusion_mode = str(settings.get('fusion_mode') or (settings.get('fusion') or {}).get('mode') or 'rrf')
        fusion_rrf_k = int(settings.get('fusion_rrf_k') or (settings.get('fusion') or {}).get('rrf_k') or 60)
        fusion_w_bm25 = float(settings.get('fusion_w_bm25') or (settings.get('fusion') or {}).get('w_bm25') or 1.0)
        fusion_w_dense = float(settings.get('fusion_w_dense') or (settings.get('fusion') or {}).get('w_dense') or 1.0)

        enable_rerank = bool(settings.get('enable_rerank', False))
        rerank_provider = str(settings.get('rerank_provider') or (settings.get('rerank') or {}).get('provider') or 'stub')
        rerank_model = str(settings.get('rerank_model') or (settings.get('rerank') or {}).get('model') or 'noop')
        rerank_topk = int(settings.get('rerank_topk') or (settings.get('rerank') or {}).get('topk') or 12)

        if preset == 2:
            # Slightly more aggressive but still deterministic/offline.
            crag_max_passes = max(int(crag_max_passes), 2)
            graphrag_expand_k = max(int(graphrag_expand_k), 8)
            raptor_summary_k = max(int(raptor_summary_k), 6)
            include_summaries = True

        # CLI flags override spec defaults when provided (tri-state)
        if getattr(args, 'enable_graphrag', None) is not None:
            enable_graphrag = bool(getattr(args, 'enable_graphrag'))
        if getattr(args, 'enable_raptor', None) is not None:
            enable_raptor = bool(getattr(args, 'enable_raptor'))
        if getattr(args, 'enable_crag', None) is not None:
            enable_crag = bool(getattr(args, 'enable_crag'))
        if getattr(args, 'crag_max_passes', None) is not None:
            crag_max_passes = int(getattr(args, 'crag_max_passes'))
        if getattr(args, 'graphrag_expand_k', None) is not None:
            graphrag_expand_k = int(getattr(args, 'graphrag_expand_k'))
        if getattr(args, 'raptor_summary_k', None) is not None:
            raptor_summary_k = int(getattr(args, 'raptor_summary_k'))

        if getattr(args, 'enable_dense', None) is not None:
            enable_dense = bool(getattr(args, 'enable_dense'))
        if getattr(args, 'dense_provider', None) is not None:
            dense_provider = str(getattr(args, 'dense_provider'))
        if getattr(args, 'dense_model', None) is not None:
            dense_model = str(getattr(args, 'dense_model'))
        if getattr(args, 'dense_dim', None) is not None:
            dense_dim = int(getattr(args, 'dense_dim'))
        if getattr(args, 'dense_backend', None) is not None:
            dense_backend = str(getattr(args, 'dense_backend'))
        if getattr(args, 'dense_topk', None) is not None:
            dense_topk = int(getattr(args, 'dense_topk'))

        if getattr(args, 'fusion_mode', None) is not None:
            fusion_mode = str(getattr(args, 'fusion_mode'))
        if getattr(args, 'fusion_rrf_k', None) is not None:
            fusion_rrf_k = int(getattr(args, 'fusion_rrf_k'))
        if getattr(args, 'fusion_w_bm25', None) is not None:
            fusion_w_bm25 = float(getattr(args, 'fusion_w_bm25'))
        if getattr(args, 'fusion_w_dense', None) is not None:
            fusion_w_dense = float(getattr(args, 'fusion_w_dense'))

        if getattr(args, 'enable_rerank', None) is not None:
            enable_rerank = bool(getattr(args, 'enable_rerank'))
        if getattr(args, 'rerank_provider', None) is not None:
            rerank_provider = str(getattr(args, 'rerank_provider'))
        if getattr(args, 'rerank_model', None) is not None:
            rerank_model = str(getattr(args, 'rerank_model'))
        if getattr(args, 'rerank_topk', None) is not None:
            rerank_topk = int(getattr(args, 'rerank_topk'))

        res = rag.query(
            args.prompt,
            limit=int(getattr(args, 'limit', 6)),
            max_context_chars=int(getattr(args, 'max_context_chars', 8000)),
            enable_graphrag=bool(enable_graphrag),
            enable_raptor=bool(enable_raptor),
            enable_crag=bool(enable_crag),
            crag_max_passes=int(crag_max_passes),
            graphrag_expand_k=int(graphrag_expand_k),
            raptor_summary_k=int(raptor_summary_k),
            include_summaries=bool(include_summaries),
            enable_dense=bool(enable_dense),
            dense_backend=str(dense_backend),
            dense_topk=int(dense_topk),
            fusion_mode=str(fusion_mode),
            fusion_rrf_k=int(fusion_rrf_k),
            fusion_w_bm25=float(fusion_w_bm25),
            fusion_w_dense=float(fusion_w_dense),
            enable_rerank=bool(enable_rerank),
            rerank_provider=str(rerank_provider),
            rerank_model=str(rerank_model),
            rerank_topk=int(rerank_topk),
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.action == 'eval':
        spec_path = str(getattr(args, 'spec', '') or '')
        eval_path = str(getattr(args, 'eval', '') or '')
        if not spec_path or not eval_path:
            print(json.dumps({'error': 'missing --spec and/or --eval'}, indent=2))
            return 2

        out = run_rag_eval(
            repo_root=repo_root,
            spec_path=spec_path,
            eval_path=eval_path,
            out_report_path=getattr(args, 'out', None),
            out_claims_path=getattr(args, 'claims_out', None),
            out_evidencepack_path=getattr(args, 'evidencepack_out', None),
            max_context_chars=int(getattr(args, 'max_context_chars', 8000)),
        )
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_v13_init(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    kinds = json.loads(args.kinds) if _norm_opt(args.kinds) else None
    res = v13_init_repo(repo_root, kinds=kinds)
    out = args.out or str(Path(repo_root) / '.vibe' / 'reports' / 'v13_init.json')
    _write_json(out, res)
    print(out)
    return 0 if res.get('ok') else 2


def cmd_v13_preflight(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    ok, res = v13_preflight(repo_root, kind=str(args.kind), spec_path=_norm_opt(args.spec))
    out = args.out or str(Path(repo_root) / '.vibe' / 'reports' / 'v13_preflight.json')
    _write_json(out, res)
    print(out)
    return 0 if ok else 2


def cmd_v13_self_review(args: argparse.Namespace) -> int:
    repo_root = str(Path(args.repo).resolve())
    res = v13_self_review(repo_root, kind=str(args.kind), spec_path=_norm_opt(args.spec))
    out_json = args.out or str(Path(repo_root) / '.vibe' / 'reports' / 'v13_self_review.json')
    _write_json(out_json, res)
    if args.md_out:
        _write_text(args.md_out, v13_self_review_md(res))
    if args.sarif_out:
        _write_json(args.sarif_out, v13_self_review_sarif(res))
    print(out_json)
    return 0 if res.get('ok') else 2



def main() -> int:
    p = argparse.ArgumentParser(prog='vibe', description='Vibe Coder v13.0.0 - Repo Intelligence & Governance OS (Antigravity)')
    sub = p.add_subparsers(dest='cmd', required=True)

    # status
    ps = sub.add_parser('status', help='Print detected stacks and tool versions')
    ps.add_argument('--repo', default='.')
    ps.set_defaults(fn=cmd_status)

    # skills-reindex
    psi = sub.add_parser('skills-reindex', help='Rebuild skill automap + audit report (routing automation)')
    psi.add_argument('--repo', default='.')
    psi.set_defaults(fn=cmd_skills_reindex)


    # doctor
    pd = sub.add_parser('doctor', help='Environment + repo readiness checks (A–Z entrypoint)')
    pd.add_argument('--repo', default='.')
    pd.add_argument('--kind', default=None, help='Optional stack kind hint (nextjs|nestjs|python)')
    pd.add_argument('--spec', default=None, help='Optional spec.yml path for validation')
    pd.add_argument('--full', action='store_true', help='Treat this as VIBE_FULL (stricter checks)')
    pd.add_argument('--baseline', default=None, help='Baseline path (defaults to .vibe/baseline.json)')
    pd.add_argument('--require-baseline', action='store_true', help='Fail if baseline missing')
    pd.add_argument('--out', default=None, help='Write doctor report JSON here (default .vibe/reports/doctor.json)')
    pd.set_defaults(fn=cmd_doctor)

    # explain
    pe = sub.add_parser('explain', help='Grounded repo explanation (hybrid retrieval + pointers)')
    pe.add_argument('--repo', default='.')
    pe.add_argument('--query', required=True)
    pe.add_argument('--topk', default=10, type=int)
    pe.add_argument('--out', default=None, help='Write explain JSON here (default .vibe/reports/explain.json)')
    pe.add_argument('--md-out', default=None, help='Optional markdown output path')
    pe.set_defaults(fn=cmd_explain)

    # fix
    pf = sub.add_parser('fix', help='Bugfix flow scaffold + optional verification (pytest)')
    pf.add_argument('--repo', default='.')
    pf.add_argument('--failing-test', default=None, help='Failing test (nodeid/path/pattern)')
    pf.add_argument('--stacktrace', default=None, help='Path to stacktrace file OR inline stacktrace text')
    pf.add_argument('--outdir', default=None, help='Output bundle directory (default .vibe/fix/latest)')
    pf.add_argument('--verify', action='store_true', help='Run focused verification (pytest on selected tests)')
    pf.add_argument('--max-tests', default=20, type=int)
    pf.add_argument('--full', action='store_true', help='Emit EvidencePack (E3) for the fix run')
    pf.add_argument('--pack-id', default=None, help='EvidencePack id (default vibe-fix)')
    pf.add_argument('--evidencepack-out', default=None, help='EvidencePack output path')
    pf.add_argument('--policy', default=None, help='Policy file for allowed commands (default policy)')
    pf.set_defaults(fn=cmd_fix)

    # cache-design
    pcd = sub.add_parser('cache-design', help='Cache-Design base skill runner (init/validate) — enterprise artifacts A–H')
    pcd.add_argument('--repo', default='.')
    pcd_sub = pcd.add_subparsers(dest='cache_cmd', required=True)

    pcdi = pcd_sub.add_parser('init', help='Scaffold .cache/cache-design folder + artifact templates')
    pcdi.add_argument('--force', action='store_true', help='Overwrite existing templates/spec')
    pcdi.set_defaults(fn=cmd_cache_design_init)

    pcdv = pcd_sub.add_parser('validate', help='Validate artifacts + validators 13.1–13.3; emits validators_report.json')
    pcdv.set_defaults(fn=cmd_cache_design_validate)


    pcdr = pcd_sub.add_parser('report', help='Emit cache-design EvidencePack + claims ledger (E3 bundle)')
    pcdr.add_argument('--out', default=None, help='Optional evidencepack output path')
    pcdr.set_defaults(fn=cmd_cache_design_report)

    pmode = sub.add_parser('mode', help='Template modes: apply/run with evidence bundles')
    sub_mode = pmode.add_subparsers(dest='mode_cmd', required=True)

    pml = sub_mode.add_parser('list', help='List available mode templates')
    pml.add_argument('--repo', default='.')
    pml.set_defaults(fn=cmd_mode_list)

    pma = sub_mode.add_parser('apply', help='Create a run workspace from a mode template')
    pma.add_argument('--repo', default='.')
    pma.add_argument('mode', help='Mode template name (e.g., build-n8n)')
    pma.add_argument('--outdir', default=None, help='Optional run directory (default: .vibe/runs/<mode>-<timestamp>)')
    pma.add_argument('--run-id', default=None, help='Optional run id (folder name)')
    pma.add_argument('--force', action='store_true')
    pma.set_defaults(fn=cmd_mode_apply)

    pmr = sub_mode.add_parser('run', help='Run a mode workflow and emit an E3 bundle (mode.evidencepack.json)')
    pmr.add_argument('--repo', default='.')
    pmr.add_argument('mode', help='Mode template name')
    pmr.add_argument('--run-dir', default=None, help='Existing run directory; if absent, one will be created')
    pmr.add_argument('--run-id', default=None, help='Optional run id for auto-created run dir')
    pmr.add_argument('--kind', default=None, help='Optional kind hint (nextjs|nestjs|tailwind|website|n8n)')
    pmr.add_argument('--spec', default=None, help='Optional spec.yml path')
    pmr.add_argument('--query', default=None, help='Optional explain query to include grounding in the bundle')
    pmr.add_argument('--full', action='store_true', help='Enable enterprise/full profile (stronger evidence expectations)')
    pmr.set_defaults(fn=cmd_mode_run)



    # graph-build
    pgb = sub.add_parser('graph-build', help='Build/update repo import graph store (incremental)')
    pgb.add_argument('--repo', default='.')
    pgb.add_argument('--files', nargs='*', default=None, help='Optional list of files to focus graph build')
    pgb.add_argument('--db', default=None, help='Graph DB path (default .vibe/graph/graph.db)')
    pgb.set_defaults(fn=cmd_graph_build)

    # graph-impact
    pgi = sub.add_parser('graph-impact', help='Compute impacted files using stored import graph')
    pgi.add_argument('--repo', default='.')
    pgi.add_argument('--changed', nargs='*', default=None, help='Changed file(s), repo-relative')
    pgi.add_argument('--depth', default=6, type=int)
    pgi.add_argument('--db', default=None)
    pgi.set_defaults(fn=cmd_graph_impact)

    # patch-check
    ppc = sub.add_parser('patch-check', help='Validate a unified diff patch against safety constraints')
    ppc.add_argument('--patch', required=True, help='Path to a unified diff file')
    ppc.add_argument('--max-files', default=5, type=int)
    ppc.add_argument('--out', default=None, help='Optional JSON output path')
    ppc.set_defaults(fn=cmd_patch_check)



    # review
    pr = sub.add_parser('review', help='Analyze repo and output report JSON (optionally MD and SARIF)')
    pr.add_argument('--repo', default='.')
    pr.add_argument('--mode', default='balanced', choices=['fast', 'balanced', 'accuracy'])
    pr.add_argument('--task', default='')
    pr.add_argument('--diff-base', default=None)
    pr.add_argument('--run-gates', action='store_true', help='Execute configured gates / suggested stack gates')
    pr.add_argument('--policy', default=None, help='Path to policy JSON (optional)')
    pr.add_argument('--seed', default=0)
    pr.add_argument('--confidence', type=int, default=80)
    pr.add_argument('--out', default=None)
    pr.add_argument('--md-out', default=None)
    pr.add_argument('--sarif-out', default=None)
    pr.add_argument('--evidencepack', action='store_true', help='Emit a run EvidencePack (hashable artifacts) and upgrade evidence_level to E3')
    pr.add_argument('--evidencepack-out', default=None, help='Optional EvidencePack output path (default: .vibe/reports/vibe-review.evidencepack.json)')
    pr.add_argument('--min-score', type=int, default=None)
    pr.add_argument('--fail-on', default=None, help='Fail if any finding severity >= threshold (critical|high|medium|low|info)')
    pr.set_defaults(fn=cmd_review)

    # sarif
    psr = sub.add_parser('sarif', help='Render SARIF from a report JSON')
    psr.add_argument('--report', required=True)
    psr.add_argument('--out', required=True)
    psr.set_defaults(fn=cmd_sarif)

    # baseline
    pb = sub.add_parser('baseline-set', help='Create baseline report for regression tracking')
    pb.add_argument('--repo', default='.')
    pb.add_argument('--mode', default='balanced', choices=['fast', 'balanced', 'accuracy'])
    pb.add_argument('--task', default='')
    pb.add_argument('--diff-base', default=None)
    pb.add_argument('--policy', default=None)
    pb.add_argument('--seed', default=0)
    pb.add_argument('--confidence', type=int, default=80)
    pb.add_argument('--filename', default='vibe-baseline.json')
    pb.set_defaults(fn=cmd_baseline_set)

    pc = sub.add_parser('baseline-compare', help='Compare current findings vs baseline')
    pc.add_argument('--repo', default='.')
    pc.add_argument('--baseline', required=True)
    pc.add_argument('--mode', default='balanced', choices=['fast', 'balanced', 'accuracy'])
    pc.add_argument('--task', default='')
    pc.add_argument('--diff-base', default=None)
    pc.add_argument('--policy', default=None)
    pc.add_argument('--seed', default=0)
    pc.add_argument('--confidence', type=int, default=80)
    pc.add_argument('--out', default=None)
    pc.add_argument('--md-out', default=None)
    pc.set_defaults(fn=cmd_baseline_compare)

    # autopatch
    pa = sub.add_parser('autopatch', help='Generate whitespace normalization patch (diff-aware if --diff-base)')
    pa.add_argument('--repo', default='.')
    pa.add_argument('--mode', default='fast', choices=['fast', 'balanced', 'accuracy'])
    pa.add_argument('--task', default='')
    pa.add_argument('--diff-base', default=None)
    pa.add_argument('--policy', default=None)
    pa.add_argument('--seed', default=0)
    pa.add_argument('--confidence', type=int, default=80)
    pa.add_argument('--out', default=None)
    pa.add_argument('--apply', action='store_true')
    pa.set_defaults(fn=cmd_autopatch)

    # golden
    pg = sub.add_parser('golden', help='Generate (create-only) golden config scaffolds as a patch')
    pg.add_argument('--repo', default='.')
    pg.add_argument('--out', default=None)
    pg.add_argument('--apply', action='store_true')
    pg.set_defaults(fn=cmd_golden)

    # resolve
    pres = sub.add_parser('resolve', help='Generate safe resolve patches (debugger/console/any/ts-ignore/n8n sanitize/whitespace)')
    pres.add_argument('--repo', default='.')
    pres.add_argument('--report', default=None, help='Use an existing report.json instead of re-analyzing')
    pres.add_argument('--mode', default='fast', choices=['fast', 'balanced', 'accuracy'])
    pres.add_argument('--task', default='')
    pres.add_argument('--diff-base', default=None)
    pres.add_argument('--policy', default=None)
    pres.add_argument('--seed', default=0)
    pres.add_argument('--confidence', type=int, default=80)
    pres.add_argument('--out', default=None)
    pres.add_argument('--apply', action='store_true', help='Apply safe patches in-place')
    pres.set_defaults(fn=cmd_resolve)

    # build
    pbuild = sub.add_parser('build', help='Project Builder Mode: spec -> scaffold -> (optional gates) -> report')
    pbuild.add_argument('--kind', required=True, choices=['nextjs', 'nestjs', 'website', 'tailwind', 'n8n'])
    pbuild.add_argument('--spec', required=True, help='YAML/JSON spec file')
    pbuild.add_argument('--outdir', required=True, help='Output directory for scaffold')
    pbuild.add_argument('--mode', default='balanced', choices=['fast', 'balanced', 'accuracy'])
    pbuild.add_argument('--run-gates', action='store_true')
    pbuild.add_argument('--policy', default=None)
    pbuild.add_argument('--seed', default=0)
    pbuild.add_argument('--confidence', type=int, default=80)
    pbuild.add_argument('--out', default=None)
    pbuild.add_argument('--md-out', default=None)
    pbuild.add_argument('--sarif-out', default=None)
    pbuild.add_argument('--baseline', default=None, help='Baseline report JSON path (default: <outdir>/.vibe/baseline.json). If exists, build fails on new findings.')
    pbuild.add_argument('--require-baseline', action='store_true', help='Fail build if baseline is missing (do not auto-initialize).')
    pbuild.add_argument('--allow-baseline-regressions', action='store_true', help='Do not fail build if new findings are detected (still emits compare artifact).')
    pbuild.set_defaults(fn=cmd_build)

    # sarif merge
    pm = sub.add_parser('sarif-merge', help='Merge SARIF runs from multiple tools into one file')
    pm.add_argument('--base', required=True)
    pm.add_argument('--extra', nargs='*', default=[])
    pm.add_argument('--out', required=True)
    pm.set_defaults(fn=cmd_sarif_merge)

    # index build
    pix = sub.add_parser('index-build', help='Build/update SQLite FTS + vector index for the repo')
    pix.add_argument('--repo', default='.')
    pix.add_argument('--db', default=None, help='Path to index db (default: .vibe/index/vibe_index.db)')
    pix.add_argument('--no-vector', action='store_true', help='Disable vector index (FTS only)')
    pix.add_argument('--vec-dim', type=int, default=256)
    pix.add_argument('--out', default=None, help='Write stats json (default: .vibe/index/index_stats.json)')
    pix.set_defaults(fn=cmd_index_build)

    # search
    psx = sub.add_parser('search', help='Search repo using FTS/vector/hybrid (requires index-build first)')
    psx.add_argument('--repo', default='.')
    psx.add_argument('--db', default=None)
    psx.add_argument('--mode', default='hybrid', choices=['fts', 'vector', 'hybrid', 'v13'])
    psx.add_argument('--query', required=True)
    psx.add_argument('--limit', type=int, default=20)
    psx.add_argument('--out', default=None)
    psx.set_defaults(fn=cmd_search)
    # test selection (impact-based)
    pst = sub.add_parser('select-tests', help='Select a focused set of tests based on changed files + import graph')
    pst.add_argument('--repo', default='.')
    pst.add_argument('--diff-base', default=None, help='Git base ref for changed files (e.g., origin/main)')
    pst.add_argument('--changed', action='append', default=None, help='Changed file (repeatable). If omitted, uses --diff-base.')
    pst.add_argument('--max-tests', type=int, default=40)
    pst.add_argument('--out', default=None)
    pst.set_defaults(fn=cmd_select_tests)

    # kb update
    pkb = sub.add_parser('kb-update', help='Fetch knowledge sources (GitHub raw, Reddit search) into .vibe/kb (network gated)')
    pkb.add_argument('--repo', default='.')
    pkb.add_argument('--policy', default=None)
    pkb.add_argument('--outdir', default=None, help='KB output directory (default: .vibe/kb)')
    pkb.add_argument('--github', action='append', default=[], help='GitHub repo spec owner/name@ref:path1,path2')
    pkb.add_argument('--reddit', action='append', default=[], help='Reddit spec subreddit:query')
    pkb.add_argument('--out', default=None)
    pkb.set_defaults(fn=cmd_kb_update)

    # dag run
    pdg = sub.add_parser('dag-run', help='Run a simple shell DAG spec (policy gated)')
    pdg.add_argument('--repo', default='.')
    pdg.add_argument('--spec', required=True, help='YAML/JSON DAG spec')
    pdg.add_argument('--policy', default=None)
    pdg.add_argument('--out', default=None)
    pdg.set_defaults(fn=cmd_dag_run)

    # debate
    pdeb = sub.add_parser('debate', help='Generate a deterministic debate frame (offline) for a proposal')
    pdeb.add_argument('--repo', default='.')
    pdeb.add_argument('--report', default=None, help='Optional report.json to attach evidence')
    pdeb.add_argument('--question', required=True)
    pdeb.add_argument('--out', default=None)
    pdeb.add_argument('--md-out', default=None)
    pdeb.set_defaults(fn=cmd_debate)



    # IKO (Issue Knowledge Object)
    piko = sub.add_parser('iko-new', help='Create a new IKO (single source of truth). State transitions are Gatekeeper-only.')
    piko.add_argument('--repo', default='.')
    piko.add_argument('--id', required=True)
    piko.add_argument('--title', required=True)
    piko.add_argument('--description', default='')
    piko.add_argument('--actor', default='user')
    piko.set_defaults(fn=cmd_iko_new)

    piko_s = sub.add_parser('iko-show', help='Show an IKO by id')
    piko_s.add_argument('--repo', default='.')
    piko_s.add_argument('--id', required=True)
    piko_s.set_defaults(fn=cmd_iko_show)

    piko_l = sub.add_parser('iko-list', help='List IKO ids in .vibe/iko')
    piko_l.add_argument('--repo', default='.')
    piko_l.set_defaults(fn=cmd_iko_list)

    # EvidencePack
    pep = sub.add_parser('evidencepack', help='Collect an EvidencePack bundle from CI/CD/Canary outputs for an IKO')
    pep.add_argument('--repo', default='.')
    pep.add_argument('--issue-id', required=True)
    pep.add_argument('--outdir', default=None)
    pep.add_argument('--ci-run-id', default=None)
    pep.set_defaults(fn=cmd_evidencepack)

    # Gatekeeper transitions
    pgk = sub.add_parser('gatekeeper', help='Gatekeeper-only IKO state transition (requires EvidencePack for key states)')
    pgk.add_argument('--repo', default='.')
    pgk.add_argument('--issue-id', required=True)
    pgk.add_argument('--to', required=True, choices=['INVESTIGATING','EVIDENCE_READY','APPROVED','REJECTED','DEPLOYING','DEPLOYED','CLOSED'])
    pgk.add_argument('--actor', default='gatekeeper')
    pgk.add_argument('--reason', default='')
    pgk.add_argument('--evidencepack', default=None)
    pgk.set_defaults(fn=cmd_gatekeeper)

    # RLM investigator
    pinv = sub.add_parser('investigate', help='RLM investigator: query-first + evidence-first. Does NOT change IKO.state.')
    pinv.add_argument('--repo', default='.')
    pinv.add_argument('--issue-id', required=True)
    pinv.add_argument('--question', required=True)
    pinv.add_argument('--db', default=None)
    pinv.add_argument('--limit', type=int, default=25)
    pinv.set_defaults(fn=cmd_investigate)

    # V13 Advanced Search
    ps13 = sub.add_parser('v13-search', help='V13 Advanced Search (Pointer registry + facets)')
    ps13.add_argument('--repo', default='.')
    ps13.add_argument('action', choices=['index', 'locate', 'facets', 'hints', 'pointer'])
    ps13.add_argument('--query', default='')
    ps13.add_argument('--limit', type=int, default=20)
    ps13.add_argument('--id', default='', help='Pointer id (for action=pointer)')
    ps13.add_argument('--symbol-id', default='', help='Alias of --id')
    ps13.set_defaults(fn=cmd_v13_search)

    # V13 Advanced RAG (SOTA/enterprise-ready, offline-first)
    pr13 = sub.add_parser('v13-rag', help='V13 Advanced RAG Engine (v2 default)')
    pr13.add_argument('--repo', default='.')
    pr13.add_argument('action', choices=['ingest', 'query', 'eval'])

    # ingest
    pr13.add_argument('--spec', default=None, help='YAML spec path (recommended)')
    pr13.add_argument('--sources', default='[]', help='Inline JSON sources (fallback)')
    pr13.add_argument('--chunk-chars', dest='chunk_chars', type=int, default=900)
    pr13.add_argument('--chunk-overlap', dest='chunk_overlap', type=int, default=120)

    # query
    pr13.add_argument('--prompt', default='')
    pr13.add_argument('--limit', type=int, default=6)
    pr13.add_argument('--max-context-chars', dest='max_context_chars', type=int, default=8000)
    pr13.add_argument('--preset', type=int, choices=[1, 2], default=None, help='RAG preset: 1 (repo QA, offline) or 2 (enterprise KB)')
    pr13.add_argument('--graphrag', dest='enable_graphrag', action='store_true', default=None, help='Enable GraphRAG term-graph expansion')
    pr13.add_argument('--no-graphrag', dest='enable_graphrag', action='store_false', default=None, help='Disable GraphRAG')
    pr13.add_argument('--raptor', dest='enable_raptor', action='store_true', default=None, help='Enable RAPTOR-style doc summaries')
    pr13.add_argument('--no-raptor', dest='enable_raptor', action='store_false', default=None, help='Disable RAPTOR')
    pr13.add_argument('--crag', dest='enable_crag', action='store_true', default=None, help='Enable CRAG corrective re-retrieval')
    pr13.add_argument('--no-crag', dest='enable_crag', action='store_false', default=None, help='Disable CRAG')
    pr13.add_argument('--crag-max-passes', dest='crag_max_passes', type=int, default=None)
    pr13.add_argument('--graphrag-expand-k', dest='graphrag_expand_k', type=int, default=None)
    pr13.add_argument('--raptor-summary-k', dest='raptor_summary_k', type=int, default=None)

    # dense + fusion + rerank adapters (skeleton; offline-first stubs by default)
    pr13.add_argument('--dense', dest='enable_dense', action='store_true', default=None, help='Enable dense embeddings retrieval (adapter-based)')
    pr13.add_argument('--no-dense', dest='enable_dense', action='store_false', default=None, help='Disable dense retrieval')
    pr13.add_argument('--dense-provider', dest='dense_provider', default=None, help='Dense embedding provider (e.g. stub_hash, openai)')
    pr13.add_argument('--dense-model', dest='dense_model', default=None, help='Embedding model name (provider-specific)')
    pr13.add_argument('--dense-dim', dest='dense_dim', type=int, default=None, help='Embedding dim (stub providers)')
    pr13.add_argument('--dense-topk', dest='dense_topk', type=int, default=None, help='TopK from dense retrieval before fusion')
    pr13.add_argument('--dense-backend', dest='dense_backend', choices=['scan', 'hnswlib', 'faiss'], default=None, help='Dense ANN backend (optional deps). scan=O(N), hnswlib/faiss=ANN cache')

    pr13.add_argument('--fusion', dest='fusion_mode', choices=['rrf', 'weighted', 'none'], default=None, help='Fusion mode for bm25+dense')
    pr13.add_argument('--fusion-rrf-k', dest='fusion_rrf_k', type=int, default=None, help='RRF k parameter')
    pr13.add_argument('--fusion-w-bm25', dest='fusion_w_bm25', type=float, default=None, help='Weighted fusion bm25 weight')
    pr13.add_argument('--fusion-w-dense', dest='fusion_w_dense', type=float, default=None, help='Weighted fusion dense weight')

    pr13.add_argument('--rerank', dest='enable_rerank', action='store_true', default=None, help='Enable rerank adapter (cross-encoder/LLM judge)')
    pr13.add_argument('--no-rerank', dest='enable_rerank', action='store_false', default=None, help='Disable rerank adapter')
    pr13.add_argument('--rerank-provider', dest='rerank_provider', default=None, help='Rerank provider (stub, cross_encoder, llm_judge)')
    pr13.add_argument('--rerank-model', dest='rerank_model', default=None, help='Rerank model name')
    pr13.add_argument('--rerank-topk', dest='rerank_topk', type=int, default=None, help='Rerank only top-k candidates')

    # eval
    pr13.add_argument('--eval', default=None, help='Eval YAML path (for action=eval)')
    pr13.add_argument('--out', default=None, help='Optional report output path')
    pr13.add_argument('--claims-out', dest='claims_out', default=None)
    pr13.add_argument('--evidencepack-out', dest='evidencepack_out', default=None)

    pr13.set_defaults(fn=cmd_v13_rag)
    # V13 init / preflight / self-review
    pinit = sub.add_parser('v13-init', help='Create V13 required input templates + folders under .vibe')
    pinit.add_argument('--repo', default='.')
    pinit.add_argument('--kinds', default=None, help='JSON list of kinds to generate (default: all)')
    pinit.add_argument('--out', default=None)
    pinit.set_defaults(fn=cmd_v13_init)

    ppf = sub.add_parser('v13-preflight', help='Validate required inputs before running agent pipelines')
    ppf.add_argument('--repo', default='.')
    ppf.add_argument('--kind', required=True, help='One of: nextjs|nestjs|tailwind|website|n8n')
    ppf.add_argument('--spec', default=None, help='Optional spec.yml path for validation')
    ppf.add_argument('--out', default=None)
    ppf.set_defaults(fn=cmd_v13_preflight)

    psv = sub.add_parser('v13-self-review', help='Run V13 self-review (skills, search, templates, gates readiness)')
    psv.add_argument('--repo', default='.')
    psv.add_argument('--kind', required=True, help='One of: nextjs|nestjs|tailwind|website|n8n')
    psv.add_argument('--spec', default=None, help='Optional spec.yml path')
    psv.add_argument('--out', default=None)
    psv.add_argument('--md-out', default=None)
    psv.add_argument('--sarif-out', default=None)
    psv.set_defaults(fn=cmd_v13_self_review)


    args = p.parse_args()
    return int(args.fn(args) or 0)


if __name__ == '__main__':
    raise SystemExit(main())

