from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.models import Finding, Report


def _level(severity: str) -> str:
    s = (severity or '').lower()
    if s in {'critical', 'high'}:
        return 'error'
    if s == 'medium':
        return 'warning'
    return 'note'


def _rel_uri(repo_root: Optional[str], file_path: str) -> str:
    if not repo_root:
        return file_path
    try:
        root = Path(repo_root).resolve()
        p = Path(file_path).resolve()
        rel = p.relative_to(root)
        return rel.as_posix()
    except Exception:
        return file_path


def findings_to_sarif(
    findings: List[Finding],
    *,
    tool_name: str = 'Vibe Coder',
    tool_version: str = '12.2',
    repo_root: Optional[str] = None,
) -> Dict[str, Any]:
    rules_index: Dict[str, int] = {}
    rules: List[Dict[str, Any]] = []

    def _ensure_rule(f: Finding) -> int:
        rid = f.rule_id or f.id
        if rid in rules_index:
            return rules_index[rid]
        idx = len(rules)
        rules_index[rid] = idx
        rules.append({
            'id': rid,
            'name': f.title[:128],
            'shortDescription': {'text': f.title[:256]},
            'fullDescription': {'text': f.description[:1024]},
            'help': {'text': f.recommendation[:1024]},
            'properties': {
                'category': f.category,
                'confidence': f.confidence,
                'severity': f.severity,
            },
        })
        return idx

    results: List[Dict[str, Any]] = []
    for f in findings:
        rid = f.rule_id or f.id
        _ensure_rule(f)

        locs: List[Dict[str, Any]] = []
        if f.evidence is not None:
            locs.append({
                'physicalLocation': {
                    'artifactLocation': {
                        'uri': _rel_uri(repo_root, f.evidence.file),
                    },
                    'region': {
                        'startLine': int(f.evidence.start_line),
                        'endLine': int(f.evidence.end_line),
                    },
                }
            })

        results.append({
            'ruleId': rid,
            'level': _level(f.severity),
            'message': {'text': f"{f.title}: {f.description}"[:2048]},
            'locations': locs,
            'properties': {
                'confidence': f.confidence,
                'category': f.category,
                'tags': f.tags or [],
            },
        })

    sarif: Dict[str, Any] = {
        '$schema': 'https://json.schemastore.org/sarif-2.1.0.json',
        'version': '2.1.0',
        'runs': [
            {
                'tool': {
                    'driver': {
                        'name': tool_name,
                        'version': tool_version,
                        'rules': rules,
                    }
                },
                'results': results,
            }
        ],
    }
    return sarif


def _load_sarif(path: str) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        if isinstance(data, dict) and isinstance(data.get('runs'), list):
            return data
    except Exception:
        return None
    return None


def _merge_sarif(base: Dict[str, Any], extras: List[Dict[str, Any]]) -> Dict[str, Any]:
    out = dict(base)
    out_runs = list(out.get('runs') or [])
    for ex in extras:
        for run in ex.get('runs') or []:
            out_runs.append(run)
    out['runs'] = out_runs
    return out


def write_sarif(path: str, report_or_findings: Union[Report, List[Finding]]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(report_or_findings, Report):
        report = report_or_findings
        base = findings_to_sarif(report.findings, tool_version=report.version, repo_root=report.repo_root)

        extra_docs: List[Dict[str, Any]] = []
        for g in report.gates or []:
            arts = getattr(g, 'artifacts', None)
            if isinstance(arts, dict):
                sarif_path = arts.get('sarif')
                if sarif_path and Path(sarif_path).exists():
                    doc = _load_sarif(sarif_path)
                    if doc:
                        extra_docs.append(doc)

        merged = _merge_sarif(base, extra_docs) if extra_docs else base
        p.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
        return str(p)

    sarif = findings_to_sarif(report_or_findings)
    p.write_text(json.dumps(sarif, indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)
