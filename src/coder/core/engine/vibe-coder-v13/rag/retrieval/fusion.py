from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class FusionConfig:
    mode: str = "rrf"  # rrf | weighted | none
    rrf_k: int = 60
    # weights only used for weighted mode
    w_bm25: float = 1.0
    w_dense: float = 1.0


def rrf_fusion(
    ranked_lists: List[List[Tuple[str, float]]],
    *,
    k: int = 60,
    limit: int | None = None,
) -> List[Tuple[str, float]]:
    """Reciprocal Rank Fusion.

    Input: list of ranked lists [(doc_id, score), ...] where order implies rank.
    Output: fused ranking with RRF score.
    """
    scores: Dict[str, float] = {}
    for lst in ranked_lists:
        for rank, (cid, _) in enumerate(lst, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / float(k + rank)
    out = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit is not None:
        out = out[: max(1, int(limit))]
    return out


def weighted_fusion(
    bm25: Dict[str, float],
    dense: Dict[str, float],
    *,
    w_bm25: float = 1.0,
    w_dense: float = 1.0,
    limit: int | None = None,
) -> List[Tuple[str, float]]:
    scores: Dict[str, float] = {}
    for cid, s in bm25.items():
        scores[cid] = scores.get(cid, 0.0) + float(w_bm25) * float(s)
    for cid, s in dense.items():
        scores[cid] = scores.get(cid, 0.0) + float(w_dense) * float(s)
    out = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit is not None:
        out = out[: max(1, int(limit))]
    return out
