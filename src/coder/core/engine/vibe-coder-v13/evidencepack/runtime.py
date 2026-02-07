from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from evidencepack.models import EvidenceArtifact, EvidencePack
from utils.hash_utils import sha256_file


def _write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')
    return str(path)


def collect_run_evidencepack(
    *,
    repo_root: str,
    pack_id: str,
    report_path: str,
    sarif_path: Optional[str] = None,
    baseline_path: Optional[str] = None,
    claims_path: Optional[str] = None,
    learning_path: Optional[str] = None,
    gate_artifacts: Optional[Dict[str, str]] = None,
    ci_run_id: Optional[str] = None,
    git_sha: Optional[str] = None,
    out_path: Optional[str] = None,
) -> str:
    """Collect a machine-verifiable EvidencePack for a single analysis/build run.

    This is NOT the IKO EvidencePack (issue-centric). This pack is run-centric and is meant
    to prevent governance-theater by making artifact presence + hashes mandatory.
    """

    root = Path(repo_root).resolve()
    out_p = Path(out_path) if out_path else (root / '.vibe' / 'reports' / f'{pack_id}.evidencepack.json')

    ep = EvidencePack(id=pack_id, issue_id=pack_id, ci_run_id=ci_run_id, git_sha=git_sha)
    ep.reports = {
        'report': str(Path(report_path)),
    }
    if sarif_path:
        ep.reports['sarif'] = str(Path(sarif_path))
    if baseline_path:
        ep.reports['baseline'] = str(Path(baseline_path))
    if claims_path:
        ep.reports['claims'] = str(Path(claims_path))
    if learning_path:
        ep.reports['learning'] = str(Path(learning_path))

    artifacts: List[EvidenceArtifact] = []
    for kind, p in [
        ('report', report_path),
        ('sarif', sarif_path),
        ('baseline', baseline_path),
        ('claims', claims_path),
        ('learning', learning_path),
    ]:
        if not p:
            continue
        fp = Path(p)
        if not fp.exists():
            continue
        artifacts.append(EvidenceArtifact(kind=kind, path=str(fp), sha256=sha256_file(fp)))

    if gate_artifacts:
        for k, p in gate_artifacts.items():
            try:
                fp = Path(p)
                if fp.exists() and fp.is_file():
                    artifacts.append(EvidenceArtifact(kind=f'gate:{k}', path=str(fp), sha256=sha256_file(fp)))
            except Exception:
                continue

    ep.artifacts = artifacts
    return _write_json(out_p, ep.to_dict())
