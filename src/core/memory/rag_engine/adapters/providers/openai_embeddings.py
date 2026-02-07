from __future__ import annotations

"""OpenAI embeddings adapter (optional).

Offline-first contract
---------------------
Core RAG must run without any heavy libs. This module is only imported when
provider is explicitly selected (e.g. `provider: openai`).

This adapter uses the official `openai` Python package if installed.
"""

from dataclasses import dataclass
from typing import List, Optional

from ..embedding import EmbeddingConfig, EmbeddingResult


@dataclass
class OpenAIEmbeddingAdapter:
    """Embedding adapter using OpenAI embeddings endpoint."""

    cfg: EmbeddingConfig

    def __post_init__(self) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "OpenAIEmbeddingAdapter requires the 'openai' package. Install it or use provider=stub_hash."
            ) from e

        self._client = OpenAI()
        # Do not assume model availability; users can override in cfg.model.
        if not (self.cfg.model or "").strip():
            self.cfg.model = "text-embedding-3-small"

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text]).vectors[0]

    def embed_texts(self, texts: List[str]) -> EmbeddingResult:
        texts = [str(t or "") for t in (texts or [])]
        if not texts:
            return EmbeddingResult(vectors=[], dim=int(self.cfg.dim or 0), provider=self.cfg.provider, model=self.cfg.model)

        resp = self._client.embeddings.create(model=str(self.cfg.model), input=texts)
        vectors: List[List[float]] = []
        for item in resp.data:
            vectors.append([float(x) for x in item.embedding])

        dim = len(vectors[0]) if vectors else int(self.cfg.dim or 0)
        return EmbeddingResult(vectors=vectors, dim=dim, provider=self.cfg.provider, model=self.cfg.model)
