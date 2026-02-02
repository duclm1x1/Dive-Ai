# ext-aiclient2api (provider gateway / OpenAI-compatible)

Source: https://github.com/justlovemaki/AIClient-2-API

## What this is

AIClient-2-API is an **API proxy / gateway** that exposes a **standard OpenAI-compatible interface** while translating to various upstream protocols (OpenAI/Claude/Gemini-style). It also advertises **provider pools**, health checks, and failover.

## Classification in Dive Coder

- **Type:** `external-integration` (provider gateway)
- **Not a base skill.** Dive Engine should treat this as a *provider endpoint* (OpenAI-compatible) and run normal provider validation + governance on it.
- **License:** GPL-3.0 (do not vendor into Dive Coder; integrate as a separate service).

## When to use

Use this integration when you need:

- a single OpenAI-compatible endpoint to front multiple upstream providers
- health-aware routing and pool scheduling *for credentials you are authorized to use*
- a self-hosted gateway for IDE/CLI tools that only speak OpenAI-compatible APIs

## Compliance note (non-negotiable)

Dive Coder does **not** implement or recommend techniques intended to bypass provider Terms of Service, quotas, or access controls. If you use any gateway that supports OAuth or multi-account, you must ensure:

- you are authorized to use those accounts/credentials
- the workflow complies with the upstream provider’s ToS and applicable law

## Dive Engine integration pattern

Treat AIClient-2-API as a provider of type `openai_compatible`.

### Example provider config

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

### Required validation (E2)

- GET `/health` (if provided)
- GET `/v1/models`
- POST `/v1/chat/completions` smoke request

### Required governance outputs (E3 in FULL/build)

- `provider_report.json`
- `models_snapshot.json`
- `provider.evidencepack.json`

## Trigger phrases

- “use a local gateway / proxy for models”
- “OpenAI-compatible endpoint for multiple providers”
- “provider pool / failover / health checks”
