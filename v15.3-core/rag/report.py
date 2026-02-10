from __future__ import annotations

"""V13 RAG eval → report + claims ledger + EvidencePack (E3).

This module is intentionally offline-first and deterministic.

Artifacts
- Report JSON: retrieval-oriented metrics per case
- Claims ledger (E2): machine-verifiable claims about artifacts
- EvidencePack manifest (E3 bundle): hashes + paths for run artifacts
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.claims import Claim, ClaimsLedger, write_claims_ledger
from evidencepack.runtime import collect_run_evidencepack
from utils.yaml_lite import load_yaml_file

from rag.engine_v2 import AdvancedRAGv2


@dataclass
class RagEvalCaseResult:
    id: str
    query: str
    ok: bool
    reason: str
    matched_sources: List[str]
    matched_snippet: str
    latency_ms: int
    techniques_used: List[str]
    corrective_passes: int
    summary_hits: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "ok": self.ok,
            "reason": self.reason,
            "matched_sources": self.matched_sources,
            "matched_snippet": self.matched_snippet,
            "latency_ms": self.latency_ms,
            "techniques_used": self.techniques_used,
            "corrective_passes": int(self.corrective_passes),
            "summary_hits": int(self.summary_hits),
        }


def _write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _load_sources_from_spec(repo_root: Path, spec_path: str) -> List[Dict[str, Any]]:
    spec = load_yaml_file(spec_path) or {}
    sources = spec.get("sources") or spec.get("kb") or []
    if not isinstance(sources, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for s in sources:
        if not isinstance(s, dict):
            continue
        out = dict(s)
        # If path is relative, anchor to repo_root
        p = out.get("path")
        if isinstance(p, str) and p.strip():
            pp = Path(p).expanduser()
            if not pp.is_absolute():
                out["path"] = str((repo_root / pp).resolve())
        normalized.append(out)
    return normalized


def run_rag_eval(
    *,
    repo_root: str,
    spec_path: str,
    eval_path: str,
    out_report_path: Optional[str] = None,
    out_claims_path: Optional[str] = None,
    out_evidencepack_path: Optional[str] = None,
    max_context_chars: int = 6000,
) -> Dict[str, str]:
    """Run end-to-end RAG eval (ingest → query cases → artifacts).

    Returns paths to generated artifacts.
    """

    root = Path(repo_root).resolve()
    report_p = Path(out_report_path) if out_report_path else (root / ".vibe" / "reports" / "v13_rag_eval.json")
    claims_p = Path(out_claims_path) if out_claims_path else (root / ".vibe" / "reports" / "v13_rag_eval.claims.json")

    ev = load_yaml_file(eval_path) or {}
    cases = ev.get("cases") or []
    if not isinstance(cases, list):
        cases = []

    # Ingest
    rag = AdvancedRAGv2(str(root))
    sources = _load_sources_from_spec(root, spec_path)
    kb_path = rag.ingest(sources)

    results: List[RagEvalCaseResult] = []
    passed = 0

    for i, c in enumerate(cases):
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id") or f"case-{i+1}")
        q = str(c.get("query") or "").strip()
        expect = c.get("expect") or {}
        if not isinstance(expect, dict):
            expect = {}

        # Backward compatible schema:
        # - New: expect: {context_contains: [...], sources_contains: [...]}
        # - Legacy: expect_context_contains / expect_sources_contain (top-level)
        exp_ctx_contains = (
            expect.get("context_contains")
            or c.get("expect_context_contains")
            or []
        )
        exp_src_contains = (
            expect.get("sources_contains")
            or c.get("expect_sources_contain")
            or c.get("expect_sources_contains")
            or []
        )
        if isinstance(exp_ctx_contains, str):
            exp_ctx_contains = [exp_ctx_contains]
        if isinstance(exp_src_contains, str):
            exp_src_contains = [exp_src_contains]

        t0 = time.time()
        r = rag.query(q, limit=int(c.get("topk") or 8), max_context_chars=max_context_chars)
        latency_ms = int((time.time() - t0) * 1000)

        ctx = str(r.get("context") or "")
        srcs = r.get("sources") or []
        src_ids: List[str] = []
        for s in srcs:
            if isinstance(s, dict):
                src_ids.append(str(s.get("source") or s.get("doc_id") or ""))

        ok = True
        reason = "OK"

        for needle in exp_ctx_contains:
            if needle and needle not in ctx:
                ok = False
                reason = f"MISSING_CONTEXT_SUBSTRING: {needle}"
                break

        if ok:
            for needle in exp_src_contains:
                if needle and all(needle not in sid for sid in src_ids):
                    ok = False
                    reason = f"MISSING_SOURCE_MATCH: {needle}"
                    break

        if ok:
            passed += 1

        results.append(
            RagEvalCaseResult(
                id=cid,
                query=q,
                ok=ok,
                reason=reason,
                matched_sources=src_ids,
                matched_snippet=ctx[:280],
                latency_ms=latency_ms,
                techniques_used=[str(x) for x in (r.get("techniques_used") or []) if isinstance(x, (str, int))],
                corrective_passes=int(r.get("corrective_passes") or 0),
                summary_hits=int(r.get("summary_hits") or 0),
            )
        )

    report_obj: Dict[str, Any] = {
        "version": "v13-rag-eval.v1",
        "ts": int(time.time()),
        "spec": str(spec_path),
        "eval": str(eval_path),
        "kb_path": str(kb_path),
        "summary": {
            "total_cases": len(results),
            "passed": passed,
            "pass_rate": (float(passed) / float(max(1, len(results)))),
        },
        "cases": [r.to_dict() for r in results],
    }

    _write_json(report_p, report_obj)

    # Claims (E2): machine-verifiable artifacts
    claims = ClaimsLedger(
        version="v13",
        run_id="v13-rag-eval",
        claims=[
            Claim(
                claim="RAG KB ingested successfully",
                evidence_level="E2",
                tool="v13-rag",
                artifact=str(kb_path),
                meta={"spec": str(spec_path)},
            ),
            Claim(
                claim="RAG eval report generated",
                evidence_level="E2",
                tool="v13-rag",
                artifact=str(report_p),
                meta={"eval": str(eval_path)},
            ),
        ],
    )
    write_claims_ledger(str(root), claims, str(claims_p))

    # EvidencePack (E3 bundle)
    pack_id = f"ep-v13-rag-eval-{int(time.time())}"
    ep_out = (
        Path(out_evidencepack_path)
        if out_evidencepack_path
        else (root / ".vibe" / "evidence" / f"{pack_id}.evidencepack.json")
    )

    ep_path = collect_run_evidencepack(
        repo_root=str(root),
        pack_id=pack_id,
        report_path=str(report_p),
        claims_path=str(claims_p),
        out_path=str(ep_out),
    )

    return {
        "kb": str(kb_path),
        "report": str(report_p),
        "claims": str(claims_p),
        "evidencepack": str(ep_path),
    }
