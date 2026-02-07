---
name: dive-coder-rag-enterprise
description: "Enterprise RAG v2 (offline-first): incremental indexing, BM25 + hybrid hooks, GraphRAG/RAPTOR/CRAG adapters, eval + EvidencePack."
metadata: '{"version":"14.4.0","project":"Dive Coder","tags":["rag","bm25","hybrid","graphrag","raptor","crag","eval","evidencepack"],"offline_first":true}'
---

## What this skill does

- RAG v2 core: incremental ingest + hash cache, BM25 lexical retrieval, heuristic multi-query + step-back, overlap rerank, max context cap
- Advanced adapters (skeletons): GraphRAG / RAPTOR / CRAG pipelines (offline-first defaults)
- Governance outputs: report JSON, claims ledger (E2), EvidencePack (E3 bundle)

## CLI usage (repo root)

```bash
export PYTHONPATH="$PWD/.shared/vibe-coder-v13:${PYTHONPATH:-}"

# Build / update KB (skips unchanged docs)
python3 .shared/vibe-coder-v13/vibe.py rag ingest \
  --spec .vibe/inputs/v13/rag_spec.yml \
  --kb .vibe/kb

# Query
python3 .shared/vibe-coder-v13/vibe.py rag query \
  --kb .vibe/kb \
  --q "your question" \
  --max-context-chars 24000

# Eval (report + claims + evidencepack)
python3 .shared/vibe-coder-v13/vibe.py rag eval \
  --kb .vibe/kb \
  --eval .vibe/inputs/v13/rag_eval.yml \
  --out .vibe/reports/rag-eval.json \
  --evidencepack-out .vibe/evidencepacks
```

## Where to extend

- Dense embeddings + hybrid fusion: `.shared/vibe-coder-v13/rag/adapters/embedding/*`
- Cross-encoder / LLM rerank: `.shared/vibe-coder-v13/rag/adapters/rerank/*`
- GraphRAG/RAPTOR/CRAG: `.shared/vibe-coder-v13/rag/advanced/*`
