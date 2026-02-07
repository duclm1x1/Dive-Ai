from __future__ import annotations

"""Cross-encoder reranker adapter (optional).

This adapter is intentionally optional because transformer dependencies are
heavy. It is only imported when provider="cross_encoder".

Implementation notes
--------------------
We use sentence-transformers CrossEncoder if available.
"""

from dataclasses import dataclass
from typing import List

from ..rerank import RerankCandidate, RerankConfig, RerankResult


@dataclass
class CrossEncoderRerankAdapter:
    cfg: RerankConfig

    def __post_init__(self) -> None:
        try:
            from sentence_transformers import CrossEncoder  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "CrossEncoderRerankAdapter requires 'sentence-transformers'. Install it or use provider=stub."
            ) from e

        model_name = (self.cfg.model or "").strip() or "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self._ce = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[RerankCandidate]) -> RerankResult:
        cands = list(candidates or [])
        if not cands:
            return RerankResult(candidates=[], provider=self.cfg.provider, model=self.cfg.model)

        pairs = [(query, c.text) for c in cands]
        scores = self._ce.predict(pairs)
        for c, s in zip(cands, scores):
            try:
                c.score = float(s)
            except Exception:
                pass

        cands.sort(key=lambda x: float(x.score), reverse=True)
        topk = max(0, int(self.cfg.topk or len(cands)))
        return RerankResult(candidates=cands[:topk], provider=self.cfg.provider, model=self.cfg.model)
