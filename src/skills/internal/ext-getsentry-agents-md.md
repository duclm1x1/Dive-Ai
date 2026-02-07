# Sentry Skill: agents-md

**Repo:** https://github.com/getsentry/agents-md

**Type:** workflow-skill

## Why this is useful
Standardizes agent instructions (AGENTS.md) across repos.

## How to integrate with Antigravity + Vibe
Add a /vibe-agent-contract workflow to generate/maintain AGENTS.md.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
