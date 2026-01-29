# RAG native-deps profile (Dive Coder v14.2)

This repo ships an **offline-first** RAG engine that runs with **no heavy dependencies** by default.

If you are okay with **Python + native dependencies** (enterprise profile), you can enable:

- Dense embeddings (SentenceTransformers or OpenAI)
- ANN backend (HNSWlib or FAISS)
- Cross-encoder reranking (SentenceTransformers)
- Optional LLM-judge reranking (via Dive UnifiedLLMGateway)

## Install

Recommended (offline/local embeddings + HNSW ANN + cross-encoder rerank):

```bash
pip install -U numpy hnswlib sentence-transformers
```

Optional (OpenAI embeddings / LLM-judge rerank):

```bash
pip install -U openai
```

Optional (FAISS ANN backend):

```bash
pip install -U faiss-cpu
```

## Use the enterprise spec

```bash
export PYTHONPATH="$PWD/.shared/vibe-coder-v13:$PYTHONPATH"

python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . \
  --spec .vibe/inputs/v13/rag_spec_enterprise_native.yml

python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . \
  --spec .vibe/inputs/v13/rag_spec_enterprise_native.yml \
  --prompt "..."
```

## Backend notes

- If native deps are missing, the engine **falls back automatically**:
  - ANN backend falls back to `scan`
  - rerank adapters fall back to `stub`

This keeps CI and air-gapped runs stable.
