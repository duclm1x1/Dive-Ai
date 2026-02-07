from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from index.db import search_fts
from index.indexer import semantic_search
from search.hybrid import search as v13_hybrid_search


def search(repo_root: str, query: str, db_path: Optional[str] = None, mode: str = 'hybrid', limit: int = 20) -> List[Dict[str, Any]]:
    """Hybrid search.

    mode:
      - 'fts': SQLite FTS match (keyword)
      - 'vector': hashing-vector cosine search (offline approximate semantic)
      - 'hybrid': fts + vector merged
      - 'v13': pointer + fts + vector, with rerank + grounding
    """
    rr = str(Path(repo_root).resolve())
    if db_path is None:
        db_path = str(Path(rr) / '.vibe' / 'index' / 'vibe_index.db')

    out: List[Dict[str, Any]] = []
    mode = (mode or 'hybrid').lower().strip()

    if mode in ('v13', 'grounded'):
        return v13_hybrid_search(rr, query, db_path=db_path, limit=limit)

    if mode in ('fts', 'hybrid'):
        for path, score, snippet in search_fts(db_path, query, limit=limit):
            out.append({'path': path, 'score': float(score), 'kind': 'fts', 'snippet': snippet})

    if mode in ('vector', 'hybrid'):
        for r in semantic_search(db_path, query, top_k=min(50, limit)):
            out.append({'path': r['path'], 'score': float(r['score']), 'kind': 'vector', 'snippet': ''})

    # Merge by best score per (path)
    merged: Dict[str, Dict[str, Any]] = {}
    for r in out:
        p = str(r.get('path'))
        if p not in merged or float(r.get('score') or 0.0) > float(merged[p].get('score') or 0.0):
            merged[p] = r

    ranked = list(merged.values())
    ranked.sort(key=lambda x: float(x.get('score') or 0.0))
    ranked.reverse()
    return ranked[: int(limit)]