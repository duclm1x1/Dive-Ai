from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.hash_utils import sha256_text

# NOTE:
# - This module is best-effort and dependency-optional.
# - If hnswlib/faiss (and numpy) are not installed, we fall back to scan in dense_index.py.
# - Cache is rebuilt only when the dense index content hash changes.


def _dense_content_fingerprint(hashes: Dict[str, str]) -> str:
    """Stable fingerprint for (chunk_id -> content_hash) map."""
    items = sorted((str(k), str(v)) for k, v in (hashes or {}).items())
    return sha256_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")))


def _ann_paths(repo_root: Path, cfg: Any) -> Tuple[Path, Path]:
    kb = repo_root / ".vibe" / "kb"
    return kb / str(getattr(cfg, "ann_index_filename", "v13_rag_v2_dense.ann")), kb / str(getattr(cfg, "ann_meta_filename", "v13_rag_v2_dense.ann.meta.json"))


def build_or_update_ann_cache(repo_root: Path, cfg: Any, dense_idx: Any) -> Optional[str]:
    backend = str(getattr(cfg, "backend", "scan") or "scan").strip().lower()
    if backend in ("", "scan", "none", "off", "disabled"):
        return None

    ann_path, meta_path = _ann_paths(repo_root, cfg)
    ann_path.parent.mkdir(parents=True, exist_ok=True)

    fingerprint = _dense_content_fingerprint(getattr(dense_idx, "hashes", {}) or {})
    meta: Dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore")) or {}
        except Exception:
            meta = {}

    if meta.get("backend") == backend and meta.get("fingerprint") == fingerprint and ann_path.exists():
        # cache is fresh
        return str(ann_path)

    # rebuild
    if backend == "hnswlib":
        return _build_hnswlib(repo_root, cfg, dense_idx, ann_path, meta_path, fingerprint)
    if backend == "faiss":
        return _build_faiss(repo_root, cfg, dense_idx, ann_path, meta_path, fingerprint)

    # unknown backend -> do nothing
    return None


def try_ann_retrieve(
    repo_root: Path,
    cfg: Any,
    dense_idx: Any,
    query_vec: List[float],
    *,
    topk: int = 24,
) -> Optional[List[Tuple[str, float]]]:
    backend = str(getattr(cfg, "backend", "scan") or "scan").strip().lower()
    if backend in ("", "scan", "none", "off", "disabled"):
        return None

    ann_path, meta_path = _ann_paths(repo_root, cfg)
    if not ann_path.exists() or not meta_path.exists():
        return None

    # Ensure cache matches current dense index
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore")) or {}
    except Exception:
        return None
    if meta.get("backend") != backend:
        return None
    if meta.get("fingerprint") != _dense_content_fingerprint(getattr(dense_idx, "hashes", {}) or {}):
        return None

    if backend == "hnswlib":
        return _search_hnswlib(ann_path, meta, query_vec, topk=topk)
    if backend == "faiss":
        return _search_faiss(ann_path, meta, query_vec, topk=topk)
    return None


def _normalize(vec: List[float]) -> List[float]:
    s = 0.0
    for x in vec:
        s += float(x) * float(x)
    n = math.sqrt(s)
    if n <= 0:
        return [0.0 for _ in vec]
    return [float(x) / n for x in vec]


def _build_hnswlib(repo_root: Path, cfg: Any, dense_idx: Any, ann_path: Path, meta_path: Path, fingerprint: str) -> Optional[str]:
    try:
        import numpy as np  # type: ignore
        import hnswlib  # type: ignore
    except Exception:
        return None

    dim = int(getattr(dense_idx, "dim", getattr(cfg, "dim", 256)) or 256)
    vectors: Dict[str, List[float]] = getattr(dense_idx, "vectors", {}) or {}

    # labels are contiguous ints
    ids = sorted(vectors.keys())
    if not ids:
        return None

    data = np.zeros((len(ids), dim), dtype=np.float32)
    for i, cid in enumerate(ids):
        v = vectors.get(cid) or []
        if len(v) != dim:
            continue
        data[i] = np.array(_normalize(v), dtype=np.float32)

    index = hnswlib.Index(space="cosine", dim=dim)
    # conservative defaults; user can tune later via cfg if needed
    index.init_index(max_elements=len(ids), ef_construction=200, M=16)
    index.add_items(data, list(range(len(ids))))
    index.set_ef(max(64, int(getattr(cfg, "topk", 24)) * 4))

    index.save_index(str(ann_path))

    meta = {
        "version": "dense.ann.v1",
        "backend": "hnswlib",
        "dim": dim,
        "metric": "cosine",
        "fingerprint": fingerprint,
        "id_map": ids,  # label -> chunk_id
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(ann_path)


def _search_hnswlib(ann_path: Path, meta: Dict[str, Any], query_vec: List[float], *, topk: int = 24) -> Optional[List[Tuple[str, float]]]:
    try:
        import numpy as np  # type: ignore
        import hnswlib  # type: ignore
    except Exception:
        return None

    dim = int(meta.get("dim") or 256)
    ids: List[str] = meta.get("id_map") or []
    if not ids:
        return None

    index = hnswlib.Index(space="cosine", dim=dim)
    index.load_index(str(ann_path))
    index.set_ef(max(64, int(topk) * 4))

    q = np.array([_normalize(query_vec)], dtype=np.float32)
    labels, distances = index.knn_query(q, k=max(1, int(topk)))
    # cosine distance = 1 - cosine_similarity
    out: List[Tuple[str, float]] = []
    for lbl, dist in zip(labels[0], distances[0]):
        try:
            cid = ids[int(lbl)]
            score = 1.0 - float(dist)
            out.append((cid, score))
        except Exception:
            continue
    return out


def _build_faiss(repo_root: Path, cfg: Any, dense_idx: Any, ann_path: Path, meta_path: Path, fingerprint: str) -> Optional[str]:
    try:
        import numpy as np  # type: ignore
        import faiss  # type: ignore
    except Exception:
        return None

    dim = int(getattr(dense_idx, "dim", getattr(cfg, "dim", 256)) or 256)
    vectors: Dict[str, List[float]] = getattr(dense_idx, "vectors", {}) or {}
    ids = sorted(vectors.keys())
    if not ids:
        return None

    data = np.zeros((len(ids), dim), dtype="float32")
    for i, cid in enumerate(ids):
        v = vectors.get(cid) or []
        if len(v) != dim:
            continue
        data[i] = np.array(_normalize(v), dtype="float32")

    # HNSW index for inner product (cosine after normalization)
    idx = faiss.IndexHNSWFlat(dim, 32)
    idx.hnsw.efConstruction = 200
    idx.add(data)
    faiss.write_index(idx, str(ann_path))

    meta = {
        "version": "dense.ann.v1",
        "backend": "faiss",
        "dim": dim,
        "metric": "cosine_via_ip_normalized",
        "fingerprint": fingerprint,
        "id_map": ids,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(ann_path)


def _search_faiss(ann_path: Path, meta: Dict[str, Any], query_vec: List[float], *, topk: int = 24) -> Optional[List[Tuple[str, float]]]:
    try:
        import numpy as np  # type: ignore
        import faiss  # type: ignore
    except Exception:
        return None

    ids: List[str] = meta.get("id_map") or []
    if not ids:
        return None
    dim = int(meta.get("dim") or 256)

    idx = faiss.read_index(str(ann_path))
    q = np.array([_normalize(query_vec)], dtype="float32")
    scores, labels = idx.search(q, k=max(1, int(topk)))
    out: List[Tuple[str, float]] = []
    for lbl, sc in zip(labels[0], scores[0]):
        if int(lbl) < 0:
            continue
        try:
            cid = ids[int(lbl)]
            out.append((cid, float(sc)))
        except Exception:
            continue
    return out
