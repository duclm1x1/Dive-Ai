from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from utils.hash_utils import sha256_text


@dataclass
class EmbeddingConfig:
    """Embedding provider configuration.

    provider: identifier string, e.g. "stub_hash", "openai", "local_sentence_transformers"
    model: provider model name
    dim: output vector dimension (for stub providers)
    batch_size: preferred batch size
    """

    provider: str = "stub_hash"
    model: str = "hash-256"
    dim: int = 256
    batch_size: int = 32
    extra: Dict[str, Any] | None = None


@dataclass
class EmbeddingResult:
    vectors: List[List[float]]
    dim: int
    provider: str
    model: str


class EmbeddingAdapter(Protocol):
    """Abstract embedding adapter."""

    cfg: EmbeddingConfig

    def embed_texts(self, texts: List[str]) -> EmbeddingResult:
        ...

    def embed_query(self, text: str) -> List[float]:
        ...


class HashEmbeddingAdapter:
    """Deterministic, offline-first embedding adapter (NOT semantic)."""

    def __init__(self, cfg: Optional[EmbeddingConfig] = None):
        self.cfg = cfg or EmbeddingConfig()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text]).vectors[0]

    def embed_texts(self, texts: List[str]) -> EmbeddingResult:
        dim = int(self.cfg.dim or 256)
        out: List[List[float]] = []
        for t in texts:
            vec = [0.0] * dim
            s = (t or "").strip()
            if not s:
                out.append(vec)
                continue
            toks = [x for x in s.lower().split() if x]
            shingles = toks if len(toks) <= 3 else [" ".join(toks[i : i + 3]) for i in range(0, len(toks) - 2)]
            for sh in shingles[:512]:
                h = sha256_text(sh)
                idx = int(h[:8], 16) % dim
                val = (int(h[8:12], 16) % 1000) / 1000.0
                vec[idx] += val
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            out.append([v / norm for v in vec])
        return EmbeddingResult(vectors=out, dim=dim, provider=self.cfg.provider, model=self.cfg.model)


def build_embedding_adapter(cfg: Optional[EmbeddingConfig]) -> EmbeddingAdapter:
    """Factory to build an embedding adapter.

    Keep imports lazy and fail-soft.
    """
    cfg = cfg or EmbeddingConfig()
    provider = (cfg.provider or "stub_hash").strip().lower()

    if provider in {"stub", "stub_hash", "hash", "offline"}:
        return HashEmbeddingAdapter(cfg)

    if provider in {"openai", "openai_embeddings"}:
        from .providers.openai_embeddings import OpenAIEmbeddingAdapter

        return OpenAIEmbeddingAdapter(cfg)

    if provider in {"sentence_transformers", "local_sentence_transformers", "st"}:
        from .providers.sentence_transformers_embeddings import SentenceTransformersEmbeddingAdapter

        return SentenceTransformersEmbeddingAdapter(cfg)

    return HashEmbeddingAdapter(cfg)
