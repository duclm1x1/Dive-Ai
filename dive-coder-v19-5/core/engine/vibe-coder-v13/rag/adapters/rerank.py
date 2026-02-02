from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class RerankConfig:
    """Rerank provider configuration."""

    provider: str = "stub"
    model: str = "noop"
    topk: int = 12
    extra: Dict[str, Any] | None = None


@dataclass
class RerankCandidate:
    chunk_id: str
    text: str
    score: float
    meta: Dict[str, Any] | None = None


@dataclass
class RerankResult:
    candidates: List[RerankCandidate]
    provider: str
    model: str


class RerankAdapter(Protocol):
    cfg: RerankConfig
    def rerank(self, query: str, candidates: List[RerankCandidate]) -> RerankResult:
        ...


class StubRerankAdapter:
    """Offline-first reranker that returns candidates unchanged."""

    def __init__(self, cfg: Optional[RerankConfig] = None):
        self.cfg = cfg or RerankConfig()

    def rerank(self, query: str, candidates: List[RerankCandidate]) -> RerankResult:
        return RerankResult(candidates=list(candidates), provider=self.cfg.provider, model=self.cfg.model)


def build_rerank_adapter(cfg: Optional[RerankConfig]) -> RerankAdapter:
    cfg = cfg or RerankConfig()
    provider = (cfg.provider or "stub").strip().lower()

    if provider in {"stub", "noop", "offline"}:
        return StubRerankAdapter(cfg)

    if provider in {"cross_encoder", "cross-encoder", "ce"}:
        from .providers.cross_encoder import CrossEncoderRerankAdapter

        return CrossEncoderRerankAdapter(cfg)

    if provider in {"llm", "llm_judge", "llm-judge", "judge"}:
        from .providers.llm_judge_rerank import LLMJudgeRerankAdapter

        return LLMJudgeRerankAdapter(cfg)

    # Placeholder for real providers (wire later):
    # if provider == "cross_encoder":
    #     from .providers.cross_encoder import CrossEncoderRerankAdapter
    #     return CrossEncoderRerankAdapter(cfg)
    # if provider == "llm_judge":
    #     from .providers.llm_judge import LLMJudgeRerankAdapter
    #     return LLMJudgeRerankAdapter(cfg)

    return StubRerankAdapter(cfg)
