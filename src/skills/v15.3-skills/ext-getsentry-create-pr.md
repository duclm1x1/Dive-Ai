# Sentry Skill: create-pr

**Repo:** https://github.com/getsentry/create-pr

**Type:** workflow-skill

## Why this is useful
PR hygiene; templates and checklists.

## How to integrate with Antigravity + Vibe
Integrate with Vibe’s report -> PR description generator.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
