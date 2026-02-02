from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.policy import Policy


@dataclass
class KBUpdateResult:
    ok: bool
    reason: str
    files_written: int = 0
    sources: List[str] = None


def _requests_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 20):
    try:
        import requests  # type: ignore
    except Exception:
        raise RuntimeError('requests is not available')
    return requests.get(url, headers=headers or {}, timeout=timeout)


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return len(rows)


def update_github_raw(repo: str, ref: str, file_paths: List[str], out_dir: str, policy: Policy) -> KBUpdateResult:
    """Fetch raw files from a public GitHub repo (best-effort).

    repo: 'owner/name'
    ref: branch/tag/sha
    file_paths: list like ['README.md','skills/react-best-practices/SKILL.md']
    """
    if not policy.allow_network:
        return KBUpdateResult(ok=False, reason='network_disabled', files_written=0, sources=[repo])

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    written = 0
    for fp in file_paths:
        url = f"https://raw.githubusercontent.com/{repo}/{ref}/{fp.lstrip('/')}"
        try:
            resp = _requests_get(url, headers={'User-Agent': 'vibe-coder-kb/12.1'}, timeout=25)
            if resp.status_code != 200:
                continue
            tgt = out / 'github' / repo.replace('/', '__') / ref / fp
            tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt.write_text(resp.text, encoding='utf-8', errors='ignore')
            written += 1
            time.sleep(0.2)
        except Exception:
            continue

    return KBUpdateResult(ok=written > 0, reason='ok' if written > 0 else 'no_files_fetched', files_written=written, sources=[repo])


def update_reddit_search(subreddit: str, query: str, out_dir: str, policy: Policy, limit: int = 25) -> KBUpdateResult:
    """Fetch reddit search results via the public JSON endpoint (best-effort)."""
    if not policy.allow_network:
        return KBUpdateResult(ok=False, reason='network_disabled', files_written=0, sources=[f'reddit:r/{subreddit}'])

    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={query}&restrict_sr=1&sort=relevance&t=year&limit={int(limit)}"
    )
    try:
        resp = _requests_get(url, headers={'User-Agent': 'vibe-coder-kb/12.1'}, timeout=25)
        if resp.status_code != 200:
            return KBUpdateResult(ok=False, reason=f'http_{resp.status_code}', files_written=0, sources=[url])
        data = resp.json()
    except Exception as e:
        return KBUpdateResult(ok=False, reason=f'error:{e}', files_written=0, sources=[url])

    rows: List[Dict[str, Any]] = []
    for ch in (data.get('data') or {}).get('children') or []:
        d = ch.get('data') or {}
        rows.append({
            'id': d.get('id'),
            'title': d.get('title'),
            'permalink': d.get('permalink'),
            'url': d.get('url'),
            'score': d.get('score'),
            'created_utc': d.get('created_utc'),
            'selftext': (d.get('selftext') or '')[:5000],
        })

    out = Path(out_dir) / 'reddit'
    out.mkdir(parents=True, exist_ok=True)
    n = _write_jsonl(out / f"r_{subreddit}__{_safe_slug(query)}.jsonl", rows)
    return KBUpdateResult(ok=n > 0, reason='ok' if n > 0 else 'empty', files_written=1 if n > 0 else 0, sources=[url])


def _safe_slug(s: str) -> str:
    import re
    s = (s or '').strip().lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s[:80] or 'query'
