# expo_production: Observability (logging/metrics/tracing + alert policy)

## Goal
Make an Expo/React Native (and backend) system observable end-to-end: you can answer **what is broken, for whom, since when, and why** with evidence.

## Outputs (Artifacts)
- `observability/architecture.md` (what signals exist, where they go)
- `observability/logging_spec.md` (schema + PII rules)
- `observability/metrics_catalog.md` (SLIs/SLOs)
- `observability/tracing_spec.md` (trace/span naming)
- `observability/alert_policy.md` (paging rules + thresholds)
- `observability/dashboards.md` (links/placeholders)
- `observability/runbook_index.md` (alerts → runbooks)
- `observability/claims.json` (Claims ledger, E1–E3)
- `observability/evidencepack.json` (E3 bundle)

## A–Z Checklist (Production)
1. **Define SLOs** (availability, latency p95, crash-free sessions).
2. **Client logging**: structured logs with correlation ids; redact PII/secrets.
3. **Client metrics**: app start time, screen load time, JS exceptions, network error rate.
4. **Crash reporting**: symbolication, release mapping, build fingerprint.
5. **Backend logs/metrics** (if any): request id propagation; error budget burn.
6. **Tracing**: propagate `traceparent` (or vendor equivalent) through API calls.
7. **Alert policy**:
   - Page only on user impact (SLO burn / crash spikes / auth failure spikes).
   - Ticket for noisy/low urgency signals.
8. **Dashboards**: top-level SLO overview + drilldowns.
9. **Runbooks**: each page-level alert must link to a runbook.
10. **Game day**: simulate outage and validate signal coverage.

## Validators
- No PII in logs (static regex + allowlist fields).
- Crash-free sessions tracked.
- Correlation id is present on all network requests.
- Alert rules have owner + severity + escalation.

