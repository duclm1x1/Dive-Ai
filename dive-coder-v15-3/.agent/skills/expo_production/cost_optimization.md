# expo_production: Cost Optimization (cache + rate-limit + batching)

## Goal
Reduce cloud + LLM + API spend without user impact.

## Outputs
- `cost/baseline.md` (current costs + top drivers)
- `cost/optimization_plan.md` (ranked by ROI)
- `cost/cache_plan.md` (ties into cache-design)
- `cost/rate_limit_plan.md`
- `cost/batching_plan.md`
- `cost/evidencepack.json` (E3 for changes)

## Checklist
1. Measure baseline: requests, bytes, compute time, LLM tokens.
2. Add caching where deterministic (use `cache-design` skill).
3. Add rate limiting:
   - per user/tenant
   - burst + sustained
4. Add batching:
   - consolidate N calls → 1 call
5. Add circuit breakers to avoid cascading retries.
6. Verify: before/after metrics.

## Validators
- No cache leakage across tenants/users.
- Rate limits have override and clear error messages.
- Before/after evidence captured.

