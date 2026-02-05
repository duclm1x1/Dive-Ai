# Sentry Skill: commit

**Repo:** https://github.com/getsentry/commit

**Type:** workflow-skill

## Why this is useful
Commit quality conventions; helps reduce review churn.

## How to integrate with Antigravity + Vibe
Add as optional workflow (commit message + change summary).

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
