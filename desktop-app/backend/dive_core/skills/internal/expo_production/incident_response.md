# expo_production: Incident Response (runbook templates)

## Goal
When something breaks, you recover fast with low chaos and documented learning.

## Outputs
- `ir/severity.md` (SEV definitions)
- `ir/roles.md` (IC, Comms, Ops)
- `ir/runbook_template.md`
- `ir/postmortem_template.md`
- `ir/alerts_to_runbooks.md`
- `ir/evidencepack.json` (E3 optional)

## Checklist
1. SEV scale and paging policy.
2. Roles & rotation.
3. Standard runbook template:
   - Symptoms
   - Triage steps
   - Mitigations
   - Rollback paths
   - Verification
4. Communication template (internal + external).
5. Postmortem: timeline + contributing factors + action items.
6. Learning loop: tag incidents → tests/alerts improvements.

## Validators
- Every page-level alert links to a runbook.
- Postmortems produce action items with owners + due dates.

