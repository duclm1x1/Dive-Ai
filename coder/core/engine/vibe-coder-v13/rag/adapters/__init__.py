"""RAG production adapter layer (offline-first).

This package defines stable interfaces for:
- Embedding providers (dense retrieval)
- Rerank providers (cross-encoder / LLM judge)

Design goals
- Optional: core engine must run without adapters.
- Offline-first: provide deterministic stub implementations.
- Provider-based: real integrations can be plugged in behind the same interfaces.

Nothing in core RAG v2 should import heavy deps at import-time.
Adapters should be imported lazily and fail-soft.
"""

from .embedding import (
    EmbeddingAdapter,
    EmbeddingConfig,
    EmbeddingResult,
    HashEmbeddingAdapter,
    build_embedding_adapter,
)
from .rerank import (
    RerankAdapter,
    RerankConfig,
    RerankCandidate,
    RerankResult,
    StubRerankAdapter,
    build_rerank_adapter,
)

__all__ = [
    "EmbeddingAdapter",
    "EmbeddingConfig",
    "EmbeddingResult",
    "HashEmbeddingAdapter",
    "build_embedding_adapter",
    "RerankAdapter",
    "RerankConfig",
    "RerankCandidate",
    "RerankResult",
    "StubRerankAdapter",
    "build_rerank_adapter",
]
