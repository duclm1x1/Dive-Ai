## A–Z Checklist (Prompt → Production-ready)

### 0. Preflight (fail-fast)
- [ ] Goal clarified (one sentence) + acceptance criteria
- [ ] Inputs available (spec/logs/test name/URLs/secrets policy)
- [ ] Risk tier set (low/med/high) → required evidence level
- [ ] Repository indexed (incremental) and pointers resolvable

### 1. Search & Locate (grounding)
- [ ] Identify relevant files/symbols via hybrid retrieval
- [ ] Produce pointer registry (path + start/end lines)
- [ ] Blast radius estimate (imports + impacted files)

### 2. Plan
- [ ] Task breakdown (small diffs)
- [ ] Verification plan (tests/gates)
- [ ] Governance plan (artifacts: report, SARIF, baseline compare, EvidencePack)

### 3. Implement (small safe changes)
- [ ] Patch policy enforced (max files, no churn, no breaking unless flagged)
- [ ] Add/adjust tests where logic changed
- [ ] Update docs/runbooks if behavior changes

### 4. Verify (E2)
- [ ] Run selected tests (impact-based) + full suite if high risk
- [ ] Run lint/static analysis (stack-specific)
- [ ] Capture tool outputs (stdout/stderr) as artifacts

### 5. Govern (E3 when VIBE_FULL=true)
- [ ] Produce SARIF (security findings)
- [ ] Baseline compare gate (fail on new findings unless allowed)
- [ ] EvidencePack + Claims Ledger (artifact hashes)
- [ ] PR bundle summary (risk, evidence links)

### 6. Release Readiness
- [ ] Rollback plan
- [ ] Monitoring/alerts in place
- [ ] On-call notes / runbook updated
