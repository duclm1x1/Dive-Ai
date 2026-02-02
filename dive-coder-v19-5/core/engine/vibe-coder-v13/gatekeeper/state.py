from __future__ import annotations

from typing import Dict, List


# State machine: Gatekeeper is the single authority to change IKO.state.
# RLM/Cruel only attach investigations/evidence.

STATES: List[str] = [
    'NEW',
    'INVESTIGATING',
    'EVIDENCE_READY',
    'APPROVED',
    'REJECTED',
    'DEPLOYING',
    'DEPLOYED',
    'CLOSED',
]

ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    'NEW': ['INVESTIGATING'],
    'INVESTIGATING': ['EVIDENCE_READY', 'REJECTED'],
    'EVIDENCE_READY': ['APPROVED', 'REJECTED'],
    'APPROVED': ['DEPLOYING', 'CLOSED'],
    'DEPLOYING': ['DEPLOYED', 'REJECTED'],
    'DEPLOYED': ['CLOSED'],
    'REJECTED': ['CLOSED'],
    'CLOSED': [],
}


def can_transition(frm: str, to: str) -> bool:
    frm = (frm or '').strip().upper() or 'NEW'
    to = (to or '').strip().upper() or ''
    return to in ALLOWED_TRANSITIONS.get(frm, [])
