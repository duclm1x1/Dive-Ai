from __future__ import annotations

"""Local SentenceTransformers embeddings adapter (optional).

This is intended for enterprise/offline deployments where you can ship a local
embedding model (and are okay with the `sentence-transformers` dependency).

Import is lazy: core RAG remains dependency-free unless enabled.
"""

from dataclasses import dataclass
from typing import List

from ..embedding import EmbeddingConfig, EmbeddingResult


@dataclass
class SentenceTransformersEmbeddingAdapter:
    cfg: EmbeddingConfig

    def __post_init__(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "SentenceTransformersEmbeddingAdapter requires 'sentence-transformers'. Install it or use provider=stub_hash."
            ) from e

        model_name = (self.cfg.model or "").strip() or "all-MiniLM-L6-v2"
        self._model = SentenceTransformer(model_name)
        # Best-effort infer dim.
        try:  # pragma: no cover
            self.cfg.dim = int(self._model.get_sentence_embedding_dimension())
        except Exception:
            pass

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text]).vectors[0]

    def embed_texts(self, texts: List[str]) -> EmbeddingResult:
        texts = [str(t or "") for t in (texts or [])]
        if not texts:
            return EmbeddingResult(vectors=[], dim=int(self.cfg.dim or 0), provider=self.cfg.provider, model=self.cfg.model)

        # encode returns numpy array; convert to python floats.
        vecs = self._model.encode(texts, batch_size=int(self.cfg.batch_size or 32), normalize_embeddings=True)
        vectors: List[List[float]] = [list(map(float, row)) for row in vecs]
        dim = len(vectors[0]) if vectors else int(self.cfg.dim or 0)
        return EmbeddingResult(vectors=vectors, dim=dim, provider=self.cfg.provider, model=self.cfg.model)
