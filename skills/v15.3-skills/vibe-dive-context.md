---
name: Dive Context
id: dive-context
version: 15.0.0
category: core
triggers:
  keywords:
    - context
    - retrieve
    - rag
    - evidence
    - citations
    - verify
    - grounded
    - trace
    - observability
routing_hints:
  preferred_mode: deep
  tags:
    - core
    - evidence
    - retrieval
    - trace
---

# Dive Context (core)

Use when the user asks for:
- Knowledge retrieval (RAG), grounded answers, citations, or evidence mapping
- Debugging/observability, timelines, tool calls, or replayable traces
- Any request that should emit **EvidencePackV2** (claims ↔ evidence) and/or **ProcessTrace** artifacts

## Responsibilities
- Drive retrieval + evidence contract compliance
- Emit UI-ready observability events (run/step/tool/rag/metrics/evidence)
- Ensure privacy-preserving trace export where applicable

## Expected artifacts
- `.vibe/runs/<run_id>/process_trace.json`
- `.vibe/runs/<run_id>/evidencepack.v2.json`
- `.vibe/runs/<run_id>/events.jsonl`

## Monitor integration
Antigravity should POST event envelopes to the monitor server:
- `POST /v1/ingest` with `events: DiveEventEnvelope[]`

And the monitor UI consumes:
- `GET /v1/runs`
- `GET /v1/runs/{run_id}/snapshot`
- `GET /v1/stream/events` (SSE)
