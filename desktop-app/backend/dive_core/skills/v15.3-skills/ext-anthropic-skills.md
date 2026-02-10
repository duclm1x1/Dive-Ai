# Anthropic Skills

**Repo:** https://github.com/anthropics/skills

**Type:** skill-pack

## Why this is useful
High-quality skills library (software + ops).

## How to integrate with Antigravity + Vibe
Import skills selectively into .agent/skills/ (copy markdown).

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
