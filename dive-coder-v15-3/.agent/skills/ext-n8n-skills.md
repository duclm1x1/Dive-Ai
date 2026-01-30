# n8n-skills (workflow automation skillset)

**Repo:** https://github.com/czlonkowski/n8n-skills

**Type:** skills-pack (n8n / automation)

## What it is
A curated set of Claude Code skills for building production-ready **n8n workflows** using the **n8n-mcp** MCP server.

## Why it matters for Vibe Coder
If your repo includes automation work (n8n workflows, integrations, ops automation), this pack provides:
- Node-level workflow construction patterns
- Best practices for robust workflows (error handling, retries, idempotency)
- A structured “how-to” for using n8n-mcp tooling effectively

## Prerequisites
- **n8n-mcp** MCP server installed/configured before using these skills.

## Recommended integration into Vibe Coder
### Option A — Copy skills into your repo skill stack (simplest)
1. Clone the repo (or vendor only the needed files).
2. Copy selected markdown files from `n8n-skills/skills/` into:
   - `.agent/skills/` (recommended), or
   - an external skills directory your orchestrator loads.

### Option B — Keep as external reference (lightweight)
- Keep this `ext-n8n-skills.md` note and only pull in the full skill markdown when you detect:
  - tasks mentioning “n8n”, “workflow automation”, “MCP”, “webhook automation”, “ETL”, “integration”.

## Trigger phrases (routing hints)
- “n8n workflow”, “automation”, “webhook flow”, “node configuration”
- “MCP server”, “n8n-mcp”, “n8n templates”
- “retry / idempotency / error handling in n8n”

## Governance notes
- Treat workflow changes as **high-impact** if they touch:
  - credentials, webhooks, payment, user data, or external side effects
- In `VIBE_FULL=true`, require:
  - Evidence level **E2** for validation runs (tool output),
  - Evidence level **E3** for exported workflow JSON + EvidencePack.
