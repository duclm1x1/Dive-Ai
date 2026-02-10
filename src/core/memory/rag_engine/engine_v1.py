from __future__ import annotations

"""Legacy V13 RAG engine (v1).

Kept for backward compatibility.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _tokenize(text: str) -> List[str]:
    # Cheap, dependency-free tokenization; stable enough for offline retrieval.
    return [t for t in re.split(r"[^A-Za-z0-9_]+", (text or "").lower()) if len(t) >= 2]


@dataclass
class _DocChunk:
    source: str
    kind: str
    content: str
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "kind": self.kind,
            "content": self.content,
            "meta": self.meta,
        }


class AdvancedRAGv1:
    """V13 Advanced RAG (offline-first, legacy).

    Contract:
      - No hidden web fetch.
      - Ingest accepts either raw `content` or a local `path`.
      - Query returns the top-ranked chunks with an explicit evidence level.
    """

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.kb_path = self.repo_root / ".vibe" / "kb" / "v13_rag.json"
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)

    def ingest(self, sources: List[Dict[str, Any]]) -> str:
        """Ingest knowledge sources.

        Each source may include:
          - source: string (url/id)
          - type: string
          - content: string (preferred)
          - path: local file path (optional)
          - meta: dict (optional)
        """

        chunks: List[_DocChunk] = []

        for src in sources or []:
            if not isinstance(src, dict):
                continue
            source_id = str(src.get("source") or src.get("url") or src.get("id") or "")
            kind = str(src.get("type") or src.get("kind") or "unknown")
            meta = dict(src.get("meta") or {})

            content = src.get("content")
            if content is None and src.get("path"):
                try:
                    p = Path(str(src.get("path"))).expanduser()
                    if not p.is_absolute():
                        p = (self.repo_root / p).resolve()
                    if p.exists() and p.is_file():
                        content = p.read_text(encoding="utf-8", errors="ignore")
                        meta["path"] = str(p)
                except Exception:
                    content = None

            if not isinstance(content, str) or not content.strip():
                # Skip empty docs; do not hallucinate.
                continue

            # Chunking: 800-1200 chars windows to keep context manageable.
            text = content.strip()
            step = 900
            for i in range(0, len(text), step):
                chunk = text[i : i + step]
                if not chunk.strip():
                    continue
                chunks.append(_DocChunk(source=source_id, kind=kind, content=chunk, meta={**meta, "offset": i}))

        payload = {
            "version": "13.0",
            "chunks": [c.to_dict() for c in chunks],
        }
        self.kb_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(self.kb_path)

    def query(self, prompt: str, *, limit: int = 5) -> Dict[str, Any]:
        """Retrieve top chunks from the ingested KB.

        Evidence level:
          - E0 if KB is empty
          - E1 if user-provided content exists (this KB)
        """

        if not self.kb_path.exists():
            return {"context": "", "sources": [], "evidence_level": "E0", "reason": "KB_NOT_FOUND"}

        try:
            data = json.loads(self.kb_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return {"context": "", "sources": [], "evidence_level": "E0", "reason": "KB_CORRUPT"}

        chunks = [c for c in (data.get("chunks") or []) if isinstance(c, dict)]
        if not chunks:
            return {"context": "", "sources": [], "evidence_level": "E0", "reason": "KB_EMPTY"}

        q_tokens = _tokenize(prompt)
        if not q_tokens:
            return {"context": "", "sources": [], "evidence_level": "E1", "reason": "EMPTY_QUERY"}

        def score_chunk(c: Dict[str, Any]) -> int:
            text = str(c.get("content") or "")
            t = text.lower()
            score = 0
            for tok in q_tokens:
                score += t.count(tok)
            # bonus if source contains tokens
            src = str(c.get("source") or "").lower()
            for tok in q_tokens:
                if tok in src:
                    score += 2
            return score

        ranked: List[Tuple[int, Dict[str, Any]]] = []
        for c in chunks:
            s = score_chunk(c)
            if s <= 0:
                continue
            ranked.append((s, c))

        ranked.sort(key=lambda x: (-x[0], str(x[1].get("source") or "")))
        top = [c for _, c in ranked[: max(1, int(limit))]]

        context = "\n\n".join([str(c.get("content") or "") for c in top])
        sources = [{"source": c.get("source"), "kind": c.get("kind"), "meta": c.get("meta")} for c in top]

        return {
            "context": context,
            "sources": sources,
            "evidence_level": "E1",
            "matched_chunks": len(top),
        }
