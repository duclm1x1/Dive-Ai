"""Provider-specific adapters.

Keep provider SDK imports inside provider modules or inside constructors.

Preferred modules
- openai_embeddings.py
- sentence_transformers_embeddings.py
- cross_encoder.py
- llm_judge_rerank.py

This package may contain older experimental modules; treat them as deprecated
unless referenced by the factories in `rag.adapters.*`.
"""
