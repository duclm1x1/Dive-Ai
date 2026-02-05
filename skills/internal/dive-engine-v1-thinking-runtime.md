# Skill: Dive Engine V1 Thinking Runtime (Cognitive Operating Mechanism)

**Category**: Core / Base (Engine)

## 0) Why this exists

This skill defines *how Dive Engine operates* — routing, reasoning effort, verification, monitorability, and evidence. It is the orchestrator’s “thinking policy” that turns a raw prompt into a production‑grade run with artifacts.

It is **not** a claim about proprietary internals of any vendor model. It is an implementable orchestration blueprint.

## 1) Inputs

- `run_spec` (JSON): mode, task_type, constraints, required evidence level, budgets
- `providers.yml`, `pools.yml`, `routing.yml`, `governance.yml`
- repo root

## 2) Outputs (Artifacts)

### Required (all non‑trivial runs)
- `router_decision.json` (E2)
- `effort_plan.json` (E2)
- `budget_plan.json` (E2)
- `process_trace_summary.md` (E0/E1)
- `mode_run.json` (E2)
- `scorecard.json` (E3)
- `claims.jsonl` (E3)
- `evidencepack.json` (E3)

### Required (high‑risk / governance modes)
- `monitor_report.json` (E2)
- `baseline_compare.json` (E3) when policy requires
- `*.sarif.json` (E3) for security tooling

## 3) Operating steps (deterministic)

1. **Preflight**: validate required inputs and policies; fail fast if missing.
2. **Route**: choose `fast|think` using risk + evidence requirements.
3. **Effort**: choose `low|medium|high`.
4. **Execute**: run planned steps, gated by `mode.yml`.
5. **Verify**: run tool gates; re‑plan only if gates fail.
6. **Monitor**: produce `monitor_report.json` from process summary + artifacts.
7. **Govern**: write claims ledger and pack E3 evidence.

## 4) Validators (pass/fail)

### V1.1 Routing correctness
- Router emits artifact and references the exact policy branch taken.
- Any `security|performance|release` run must route to `think`.

### V1.2 Effort policy
- `fast` → effort defaults to `low`.
- `security/perf/release` → effort must be `high`.

### V1.3 Evidence integrity
- Every claim references at least one artifact + sha256.
- EvidencePack hash index matches files on disk.

### V1.4 Privacy & redaction
- Engine scratchpad is not persisted unless explicitly enabled.
- Logs are redacted for secrets when policy requires.

## 5) Configuration hooks

- `configs/routing.yml`: defines routing rules and tier mapping
- `configs/governance.yml`: defines required evidence by mode and baseline policies

## 6) References

- See: `docs/dive/dive-engine-v1-cognitive-runtime.md`