from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..adapters.embedding import EmbeddingAdapter, EmbeddingConfig, build_embedding_adapter
from utils.hash_utils import sha256_text

from .ann import build_or_update_ann_cache, try_ann_retrieve


@dataclass
class DenseIndexConfig:
    enabled: bool = False
    provider: str = "stub_hash"
    model: str = "hash-256"
    dim: int = 256
    # ANN backend: scan|hnswlib|faiss (optional deps; falls back to scan)
    backend: str = "scan"
    # persistence
    index_filename: str = "v13_rag_v2_dense.json"
    ann_index_filename: str = "v13_rag_v2_dense.ann"
    ann_meta_filename: str = "v13_rag_v2_dense.ann.meta.json"
    # retrieval
    topk: int = 24


@dataclass
class DenseIndex:
    dim: int
    vectors: Dict[str, List[float]]          # chunk_id -> vector
    hashes: Dict[str, str]                  # chunk_id -> sha256(content)
    provider: str
    model: str


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(len(a)):
        av = float(a[i]); bv = float(b[i])
        dot += av * bv
        na += av * av
        nb += bv * bv
    denom = math.sqrt(na) * math.sqrt(nb)
    if denom <= 0:
        return 0.0
    return dot / denom


def load_dense_index(repo_root: Path, cfg: DenseIndexConfig) -> Optional[DenseIndex]:
    p = repo_root / ".vibe" / "kb" / cfg.index_filename
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    dim = int(data.get("dim") or cfg.dim or 256)
    vectors_raw = data.get("vectors") or {}
    hashes_raw = data.get("hashes") or {}
    if not isinstance(vectors_raw, dict) or not isinstance(hashes_raw, dict):
        return None
    vectors: Dict[str, List[float]] = {}
    for cid, vec in vectors_raw.items():
        if isinstance(vec, list):
            try:
                vectors[str(cid)] = [float(x) for x in vec]
            except Exception:
                continue
    hashes: Dict[str, str] = {}
    for cid, h in hashes_raw.items():
        if isinstance(h, str):
            hashes[str(cid)] = h
    return DenseIndex(dim=dim, vectors=vectors, hashes=hashes, provider=str(data.get("provider") or cfg.provider), model=str(data.get("model") or cfg.model))


def save_dense_index(repo_root: Path, cfg: DenseIndexConfig, idx: DenseIndex) -> str:
    p = repo_root / ".vibe" / "kb" / cfg.index_filename
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "dense.v2",
        "provider": idx.provider,
        "model": idx.model,
        "dim": int(idx.dim),
        "backend": str(getattr(cfg, 'backend', 'scan')),
        "vectors": idx.vectors,
        "hashes": idx.hashes,
    }
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(p)


def build_or_update_dense_index(
    repo_root: Path,
    cfg: DenseIndexConfig,
    *,
    chunks: Dict[str, str],  # chunk_id -> content
    skip_if_kind_summary: Dict[str, bool] | None = None,
) -> Tuple[Optional[DenseIndex], Optional[str]]:
    """Incrementally build/update dense index.

    Offline-first default uses HashEmbeddingAdapter, but factory allows real providers later.
    """
    if not cfg.enabled:
        return None, None

    embed_cfg = EmbeddingConfig(provider=cfg.provider, model=cfg.model, dim=cfg.dim)
    adapter: EmbeddingAdapter = build_embedding_adapter(embed_cfg)

    existing = load_dense_index(repo_root, cfg) or DenseIndex(dim=int(cfg.dim), vectors={}, hashes={}, provider=cfg.provider, model=cfg.model)

    # Prepare batch of changed chunks
    to_embed: List[str] = []
    ids: List[str] = []
    for cid, text in chunks.items():
        if skip_if_kind_summary and skip_if_kind_summary.get(cid, False):
            continue
        h = sha256_text(text or "")
        if existing.hashes.get(cid) == h and cid in existing.vectors:
            continue
        ids.append(cid)
        to_embed.append(text or "")

    if ids:
        res = adapter.embed_texts(to_embed)
        # Ensure dim
        existing.dim = int(res.dim or existing.dim)
        for cid, vec in zip(ids, res.vectors):
            if isinstance(vec, list) and len(vec) == existing.dim:
                existing.vectors[cid] = [float(x) for x in vec]
                existing.hashes[cid] = sha256_text(chunks.get(cid, "") or "")

    # Remove stale chunks
    stale = [cid for cid in list(existing.vectors.keys()) if cid not in chunks]
    for cid in stale:
        existing.vectors.pop(cid, None)
        existing.hashes.pop(cid, None)

    path = save_dense_index(repo_root, cfg, existing)

    # Optional ANN cache (best-effort; offline-safe fallback)
    try:
        build_or_update_ann_cache(repo_root, cfg, existing)
    except Exception:
        pass

    return existing, path


def dense_retrieve(repo_root: Path, cfg: DenseIndexConfig, idx: DenseIndex, query_vec: List[float], *, topk: int = 24) -> List[Tuple[str, float]]:
    """Dense retrieval.

    If cfg.backend is hnswlib/faiss and cache exists + dependency installed, use ANN.
    Otherwise fall back to O(N) cosine scan.
    """
    ann = try_ann_retrieve(repo_root, cfg, idx, query_vec, topk=topk)
    if ann is not None:
        return ann

    scored: List[Tuple[str, float]] = []
    for cid, vec in idx.vectors.items():
        scored.append((cid, float(_cosine(query_vec, vec))))
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    return scored[: max(1, int(topk))]
