# Vibe Base Skill: cache-design (v13, Enterprise)

> Purpose: design a **correct, fast, tenant-safe, auditable caching system** — not “just store values”.
>
> Output: a **single deterministic folder** containing **Artifacts A–H + ledger + validators report** so the system can **fetch, verify, tune, and audit**.

---

## Why this skill exists
A cache is a distributed system feature. If it’s not designed, you will hit:

- **Stampede / dogpile** (thundering herd on expiry)
- **Hot key collapse** (one key dominates traffic/shard)
- **Cache avalanche** (many keys expiring together)
- **Cache penetration** (miss storms for non-existent keys)
- **Cache inconsistency** (double-writes, stale permissions)
- **Tenant leakage** (catastrophic security incident)
- **Cascading failures** when dependencies degrade

This base skill produces a **production-ready design** with **validators + telemetry** and is compatible with **Claude / Antigravity / any LLM** via a strict artifact contract.

---

## Trigger conditions
Use **cache-design** when you need any of the following:

- Reduce expensive upstream calls (API/DB/LLM/vector/aggregation) with a measurable target (e.g. **90% call reduction**)
- Define **freshness contracts** (TTL / SWR / event-driven invalidation / stale-if-error)
- Prevent **stampede** and **hot-key** failures
- Guarantee **cross-tenant & per-user isolation**
- Ship an **enterprise roll-out plan** (SLOs, telemetry, runbooks, baseline policy)

---

## Preflight inputs (required)
Provide:

1) **Surfaces list** (endpoints/queries/jobs) with parameters and expected response shape
2) **Scope model**: `tenant_id`, `user_id/principal_id`, permissions model
3) **Freshness tolerance** per surface (fresh / bounded stale / must be real-time)
4) **Write signals** (events/CDC/webhooks) if event-driven invalidation is possible
5) **Traffic profile**: QPS, burstiness, hot-key risk, fan-out, tail-latency targets
6) **Data sensitivity**: PII/Secrets and security constraints
7) Backend constraints: Redis/Memcached/Mongo/local FS, multi-region, cost caps

If missing → **Preflight fail**.

---

## Output folder contract (single folder, deterministic)
The skill MUST produce exactly one output root:

```
.cache/cache-design/
  spec.yml
  artifacts/
    A_cacheability_matrix.md
    B_freshness_contracts.md
    C_key_design_spec.md
    D_invalidation_strategies.md
    E_stampede_protection.md
    F_hot_key_mitigation.md
    G_failure_modes.md
    H_single_host_integration.md
    validators_report.json
    ledger.jsonl
  index/
    tags.json
    stats.json
  locks/
  store/
  tmp/
```

Principles:
- **Read path**: key → meta → value; corrupt meta/value ⇒ miss + recompute.
- **Write path**: atomic write (tmp → fsync → rename), never half-write.
- **Lock** per key for singleflight/coalescing.

---

## Artifact set (A–H) — enterprise required content

### Artifact A — Cacheability Matrix
For each surface:
- cacheable? (yes/no)
- why (determinism, scope, privacy)
- freshness class
- TTL/SWR/event strategy
- data size & cardinality risks
- “do-not-cache” reasons (PII, auth tokens, non-determinism)

### Artifact B — Freshness Contracts (TTL / SWR / stale-if-error)
Define per surface:
- `ttl_seconds`
- `swr_seconds`
- `stale_if_error_seconds`
- refresh mode: `sync|async`
- early refresh policy (probabilistic or threshold-based)
- jitter policy to avoid avalanche

### Artifact C — Key Design Spec (mandatory isolation)
Keys MUST include:
- `tenant_id`
- `user_id/principal_id`
- `surface_name`
- `version` (bust on logic changes)
- `request_fingerprint` (normalized request hash)
- optional `permissions_fingerprint` if output depends on ACL

Rules:
- No raw PII in keys.
- Encode with stable canonicalization.
- Include explicit “scope namespace”.

### Artifact D — Invalidation Strategies
Classify each surface into:
- TTL-only
- SWR (bounded-stale acceptable)
- Event-driven (CDC/webhook/job)

Include:
- invalidation fan-out plan
- tag index strategy (invalidate_by_tag)
- write-order policy (avoid stale permissions)
- multi-region invalidation propagation (if applicable)

### Artifact E — Stampede Protection (dogpile control)
Include:
- singleflight / request coalescing by key
- lock TTL + lease (avoid lock leakage)
- soft-expire + async refresh
- early refresh / jitter / backoff
- negative caching + Bloom filter (penetration mitigation) where relevant

### Artifact F — Hot-key Mitigation
Include:
- L1 in-process (LRU+TTL) + L2 shared cache
- hot-key detection threshold + circuit to throttle rebuild
- key splitting / replication strategy (if needed)
- admission control / max rebuild QPS per key

### Artifact G — Failure-mode behavior & resilience
Must cover:
- backend partial outage: circuit breaker + fallback
- stale serving policy (bounded)
- cold cache storms (ramp, warmup)
- cache poisoning defenses
- dependency admission control (avoid cascading failures)
- operational runbook snippets

### Artifact H — Single-host integration + budgets (enterprise)
Include:
- memory/size budget per tenant/namespace
- eviction policy (LRU/LFU/TTL hybrids)
- big-key detection & compression policy
- audit logging fields
- local dev & single-host deployment plan
- compatibility notes: Redis/Mongo/Chroma/local FS

---

## Validators (mandatory) — 13.1–13.3
The skill must output `validators_report.json` with:

### Validator 13.1 — Correctness + leakage safety
- key includes tenant_id + user_id/principal
- permission-aware where required
- no caching of secrets/tokens/raw PII
- cross-tenant isolation test cases listed

### Validator 13.2 — Contract alignment
- TTL/SWR matches declared freshness class
- jitter present for broad key sets
- stale-if-error bounded
- 1 minor mismatch is acceptable only if explicitly listed with impact

### Validator 13.3 — Stampede + failure-mode rigor
- concurrency test plan included (100–1000)
- lock timeout + lease + fallback defined
- circuit breaker & admission control defined

---

## Ledger (mandatory)
`ledger.jsonl` must contain statements with:
- id, statement, confidence (0–1), owner, status (draft/accepted/blocked), evidence refs

Use the ledger to track which claims require 2–4 weeks production telemetry to tune.

---

## SOTA enterprise add-ons (recommended)
- Multi-region: write-through vs read-through tradeoffs, replication delay budgets
- Consistency: session consistency for user-scoped keys
- Security: cache poisoning prevention, per-tenant quotas, audit trails
- Observability: OTel metrics/traces, dashboards, SLOs (hit-rate, stale-served, backend calls saved)
- Cost controls: per-tenant cache budgets and “cache ROI” tracking

---

## Compatibility: Claude / Antigravity / Any LLM
This skill is **artifact-first**, so any LLM can run it if it can:
- produce the folder structure
- fill A–H with grounded content
- produce `validators_report.json` and `ledger.jsonl`

If the LLM is unreliable, require strict JSON and validate with `vibe cache-design validate`.



## CLI (Working, deterministic)

```bash
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . init
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . validate
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . report
```

- `validate` loads `spec.yml`, enforces expected invalidation strategy counts (if configured), and regenerates Artifact A & D skeletons.
- `report` emits an **E3 bundle**: EvidencePack + skill-scoped claims ledger.
