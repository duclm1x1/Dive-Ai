_# CAC - Context-Aware Compression Engine

**Version:** 2.0 (Upgraded from RAG Skill)
**Status:** Active

## 1. Overview

The Context-Aware Compression (CAC) Engine is an advanced system designed to intelligently reduce the size of the context provided to language models without losing critical information. This upgrade to the previous RAG skill focuses on semantic understanding, compressing the context in a way that is specifically tailored to the current query or task. This results in faster inference, lower computational costs, and improved performance on context-heavy tasks.

## 2. Core Functionality

- **Semantic Analysis:** Deeply analyzes the user's query and the source documents to identify the most relevant pieces of information.
- **Query-Guided Compression:** Instead of generic compression, the engine selectively extracts and summarizes information that is directly relevant to answering the user's query.
- **Abstractive Summarization:** Generates concise, abstractive summaries of long documents, capturing the key ideas in a compact form.
- **Lossless Compression:** For structured data and code, it uses lossless compression techniques to reduce size while preserving all information perfectly.

## 3. Integration with Dive Engine

CAC is an always-on pre-processing step in the Dive Engine. Before any large context is sent to a core language model, it is first passed through the CAC Engine. The engine returns a compressed, contextually-rich prompt that allows the model to perform at its best.

## 4. Key Files

- `src/main.py`: The core CAC engine.
- `src/semantic_analyzer.py`: The query and document analysis module.
- `src/compressor.py`: The core compression and summarization logic.
- `tests/test_cac.py`: Test suite for the CAC engine.
- `examples/large_document_qa.py`: Example of using CAC to answer a question from a large PDF document.
_
