# RAG Techniques Catalog (2025) — Dive Coder / v13-rag

Legend:
- ✅ implemented (in v13-rag v2)
- 🧩 adapter/hook planned (add via `rag.adapters.*`)
- 🧪 planned / future work (needs new subsystems)

---

## Foundational RAG
1. Simple RAG — ✅
   - Ingest → retrieve top chunks → return grounded context
2. RAG from CSV — ✅
   - Ingest CSV (dependency-free) → one row per chunk (`key: value` rendering)
3. Reliable RAG — ✅ (governance-first)
   - Claims ledger + EvidencePack; retrieval determinism
4. Choose Chunk Size — ✅
   - `chunk_chars` + `chunk_overlap_chars`
5. Proposition Chunking — ✅
   - Offline deterministic: sentence/bullet → chunk (adapter upgrade later)

## Query Enhancement
6. Query Transformations (rewrite / step-back / decomposition) — ✅ (heuristic)
7. HyDE — 🧩
   - Adapter: LLM-generated hypothetical document → dense retrieval
8. HyPE — 🧪
   - Precompute prompt embeddings

## Context & Content Enrichment
9. Contextual Chunk Headers — 🧩
10. Relevant Segment Extraction (RSE) — 🧩
11. Context Enrichment (neighbors) — 🧩
12. Semantic Chunking — 🧩
13. Contextual Compression — 🧩
14. Doc Augmentation (QG) — 🧩

## Advanced Retrieval
15. Fusion Retrieval (keyword + vector) — ✅ (offline-first, provider adapters)
    - BM25 + optional dense retrieval + fusion (RRF/weighted/none).
    - Dense adapters:
      - ✅ `stub_hash` (deterministic offline)
      - 🧩 `openai` (requires `openai`)
      - 🧩 `sentence_transformers` (requires `sentence-transformers`)
16. Intelligent Reranking — ✅ (offline-first, provider adapters)
    - Always-on overlap rerank (offline) + optional rerank adapters:
      - ✅ `stub` (no-op)
      - 🧩 `cross_encoder` (requires `sentence-transformers`)
      - 🧩 `llm_judge` (uses Dive `UnifiedLLMGateway`)
17. Multi-faceted Filtering — 🧩
18. Hierarchical Indices — ✅ (RAPTOR-style summaries)
19. Ensemble Retrieval — 🧩
20. Dartboard Retrieval — 🧪
21. Multi-modal Retrieval — 🧪

## Iterative & Adaptive
22. Feedback Loops — 🧪
23. Adaptive Retrieval Routing — 🧪
24. Iterative Retrieval — 🧩

## Evaluation
25. DeepEval-style metrics — ✅ (retrieval eval) / 🧩 (LLM-judge scoring via rerank adapter)
26. GroUSE-style evaluation — 🧩

## Explainability
27. Explainable Retrieval — ✅
    - v2 returns ranked sources + scores + matched context

## Advanced Architectures
28. Agentic RAG — 🧩
29. GraphRAG — ✅ (offline heuristic term graph)
30. Knowledge Graph integration — 🧪
31. Microsoft GraphRAG — 🧪
32. RAPTOR — ✅ (offline extractive summaries)
33. Self-RAG — 🧪
34. CRAG — ✅ (1-pass corrective re-retrieval, offline heuristic)
35. Sophisticated controllable agent pipeline — 🧪

---

## Where code lives

- Core engine: `.shared/vibe-coder-v13/rag/engine_v2.py`
- Legacy engine: `.shared/vibe-coder-v13/rag/engine_v1.py`
- Wrapper: `.shared/vibe-coder-v13/rag/engine.py`
- Eval + governance: `.shared/vibe-coder-v13/rag/report.py`

## Roadmap to “full SOTA”

Recommended next adapters:
1) ✅ `rag.adapters.embedding` (provider-based skeleton) → enable hybrid fusion
2) ✅ `rag.adapters.rerank` (provider-based skeleton) → boost precision
3) ✅ `rag.retrieval.fusion` (RRF/weighted) → robust hybrid ranking
4) `rag.active_retrieval` (CRAG) → re-retrieve + optional tool/web hooks
5) `rag.graph` / `rag.hierarchy` (GraphRAG / RAPTOR)
