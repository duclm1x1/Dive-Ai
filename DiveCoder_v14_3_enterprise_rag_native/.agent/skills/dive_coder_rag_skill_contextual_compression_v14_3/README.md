# Dive Coder — RAG Skill: Contextual Compression (v14.3)

## Purpose
Keep retrieval grounded while respecting a strict prompt budget.

## Current state (v14.3)
- The engine already enforces a **grounding cap** via `max_context_chars` during query.
- No LLM-based compression is forced (offline-first).

## Recommended implementation (production adapter)
Add a compression step that runs *after retrieval* and *before* context assembly.

### 1) Offline-safe extractive compressor
Algorithm:
- For each retrieved chunk: split into sentences
- Score sentences by overlap with query tokens
- Keep top-N sentences + 1 neighbor sentence on each side
- Stop when `max_context_chars` is reached

Where to hook:
- In `.shared/vibe-coder-v13/rag/engine_v2.py` during context assembly.

### 2) Optional abstractive compressor (LLM)
Add adapter `rag.adapters.compression`:
- `provider=llm` (uses Dive UnifiedLLMGateway)
- fallback to extractive when no provider configured

## Acceptance criteria
- Deterministic output in offline mode
- Emits a trace explaining which sentences were kept
- Never exceeds `max_context_chars`
