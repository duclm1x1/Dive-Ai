from __future__ import annotations

import json
import struct
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from index.db import IndexStats, build_index, ensure_schema, _connect
from search.vector import embed_text, cosine


def _ensure_vec_schema(con) -> None:
    try:
        con.execute('CREATE TABLE IF NOT EXISTS vec (path TEXT PRIMARY KEY, dim INTEGER, vec BLOB)')
        con.commit()
    except Exception:
        pass


def build_vector_index(db_path: str, paths: List[str], dim: int = 256) -> Dict[str, Any]:
    con = _connect(db_path)
    ensure_schema(con)
    _ensure_vec_schema(con)
    n = 0
    for fp in paths:
        try:
            text = Path(fp).read_text(encoding='utf-8', errors='ignore')
            v = embed_text(text, dim=dim)
            blob = struct.pack('<' + 'f' * dim, *[float(x) for x in v])
            con.execute('INSERT OR REPLACE INTO vec(path, dim, vec) VALUES (?,?,?)', (str(Path(fp).resolve()), int(dim), blob))
            n += 1
        except Exception:
            continue
    con.commit()
    con.close()
    return {'vectors_indexed': n, 'dim': dim}


def semantic_search(db_path: str, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    con = _connect(db_path)
    ensure_schema(con)
    _ensure_vec_schema(con)

    qv = embed_text(query)
    out: List[Dict[str, Any]] = []
    rows = con.execute('SELECT path, dim, vec FROM vec').fetchall()
    for path, dim, blob in rows:
        try:
            dim = int(dim)
            vals = struct.unpack('<' + 'f' * dim, blob)
            score = cosine(qv, vals)
            out.append({'path': path, 'score': float(score)})
        except Exception:
            continue
    out.sort(key=lambda r: r['score'], reverse=True)
    con.close()
    return out[: int(top_k)]


def build(repo_root: str, db_path: str, vector: bool = True, vector_dim: int = 256) -> Dict[str, Any]:
    """Build the repo index.

    This is incremental:
      - `build_index` updates only changed/new files.
      - vector indexing updates only the changed/new files (paths_updated).
    """
    stats = build_index(repo_root, db_path)
    out: Dict[str, Any] = {'index': asdict(stats)}
    if vector:
        paths = list(stats.updated_paths or [])
        # If this is the first run (no updated paths captured for some reason),
        # fall back to indexing everything once.
        if not paths:
            con = _connect(db_path)
            ensure_schema(con)
            rows = con.execute('SELECT path FROM files').fetchall()
            con.close()
            paths = [r[0] for r in rows]

        out['vector'] = build_vector_index(db_path, paths, dim=vector_dim)
    return out


def save_stats(repo_root: str, payload: Dict[str, Any]) -> str:
    p = Path(repo_root) / '.vibe' / 'index' / 'index_stats.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return str(p)
