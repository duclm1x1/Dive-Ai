from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from search.hybrid import search as hybrid_search


@dataclass
class ExplainResult:
    repo: str
    query: str
    evidence_level: str  # E0 (unless tool-executed)
    hits: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {"repo": self.repo, "query": self.query, "evidence_level": self.evidence_level, "hits": self.hits}


def to_markdown(res: ExplainResult, max_hits: int = 8) -> str:
    lines: List[str] = []
    lines.append(f"# Vibe Explain\n")
    lines.append(f"**Query:** `{res.query}`\n")
    lines.append(f"**Evidence Level:** {res.evidence_level}\n")
    hits = res.hits[: int(max_hits)]
    if not hits:
        lines.append("No grounded hits found. Consider refining the query or running `v13-search index`.")
        return "\n".join(lines)

    for i, h in enumerate(hits, start=1):
        kind = h.get("kind") or "file"
        path = h.get("path") or ""
        score = h.get("score")
        lines.append(f"## {i}. `{path}` ({kind}, score={score})\n")
        if h.get("symbol"):
            lines.append(f"- **Symbol:** `{h.get('symbol')}`")
        if h.get("pointer_id"):
            lines.append(f"- **Pointer ID:** `{h.get('pointer_id')}`")
        sn = h.get("snippet") or {}
        if sn and sn.get("text") is not None:
            sl = sn.get("start_line") or ""
            el = sn.get("end_line") or ""
            lines.append(f"- **Lines:** {sl}–{el}\n")
            lines.append("```")
            lines.append(sn.get("text") or "")
            lines.append("```\n")
        else:
            lines.append("")
    return "\n".join(lines)


def run_explain(repo_root: str, query: str, *, topk: int = 12) -> ExplainResult:
    rr = Path(repo_root).resolve()
    hits = hybrid_search(str(rr), query, limit=int(topk))
    # This is grounded retrieval but no tool execution -> E0
    return ExplainResult(repo=str(rr), query=query, evidence_level="E0", hits=hits)
