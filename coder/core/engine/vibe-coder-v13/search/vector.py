from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


def _stable_hash(s: str) -> int:
    # Deterministic 32-bit FNV-1a
    h = 2166136261
    for ch in s.encode('utf-8', errors='ignore'):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text or '')]


@dataclass
class VectorResult:
    path: str
    score: float
    snippet: str = ''


def embed_text(text: str, dim: int = 256) -> List[float]:
    """Simple hashing-vector embedding (bag-of-tokens), L2-normalized.

    This is NOT an LLM embedding; it's deterministic, offline, fast, and good enough
    to approximate semantic-ish retrieval across code/docs.
    """
    v = [0.0] * int(dim)
    toks = tokenize(text)
    if not toks:
        return v
    for t in toks:
        h = _stable_hash(t)
        idx = h % dim
        sign = -1.0 if (h >> 31) & 1 else 1.0
        v[idx] += sign
    # L2 normalize
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    return float(sum(a[i] * b[i] for i in range(n)))


def rank(query: str, corpus: Iterable[Tuple[str, str]], top_k: int = 10, dim: int = 256) -> List[VectorResult]:
    """Rank (path, text) by cosine similarity to query."""
    qv = embed_text(query, dim=dim)
    out: List[VectorResult] = []
    for path, text in corpus:
        tv = embed_text(text, dim=dim)
        out.append(VectorResult(path=path, score=cosine(qv, tv)))
    out.sort(key=lambda r: r.score, reverse=True)
    return out[: int(top_k)]
