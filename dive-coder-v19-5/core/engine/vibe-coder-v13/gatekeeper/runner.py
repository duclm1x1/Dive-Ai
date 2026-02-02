from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from gatekeeper.state import can_transition
from iko.store import load as load_iko, save as save_iko


def _load_evidencepack(path: str) -> Optional[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def transition_iko(
    repo_root: str,
    issue_id: str,
    to_state: str,
    actor: str,
    reason: str = '',
    evidencepack_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Gatekeeper-only state transition.

    Rules:
    - Only Gatekeeper may change IKO.state.
    - EvidencePack is required for EVIDENCE_READY/APPROVED/DEPLOYING/DEPLOYED/CLOSED transitions.
    """

    iko = load_iko(repo_root, issue_id)
    if not iko:
        return {'ok': False, 'error': 'IKO_NOT_FOUND', 'issue_id': issue_id}

    frm = (iko.state or 'NEW').upper()
    to = (to_state or '').upper().strip()

    if not can_transition(frm, to):
        return {'ok': False, 'error': 'INVALID_TRANSITION', 'from': frm, 'to': to}

    requires_evidence = to in {'EVIDENCE_READY', 'APPROVED', 'DEPLOYING', 'DEPLOYED', 'CLOSED'}
    ep = None
    if evidencepack_path:
        ep = _load_evidencepack(evidencepack_path)
        if not ep:
            return {'ok': False, 'error': 'EVIDENCEPACK_NOT_FOUND', 'path': evidencepack_path}
        if str(ep.get('issue_id') or '') != str(iko.id):
            return {'ok': False, 'error': 'EVIDENCEPACK_ISSUE_MISMATCH', 'expected': iko.id, 'got': ep.get('issue_id')}

    if requires_evidence and not ep:
        return {'ok': False, 'error': 'EVIDENCEPACK_REQUIRED', 'to': to}

    iko.state = to
    if evidencepack_path:
        if evidencepack_path not in iko.evidence_packs:
            iko.evidence_packs.append(evidencepack_path)

    iko.add_event(actor=actor, action='GATEKEEPER_TRANSITION', from_state=frm, to_state=to, reason=reason, evidencepack=evidencepack_path or '')

    path = save_iko(repo_root, iko)
    return {'ok': True, 'issue_id': iko.id, 'from': frm, 'to': to, 'saved_to': path}
