# Sentry Skill: deslop

**Repo:** https://github.com/getsentry/deslop

**Type:** workflow-skill

## Why this is useful
Cleanup sloppy code; pairs well with diff-aware autopatch.

## How to integrate with Antigravity + Vibe
Use as a source for refactor heuristics & safe transformations.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
