# Dive Coder — RAG Enterprise Skill (v14.3)

## Summary

This skill folder is versioned (per Dive Coder convention) and maps to an **offline-first, enterprise-ready RAG** pipeline built on **v13-rag v2**:

- Incremental indexing + hash cache (fast re-ingest)
- BM25 lexical retrieval (no heavy deps)
- Query enhancement (offline-safe)
- Overlap rerank (lightweight reranker)
- Grounding cap (`max_context_chars`) to control prompt budget
- Governance outputs: **eval report JSON + claims ledger (E2) + EvidencePack (E3)**

This skill is designed to run in CI / air-gapped environments.

Preset 1 (default) implements these **offline heuristic SOTA** components:
- GraphRAG (term graph expansion)
- RAPTOR (doc-level extractive summaries → child chunk boost)
- CRAG (1-pass corrective re-retrieval)

Additional offline upgrades in v14.3:
- CSV ingestion (dependency-free): 1 row = 1 chunk
- Proposition chunking (deterministic): sentence/bullet = chunk
- Dive Engine integration hook: `enable_rag_context=True` attaches retrieved context to orchestrated runs

Dense embeddings + cross-encoder/LLM rerank are **adapter-based**. This preset ships a production-style **adapter skeleton** (offline stubs) and wiring in the engine + CLI.

---

## CLI (Dive/V13)

Run from repo root.

```bash
export PYTHONPATH="$PWD/.shared/vibe-coder-v13:$PYTHONPATH"
```

### 1) Ingest (build KB)

Using spec:

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest \
  --repo . \
  --spec .vibe/inputs/v13/rag_spec.yml
```

**Enterprise preset (native deps enabled):**

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest \
  --repo . \
  --spec .vibe/inputs/v13/rag_spec_enterprise_native.yml
```

Or using inline JSON sources:

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest \
  --repo . \
  --sources '[{"source":"doc:1","type":"text","content":"hello"}]'
```

### 2) Query

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query \
  --repo . \
  --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "How do I run preflight?" \
  --limit 6 \
  --max-context-chars 8000
```

Optional toggles:

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . \
  --prompt "..." --preset 1 --graphrag --raptor --crag
```


### 2.1) Dense + fusion + rerank (optional)

Dense retrieval builds a separate index file under `.vibe/kb/` during ingest. Default provider is **offline stub**.

Enable dense index build:
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . --spec .vibe/inputs/v13/rag_spec.yml --dense
```

Query with dense + fusion (RRF):
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --dense --fusion rrf
```

Enable rerank adapter (stub/no-op by default):
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --rerank --rerank-provider stub
```

### Real providers (optional)

OpenAI embeddings (requires `pip install openai`):

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --dense --dense-provider openai --dense-model text-embedding-3-small
```

SentenceTransformers embeddings (requires `pip install sentence-transformers`):

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --dense --dense-provider sentence_transformers --dense-model all-MiniLM-L6-v2
```

Cross-encoder rerank (requires `pip install sentence-transformers`):

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --rerank --rerank-provider cross_encoder --rerank-model cross-encoder/ms-marco-MiniLM-L-6-v2
```

LLM-judge rerank (requires gateway configured + `pip install openai`):

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --rerank --rerank-provider llm_judge --rerank-model gpt-4.1-mini
```

Provider adapters live under:
- `.shared/vibe-coder-v13/rag/adapters/`
- `.shared/vibe-coder-v13/rag/adapters/providers/`

### 3) Eval + Governance artifacts (E3 bundle)

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag eval \
  --repo . \
  --spec .vibe/inputs/v13/rag_spec.yml \
  --eval .vibe/inputs/v13/rag_eval.yml
```

Outputs:
- `.vibe/reports/v13_rag_eval.json`
- `.vibe/reports/v13_rag_eval.claims.json`
- `.vibe/evidence/ep-v13-rag-eval-<ts>.evidencepack.json`

---

## Extensibility (Adapters)

The v2 engine is **hybrid-ready**. To reach “full SOTA 2025” beyond offline heuristics, add adapters:

- Dense embeddings + true hybrid fusion (RRF/weighted)
- Cross-encoder / LLM reranker
- Stronger RAPTOR/GraphRAG/CRAG via richer indices + active retrieval hooks (tools/web)
- Self-RAG style routing (retrieve-or-not + verify)

See `TECHNIQUES.md` for the technique map.

## Dense ANN backend (enterprise)

Dense retrieval supports an optional ANN cache backend. This keeps the existing API/CLI the same, but accelerates retrieval for large KBs.

- `scan` (default): O(N) cosine scan, no extra deps.
- `hnswlib`: ANN via HNSW (requires `pip install hnswlib numpy`).
- `faiss`: ANN via FAISS (requires `pip install faiss-cpu numpy`).

CLI example (build cache during ingest, then query uses it automatically):

```bash
export PYTHONPATH="$PWD/.shared/vibe-coder-v13:$PYTHONPATH"

python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --dense --dense-provider openai --dense-model text-embedding-3-small \
  --dense-backend hnswlib

python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --dense --fusion rrf
```
