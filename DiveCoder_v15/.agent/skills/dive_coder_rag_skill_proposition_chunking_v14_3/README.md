# Dive Coder — RAG Skill: Proposition Chunking (v14.3)

## What it is
"Proposition chunking" splits text into *atomic factual units* (typically single sentences/bullets). This tends to improve factual recall for:
- legal / compliance text
- policy and SOPs
- audit reports
- requirements/specs

## What’s implemented (offline-first)
The v13-rag v2 ingest supports a deterministic `chunk_strategy=proposition` mode:
- Each sentence/bullet is a chunk (no LLM)
- Min length filter uses `min_chunk_chars`
- Stable chunk ids `doc_id::off<offset>`

## How to use
### Ingest
Either pass it via code:
- `AdvancedRAGv2.ingest(..., chunk_strategy="proposition")`

Or wire it in your own spec runner by mapping:
- `settings.chunk_strategy: proposition`

### When not to use it
Avoid proposition chunking when:
- you rely on broader local context to interpret a sentence
- the corpus is very noisy (OCR artifacts) → prefer char windows + compression

## SOTA upgrade path (adapter)
To reach "true" proposition chunking (LLM-generated propositions + grading):
- Add an adapter `rag.adapters.propositionizer`:
  - offline fallback: current deterministic splitter
  - online/LLM mode: generate propositions + grade + store
