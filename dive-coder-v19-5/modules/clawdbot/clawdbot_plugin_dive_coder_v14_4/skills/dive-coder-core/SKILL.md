---
name: dive-coder-core
description: "Dive Coder core workflows: review/resolve/build, evidence bundles, and runtime gates."
metadata: '{"version":"14.4.0","project":"Dive Coder","tags":["dive","vibe-coder","review","resolve","evidencepack"],"offline_first":true}'
---

## What this skill does

- Runs Dive/V13 CLI workflows (review → resolve → gates)
- Generates EvidencePack bundles (E3) and claims ledgers (E2)
- Provides copy/paste command recipes for consistent ops

## Quickstart (repo root)

```bash
export PYTHONPATH="$PWD/.shared/vibe-coder-v13:${PYTHONPATH:-}"

python3 .shared/vibe-coder-v13/vibe.py review --repo . --mode balanced --seed 42 \
  --out .vibe/reports/vibe-report.json \
  --md-out docs/vibe-report.md \
  --sarif-out .vibe/reports/vibe-report.sarif.json

python3 .shared/vibe-coder-v13/vibe.py resolve --repo . --run-gates \
  --patch-out .vibe/reports/vibe-resolve.patch \
  --out .vibe/reports/vibe-resolve.json
```

## Notes

- For private Git repos, prefer **read-only deploy keys** or GitHub App tokens. Do not paste private keys into chat.
