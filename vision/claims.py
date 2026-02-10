from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.models import EvidenceLevel
from utils.hash_utils import sha256_file


@dataclass
class Claim:
    """A machine-verifiable claim about an execution or decision.

    The point is to prevent governance theater: any claim that implies
    tool execution or verification must map to an artifact (or be E0).
    """
    claim: str
    evidence_level: EvidenceLevel
    tool: Optional[str] = None
    artifact: Optional[str] = None
    sha256: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClaimsLedger:
    version: str
    run_id: str
    claims: List[Claim]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'run_id': self.run_id,
            'claims': [c.to_dict() for c in self.claims],
        }


def _hash_if_exists(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    try:
        fp = Path(p)
        if fp.exists() and fp.is_file():
            return sha256_file(str(fp))
    except Exception:
        return None
    return None


def write_claims_ledger(repo_root: str, ledger: ClaimsLedger, out_path: str) -> str:
    # Auto-fill hashes for artifacts
    for c in ledger.claims:
        if c.artifact and not c.sha256:
            c.sha256 = _hash_if_exists(c.artifact)
        # If artifact missing, downgrade evidence to E0
        if c.evidence_level in ('E2', 'E3') and c.artifact and not c.sha256:
            c.evidence_level = 'E0'

    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ledger.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)
