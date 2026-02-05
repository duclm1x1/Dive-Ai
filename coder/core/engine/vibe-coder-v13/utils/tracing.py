from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, Iterator, List, Optional

from core.models import TraceSpan


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


@dataclass
class Tracer:
    spans: List[TraceSpan]

    def __init__(self) -> None:
        self.spans = []

    @contextmanager
    def span(self, name: str, meta: Optional[Dict[str, Any]] = None) -> Iterator[None]:
        started_at = _utc_iso()
        t0 = perf_counter()
        try:
            yield
        finally:
            t1 = perf_counter()
            finished_at = _utc_iso()
            dur_ms = int((t1 - t0) * 1000)
            self.spans.append(TraceSpan(
                name=name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=dur_ms,
                meta=meta or {},
            ))
