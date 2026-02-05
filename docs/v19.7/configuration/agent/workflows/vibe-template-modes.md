# V13 Template Modes (Prompt → Production-ready)

This repository ships **mode templates** under `.vibe/templates/modes/`.

Each mode is an A–Z runbook that forces:
- **Preflight** (fail-fast)
- **Grounding** (pointers, no hallucination)
- **Verification** (E2 tool output)
- **Governance** (E3 EvidencePack + claims when VIBE_FULL=true)
- **Scorecard** (evidence-backed)

## Available modes
- `build-app`
- `build-n8n`
- `build`
- `debug`
- `website`
- `security-review`
- `performance`

## How to use
1) Pick a mode folder.
2) Start from `PROMPT.md` (paste as system/first message into your LLM/agent).
3) Execute the steps in `CHECKLIST.md`.
4) Fill `VERIFY_PLAN.md`.
5) Produce evidence artifacts and score using `SCORECARD.md`.

## Evidence policy
- For PR / security / release: set `VIBE_FULL=true` and require E3 bundle.
- For small tasks: `VIBE_MINIMAL=true` is allowed, but still pointer-first.
