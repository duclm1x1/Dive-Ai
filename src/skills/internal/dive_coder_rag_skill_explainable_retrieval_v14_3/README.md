# Dive Coder — RAG Skill: Explainable Retrieval (v14.3)

## Why
Enterprise RAG needs a paper trail:
- why a chunk was retrieved
- what signals contributed to rank
- what claims are backed by which evidence

## Current state
v13-rag v2 already returns `sources` with:
- `chunk_id` / `doc_id` / `source` / `kind`
- rank scores (BM25 + fusion)
- matched terms set (BM25 lexical)

Governance outputs:
- claims ledger (E2)
- EvidencePack manifest (E3)

## Upgrade target
Add a `retrieval_trace` payload that can be packed into EvidencePack:
- per candidate: {bm25, dense, fusion, overlap_rerank, graphrag_boost, raptor_boost}
- top matched terms and their contributions
- any corrective pass decisions (CRAG)

## Hook points
- `.shared/vibe-coder-v13/rag/engine_v2.py` query pipeline
- `.shared/vibe-coder-v13/rag/report.py` include trace hashes in EvidencePack

## Minimal acceptance test
Given a query, the JSON trace must let a reviewer answer:
1) "Why is this chunk here?"
2) "What changed when CRAG re-retrieved?"
3) "Did the engine respect max_context_chars?"
