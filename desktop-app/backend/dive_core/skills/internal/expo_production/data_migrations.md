# expo_production: Data Migrations (schema change safety + backfill)

## Goal
Zero-downtime schema evolution with predictable backfill and rollback.

## Outputs
- `migrations/plan.md` (expand/contract strategy)
- `migrations/schema_contract.md` (compat windows)
- `migrations/backfill_plan.md`
- `migrations/rollback_plan.md`
- `migrations/verification.md` (queries + metrics)
- `migrations/evidencepack.json` (E3)

## Checklist
1. Choose migration pattern: **Expand → Backfill → Contract**.
2. Add new columns/tables first (expand); keep old readers working.
3. Dual-write or write-new/read-old policy during window.
4. Backfill:
   - chunking, checkpoints, retries, idempotency
   - rate limiting to protect DB
5. Verification:
   - consistency queries
   - sample audits
6. Contract:
   - remove old fields only after stability window
7. Rollback:
   - disable writer, revert readers
8. Monitor:
   - replication lag, error rates, slow query, lock contention

## Validators
- No breaking reads in compat window.
- Backfill is idempotent and resumable.
- Metrics exist for progress + failure + lag.

