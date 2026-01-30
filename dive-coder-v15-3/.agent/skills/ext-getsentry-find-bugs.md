# Sentry Skill: find-bugs

**Repo:** https://github.com/getsentry/find-bugs

**Type:** workflow-skill

## Why this is useful
Bug discovery workflow; aligns with QA/Debugging.

## How to integrate with Antigravity + Vibe
Integrate as a “bug sweep” workflow on PR diff.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
