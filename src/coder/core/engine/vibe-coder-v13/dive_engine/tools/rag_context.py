"""RAG context integration for Dive Engine.

Goal
----
Provide an *offline-first* way to attach grounded context to a Dive Engine run
using the v13-rag engine.

Design constraints
------------------
- No heavy dependencies.
- Must not fail the run if the KB is missing.
- Must emit artifacts suitable for EvidencePack (E3).

Artifacts
---------
- rag_context.md: concatenated retrieved context
- rag_sources.json: ranked evidence list with chunk ids + doc ids
- rag_query.json: query settings + techniques used
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from utils.yaml_lite import load_yaml_file


def build_rag_context(
    *,
    repo_root: Path,
    output_dir: Path,
    prompt: str,
    spec_path: Optional[str] = None,
    max_context_chars: int = 8000,
) -> Tuple[Optional[Path], Dict[str, Path]]:
    """Build a RAG context file (if KB exists).

    Returns
    - (context_path | None, artifacts)
    """

    repo_root = Path(repo_root).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Late imports to keep startup light.
    try:
        from rag.engine import AdvancedRAG  # type: ignore
    except Exception:
        return None, {}

    kb_path = repo_root / ".vibe" / "kb" / "v13_rag_v2.json"
    if not kb_path.exists():
        # No KB yet → do not block the run.
        return None, {}

    rag = AdvancedRAG(str(repo_root))

    # Load optional YAML spec for settings.
    settings: Dict[str, Any] = {}
    if spec_path:
        spec = load_yaml_file(str((repo_root / spec_path).resolve() if not Path(spec_path).is_absolute() else spec_path))
        settings = dict(spec.get("settings") or {})

    q_kwargs: Dict[str, Any] = {}
    # Map known settings keys -> query kwargs (safe defaults).
    for k in [
        "enable_graphrag",
        "enable_raptor",
        "enable_crag",
        "crag_max_passes",
        "graphrag_expand_k",
        "raptor_summary_k",
        "enable_dense",
        "dense_backend",
        "fusion",
        "enable_rerank",
        "rerank",
    ]:
        if k in settings:
            q_kwargs[k] = settings[k]

    # Flatten nested sections
    dense = settings.get("dense") if isinstance(settings.get("dense"), dict) else {}
    fusion = settings.get("fusion") if isinstance(settings.get("fusion"), dict) else {}
    rerank = settings.get("rerank") if isinstance(settings.get("rerank"), dict) else {}

    if dense:
        q_kwargs.setdefault("dense_backend", settings.get("dense_backend", "scan"))
    if fusion:
        q_kwargs.setdefault("fusion_mode", fusion.get("mode", "rrf"))
        q_kwargs.setdefault("fusion_rrf_k", fusion.get("rrf_k", 60))
        q_kwargs.setdefault("fusion_w_bm25", fusion.get("w_bm25", 1.0))
        q_kwargs.setdefault("fusion_w_dense", fusion.get("w_dense", 1.0))
    if rerank:
        q_kwargs.setdefault("rerank_provider", rerank.get("provider", "stub"))
        q_kwargs.setdefault("rerank_model", rerank.get("model", "noop"))
        q_kwargs.setdefault("rerank_topk", rerank.get("topk", 12))

    try:
        res = rag.query(
            prompt,
            max_context_chars=int(max_context_chars),
            **q_kwargs,
        )
    except Exception:
        return None, {}

    context_text = str(res.get("context") or "").strip()
    if not context_text:
        return None, {}

    ctx_path = output_dir / "rag_context.md"
    src_path = output_dir / "rag_sources.json"
    qry_path = output_dir / "rag_query.json"

    ctx_path.write_text(context_text + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(res.get("sources") or [], indent=2, ensure_ascii=False), encoding="utf-8")
    qry_path.write_text(json.dumps({k: res.get(k) for k in [
        "queries",
        "techniques_used",
        "latency_ms",
        "matched_chunks",
        "fusion_mode",
        "dense_candidates",
        "summary_hits",
        "corrective_passes",
    ]}, indent=2, ensure_ascii=False), encoding="utf-8")

    artifacts = {
        "rag_context": ctx_path,
        "rag_sources": src_path,
        "rag_query": qry_path,
    }
    return ctx_path, artifacts
