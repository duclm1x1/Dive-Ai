from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


DEFAULT_EXCLUDE_DIRS = {
    '.git', '.vibe', 'node_modules', 'dist', 'build', '.next', '.turbo', '.cache',
    'coverage', '__pycache__', '.pytest_cache', '.mypy_cache', '.idea', '.venv', 'venv'
}


@dataclass
class IndexStats:
    files_scanned: int = 0
    files_indexed: int = 0
    files_unchanged: int = 0
    bytes_indexed: int = 0
    skipped: int = 0
    # Paths that were updated in the index (absolute paths).
    updated_paths: List[str] = field(default_factory=list)


def _connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.execute('PRAGMA journal_mode=WAL;')
    con.execute('PRAGMA synchronous=NORMAL;')
    return con


def _ensure_column(con: sqlite3.Connection, table: str, column: str, ddl_type: str) -> None:
    try:
        cols = [r[1] for r in con.execute(f'PRAGMA table_info({table})').fetchall()]
        if column in cols:
            return
        con.execute(f'ALTER TABLE {table} ADD COLUMN {column} {ddl_type}')
        con.commit()
    except Exception:
        # Best-effort; if schema is broken we still want index usage to degrade gracefully.
        return


def ensure_schema(con: sqlite3.Connection) -> None:
    con.execute(
        'CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, mtime REAL, size INTEGER, content_hash TEXT)'
    )
    _ensure_column(con, 'files', 'content_hash', 'TEXT')

    # FTS5 if available; fallback to plain table
    try:
        con.execute('CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(path, content)')
    except Exception:
        con.execute('CREATE TABLE IF NOT EXISTS fts (path TEXT PRIMARY KEY, content TEXT)')
    con.commit()


def iter_text_files(repo_root: str, include_exts: Optional[set[str]] = None) -> Iterable[str]:
    root = Path(repo_root)
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(root).parts
        if rel_parts and rel_parts[0] in DEFAULT_EXCLUDE_DIRS:
            continue
        if any(part in DEFAULT_EXCLUDE_DIRS for part in rel_parts):
            continue
        if include_exts is not None and p.suffix.lower() not in include_exts:
            continue
        yield str(p)


def build_index(repo_root: str, db_path: str, max_file_bytes: int = 512_000) -> IndexStats:
    """Build/update an on-disk SQLite index incrementally.

    Speed model:
      - Uses (mtime,size) fast-path to skip unchanged files.
      - Only decodes and writes content for changed/new files.

    Stores:
      - `files`: path, mtime, size, content_hash (optional)
      - `fts`: full text (FTS5 if available)
    """
    con = _connect(db_path)
    ensure_schema(con)

    stats = IndexStats()

    # Load existing metadata for quick skip checks.
    existing: dict[str, tuple[float, int]] = {}
    try:
        for path, mtime, size in con.execute('SELECT path, mtime, size FROM files').fetchall():
            existing[str(path)] = (float(mtime or 0.0), int(size or 0))
    except Exception:
        existing = {}

    for fp in iter_text_files(repo_root):
        stats.files_scanned += 1
        try:
            st = os.stat(fp)
            if st.st_size > max_file_bytes:
                stats.skipped += 1
                continue

            abs_path = str(Path(fp).resolve())
            prev = existing.get(abs_path)

            # Fast skip: identical (mtime,size) -> unchanged.
            if prev and abs(prev[0] - float(st.st_mtime)) < 1e-6 and int(prev[1]) == int(st.st_size):
                stats.files_unchanged += 1
                continue

            # Skip binaries by naive heuristic
            data = Path(fp).read_bytes()
            if b'\x00' in data[:2048]:
                stats.skipped += 1
                continue

            text = data.decode('utf-8', errors='ignore')

            # Hash is optional, but helps CI auditing and deterministic caching.
            # We avoid importing hashlib at module scope for speed if unused elsewhere.
            import hashlib
            content_hash = hashlib.sha256(data).hexdigest()

            con.execute(
                'INSERT OR REPLACE INTO files(path, mtime, size, content_hash) VALUES (?,?,?,?)',
                (abs_path, float(st.st_mtime), int(st.st_size), content_hash),
            )
            try:
                con.execute('INSERT OR REPLACE INTO fts(path, content) VALUES (?,?)', (abs_path, text))
            except Exception:
                con.execute('DELETE FROM fts WHERE path=?', (abs_path,))
                con.execute('INSERT INTO fts(path, content) VALUES (?,?)', (abs_path, text))

            stats.files_indexed += 1
            stats.bytes_indexed += int(st.st_size)
            stats.updated_paths.append(abs_path)

        except Exception:
            stats.skipped += 1
            continue

    con.commit()
    con.close()
    return stats


def search_fts(db_path: str, query: str, limit: int = 20) -> List[Tuple[str, float, str]]:
    """Return list of (path, score, snippet). Score is rank-ish if FTS5, else 0."""
    con = _connect(db_path)
    ensure_schema(con)
    out: List[Tuple[str, float, str]] = []

    # Try FTS5 bm25() if available
    try:
        rows = con.execute(
            "SELECT path, bm25(fts) as score, snippet(fts, 1, '[', ']', '…', 12) as snip FROM fts WHERE fts MATCH ? ORDER BY score LIMIT ?",
            (query, int(limit)),
        ).fetchall()
        for path, score, snip in rows:
            out.append((str(path), float(score), str(snip)))
        con.close()
        return out
    except Exception:
        pass

    # Fallback: LIKE scan
    try:
        q = (query or '').strip().lower()
        if not q:
            return []
        rows = con.execute('SELECT path, content FROM fts').fetchall()
        for path, content in rows:
            txt = str(content or '')
            if q in txt.lower():
                out.append((str(path), 0.0, txt[:240]))
                if len(out) >= int(limit):
                    break
    finally:
        con.close()

    return out
