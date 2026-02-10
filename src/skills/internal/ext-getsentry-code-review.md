# Sentry Skill: code-review

**Repo:** https://github.com/getsentry/code-review

**Type:** workflow-skill

## Why this is useful
Repeatable review workflow; good patterns for PR feedback.

## How to integrate with Antigravity + Vibe
Port workflow steps into Antigravity /vibe-review + /vibe-pr.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
