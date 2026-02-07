# Dive Engine Spec v1 (Dive Coder v13)

> Status: **Spec v1** (implementation-ready)
>
> Purpose: Define **Dive Engine** as the runtime orchestrator for Dive Coder (CLI/IDE/Antigravity), delivering deterministic **Prompt → Verified → Governed** execution with evidence artifacts.

## 0) Executive summary

**Dive Engine** is the *runtime control plane* for Dive Coder:

- **Orchestrates**: Preflight → Retrieve/Locate → Plan → Execute tools → Verify gates → Govern artifacts
- **Routes**: chooses providers/models/accounts via policy (latency/cost/features), supports failover + degradation
- **Proves**: emits EvidencePack/Claims/Baseline Compare (E2/E3) so “DONE” is auditable

Design targets:

- **Antigravity-first** (IDE/agent orchestration friendly)
- **Python core** (tight integration with Dive Coder engine)
- **Node gateway friendly** (can treat external proxies as providers)

## 0.1 Cognitive runtime (how the engine "thinks")

This spec defines the *plumbing* (providers/pools/policies). The **operating mechanism** — dual‑path routing, effort control, verify loops, proxy‑monitorability, and evidence binding — lives here:

- `docs/dive/dive-engine-v1-cognitive-runtime.md`

This split keeps the system modular: **Spec v1** for interfaces/contracts, **Cognitive Runtime** for deterministic behavior.

## 1) Non-negotiables

### 1.1 Contract with imperfect LLMs

- All LLM outputs are treated as **untrusted suggestions** until backed by artifacts.
- Missing required inputs → **Preflight Fail**.
- Responses must be **grounded** (pointers/artifacts). No file/symbol hallucination.

### 1.2 Evidence levels

- **E0** reasoning only
- **E1** user-provided logs
- **E2** tool-executed output (stdout, test logs)
- **E3** reproducible artifacts (SARIF/report/baseline-compare/evidencepack)

Build/release/security modes require **E2/E3**.

## 2) High-level architecture

### 2.1 Components (Python)

1) **Engine Daemon (optional but recommended)**
   - `dive engine serve` exposes local JSON-RPC over stdio or unix socket
   - keeps hot caches: index, graph, provider health

2) **Provider Registry**
   - describes providers, supported protocols, model allowlists, pricing tiers

3) **Account Pool Manager**
   - manages multiple credentials per provider
   - health state, cooldowns, backoff, token-bucket limits

4) **Router + Policy Engine**
   - chooses provider/account/model for each request
   - supports fallback chains and graceful degradation

5) **Protocol Adapters**
   - OpenAI-compatible (`/v1/chat/completions`, `/v1/models`)
   - Anthropic-native (`/v1/messages`) when available
   - (optional) Gemini-native

6) **Execution Controller**
   - runs mode steps from `mode.yml`
   - executes gates (tests/scans/build) and collects artifacts

7) **Governance Packager**
   - writes Claims Ledger + EvidencePack + Baseline Compare artifacts

8) **Observability Layer**
   - structured logs, metrics, trace IDs per run

### 2.2 Node.js role

Node.js is **not required** for the core orchestrator. It is used for:

- External provider gateways/proxies (treated as an **OpenAI-compatible provider**)
- Optional “plugin runners” for ecosystem tools that are Node-first

Dive Engine treats these as **providers**, not as core logic.

## 3) Data contracts (configs)

All configs are YAML (human-editable) with a strict schema.

### 3.1 `configs/providers.yml`

```yaml
version: 1
providers:
  aicoding:
    type: openai_compatible
    base_url: https://aicoding.io.vn/v1
    auth:
      kind: bearer_env
      env: DIVE_AICODING_API_KEY
    models:
      allow:
        - claude-sonnet-4-5
        - claude-opus-4-5
    capabilities:
      json_schema: true
      tool_calls: false
      streaming: true
    health:
      endpoint: https://aicoding.io.vn/health
      timeout_ms: 2500

  local_gateway:
    type: openai_compatible
    base_url: http://127.0.0.1:3000/v1
    auth:
      kind: bearer_env
      env: DIVE_GATEWAY_API_KEY
    capabilities:
      json_schema: true
      tool_calls: true
      streaming: true
```

### 3.2 `configs/pools.yml`

```yaml
version: 1
pools:
  aicoding:
    strategy: weighted_rr
    accounts:
      - id: aicoding-main
        weight: 100
        auth_ref: providers.aicoding.auth
        limits:
          rps: 8
          concurrent: 4
    failure_policy:
      retry:
        max_attempts: 2
        backoff_ms: [200, 800]
        jitter: true
      circuit_breaker:
        open_after: 8
        half_open_after_ms: 15000
      cooldown_after_429_ms: 20000

  local_gateway:
    strategy: least_loaded
    accounts:
      - id: gateway-1
        weight: 100
        auth_ref: providers.local_gateway.auth
        limits:
          rps: 20
          concurrent: 10
```

### 3.3 `configs/routing.yml`

```yaml
version: 1
defaults:
  provider: aicoding
  model: claude-sonnet-4-5

routes:
  code_review:
    require:
      json_schema: true
    prefer:
      - provider: aicoding
        model: claude-opus-4-5
      - provider: local_gateway
        model: claude-sonnet-4-5

  cheap_batch:
    budgets:
      max_cost_per_1k_tokens_usd: 0.01
    prefer:
      - provider: local_gateway
        model: qwen3-coder-plus

fallback_chains:
  aicoding:
    - local_gateway
```

### 3.4 `configs/governance.yml`

```yaml
version: 1
profiles:
  minimal:
    require_evidence_level: E1
    require_baseline_compare: false

  full:
    require_evidence_level: E2
    require_baseline_compare: true
    required_artifacts:
      - mode.evidencepack.json
      - mode.claims.json
      - scorecard.json

baseline:
  semgrep:
    baseline_path: .vibe/baseline/semgrep.sarif.json
    fail_on_new_findings: true
```

## 4) Engine runtime protocol (Antigravity/IDE-friendly)

### 4.1 Local JSON-RPC (recommended)

Transport options:

- stdio (best for CLI tools)
- unix socket / named pipe (best for IDE extension)

#### Methods

1) `engine.ping` → health
2) `provider.validate` → returns provider_report (E2)
3) `provider.list_models` → models snapshot
4) `mode.apply` → creates run workspace
5) `mode.run` → runs manifest steps, emits E3
6) `artifacts.list` → list artifacts for a run
7) `artifacts.read` → read artifact content (bounded)

### 4.2 Request/response envelope

```json
{
  "jsonrpc": "2.0",
  "id": "...",
  "method": "mode.run",
  "params": {
    "repo_root": ".",
    "mode": "security-review",
    "run_id": "sec-2026-01-25",
    "profile": "full",
    "query": "Review auth flow + SAST",
    "provider_route": "code_review"
  }
}
```

Response returns:

- `status`: OK/WARN/FAIL
- `artifacts`: list of `{path, sha256, evidence_level}`
- `scorecard`: summary

## 5) Scheduling algorithms (high availability, compliant)

Dive Engine improves availability and throughput using **standard SRE patterns**:

- **Health-aware selection** (exclude unhealthy accounts)
- **Weighted round robin** or **least-loaded** selection
- **Token-bucket rate limits** per account/provider
- **Circuit breaker** per account (open/half-open/closed)
- **Retry budget** (bounded retries for transient errors)
- **Cooldown after 429**

> Note: Dive Engine is designed to respect provider policies. It does **not** implement mechanisms intended to bypass third-party restrictions.

## 6) Step execution (mode.yml)

Dive Engine executes mode steps declared in `mode.yml`:

### 6.1 Step types

- `doctor` (repo readiness)
- `preflight` (input/spec validation)
- `gate` (tests/build/lint)
- `scan` (semgrep/gitleaks/etc.)
- `baseline-compare` (E3)
- `pack` (evidencepack/claims/scorecard)

Each step declares:

- required evidence level (E1/E2/E3)
- required output artifacts
- exit behavior (blocking vs non-blocking)

## 7) Outputs & artifacts (definition of done)

For a **FULL** run, Engine must emit:

- `.vibe/runs/<run_id>/mode_run.json` (E2)
- `.vibe/runs/<run_id>/scorecard.json` (E3)
- `.vibe/runs/<run_id>/mode.claims.json` (E3)
- `.vibe/runs/<run_id>/mode.evidencepack.json` (E3)

If security scan present:

- `.vibe/runs/<run_id>/security.sarif.json` (E3)
- `.vibe/runs/<run_id>/baseline-compare.json` (E3)

## 8) Observability

### 8.1 Logs

Structured JSON logs with fields:

- `run_id`, `mode`, `step`, `provider`, `account_id`
- `latency_ms`, `status`, `error_class` (429/5xx/timeout)

### 8.2 Metrics

- success rate, p95 latency per provider
- retries, fallback count, circuit breaker opens
- token usage (if available)

### 8.3 Tracing

Propagate `trace_id` across:

- IDE request → engine → provider

## 9) Security requirements

- Secrets from env var or OS keychain only (no plaintext in repo).
- Artifact redaction policy for logs (tokens/PII).
- Optional “audit log mode” for compliance.

## 10) Compatibility notes for Antigravity

- Prefer local daemon JSON-RPC to avoid repeated cold-start indexing.
- Provide a single “run endpoint”: `mode.run` that returns *artifact pointers*.
- Support OpenAI-compatible providers as the primary integration surface.
