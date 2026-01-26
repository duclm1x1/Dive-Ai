"""Dive Engine tools.

Small utility modules that integrate optional capabilities (e.g., RAG) into
Dive Engine runs without introducing heavy dependencies.
"""

from __future__ import annotations

__all__ = [
    "build_rag_context",
]

from dive_engine.tools.rag_context import build_rag_context  # noqa: E402
