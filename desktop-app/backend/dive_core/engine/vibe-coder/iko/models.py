from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IKOEvent:
    ts: str
    actor: str
    action: str
    detail: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'ts': self.ts,
            'actor': self.actor,
            'action': self.action,
            'detail': self.detail,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'IKOEvent':
        return IKOEvent(
            ts=str(d.get('ts') or utcnow_iso()),
            actor=str(d.get('actor') or 'unknown'),
            action=str(d.get('action') or 'unknown'),
            detail=dict(d.get('detail') or {}),
        )


@dataclass
class IKO:
    """Issue Knowledge Object (IKO)

    Single Source of Truth for an issue:
    - State machine is controlled ONLY by Gatekeeper.
    - RLM/Cruel are investigators/verifiers that attach evidence & recommendations.
    """

    id: str
    title: str
    description: str = ''

    # Gatekeeper-owned state
    state: str = 'NEW'

    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    updated_at: str = field(default_factory=utcnow_iso)
    labels: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)

    # Evidence/analysis
    evidence_packs: List[str] = field(default_factory=list)  # paths
    investigations: List[str] = field(default_factory=list)  # paths

    # Audit trail
    events: List[IKOEvent] = field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = utcnow_iso()

    def add_event(self, actor: str, action: str, **detail: Any) -> None:
        self.events.append(IKOEvent(ts=utcnow_iso(), actor=actor, action=action, detail=dict(detail)))
        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'state': self.state,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'labels': self.labels,
            'links': self.links,
            'evidence_packs': self.evidence_packs,
            'investigations': self.investigations,
            'events': [e.to_dict() for e in self.events],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'IKO':
        iko = IKO(
            id=str(d.get('id') or ''),
            title=str(d.get('title') or ''),
            description=str(d.get('description') or ''),
            state=str(d.get('state') or 'NEW'),
            created_at=str(d.get('created_at') or utcnow_iso()),
            updated_at=str(d.get('updated_at') or utcnow_iso()),
            labels=list(d.get('labels') or []),
            links=list(d.get('links') or []),
            evidence_packs=list(d.get('evidence_packs') or []),
            investigations=list(d.get('investigations') or []),
            events=[IKOEvent.from_dict(x) for x in (d.get('events') or []) if isinstance(x, dict)],
        )
        return iko
