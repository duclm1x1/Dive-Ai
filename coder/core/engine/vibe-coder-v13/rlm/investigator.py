from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from iko.store import load as load_iko, save as save_iko
from search.semantic import search as semantic_search


@dataclass
class RLMInvestigation:
    issue_id: str
    question: str
    created_at: str
    strategy: Dict[str, Any] = field(default_factory=dict)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    conclusion: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'issue_id': self.issue_id,
            'question': self.question,
            'created_at': self.created_at,
            'strategy': self.strategy,
            'observations': self.observations,
            'evidence': self.evidence,
            'conclusion': self.conclusion,
        }


def _utc_iso() -> str:
    # avoid importing timezone utils; keep self-contained
    import datetime
    return datetime.datetime.utcnow().isoformat() + 'Z'


def investigate(repo_root: str, issue_id: str, question: str, db_path: Optional[str] = None, limit: int = 25) -> str:
    """RLM investigator: query-first, evidence-first.

    NOTE: This does NOT change IKO.state. Gatekeeper is the only authority.
    """

    repo = Path(repo_root).resolve()
    iko = load_iko(str(repo), issue_id)
    if not iko:
        raise SystemExit(f'IKO_NOT_FOUND: {issue_id}')

    inv = RLMInvestigation(issue_id=issue_id, question=question, created_at=_utc_iso())

    # Minimal strategy: hybrid lexical+semantic via existing semantic_search
    inv.strategy = {
        'mode': 'hybrid',
        'limit': int(limit),
        'note': 'This is a deterministic investigator scaffold. Use it to gather candidates + evidence pointers; do not decide DONE.',
    }

    results = semantic_search(str(repo), question, db_path=db_path, mode='hybrid', limit=int(limit))
    inv.observations.append({'type': 'search', 'query': question, 'results': results})

    # Evidence: top spans with path + line ranges + text hash
    evidence: List[Dict[str, Any]] = []
    for r in results[: min(len(results), 10)]:
        if not isinstance(r, dict):
            continue
        evidence.append({
            'path': r.get('path') or r.get('file') or '',
            'start_line': r.get('start_line'),
            'end_line': r.get('end_line'),
            'score': r.get('score'),
            'why': r.get('why') or r.get('snippet') or '',
        })
    inv.evidence = evidence

    inv.conclusion = {
        'status': 'INVESTIGATED',
        'recommendation': 'Attach EvidencePack, then ask Gatekeeper to transition state when criteria are met.',
        'stop_reason': 'search_top_k',
        'confidence': 60 if evidence else 30,
    }

    out_dir = repo / '.vibe' / 'iko' / 'investigations'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"inv-{issue_id}-{os.getpid()}.json"
    out_path.write_text(json.dumps(inv.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')

    # Link investigation to IKO
    if str(out_path) not in iko.investigations:
        iko.investigations.append(str(out_path))
        iko.add_event(actor='RLM', action='INVESTIGATION_ATTACHED', investigation=str(out_path), question=question)
        save_iko(str(repo), iko)

    return str(out_path)
