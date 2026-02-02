from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from evidencepack.models import EvidenceArtifact, EvidencePack

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _git_sha(repo_root: str) -> Optional[str]:
    head = Path(repo_root) / '.git' / 'HEAD'
    if not head.exists():
        return None
    ref = head.read_text(encoding='utf-8', errors='ignore').strip()
    if ref.startswith('ref:'):
        ref_path = ref.split(' ', 1)[-1].strip()
        p = Path(repo_root) / '.git' / ref_path
        if p.exists():
            return p.read_text(encoding='utf-8', errors='ignore').strip()[:40]
    return ref[:40] if ref else None


def collect_evidencepack(repo_root: str, issue_id: str, out_dir: str, ci_run_id: Optional[str] = None) -> str:
    """Collect an EvidencePack from standard Vibe outputs.

    This is meant to be used in CI/CD or canary jobs.
    """

    repo = Path(repo_root).resolve()
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    pack_id = f"ep-{issue_id}-{os.getpid()}"
    ep = EvidencePack(id=pack_id, issue_id=issue_id, git_sha=_git_sha(str(repo)), ci_run_id=ci_run_id)

    artifacts: List[EvidenceArtifact] = []

    # Standard reports
    report_dir = repo / '.vibe' / 'reports'
    candidates = [
        ('vibe_report', report_dir / 'vibe-report.json'),
        ('vibe_report_md', report_dir / 'vibe-report.md'),
        ('sarif', report_dir / 'vibe.sarif.json'),
        ('build_report', report_dir / 'vibe-build-report.json'),
    ]
    for kind, p in candidates:
        if p.exists() and p.is_file():
            artifacts.append(EvidenceArtifact(kind=kind, path=str(p), sha256=sha256_file(p)))

    # Gates output (if present)
    gates_dir = repo / '.vibe' / 'gates'
    if gates_dir.exists():
        for fp in sorted(gates_dir.glob('*.json')):
            artifacts.append(EvidenceArtifact(kind='gate_result', path=str(fp), sha256=sha256_file(fp)))

    # Canary metrics (optional)
    canary_path = repo / '.vibe' / 'canary' / 'metrics.json'
    if canary_path.exists():
        try:
            ep.canary = json.loads(canary_path.read_text(encoding='utf-8', errors='ignore'))
        except Exception:
            ep.canary = {'raw': canary_path.read_text(encoding='utf-8', errors='ignore')[:2000]}
        artifacts.append(EvidenceArtifact(kind='canary_metrics', path=str(canary_path), sha256=sha256_file(canary_path)))

    # Tool versions snapshot (optional)
    vers_path = repo / '.vibe' / 'tool_versions.json'
    if vers_path.exists():
        artifacts.append(EvidenceArtifact(kind='tool_versions', path=str(vers_path), sha256=sha256_file(vers_path)))

    ep.artifacts = artifacts

    # Lightweight summary pointers
    ep.reports = {
        'reports_dir': str(report_dir),
        'has_vibe_report': (report_dir / 'vibe-report.json').exists(),
        'has_sarif': (report_dir / 'vibe.sarif.json').exists(),
    }
    ep.gates = {
        'gates_dir': str(gates_dir),
        'gate_results': len(list(gates_dir.glob('*.json'))) if gates_dir.exists() else 0,
    }

    out_path = out / f"{pack_id}.evidencepack.json"
    out_path.write_text(json.dumps(ep.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    return str(out_path)
