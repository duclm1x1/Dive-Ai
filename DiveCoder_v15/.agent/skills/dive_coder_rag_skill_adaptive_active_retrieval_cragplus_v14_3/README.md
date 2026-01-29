# Dive Coder — RAG Skill: Adaptive Active Retrieval (CRAG+) (v14.3)

## What it is
CRAG+ extends Corrective RAG with:
- a *routing* decision (should we re-retrieve?)
- optional tool hooks (repo search, web search) when offline corpus insufficient
- multi-pass retrieval until confidence is high enough or budgets are exhausted

## Current state
Preset 1 implements **offline** CRAG:
- 1 corrective pass (`crag_max_passes: 1`)
- heuristic failure signal: low lexical overlap / low top score

## Production adapter plan
### 1) Routing heuristic (offline)
- if top BM25 < threshold OR context contains “no relevant info” patterns → reretrieve
- if query contains multi-hop cues (“compare”, “why”, “root cause”) → enable GraphRAG expansion

### 2) Tool hooks (optional)
Define interfaces:
- `rag.active_retrieval.tools.repo_search(query)`
- `rag.active_retrieval.tools.web_search(query)`

Default behavior:
- offline: only `repo_search` (grep-like) with tight timeouts
- online: allow `web_search` when explicitly enabled

### 3) Evidence requirements
Each corrective pass must emit:
- pass decision rationale
- newly added sources list
- delta in scores

## Acceptance criteria
- Can run fully offline
- Deterministic decisions in offline mode
- EvidencePack includes the per-pass trace
