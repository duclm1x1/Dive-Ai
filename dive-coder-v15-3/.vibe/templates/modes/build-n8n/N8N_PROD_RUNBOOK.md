# n8n Workflow — Production Runbook (A–Z)

## Inputs you MUST collect (Preflight)
- Business goal + success metric
- Trigger type (webhook/cron/queue/manual)
- Systems involved (APIs/DBs/SaaS) + auth method
- Data classification (PII/PCI/Secrets) + retention policy
- Failure tolerance + SLO (latency, retries, max delay)
- Idempotency strategy (dedupe key)
- Rate limits + quotas for each external system
- Deployment target (n8n cloud/self-host) + version

## Architecture checklist
- Workflow boundaries: one workflow per bounded context
- Error path: every external call has retry/backoff + timeout
- Circuit breaker / admission control (avoid cascading failure)
- Dead-letter handling (store failed items + replay)
- Idempotency: dedupe by (tenant_id, event_id) or request hash
- Secrets: use n8n credentials store; never inline secrets
- Observability: structured logs, correlation_id, metrics

## Node-by-node requirements
- Webhook/Trigger node:
  - Validate schema, reject invalid early
  - Extract tenant_id/user_id/principal_id
- HTTP Request nodes:
  - Timeouts set
  - Retry policy defined (max attempts, backoff)
  - Rate limit handling (429) + jitter
- Function/Code nodes:
  - Deterministic transforms; avoid hidden state
  - Unit-test logic (export pure functions) when possible
- Data store nodes:
  - Ensure transactions/atomicity when needed

## Testing strategy (minimum)
- Golden payload tests (fixtures):
  - success path
  - partial failure
  - invalid payload
  - rate limited
- Replay testing (idempotency)
- Load simulation for hot-path nodes

## Security checklist
- Tenant isolation: tenant_id in every key / record
- Least privilege creds
- Audit log for sensitive actions
- PII redaction in logs

## Release checklist
- Version workflow (export JSON)
- Change log
- Rollback plan (previous workflow version)
- Alerts: error rate, retries, queue depth, latency
