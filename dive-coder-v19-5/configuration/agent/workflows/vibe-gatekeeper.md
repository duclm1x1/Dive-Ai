# Workflow: Gatekeeper

Gatekeeper is the **only place allowed to transition IKO state**.

## Transition

```bash
python3 .shared/vibe-coder-v13/vibe.py gatekeeper --repo . --issue-id IKO-123 \
  --to EVIDENCE_READY --actor gatekeeper --reason "CI passed" \
  --evidencepack .vibe/evidence/ep-IKO-123-<pid>.evidencepack.json
```

## Rules

- Gatekeeper enforces allowed transitions.
- EvidencePack required for: EVIDENCE_READY/APPROVED/DEPLOYING/DEPLOYED/CLOSED.
- RLM/Cruel cannot transition.
