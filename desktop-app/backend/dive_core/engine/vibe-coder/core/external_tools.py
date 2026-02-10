from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .models import Evidence, Finding
from utils.hash_utils import sha256_text


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _evidence(file: str, start_line: int, end_line: int, snippet: str) -> Evidence:
    return Evidence(file=file, start_line=int(start_line), end_line=int(end_line), snippet_hash=sha256_text(snippet)[:16])


def run_ruff(repo_root: str) -> List[Finding]:
    if not _has('ruff'):
        return []
    try:
        cmd = ['ruff', 'check', '--output-format', 'json', '.']
        out = subprocess.check_output(cmd, cwd=repo_root, stderr=subprocess.STDOUT, text=True)
        data = json.loads(out)
    except Exception:
        return []

    findings: List[Finding] = []
    if not isinstance(data, list):
        return findings

    for d in data:
        try:
            code = str(d.get('code') or 'RUFF')
            msg = str(d.get('message') or 'Ruff finding')
            path = str(Path(repo_root) / str(d.get('filename') or ''))
            loc = d.get('location') or {}
            line = int(loc.get('row') or 1)
            col = int(loc.get('column') or 1)
            rule_id = f'RUFF_{code}'
            evidence = _evidence(path, line, line, f'{msg} (col {col})')
            findings.append(Finding(
                id=rule_id,
                category='style',
                severity='low',
                title=f'Ruff {code}',
                description=msg,
                recommendation='Fix lint according to Ruff suggestion.',
                confidence=90,
                rule_id=rule_id,
                tool='ruff',
                evidence=evidence,
                tags=['ruff'],
            ))
        except Exception:
            continue
    return findings


def run_bandit(repo_root: str) -> List[Finding]:
    if not _has('bandit'):
        return []
    try:
        cmd = ['bandit', '-r', '.', '-f', 'json', '-q']
        out = subprocess.check_output(cmd, cwd=repo_root, stderr=subprocess.STDOUT, text=True)
        data = json.loads(out)
    except Exception:
        return []

    findings: List[Finding] = []
    issues = (data or {}).get('results') if isinstance(data, dict) else []
    if not isinstance(issues, list):
        return findings

    sev_map = {'HIGH': 'high', 'MEDIUM': 'medium', 'LOW': 'low'}
    for it in issues:
        try:
            test_id = str(it.get('test_id') or 'BANDIT')
            title = str(it.get('issue_text') or 'Bandit issue')
            sev = sev_map.get(str(it.get('issue_severity') or '').upper(), 'medium')
            fname = str(Path(repo_root) / str(it.get('filename') or ''))
            line = int(it.get('line_number') or 1)
            snippet = str(it.get('code') or '')
            evidence = _evidence(fname, line, line, snippet)
            findings.append(Finding(
                id=f'BANDIT_{test_id}',
                category='security',
                severity=sev,
                title=f'Bandit {test_id}',
                description=title,
                recommendation='Address the security issue per Bandit guidance.',
                confidence=92,
                rule_id=f'BANDIT_{test_id}',
                tool='bandit',
                evidence=evidence,
                tags=['bandit'],
            ))
        except Exception:
            continue
    return findings


def run_semgrep(repo_root: str, config: str = 'auto') -> List[Finding]:
    if not _has('semgrep'):
        return []
    try:
        cmd = ['semgrep', '--config', config, '--json']
        out = subprocess.check_output(cmd, cwd=repo_root, stderr=subprocess.STDOUT, text=True)
        data = json.loads(out)
    except Exception:
        return []

    findings: List[Finding] = []
    results = (data or {}).get('results') if isinstance(data, dict) else []
    if not isinstance(results, list):
        return findings

    sev_map = {'ERROR': 'high', 'WARNING': 'medium', 'INFO': 'low'}
    for r in results:
        try:
            check_id = str(r.get('check_id') or 'SEMGREP')
            extra = r.get('extra') or {}
            msg = str(extra.get('message') or 'Semgrep finding')
            sev = sev_map.get(str(extra.get('severity') or '').upper(), 'medium')
            path = str(Path(repo_root) / str(r.get('path') or ''))
            start = (r.get('start') or {}).get('line') or 1
            end = (r.get('end') or {}).get('line') or start
            snippet = str((extra.get('lines') or '')).strip()
            evidence = _evidence(path, int(start), int(end), snippet)
            findings.append(Finding(
                id=f'SEMGREP_{check_id}',
                category='security' if 'security' in str(extra.get('metadata') or '').lower() else 'bug',
                severity=sev,
                title=f'Semgrep {check_id}',
                description=msg,
                recommendation='Fix according to the Semgrep rule guidance.',
                confidence=85,
                rule_id=f'SEMGREP_{check_id}',
                tool='semgrep',
                evidence=evidence,
                tags=['semgrep'],
            ))
        except Exception:
            continue
    return findings


def tool_versions() -> Dict[str, str]:
    vers: Dict[str, str] = {}
    for tool in ['python3', 'git', 'ruff', 'bandit', 'semgrep']:
        if not _has(tool):
            continue
        try:
            out = subprocess.check_output([tool, '--version'], stderr=subprocess.STDOUT, text=True)
            vers[tool] = out.strip().split('\n')[0][:200]
        except Exception:
            continue
    return vers
