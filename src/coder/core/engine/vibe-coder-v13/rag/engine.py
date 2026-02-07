from __future__ import annotations

"""RAG engine wrapper.

- AdvancedRAG defaults to v2 (enterprise-ready, offline-first).
- AdvancedRAGv1 is kept for compatibility.
"""

from rag.engine_v1 import AdvancedRAGv1
from rag.engine_v2 import AdvancedRAGv2


# Default engine
AdvancedRAG = AdvancedRAGv2

__all__ = [
    "AdvancedRAG",
    "AdvancedRAGv1",
    "AdvancedRAGv2",
]
