# Dive Engine V1 — Cognitive Runtime (Dual‑Path + Verify + Govern)

This document defines the **operating mechanism** of **Dive Engine V1**: how the orchestrator routes tasks, allocates reasoning effort, runs verification loops, monitors process quality, and packages evidence.

## 0) Scope and boundaries

Dive Engine is an **orchestrator**. It coordinates:

1) **Routing** (fast vs deep)
2) **Reasoning compute control** (effort, sampling, search)
3) **Verification** (tests, builds, scans)
4) **Governance** (Evidence levels E0–E3, Claims Ledger, EvidencePack, Baseline compare)

**Non‑goal**: claiming proprietary internals of any model. Where we reference “reasoning effort” and “monitorability”, we only rely on **public** descriptions and turn them into implementable orchestration behaviors.

## 1) Dual‑Path routing (Fast Path vs Thinking Path)

### 1.1 Router objective

Given a `run_spec` (task + constraints), the router chooses:

- `path = fast` for simple/low‑risk tasks
- `path = think` for complex/high‑risk tasks

Router output becomes an artifact: `router_decision.json` (E2).

### 1.2 Routing signals (inputs)

Signals are computed from:

- **Task type**: `debug | build | security | performance | website | generic`
- **Risk class**: `low | medium | high` (from mode + files touched + policy)
- **Evidence requirement**: minimum required evidence level by mode (`E0`..`E3`)
- **Complexity hints**: codebase size, number of files/symbols touched, required steps
- **SLO**: latency budget, cost budget

### 1.3 Default routing policy

| Condition | Route | Rationale |
|---|---|---|
| `risk=low` AND `evidence<=E1` AND `task in {website,generic}` | `fast` | speed/cost |
| `task=debug` AND has failing tests/logs (E1/E2) | `think` | root‑cause accuracy |
| `task in {security,performance}` OR `evidence>=E2` | `think` | precision + verification |
| touched files include auth/crypto/billing | `think` | blast radius |

### 1.4 Model tier mapping (abstract)

Dive Engine does not hardcode “brands” into logic. It uses tier labels:

- `tier_fast`: low‑cost, low latency
- `tier_think`: deep reasoning, multi‑step
- `tier_monitor`: small/cheap “judge/monitor” model

Providers map tiers to concrete models in `providers.yml` + `routing.yml`.

## 2) Reasoning compute control (Effort Controller)

### 2.1 Effort levels

We standardize `effort = low | medium | high`.

**If provider supports native effort control** (e.g., OpenAI reasoning models expose `reasoning.effort`), Dive Engine passes it through. OpenAI documents `reasoning.effort` as `low/medium/high` to control reasoning tokens before generating a response. citeturn0search1

**If provider does not support native effort**, Dive Engine emulates effort via *inference‑time scaling*:

- `low`: single sample, no search
- `medium`: 2–3 samples + lightweight self‑check
- `high`: N samples + voting / best‑of + tool‑verification loop

### 2.2 Effort selection rules

Effort is chosen from router output + evidence needs:

- `fast` path: `effort=low` (default)
- `think` path: `effort=medium` (default)
- `security/performance/release` OR `baseline gate present`: `effort=high`

Effort choice artifact: `effort_plan.json` (E2).

### 2.3 Inference‑time scaling primitives

Dive Engine exposes a uniform set of primitives, regardless of provider:

1) **Multi‑sample**: generate `k` candidate plans/patches
2) **Self‑consistency**: majority vote on key decisions
3) **Search‑style**: beam‑like exploration on plan steps (bounded)
4) **Tool‑verify loop**: run tools/tests, then regenerate with the observed failures

## 2.4 Cognitive phases (Think Path)

For `path=think`, Dive Engine executes a **6‑phase cognitive loop**. This is a *behavioral contract* (what the orchestrator must do), not a claim about any model’s hidden internals:

1) **Input processing**: normalize prompt → structured task spec (scope, constraints, acceptance criteria)
2) **Exploration**: generate candidate approaches (at least 2 when effort ≥ medium)
3) **Analysis**: pick approach, write plan with risks + dependencies
4) **Verification**: run gates/tests/scans and reconcile failures
5) **Conclusion**: synthesize final decisions + patch summary
6) **Output generation**: format final answer + pointers to artifacts

Artifacts by phase (minimum):

- (1) `task_normalized.json` (E1/E2)
- (2) `candidates.json` (E0/E1)
- (3) `plan.md` (E0/E1)
- (4) `tool_run/*` (E2) + optional `*.sarif.json` (E3)
- (5) `decision_log.md` (E0/E1)
- (6) `final_output.md` (E0) + `claims.jsonl` (E3)

## 3) Private workspace (Engine Scratchpad)

### 3.1 Purpose

We want a “private workspace” where the agent can explore options without leaking noisy intermediate text into the user channel.

OpenAI notes that reasoning models generate an explicit chain‑of‑thought and that monitoring that reasoning can be useful; the chain‑of‑thought is treated as a private space in their training context. citeturn0search0

### 3.2 Dive Engine implementation

Dive Engine maintains an **Engine Scratchpad** that is:

- **Ephemeral** by default (in‑memory, per run)
- **Never written to disk** unless explicitly enabled
- **Never included** in EvidencePack (unless redacted)

Instead, the engine stores only a **Process Trace Summary** artifact:

- `process_trace_summary.md` (E0/E1) — structured bullet steps, assumptions, risks, evidence plan

This keeps the system auditable without storing sensitive intermediate reasoning.

## 4) Verification loop (Verify‑first, not “answer‑first”)

Verification is not optional for production modes.

### 4.1 Verification stages

1) **Static**: lint/typecheck/schema validate
2) **Build**: compile/bundle
3) **Tests**: unit/integration (selective first, then critical subset)
4) **Security**: SAST/dep audit/secrets scan (where required)

Each stage writes:

- `tool_run/*.log` (E2)
- `tool_run/*.json` where available (E2)
- `*.sarif.json` for security scans (E3)

### 4.2 “Fail fast” rules

- missing required inputs → `PRECHECK_FAIL`
- verification gate fails → `GATE_FAIL`
- baseline compare introduces new findings in blocked categories → `BASELINE_FAIL` (E3)

## 5) Monitorability layer (Process Monitor)

### 5.1 Goal

We want a monitor that can predict critical properties about agent behavior (e.g., likely errors, unsafe shortcuts) from **process evidence**, not just final output.

OpenAI’s public work defines monitorability and finds monitoring chain‑of‑thought can outperform monitoring actions/outputs alone; longer reasoning can improve monitorability, and follow‑up questions can improve monitoring. citeturn0search0

### 5.2 Practical constraint

Many providers do not expose raw chain‑of‑thought. Dive Engine therefore implements a **Proxy Monitorability** approach:

1) Require a structured **Process Trace Summary** (not raw CoT)
2) Use a **Monitor Model** (`tier_monitor`) to evaluate:
   - completeness
   - logical gaps
   - missing evidence
   - over‑broad changes
   - test coverage risk
3) Optionally ask **follow‑up questions** (monitor prompts) to improve clarity, inspired by the follow‑up improvement observation. citeturn0search0

Monitor artifacts:

- `monitor_report.json` (E2)
- `monitor_findings.md` (E1/E2)

## 6) Budgeting (tokens, time, money)

Dive Engine enforces budgets per run:

- `latency_budget_ms`
- `cost_budget_usd` (or token budget proxy)
- `max_tool_calls`
- `max_llm_calls`

### 6.1 Monitorability tax (tradeoff)

Higher reasoning effort (and longer process traces) can improve monitorability, but costs more inference compute. OpenAI describes this as a tradeoff and highlights that longer “thinking” tends to be more monitorable. citeturn0search0

Dive Engine therefore couples `effort` to budgets:

- If `effort=high` is requested but `cost_budget` is tight, the engine prefers **smaller tier models at higher effort** or **fewer samples + stronger tool verification**, rather than silently downgrading to low-effort.

Budgets are recorded:

- `budget_plan.json` (E2)
- `usage_summary.json` (E2)

## 7) Evidence binding (Claims ↔ Artifacts)

Dive Engine treats “production‑ready” as **evidence‑backed**.

Rules:

- Every claim must reference at least one artifact path + sha256.
- Build modes must emit Evidence Level declarations for gate tools.
- Security/release modes must include **Baseline Compare Gate (E3)** when policy requires.

Artifacts:

- `claims.jsonl` (E3)
- `evidencepack.json` (E3)
- `baseline_compare.json` (E3) where applicable

## 8) Engine interfaces (JSON‑RPC)

### 8.1 `run_spec` (minimal)

```json
{
  "run_id": "RUN-2026-01-25-001",
  "mode": "security-review",
  "task_type": "security",
  "repo_root": ".",
  "inputs": {
    "prompt": "...",
    "references": []
  },
  "constraints": {
    "required_evidence_level": "E3",
    "latency_budget_ms": 900000,
    "cost_budget_usd": 3.0,
    "privacy": {
      "store_scratchpad": false,
      "redact_logs": true
    }
  }
}
```

### 8.2 Required run artifacts

- `router_decision.json`
- `effort_plan.json`
- `budget_plan.json`
- `process_trace_summary.md`
- `monitor_report.json`
- `mode_run.json`
- `scorecard.json`
- `claims.jsonl`
- `evidencepack.json`

## 9) Upgrade path (V1 → V2)

V1 focuses on deterministic routing, effort control, verify loops, and evidence.

V2 should add:

- model‑based complexity classifier (trained on run outcomes)
- replayable “run cassette” for deterministic reproduction
- richer test selection via repo graph
- stronger artifact validator (CI enforced)
