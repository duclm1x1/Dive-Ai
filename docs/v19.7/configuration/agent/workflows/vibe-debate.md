# /vibe-debate

Generate a debate frame (deterministic, offline) to challenge a proposed change.

Run:
```bash
python3 .shared/vibe-coder-v13/vibe.py debate --repo . --question "Should we auto-apply resolve patches?" --report .vibe/reports/vibe-report.json --md-out .vibe/reports/vibe-debate.md
```

Use the output to drive an agent debate step (PRO/CON + guardrails) before merge.
