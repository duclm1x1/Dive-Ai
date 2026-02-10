from __future__ import annotations

"""LLM judge reranker (provider="llm_judge").

Offline-first contract
---------------------
This adapter is only constructed when the user explicitly enables it.
It depends on the UnifiedLLMGateway (Dive Engine) and (transitively) the
optional `openai` package used by the gateway.

Behavior
--------
The reranker asks the LLM to assign a relevance score [0, 1] for each
candidate chunk. The model must return JSON.

Fail-soft: if the model call fails or JSON parsing fails, we fall back to the
input order.
"""

import asyncio
import concurrent.futures
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from dive_engine.llm.gateway import UnifiedLLMGateway

from ..rerank import RerankCandidate, RerankConfig, RerankResult


def _safe_json_loads(s: str) -> Any:
    s = (s or "").strip()
    if not s:
        raise ValueError("empty")
    # Best-effort strip code fences
    if s.startswith("```"):
        s = s.strip("`")
        # remove optional language tag
        lines = s.splitlines()
        if lines and lines[0].isalpha():
            s = "\n".join(lines[1:])
    return json.loads(s)


def _extract_text_from_chat_completion(resp: Any) -> str:
    # Supports OpenAI-style objects and plain dicts.
    try:
        return str(resp.choices[0].message.content or "")
    except Exception:
        try:
            return str(resp["choices"][0]["message"]["content"])
        except Exception:
            return str(resp)


def _build_prompt(query: str, candidates: List[RerankCandidate]) -> str:
    items = []
    for c in candidates:
        txt = (c.text or "").strip()
        if len(txt) > 600:
            txt = txt[:600] + "…"
        items.append({"chunk_id": c.chunk_id, "text": txt})

    schema = {
        "scores": [
            {
                "chunk_id": "<string>",
                "score": 0.0,
            }
        ]
    }

    return (
        "You are a retrieval reranker. Given a query and candidate passages, "
        "assign relevance scores in [0,1]. Higher is more relevant. "
        "Return ONLY valid JSON matching this schema:\n"
        f"{json.dumps(schema)}\n\n"
        f"QUERY:\n{query}\n\n"
        f"CANDIDATES (JSON):\n{json.dumps(items, ensure_ascii=False)}\n"
    )


@dataclass
class LLMJudgeRerankAdapter:
    cfg: RerankConfig

    def __post_init__(self) -> None:
        self._gateway = UnifiedLLMGateway()

    async def _rerank_async(self, query: str, candidates: List[RerankCandidate]) -> List[Tuple[str, float]]:
        prompt = _build_prompt(query, candidates)
        model = (self.cfg.model or "gpt-4.1-mini").strip()
        resp = await self._gateway.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.0,
            max_tokens=800,
            stream=False,
        )
        text = _extract_text_from_chat_completion(resp)
        data = _safe_json_loads(text)
        scores = data.get("scores") if isinstance(data, dict) else None
        if not isinstance(scores, list):
            raise ValueError("missing scores")

        out: List[Tuple[str, float]] = []
        for row in scores:
            if not isinstance(row, dict):
                continue
            cid = str(row.get("chunk_id") or "").strip()
            try:
                sc = float(row.get("score"))
            except Exception:
                continue
            if cid:
                out.append((cid, max(0.0, min(1.0, sc))))
        return out

    def rerank(self, query: str, candidates: List[RerankCandidate]) -> RerankResult:
        cands = list(candidates or [])
        if not cands:
            return RerankResult(candidates=[], provider=self.cfg.provider, model=self.cfg.model)

        topk = max(0, int(self.cfg.topk or len(cands)))
        working = cands[: max(topk, min(len(cands), 32))]

        def _run_coroutine(coro):
            """Run coroutine from sync code.

            - If no running loop, use asyncio.run.
            - If already inside an event loop, run in a dedicated thread with a fresh loop.
            """
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(coro)

            def _thread_runner():
                return asyncio.run(coro)

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_thread_runner).result(timeout=60)

        try:
            pairs = _run_coroutine(self._rerank_async(query, working))
            score_map: Dict[str, float] = {cid: sc for cid, sc in pairs}
            for c in working:
                if c.chunk_id in score_map:
                    c.score = float(score_map[c.chunk_id])
            working.sort(key=lambda x: float(x.score), reverse=True)
            return RerankResult(candidates=working[:topk], provider=self.cfg.provider, model=self.cfg.model)
        except Exception:
            # Fail-soft
            return RerankResult(candidates=working[:topk], provider=self.cfg.provider, model=self.cfg.model)
