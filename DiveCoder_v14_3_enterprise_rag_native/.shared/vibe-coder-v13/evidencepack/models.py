from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EvidenceArtifact:
    kind: str
    path: str
    sha256: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'kind': self.kind,
            'path': self.path,
            'sha256': self.sha256,
            'meta': self.meta,
        }


@dataclass
class EvidencePack:
    """EvidencePack

    A machine-generated, CI/CD-friendly bundle of evidence for an IKO.
    RLM/Cruel attach investigation results, but Gatekeeper owns state.
    """

    id: str
    issue_id: str
    created_at: str = field(default_factory=utcnow_iso)
    git_sha: Optional[str] = None
    ci_run_id: Optional[str] = None
    canary: Dict[str, Any] = field(default_factory=dict)
    gates: Dict[str, Any] = field(default_factory=dict)
    reports: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[EvidenceArtifact] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'created_at': self.created_at,
            'git_sha': self.git_sha,
            'ci_run_id': self.ci_run_id,
            'canary': self.canary,
            'gates': self.gates,
            'reports': self.reports,
            'artifacts': [a.to_dict() for a in self.artifacts],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'EvidencePack':
        ep = EvidencePack(
            id=str(d.get('id') or ''),
            issue_id=str(d.get('issue_id') or ''),
            created_at=str(d.get('created_at') or utcnow_iso()),
            git_sha=d.get('git_sha'),
            ci_run_id=d.get('ci_run_id'),
            canary=dict(d.get('canary') or {}),
            gates=dict(d.get('gates') or {}),
            reports=dict(d.get('reports') or {}),
            artifacts=[EvidenceArtifact(**x) for x in (d.get('artifacts') or []) if isinstance(x, dict)],
        )
        return ep
