from __future__ import annotations

"""OpenAI embedding adapter (skeleton).

This module is intentionally import-light:
- If openai SDK is not installed, it will raise a clear error when instantiated.

You can wire API keys via environment variables expected by the provider SDK.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class OpenAIEmbeddingAdapter:
    model: Optional[str] = None
    dim: int = 1536
    options: Dict[str, Any] = None

    def __post_init__(self) -> None:
        # defer SDK import until adapter is used
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "OpenAIEmbeddingAdapter requires the 'openai' package. Install it or use provider=hash."
            ) from e

        self._client = OpenAI()
        if not self.model:
            # Do not assume model availability; user should set explicitly.
            self.model = "text-embedding-3-small"

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        texts = [str(t or "") for t in (texts or [])]
        if not texts:
            return []
        # Minimal call pattern (SDK-specific responses may vary between versions)
        resp = self._client.embeddings.create(model=str(self.model), input=texts)
        out: List[List[float]] = []
        for item in resp.data:
            out.append([float(x) for x in item.embedding])
        return out
