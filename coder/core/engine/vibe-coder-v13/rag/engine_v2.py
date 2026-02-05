from __future__ import annotations

"""V13 RAG v2: SOTA/enterprise-ready (offline-first).

Key features (offline-first)
- Incremental indexing + hash cache: unchanged docs are reused.
- BM25 lexical retrieval (pure Python) with hybrid hooks (dense optional).
- Query enhancement (offline-safe): multi-query + step-back heuristics.
- Reranker: overlap rerank (lightweight, offline).
- Grounding cap: max_context_chars to control prompt budget.

This module intentionally avoids heavy dependencies so it can run in minimal CI
and in air-gapped environments.
"""

import json
import math
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from utils.hash_utils import sha256_text

# Optional production adapter layer (dependency-light). These modules are safe to import.
from rag.adapters.embedding import EmbeddingConfig, build_embedding_adapter
from rag.adapters.rerank import RerankConfig, RerankCandidate, build_rerank_adapter
from rag.retrieval.dense_index import DenseIndexConfig, build_or_update_dense_index, dense_retrieve, load_dense_index
from rag.retrieval.fusion import FusionConfig, rrf_fusion, weighted_fusion


_TOKEN_RE = re.compile(r"[^A-Za-z0-9_]+")


def _tokenize(text: str) -> List[str]:
    # Stable, dependency-free tokenizer for lexical retrieval.
    return [t for t in _TOKEN_RE.split((text or "").lower()) if len(t) >= 2]


def _dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        out.append(it)
    return out


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _split_sentences(text: str) -> List[str]:
    # Minimal sentence splitter (offline-safe). Prefer newlines, then periods.
    if not text:
        return []
    parts: List[str] = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        # Keep bullet lines as-is
        if line.startswith(('-', '*', '•')):
            parts.append(line)
            continue
        for seg in line.split('.'):
            seg = seg.strip()
            if seg:
                parts.append(seg + '.')
    return parts


def _extractive_summary(text: str, *, max_chars: int = 600, min_chars: int = 160) -> str:
    """Heuristic, deterministic summary for RAPTOR-like hierarchical retrieval.

    This is intentionally offline-first (no LLM calls). It favors early sentences
    and bullet points.
    """

    t = (text or "").strip()
    if len(t) <= max_chars:
        return t

    sents = _split_sentences(t)
    out: List[str] = []
    used = 0
    for s in sents:
        if used + len(s) > max_chars:
            break
        out.append(s)
        used += len(s)
        if used >= min_chars:
            # early stop once we have a minimally useful summary
            break
    if not out:
        return t[:max_chars]
    return " ".join(out).strip()


def _chunk_char_windows(
    text: str,
    *,
    chunk_size_chars: int,
    chunk_overlap_chars: int,
    min_chunk_chars: int,
) -> List[Tuple[int, str]]:
    """Deterministic char-window chunking (offline-safe)."""
    out: List[Tuple[int, str]] = []
    t = text or ""
    step = max(1, int(chunk_size_chars) - int(chunk_overlap_chars))
    for offset in range(0, len(t), step):
        chunk_text = t[offset : offset + int(chunk_size_chars)]
        if len(chunk_text.strip()) < int(min_chunk_chars):
            continue
        out.append((int(offset), chunk_text))
    return out


def _chunk_propositions(
    text: str,
    *,
    min_chunk_chars: int,
) -> List[Tuple[int, str]]:
    """Offline proposition chunking.

    Deterministic approximation of "Proposition Chunking": each sentence/bullet
    becomes a chunk. For production SOTA, swap with an LLM propositionizer via
    adapter layer later.
    """
    out: List[Tuple[int, str]] = []
    t = (text or "").strip()
    if not t:
        return out
    cursor = 0
    for sent in _split_sentences(t):
        s = sent.strip()
        if len(s) >= int(min_chunk_chars):
            out.append((int(cursor), s))
        cursor += len(sent)
    return out


def _chunk_csv_rows(text: str, *, min_chunk_chars: int = 16) -> List[Tuple[int, str]]:
    """CSV row chunking (dependency-free).

    Produces one chunk per row with a stable "key: value" rendering.
    Offsets are row indices (not byte offsets).
    """
    import csv
    from io import StringIO

    t = (text or "").strip()
    if not t:
        return []

    reader = csv.reader(StringIO(t))
    rows = [r for r in reader]
    if not rows:
        return []

    header = rows[0]
    data_rows = rows[1:] if header else rows

    out: List[Tuple[int, str]] = []
    for i, row in enumerate(data_rows):
        parts: List[str] = []
        if header and len(header) == len(row):
            for k, v in zip(header, row):
                kk = (k or "").strip()
                vv = (v or "").strip()
                if kk and vv:
                    parts.append(f"{kk}: {vv}")
        else:
            parts = [str(x).strip() for x in row if str(x).strip()]
        rendered = " | ".join(parts).strip()
        if len(rendered) < int(min_chunk_chars):
            continue
        out.append((int(i), rendered))
    return out


def _cooccurrence_pairs(tokens: List[str], *, cap: int = 32) -> List[Tuple[str, str]]:
    uniq = _dedupe_keep_order([t for t in tokens if t])[: max(1, int(cap))]
    pairs: List[Tuple[str, str]] = []
    for i in range(len(uniq)):
        a = uniq[i]
        for j in range(i + 1, len(uniq)):
            b = uniq[j]
            if a == b:
                continue
            pairs.append((a, b))
    return pairs


@dataclass
class ChunkV2:
    chunk_id: str
    doc_id: str
    source: str
    kind: str
    content: str
    offset: int
    meta: Dict[str, Any]
    # retrieval stats
    length: int
    tf: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "source": self.source,
            "kind": self.kind,
            "content": self.content,
            "offset": self.offset,
            "meta": self.meta,
            "length": self.length,
            "tf": self.tf,
        }


@dataclass
class DocV2:
    doc_id: str
    source: str
    kind: str
    meta: Dict[str, Any]
    content_sha256: str
    chunk_ids: List[str]
    # RAPTOR-style hierarchical index (offline heuristic): summary node per doc
    summary_chunk_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source": self.source,
            "kind": self.kind,
            "meta": self.meta,
            "content_sha256": self.content_sha256,
            "chunk_ids": self.chunk_ids,
            "summary_chunk_id": self.summary_chunk_id,
        }


@dataclass
class KBV2:
    version: str
    docs: Dict[str, DocV2]
    chunks: Dict[str, ChunkV2]
    df: Dict[str, int]
    n_chunks: int
    avgdl: float
    # GraphRAG-style lightweight term graph (offline heuristic)
    graph: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "docs": {k: v.to_dict() for k, v in self.docs.items()},
            "chunks": {k: v.to_dict() for k, v in self.chunks.items()},
            "bm25": {
                "df": self.df,
                "n_chunks": self.n_chunks,
                "avgdl": self.avgdl,
            },
            "graph": self.graph,
        }


class AdvancedRAGv2:
    """AdvancedRAG v2.

    Storage
      - .vibe/kb/v13_rag_v2.json

    Public API
      - ingest(sources) -> kb_path
      - query(prompt, ...) -> {context, sources, ...}
    """

    KB_FILENAME = "v13_rag_v2.json"
    VERSION = "13.0-rag-v2"

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.kb_path = self.repo_root / ".vibe" / "kb" / self.KB_FILENAME
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------- ingest ---------------------------

    def ingest(
        self,
        sources: List[Dict[str, Any]],
        *,
        chunk_size_chars: int = 900,
        chunk_overlap_chars: int = 120,
        min_chunk_chars: int = 80,
        chunk_strategy: str = "char",  # char | proposition
        # Preset 1 defaults: offline-first GraphRAG + RAPTOR summaries
        enable_graphrag: bool = True,
        graphrag_max_terms_per_chunk: int = 32,
        graphrag_max_neighbors: int = 12,
        enable_raptor: bool = True,
        raptor_summary_max_chars: int = 600,
        raptor_summary_min_chars: int = 160,
        # Dense embeddings (optional; adapter-based). Default off for offline-first.
        enable_dense: bool = False,
        dense_provider: str = "stub_hash",
        dense_model: str = "hash-256",
        dense_dim: int = 256,
        dense_backend: str = "scan",
    ) -> str:
        """Incrementally ingest sources into the KB.

        Each source dict may include:
          - source/url/id: stable identifier (preferred)
          - type/kind
          - content (preferred) OR path (local file)
          - meta

        Hash cache behavior
          - If doc_id exists and content hash unchanged, we reuse its chunks.
        """

        existing = self._load_kb()
        docs: Dict[str, DocV2] = dict(existing.docs) if existing else {}
        chunks: Dict[str, ChunkV2] = dict(existing.chunks) if existing else {}

        # Process each source as an upsert.
        for src in sources or []:
            if not isinstance(src, dict):
                continue

            source_id = str(src.get("source") or src.get("url") or src.get("id") or "").strip()
            kind = str(src.get("type") or src.get("kind") or "unknown").strip()
            meta: Dict[str, Any] = dict(src.get("meta") or {})

            content = src.get("content")
            if content is None and src.get("path"):
                p = Path(str(src.get("path"))).expanduser()
                if not p.is_absolute():
                    p = (self.repo_root / p).resolve()
                if p.exists() and p.is_file():
                    meta["path"] = str(p)
                    content = _safe_read_text(p)

            if not isinstance(content, str) or not content.strip():
                # Skip empty docs (offline-safe; no hallucination).
                continue

            content = content.strip()
            content_hash = sha256_text(content)

            doc_id = str(src.get("doc_id") or source_id or meta.get("path") or "").strip()
            if not doc_id:
                doc_id = f"doc:{content_hash[:12]}"

            prev = docs.get(doc_id)
            if prev and prev.content_sha256 == content_hash:
                # Unchanged: keep existing chunks.
                continue

            # Changed doc: remove previous chunks
            if prev:
                for cid in prev.chunk_ids:
                    chunks.pop(cid, None)
                if prev.summary_chunk_id:
                    chunks.pop(str(prev.summary_chunk_id), None)

            # Re-chunk
            new_chunk_ids: List[str] = []

            # Choose chunker (offline-first):
            # - CSV sources: one row per chunk
            # - proposition strategy: one sentence/bullet per chunk
            # - default: fixed char windows
            path_hint = str(meta.get("path") or "")
            is_csv = kind.lower() == "csv" or path_hint.lower().endswith(".csv")
            strategy = str(chunk_strategy or "char").strip().lower()

            if is_csv:
                pieces = _chunk_csv_rows(content, min_chunk_chars=max(16, int(min_chunk_chars // 4)))
            elif strategy == "proposition":
                pieces = _chunk_propositions(content, min_chunk_chars=int(min_chunk_chars))
            else:
                pieces = _chunk_char_windows(
                    content,
                    chunk_size_chars=int(chunk_size_chars),
                    chunk_overlap_chars=int(chunk_overlap_chars),
                    min_chunk_chars=int(min_chunk_chars),
                )

            for offset, chunk_text in pieces:
                cid = f"{doc_id}::off{offset}"
                toks = _tokenize(chunk_text)
                tf: Dict[str, int] = {}
                for t in toks:
                    tf[t] = tf.get(t, 0) + 1
                chunks[cid] = ChunkV2(
                    chunk_id=cid,
                    doc_id=doc_id,
                    source=source_id or doc_id,
                    kind=kind,
                    content=chunk_text,
                    offset=int(offset),
                    meta={**meta, "offset": int(offset), "chunk_strategy": ("csv" if is_csv else strategy)},
                    length=len(toks),
                    tf=tf,
                )
                new_chunk_ids.append(cid)

            # RAPTOR (preset-1 heuristic): add one summary "node" per doc.
            summary_cid: Optional[str] = None
            if enable_raptor:
                summary = _extractive_summary(
                    content,
                    max_chars=int(raptor_summary_max_chars),
                    min_chars=int(raptor_summary_min_chars),
                )
                if isinstance(summary, str) and summary.strip():
                    summary_cid = f"{doc_id}::summary"
                    toks = _tokenize(summary)
                    tf: Dict[str, int] = {}
                    for t in toks:
                        tf[t] = tf.get(t, 0) + 1
                    chunks[summary_cid] = ChunkV2(
                        chunk_id=summary_cid,
                        doc_id=doc_id,
                        source=source_id or doc_id,
                        kind="summary",
                        content=summary,
                        offset=0,
                        meta={**meta, "summary": True},
                        length=len(toks),
                        tf=tf,
                    )

            docs[doc_id] = DocV2(
                doc_id=doc_id,
                source=source_id or doc_id,
                kind=kind,
                meta=meta,
                content_sha256=content_hash,
                chunk_ids=new_chunk_ids,
                summary_chunk_id=summary_cid,
            )

        # Recompute BM25 document frequencies + avgdl.
        df: Dict[str, int] = {}
        total_len = 0
        n_chunks = 0
        for ch in chunks.values():
            n_chunks += 1
            total_len += int(ch.length or 0)
            for term in ch.tf.keys():
                df[term] = df.get(term, 0) + 1

        avgdl = (float(total_len) / float(n_chunks)) if n_chunks else 0.0
        graph: Dict[str, Any] = {}
        if enable_graphrag:
            graph = self._build_term_graph(
                chunks,
                max_terms_per_chunk=int(graphrag_max_terms_per_chunk),
                max_neighbors=int(graphrag_max_neighbors),
            )

        # Optional dense index build/update (separate file; incremental via hash cache)
        dense_meta: Dict[str, Any] = {}
        if enable_dense:
            dense_cfg = DenseIndexConfig(
                enabled=True,
                provider=str(dense_provider or "stub_hash"),
                model=str(dense_model or "hash-256"),
                dim=int(dense_dim or 256),
                backend=str(dense_backend or "scan"),
            )
            # Build map of chunk_id -> content (skip summaries)
            chunk_texts: Dict[str, str] = {cid: ch.content for cid, ch in chunks.items()}
            skip_summary: Dict[str, bool] = {cid: (ch.kind == "summary") for cid, ch in chunks.items()}
            idx, idx_path = build_or_update_dense_index(self.repo_root, dense_cfg, chunks=chunk_texts, skip_if_kind_summary=skip_summary)
            if idx and idx_path:
                dense_meta = {
                    "enabled": True,
                    "provider": idx.provider,
                    "model": idx.model,
                    "dim": int(idx.dim),
                    "index_filename": dense_cfg.index_filename,
                    "index_path": str(idx_path),
                }


        if dense_meta:
            graph = dict(graph or {})
            graph["dense"] = dense_meta

        kb = KBV2(
            version=self.VERSION,
            docs=docs,
            chunks=chunks,
            df=df,
            n_chunks=n_chunks,
            avgdl=avgdl,
            graph=graph,
        )
        self.kb_path.write_text(json.dumps(kb.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return str(self.kb_path)

    # --------------------------- query ---------------------------

    def query(
        self,
        prompt: str,
        *,
        limit: int = 6,
        max_context_chars: int = 8000,
        candidate_k: int = 24,
        # Preset 1 defaults (offline-first)
        enable_graphrag: bool = True,
        enable_raptor: bool = True,
        enable_crag: bool = True,
        crag_max_passes: int = 1,
        graphrag_expand_k: int = 6,
        raptor_summary_k: int = 4,
        include_summaries: bool = False,
        bm25_k1: float = 1.2,
        bm25_b: float = 0.75,
        # Dense retrieval + fusion (adapter-based; default off)
        enable_dense: bool = False,
        dense_backend: str = "scan",
        dense_topk: int = 24,
        fusion_mode: str = "rrf",  # rrf | weighted | none
        fusion_rrf_k: int = 60,
        fusion_w_bm25: float = 1.0,
        fusion_w_dense: float = 1.0,
        # Optional rerank adapter (cross-encoder / LLM judge; default off)
        enable_rerank: bool = False,
        rerank_provider: str = "stub",
        rerank_model: str = "noop",
        rerank_topk: int = 12,
    ) -> Dict[str, Any]:
        """Retrieve grounded context.

        Returns
          - context: concatenated chunk content capped by max_context_chars
          - sources: list of ranked evidence items (chunk-level)
          - evidence_level: E0 (no KB) or E1 (KB grounded)
        """

        kb = self._load_kb()
        if not kb or not kb.chunks:
            return {"context": "", "sources": [], "evidence_level": "E0", "reason": "KB_EMPTY"}

        prompt = str(prompt or "").strip()
        if not prompt:
            return {"context": "", "sources": [], "evidence_level": "E1", "reason": "EMPTY_QUERY"}

        techniques_used: List[str] = ["bm25", "heuristic_query_enhancement", "overlap_rerank", "context_cap"]

        # Query enhancement (offline-safe)
        queries = self._enhance_queries(prompt)

        # GraphRAG (preset-1 heuristic): term graph expansion
        if enable_graphrag and isinstance(getattr(kb, "graph", None), dict) and kb.graph.get("adj"):
            queries = _dedupe_keep_order(queries + self._graphrag_expand_queries(queries, kb.graph, topk=int(graphrag_expand_k)))
            techniques_used.append("graphrag_term_graph")

        start = time.time()
        bm25_scored: Dict[str, float] = {}

        def _score_with_queries(qs: List[str], *, mult: float = 1.0) -> None:
            for q in qs:
                q_toks = _tokenize(q)
                if not q_toks:
                    continue
                for cid, score in self._bm25_scores(kb, q_toks, k1=bm25_k1, b=bm25_b):
                    bm25_scored[cid] = max(bm25_scored.get(cid, 0.0), float(score) * float(mult))

        _score_with_queries(queries)

        summary_hits = 0
        if enable_raptor:
            summary_hits = self._raptor_boost_from_summaries(
                kb,
                bm25_scored,
                queries,
                topk=int(raptor_summary_k),
                bm25_k1=float(bm25_k1),
                bm25_b=float(bm25_b),
            )
            techniques_used.append("raptor_doc_summary")

        corrective_passes = 0
        if enable_crag and int(crag_max_passes) > 0 and self._crag_should_correct(bm25_scored, min_candidates=int(limit)):
            corrective_passes = 1
            techniques_used.append("crag_corrective_retrieval")
            extra_q = self._crag_expand_queries(prompt, queries)
            if enable_graphrag and isinstance(getattr(kb, "graph", None), dict) and kb.graph.get("adj"):
                extra_q = _dedupe_keep_order(extra_q + self._graphrag_expand_queries(extra_q, kb.graph, topk=max(4, int(graphrag_expand_k))))
            _score_with_queries(extra_q, mult=0.95)
            if enable_raptor:
                summary_hits = max(
                    summary_hits,
                    self._raptor_boost_from_summaries(
                        kb,
                        bm25_scored,
                        extra_q,
                        topk=int(raptor_summary_k),
                        bm25_k1=float(bm25_k1),
                        bm25_b=float(bm25_b),
                    ),
                )


        

        # Optional dense retrieval + fusion
        dense_scored: Dict[str, float] = {}
        if enable_dense:
            dense_cfg = DenseIndexConfig(enabled=True, backend=str(dense_backend or "scan"))
            # Try to read index metadata from KB (preferred)
            dense_meta = (kb.graph or {}).get("dense") if isinstance(getattr(kb, "graph", None), dict) else None
            if isinstance(dense_meta, dict):
                dense_cfg.provider = str(dense_meta.get("provider") or dense_cfg.provider)
                dense_cfg.model = str(dense_meta.get("model") or dense_cfg.model)
                dense_cfg.dim = int(dense_meta.get("dim") or dense_cfg.dim)
                dense_cfg.index_filename = str(dense_meta.get("index_filename") or dense_cfg.index_filename)
            dense_cfg.topk = int(dense_topk or dense_cfg.topk)

            idx_obj = load_dense_index(self.repo_root, dense_cfg)
            if idx_obj and idx_obj.vectors:
                # Build embedding adapter and retrieve by cosine
                embed_cfg = EmbeddingConfig(provider=dense_cfg.provider, model=dense_cfg.model, dim=int(dense_cfg.dim))
                emb = build_embedding_adapter(embed_cfg)
                qv = emb.embed_query(prompt)
                dense_ranked = dense_retrieve(self.repo_root, dense_cfg, idx_obj, qv, topk=int(dense_cfg.topk))
                for cid, s in dense_ranked:
                    if s > 0:
                        dense_scored[cid] = float(s)
                techniques_used.append("dense_retrieval")

        fusion_cfg = FusionConfig(
            mode=str(fusion_mode or "rrf"),
            rrf_k=int(fusion_rrf_k or 60),
            w_bm25=float(fusion_w_bm25 or 1.0),
            w_dense=float(fusion_w_dense or 1.0),
        )

        # Final scored signal used for candidate selection
        scored: Dict[str, float] = dict(bm25_scored)
        if dense_scored:
            if fusion_cfg.mode == "weighted":
                fused = weighted_fusion(bm25_scored, dense_scored, w_bm25=fusion_cfg.w_bm25, w_dense=fusion_cfg.w_dense)
                scored = {cid: float(s) for cid, s in fused}
                techniques_used.append("fusion_weighted")
            elif fusion_cfg.mode == "none":
                # dense-only (if bm25 empty)
                scored = dict(dense_scored) if not bm25_scored else dict(bm25_scored)
                techniques_used.append("fusion_none")
            else:
                bm25_ranked = sorted(bm25_scored.items(), key=lambda kv: (-kv[1], kv[0]))
                dense_ranked = sorted(dense_scored.items(), key=lambda kv: (-kv[1], kv[0]))
                fused = rrf_fusion([bm25_ranked, dense_ranked], k=fusion_cfg.rrf_k)
                scored = {cid: float(s) for cid, s in fused}
                techniques_used.append("fusion_rrf")

        # Preselect candidates
        cands = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))[: max(1, int(candidate_k))]
        candidate_chunks: List[Tuple[str, float, ChunkV2]] = []
        for cid, s in cands:
            ch = kb.chunks.get(cid)
            if ch:
                if (not include_summaries) and ch.kind == "summary":
                    continue
                candidate_chunks.append((cid, s, ch))

        # Overlap rerank (lightweight)
        final = self._overlap_rerank(prompt, candidate_chunks)
        final = final[: max(1, int(limit))]

        # Optional adapter rerank (stub by default)
        if enable_rerank and final:
            rr_cfg = RerankConfig(provider=str(rerank_provider or "stub"), model=str(rerank_model or "noop"), topk=int(rerank_topk or 12))
            rr = build_rerank_adapter(rr_cfg)
            # rerank only top-k
            topk = max(1, min(int(rr_cfg.topk), len(final)))
            rr_in = [
                RerankCandidate(chunk_id=cid, text=ch.content, score=float(score), meta={"doc_id": ch.doc_id, "source": ch.source, "kind": ch.kind})
                for (cid, score, ch) in final[:topk]
            ]
            rr_out = rr.rerank(prompt, rr_in)
            # rebuild final list order using reranked candidates; keep tail
            new_order = {c.chunk_id: c for c in (rr_out.candidates or [])}
            reranked: List[Tuple[str, float, ChunkV2]] = []
            for item in rr_out.candidates or []:
                # find corresponding chunk
                for (cid, _s, ch) in final:
                    if cid == item.chunk_id:
                        reranked.append((cid, float(item.score), ch))
                        break
            # append any candidates that weren't reranked
            seen = {cid for cid, _, _ in reranked}
            for cid, s, ch in final:
                if cid not in seen:
                    reranked.append((cid, float(s), ch))
            final = reranked[: max(1, int(limit))]
            techniques_used.append("adapter_rerank")

        # Grounding cap
        ctx_parts: List[str] = []
        used = 0
        out_sources: List[Dict[str, Any]] = []
        for rank, (cid, score, ch) in enumerate(final, start=1):
            text = ch.content
            if not text:
                continue
            if used + len(text) > int(max_context_chars):
                remaining = int(max_context_chars) - used
                if remaining <= 0:
                    break
                text = text[:remaining]
            ctx_parts.append(text)
            used += len(text)
            out_sources.append(
                {
                    "rank": rank,
                    "chunk_id": cid,
                    "doc_id": ch.doc_id,
                    "source": ch.source,
                    "kind": ch.kind,
                    "offset": ch.offset,
                    "score": float(score),
                    "meta": ch.meta,
                }
            )

        latency_ms = int((time.time() - start) * 1000)
        return {
            "context": "\n\n".join(ctx_parts),
            "sources": out_sources,
            "evidence_level": "E1",
            "matched_chunks": len(out_sources),
            "queries": queries,
            "expanded_queries": len(queries),
            "fusion_mode": str(fusion_mode or "rrf"),
            "dense_candidates": int(len(dense_scored) if "dense_scored" in locals() else 0),
            "summary_hits": int(summary_hits),
            "corrective_passes": int(corrective_passes),
            "techniques_used": _dedupe_keep_order(techniques_used),
            "latency_ms": latency_ms,
        }

    # --------------------------- internals ---------------------------

    def _load_kb(self) -> Optional[KBV2]:
        if not self.kb_path.exists():
            return None
        try:
            data = json.loads(self.kb_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return None

        docs_raw = data.get("docs") or {}
        chunks_raw = data.get("chunks") or {}
        bm25 = data.get("bm25") or {}

        docs: Dict[str, DocV2] = {}
        for k, v in (docs_raw.items() if isinstance(docs_raw, dict) else []):
            if not isinstance(v, dict):
                continue
            docs[str(k)] = DocV2(
                doc_id=str(v.get("doc_id") or k),
                source=str(v.get("source") or ""),
                kind=str(v.get("kind") or "unknown"),
                meta=dict(v.get("meta") or {}),
                content_sha256=str(v.get("content_sha256") or ""),
                chunk_ids=[str(x) for x in (v.get("chunk_ids") or []) if isinstance(x, (str, int))],
                summary_chunk_id=(str(v.get("summary_chunk_id")) if v.get("summary_chunk_id") else None),
            )

        chunks: Dict[str, ChunkV2] = {}
        for k, v in (chunks_raw.items() if isinstance(chunks_raw, dict) else []):
            if not isinstance(v, dict):
                continue
            tf_raw = v.get("tf") or {}
            tf: Dict[str, int] = {}
            if isinstance(tf_raw, dict):
                for tk, tv in tf_raw.items():
                    try:
                        tf[str(tk)] = int(tv)
                    except Exception:
                        continue
            chunks[str(k)] = ChunkV2(
                chunk_id=str(v.get("chunk_id") or k),
                doc_id=str(v.get("doc_id") or ""),
                source=str(v.get("source") or ""),
                kind=str(v.get("kind") or "unknown"),
                content=str(v.get("content") or ""),
                offset=int(v.get("offset") or 0),
                meta=dict(v.get("meta") or {}),
                length=int(v.get("length") or 0),
                tf=tf,
            )

        df_raw = (bm25.get("df") or {}) if isinstance(bm25, dict) else {}
        df: Dict[str, int] = {}
        if isinstance(df_raw, dict):
            for tk, tv in df_raw.items():
                try:
                    df[str(tk)] = int(tv)
                except Exception:
                    continue

        graph = data.get("graph") or {}
        if not isinstance(graph, dict):
            graph = {}

        return KBV2(
            version=str(data.get("version") or self.VERSION),
            docs=docs,
            chunks=chunks,
            df=df,
            n_chunks=int(bm25.get("n_chunks") or len(chunks)),
            avgdl=float(bm25.get("avgdl") or 0.0),
            graph=graph,
        )

    def _bm25_scores(self, kb: KBV2, q_tokens: List[str], *, k1: float, b: float) -> List[Tuple[str, float]]:
        # Standard BM25 (Okapi) scoring over chunks.
        N = max(1, int(kb.n_chunks or len(kb.chunks)))
        avgdl = float(kb.avgdl or 1.0)
        q_terms = [t for t in q_tokens if t]
        scores: List[Tuple[str, float]] = []

        # Speed: compute idf once per term
        idf: Dict[str, float] = {}
        for t in q_terms:
            df = float(kb.df.get(t, 0))
            # stable + avoids negative IDF
            idf[t] = math.log(1.0 + (N - df + 0.5) / (df + 0.5))

        for cid, ch in kb.chunks.items():
            dl = float(ch.length or 0)
            if dl <= 0:
                continue
            denom_base = k1 * (1.0 - b + b * (dl / avgdl))
            s = 0.0
            for t in q_terms:
                tf = float(ch.tf.get(t, 0))
                if tf <= 0:
                    continue
                s += idf.get(t, 0.0) * ((tf * (k1 + 1.0)) / (tf + denom_base))
            if s > 0:
                scores.append((cid, s))

        scores.sort(key=lambda kv: (-kv[1], kv[0]))
        return scores

    def _overlap_rerank(self, prompt: str, candidates: List[Tuple[str, float, ChunkV2]]) -> List[Tuple[str, float, ChunkV2]]:
        q = set(_tokenize(prompt))
        if not q:
            return sorted(candidates, key=lambda x: (-x[1], x[0]))

        out: List[Tuple[str, float, ChunkV2]] = []
        for cid, bm25, ch in candidates:
            ch_terms = set(ch.tf.keys())
            inter = len(q.intersection(ch_terms))
            overlap = float(inter) / float(max(1, len(q)))
            # overlap dominates ties, but keep bm25 signal
            score = float(bm25) + 0.25 * overlap
            out.append((cid, score, ch))

        out.sort(key=lambda x: (-x[1], x[0]))
        return out

    def _enhance_queries(self, prompt: str) -> List[str]:
        # Offline-safe multi-query + step-back heuristics.
        base = " ".join(str(prompt).strip().split())
        toks = _tokenize(base)

        variants: List[str] = [base]

        # Step-back (broader query): keep top tokens, drop numeric-ish noise
        if toks:
            coarse = " ".join([t for t in toks if not t.isdigit()])
            if coarse and coarse != base:
                variants.append(coarse)

        # If prompt looks like a stacktrace, extract keywords
        if any(k in base.lower() for k in ["traceback", "exception", "error", "failed", "assert"]):
            keywords = [t for t in toks if t not in {"traceback", "exception", "error", "failed", "assert"}]
            if keywords:
                variants.append(" ".join(keywords[:10]))

        # Multi-query expansion: shorter focus query
        if len(toks) > 10:
            variants.append(" ".join(toks[:10]))

        # Generic intent rewrites
        if base.lower().startswith("how ") or base.lower().startswith("how to"):
            variants.append("guide " + " ".join(toks[:10]))

        return _dedupe_keep_order([v for v in variants if isinstance(v, str) and v.strip()])

    # --------------------------- preset-1 add-ons ---------------------------

    def _build_term_graph(
        self,
        chunks: Dict[str, ChunkV2],
        *,
        max_terms_per_chunk: int = 32,
        max_neighbors: int = 12,
    ) -> Dict[str, Any]:
        """Build a lightweight term co-occurrence graph (GraphRAG-style, offline heuristic).

        We only use lexical terms (tokenized) and keep top-N neighbors per term.
        """

        counts: Dict[str, Dict[str, int]] = {}
        for ch in chunks.values():
            # Skip summary nodes (keep them as retrieval-only for RAPTOR)
            if ch.kind == "summary":
                continue
            toks = list(ch.tf.keys()) if ch.tf else _tokenize(ch.content)
            for a, b in _cooccurrence_pairs(toks, cap=int(max_terms_per_chunk)):
                if a == b:
                    continue
                ca = counts.setdefault(a, {})
                ca[b] = ca.get(b, 0) + 1
                cb = counts.setdefault(b, {})
                cb[a] = cb.get(a, 0) + 1

        # Prune neighbors per term
        adj: Dict[str, Dict[str, int]] = {}
        for term, neigh in counts.items():
            if not neigh:
                continue
            top = sorted(neigh.items(), key=lambda kv: (-kv[1], kv[0]))[: max(1, int(max_neighbors))]
            adj[term] = {k: int(v) for k, v in top}

        return {
            "version": "graphrag.v1",
            "max_neighbors": int(max_neighbors),
            "adj": adj,
        }

    def _graphrag_expand_queries(self, queries: List[str], graph: Dict[str, Any], *, topk: int = 6) -> List[str]:
        adj = graph.get("adj") if isinstance(graph, dict) else None
        if not isinstance(adj, dict):
            return []

        out: List[str] = []
        for q in queries or []:
            toks = _tokenize(q)
            expanded: List[str] = []
            for t in toks[:10]:
                neigh = adj.get(t)
                if not isinstance(neigh, dict):
                    continue
                # pick strongest neighbors
                nn = sorted(neigh.items(), key=lambda kv: (-int(kv[1]), str(kv[0])))[: max(1, int(topk))]
                expanded.extend([str(k) for k, _ in nn if isinstance(k, str)])
            expanded = _dedupe_keep_order(expanded)
            if expanded:
                out.append(" ".join(_dedupe_keep_order(toks + expanded[: int(topk)])))
        return out

    def _raptor_boost_from_summaries(
        self,
        kb: KBV2,
        scored: Dict[str, float],
        queries: List[str],
        *,
        topk: int = 4,
        bm25_k1: float,
        bm25_b: float,
    ) -> int:
        """RAPTOR-style: retrieve doc-level summaries, then boost child chunks for those docs."""

        # retrieve summaries only
        summary_scored: Dict[str, float] = {}
        for q in queries or []:
            toks = _tokenize(q)
            if not toks:
                continue
            for cid, s in self._bm25_scores(kb, toks, k1=bm25_k1, b=bm25_b):
                ch = kb.chunks.get(cid)
                if not ch or ch.kind != "summary":
                    continue
                summary_scored[cid] = max(summary_scored.get(cid, 0.0), float(s))

        top = sorted(summary_scored.items(), key=lambda kv: (-kv[1], kv[0]))[: max(0, int(topk))]
        hits = 0
        for cid, s in top:
            ch = kb.chunks.get(cid)
            if not ch:
                continue
            doc = kb.docs.get(ch.doc_id)
            if not doc:
                continue
            hits += 1
            boost = float(s) * 0.85
            for child in doc.chunk_ids or []:
                if child not in kb.chunks:
                    continue
                scored[child] = max(scored.get(child, 0.0), boost)
        return hits

    def _crag_should_correct(self, scored: Dict[str, float], *, min_candidates: int) -> bool:
        if not scored:
            return True
        # Use a simple confidence signal: top score dominance + separation.
        top = sorted(scored.values(), reverse=True)
        if len(top) < max(1, int(min_candidates)):
            return True
        s1 = float(top[0])
        s2 = float(top[1]) if len(top) > 1 else 0.0
        if s1 <= 0:
            return True
        sep = (s1 - s2) / (s1 + 1e-9)
        # low separation means ambiguous retrieval; do corrective pass
        if sep < 0.05:
            return True
        # if scores are very low overall, do corrective pass
        if s1 < 0.15:
            return True
        return False

    def _crag_expand_queries(self, prompt: str, base_queries: List[str]) -> List[str]:
        """CRAG-style corrective query expansion (offline heuristic)."""
        out: List[str] = []
        out.extend(base_queries or [])

        # Decompose by common separators
        raw = " ".join(str(prompt or "").strip().split())
        for sep in ["?", ".", ";", " and ", " & ", "\n"]:
            if sep in raw:
                parts = [p.strip() for p in raw.split(sep) if p.strip()]
                for p in parts[:5]:
                    if len(_tokenize(p)) >= 2:
                        out.append(p)

        # Focused keyword query
        toks = _tokenize(raw)
        if toks:
            out.append(" ".join(toks[:12]))
        return _dedupe_keep_order([q for q in out if isinstance(q, str) and q.strip()])
