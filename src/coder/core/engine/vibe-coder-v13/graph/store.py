from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from utils.hash_utils import sha256_text
from .import_graph import build_import_graph


_SCHEMA = [
    """CREATE TABLE IF NOT EXISTS files(
        relpath TEXT PRIMARY KEY,
        content_hash TEXT NOT NULL
    );""",
    """CREATE TABLE IF NOT EXISTS edges(
        src TEXT NOT NULL,
        dst TEXT NOT NULL,
        type TEXT NOT NULL,
        PRIMARY KEY (src, dst, type)
    );""",
    """CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src);""",
    """CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);""",
]


def _read_file(repo: Path, rel: str) -> str:
    try:
        return (repo / rel).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def _file_hash(repo: Path, rel: str) -> str:
    return sha256_text(_read_file(repo, rel))


@dataclass
class GraphBuildResult:
    db_path: str
    updated_files: List[str]
    edges_added: int


def ensure_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.cursor()
        for stmt in _SCHEMA:
            cur.execute(stmt)
        con.commit()
    finally:
        con.close()


def build_graph(repo_root: str, *, files: Optional[List[str]] = None, db_path: Optional[str] = None) -> GraphBuildResult:
    """Incremental import graph store.

    Stores file->file import edges (best-effort) plus file content hashes.
    This is a V2 stepping stone toward full symbol/test graphs.
    """
    repo = Path(repo_root).resolve()
    dbp = Path(db_path) if db_path else (repo / '.vibe' / 'graph' / 'graph.db')
    ensure_db(dbp)

    # Determine candidate files
    if files:
        cand = [str(Path(f)) for f in files]
    else:
        # Default: all code files (bounded by import_graph file selection)
        cand = []

    # Read prior hashes
    con = sqlite3.connect(str(dbp))
    try:
        cur = con.cursor()
        cur.execute("SELECT relpath, content_hash FROM files")
        old = {r[0]: r[1] for r in cur.fetchall()}

        # Build best-effort import graph (this already supports restricting to 'files')
        g = build_import_graph(str(repo), files=cand if cand else None)

        updated: List[str] = []
        edges_added = 0

        # Upsert hashes for all nodes we observed
        for rel in g.nodes:
            h = _file_hash(repo, rel)
            if old.get(rel) != h:
                updated.append(rel)
            cur.execute("INSERT OR REPLACE INTO files(relpath, content_hash) VALUES(?,?)", (rel, h))

        # For simplicity, rebuild edges for updated files only
        for rel in updated:
            cur.execute("DELETE FROM edges WHERE src=? AND type='import'", (rel,))

        for src, dsts in g.imports.items():
            if updated and src not in updated:
                continue
            for dst in dsts:
                cur.execute(
                    "INSERT OR IGNORE INTO edges(src, dst, type) VALUES(?,?,?)",
                    (src, dst, 'import'),
                )
                edges_added += 1

        con.commit()
        return GraphBuildResult(db_path=str(dbp), updated_files=sorted(set(updated)), edges_added=int(edges_added))
    finally:
        con.close()


def impacted_files(repo_root: str, changed_files: List[str], *, db_path: Optional[str] = None, depth: int = 6) -> List[str]:
    """Compute impacted files using stored import edges (reverse reachability)."""
    repo = Path(repo_root).resolve()
    dbp = Path(db_path) if db_path else (repo / '.vibe' / 'graph' / 'graph.db')
    if not dbp.exists():
        # fallback: compute on the fly
        g = build_import_graph(str(repo), files=changed_files)
        return sorted(set(changed_files) | g.impacted_by(changed_files, depth=depth))

    con = sqlite3.connect(str(dbp))
    try:
        cur = con.cursor()
        frontier = set(changed_files)
        seen = set(changed_files)
        for _ in range(int(depth)):
            nxt: Set[str] = set()
            for f in list(frontier):
                cur.execute("SELECT src FROM edges WHERE dst=? AND type='import'", (f,))
                for (src,) in cur.fetchall():
                    if src not in seen:
                        nxt.add(src)
                        seen.add(src)
            if not nxt:
                break
            frontier = nxt
        return sorted(seen)
    finally:
        con.close()
