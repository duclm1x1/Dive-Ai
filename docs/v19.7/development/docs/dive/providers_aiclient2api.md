# Provider: AIClient-2-API (gateway)

This document describes how Dive Engine integrates with **AIClient-2-API** as an external gateway.

Repo: https://github.com/justlovemaki/AIClient-2-API

## Role in the stack

- AIClient-2-API is treated as an **external provider gateway**.
- Dive Engine talks to it through the **OpenAI-compatible adapter**.
- Dive Engine remains responsible for **routing policy**, **evidence**, and **governance**.

## Non-negotiable compliance

Dive Coder/Dive Engine does not provide instructions to bypass third-party access controls. You must ensure all credentials and usage patterns comply with upstream provider Terms of Service and local law.

## Provider configuration

Add a provider entry to `configs/providers.yml`:

```yaml
providers:
  aiclient2api:
    type: openai_compatible
    base_url: http://127.0.0.1:3000/v1
    auth:
      kind: bearer_env
      env: DIVE_AICLIENT2API_API_KEY
    capabilities:
      json_schema: true
      tool_calls: true
      streaming: true
    health:
      endpoint: http://127.0.0.1:3000/health
      timeout_ms: 2500
```

## Required validation

When this provider is configured, `dive provider validate aiclient2api` must:

1. GET `/health` (if present)
2. GET `/v1/models`
3. POST `/v1/chat/completions` smoke request

Artifacts (E2):

- `.vibe/evidence/provider/aiclient2api/provider_report.json`
- `.vibe/evidence/provider/aiclient2api/models_snapshot.json`

In FULL/build: EvidencePack (E3)

- `.vibe/evidence/provider/aiclient2api/provider.evidencepack.json`

## Licensing note

The upstream project is GPL-3.0. Integrate as a separate service; do not vendor or embed into Dive Coder without a deliberate licensing decision.
