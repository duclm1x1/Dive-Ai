# Workflow: RLM Investigate (query-first)

RLM is an **investigator/verifier**: it produces candidate evidence, not a final “done” decision.

## Usage

```bash
python3 .shared/vibe-coder-v13/vibe.py index-build --repo .
python3 .shared/vibe-coder-v13/vibe.py investigate --repo . --issue-id IKO-123 \
  --question "Where is idempotency missing in our n8n workflows?" --limit 25
```

## Output

- Investigation JSON is written to `.vibe/iko/investigations/`.
- The IKO is updated with an event `INVESTIGATION_ATTACHED`.

## Non-goals

- RLM does not transition IKO state.
- Only Gatekeeper can transition state.
