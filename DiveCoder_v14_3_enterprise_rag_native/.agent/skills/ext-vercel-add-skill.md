# Vercel add-skill (installer)

**Repo:** https://github.com/vercel-labs/add-skill

**Type:** installer

## Why this is useful
One-command installer (npx) to pull skill content from a Git repo into your agent skill directory.

## How to integrate with Antigravity + Vibe
Expose via workflow: npx add-skill <repo_or_path> (policy-gated).

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
