# Dive Coder — RAG Skill: CSV Q&A (v14.3)

## What it is
A lightweight pattern to turn CSV tables into a retrieval-friendly knowledge base.

Use cases:
- configuration matrices
- KPI exports
- feature flags / allowlists
- product catalogs

## What’s implemented (offline-first)
The v13-rag v2 ingest supports CSV chunking automatically when:
- `type: csv` in the source, **or**
- `path` ends with `.csv`

Chunking behavior:
- 1 data row = 1 chunk
- Rendering format: `col1: val1 | col2: val2 | ...`
- Offset is the row index (stable across re-ingest when the row order is stable)

## How to use
### Spec example
```yml
sources:
  - source: data:pricing
    type: csv
    path: data/pricing.csv
```

Then ingest normally:
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . --spec .vibe/inputs/v13/rag_spec.yml
```

## SOTA upgrade path
For true "table RAG":
- Add metadata-aware filtering (`rag.filters`) for columns
- Add a structured reranker (LLM judge or cross-encoder) for numeric comparison
- Add a row-to-proposition transformer for long cells
