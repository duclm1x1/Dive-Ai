from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from advanced_searching.api import AdvancedSearch
from index.db import search_fts
from index.indexer import semantic_search


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


def _tokens(q: str) -> List[str]:
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(q or '')]


def _read_lines(p: Path) -> List[str]:
    try:
        return p.read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        return []


def _ground_file(repo_root: Path, abs_path: str, query: str, context: int = 18) -> Dict[str, Any]:
    """Best-effort grounding for a file-level hit.

    We locate the first occurrence of any query token and return a snippet with line numbers.
    If no token is found, we return the file head (bounded).
    """
    p = Path(abs_path)
    rel = str(p.resolve().relative_to(repo_root.resolve())) if p.exists() else str(p)
    lines = _read_lines(p)
    if not lines:
        return {'path': rel, 'snippet': {'start_line': 1, 'end_line': 1, 'text': ''}}

    toks = _tokens(query)
    hit_line = None
    if toks:
        for i, ln in enumerate(lines, start=1):
            lnl = ln.lower()
            if any(t in lnl for t in toks):
                hit_line = i
                break

    if hit_line is None:
        hit_line = 1

    half = max(3, int(context) // 2)
    s = max(1, hit_line - half)
    e = min(len(lines), hit_line + half)
    return {
        'path': rel,
        'snippet': {'start_line': s, 'end_line': e, 'text': "\n".join(lines[s-1:e])},
    }


@dataclass
class HybridHit:
    path: str                 # repo-relative path
    score: float
    kind: str                 # pointer|file
    sources: List[str]
    pointer_id: Optional[str] = None
    pointer_kind: Optional[str] = None
    symbol: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    snippet: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _rerank(hits: List[HybridHit], query: str) -> List[HybridHit]:
    """Heuristic reranker: favors exact symbol matches and path proximity."""
    toks = _tokens(query)
    for h in hits:
        bonus = 0.0
        if h.symbol:
            sym = (h.symbol or '').lower()
            for t in toks:
                if t == sym:
                    bonus += 3.0
                elif sym.startswith(t):
                    bonus += 1.5
                elif t in sym:
                    bonus += 0.8
        p = (h.path or '').lower()
        for t in toks:
            if t in p:
                bonus += 0.2
        h.score = float(h.score) + bonus
    hits.sort(key=lambda x: x.score, reverse=True)
    return hits


def search(
    repo_root: str,
    query: str,
    db_path: Optional[str] = None,
    limit: int = 20,
    context_lines: int = 18,
) -> List[Dict[str, Any]]:
    """V13 Hybrid retrieval + rerank + grounding.

    Sources:
      - Pointer registry (AdvancedSearch): symbol-aware
      - FTS: keyword
      - Vector: offline hashing embeddings

    Output is grounded with (path, start_line/end_line, snippet) whenever possible.
    """
    rr = Path(repo_root).resolve()
    if db_path is None:
        db_path = str(rr / '.vibe' / 'index' / 'vibe_index.db')

    hits: List[HybridHit] = []

    # Pointer hits (symbol-aware)
    adv = AdvancedSearch(str(rr))
    try:
        # Ensure we have an index (incremental behavior lives inside AdvancedSearch.index).
        if not (rr / '.vibe' / 'index' / 'v13_search.json').exists():
            adv.index()
    except Exception:
        pass

    try:
        ptr_res = adv.locate(query, limit=min(30, max(10, limit)))
        for r in ptr_res:
            if r.get('kind') in ('function', 'class', 'export', 'symbol'):
                pid = r.get('id')
                ptr = adv.pointer(str(pid), context_lines=context_lines) if pid else {}
                if not ptr:
                    continue
                hits.append(HybridHit(
                    path=str(ptr.get('path') or ''),
                    score=float(r.get('score') or 0.0),
                    kind='pointer',
                    sources=['pointer'],
                    pointer_id=str(pid),
                    pointer_kind=str(ptr.get('kind') or ''),
                    symbol=str(ptr.get('name') or ''),
                    start_line=int(ptr.get('start_line') or 1),
                    end_line=int(ptr.get('end_line') or int(ptr.get('start_line') or 1)),
                    snippet=ptr.get('snippet'),
                ))
            elif r.get('kind') == 'file':
                # fallback file result, ground later
                pass
    except Exception:
        pass

    # FTS hits
    try:
        for path, score, snippet in search_fts(db_path, query, limit=min(40, max(10, limit))):
            abs_path = str(Path(path))
            grounded = _ground_file(rr, abs_path, query, context=context_lines)
            hits.append(HybridHit(
                path=str(grounded.get('path') or ''),
                score=float(score or 0.0),
                kind='file',
                sources=['fts'],
                snippet=grounded.get('snippet'),
            ))
    except Exception:
        pass

    # Vector hits
    try:
        for r in semantic_search(db_path, query, top_k=min(40, max(10, limit))):
            abs_path = str(r.get('path') or '')
            grounded = _ground_file(rr, abs_path, query, context=context_lines)
            hits.append(HybridHit(
                path=str(grounded.get('path') or ''),
                score=float(r.get('score') or 0.0),
                kind='file',
                sources=['vector'],
                snippet=grounded.get('snippet'),
            ))
    except Exception:
        pass

    # Merge hits by (kind, pointer_id) or by path.
    merged: Dict[str, HybridHit] = {}
    for h in hits:
        key = f"ptr:{h.pointer_id}" if h.pointer_id else f"file:{h.path}"
        if key not in merged:
            merged[key] = h
        else:
            # Keep max score; merge sources.
            if h.score > merged[key].score:
                merged[key].score = h.score
                merged[key].snippet = h.snippet or merged[key].snippet
            merged[key].sources = sorted(set((merged[key].sources or []) + (h.sources or [])))

    reranked = _rerank(list(merged.values()), query)
    return [h.to_dict() for h in reranked[: int(limit)]]
