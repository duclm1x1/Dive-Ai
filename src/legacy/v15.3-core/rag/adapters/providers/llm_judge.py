from __future__ import annotations

"""LLM judge reranker (skeleton).

By default we keep this as a no-op unless user explicitly enables provider=llm.

In production you typically:
- construct a prompt that asks for relevance ranking or scalar scores
- enforce JSON output
- apply robust parsing + retry

This skeleton intentionally avoids hard dependency on any specific LLM client.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..rerank import RerankCandidate


@dataclass
class LLMJudgeRerankAdapter:
    model: Optional[str] = None
    options: Dict[str, Any] = None

    def rerank(self, query: str, candidates: List[RerankCandidate], *, topk: int) -> List[RerankCandidate]:
        # Skeleton behavior: return original order.
        # Implementations should call UnifiedLLMGateway and produce scores.
        return (candidates or [])[: max(0, int(topk))]
