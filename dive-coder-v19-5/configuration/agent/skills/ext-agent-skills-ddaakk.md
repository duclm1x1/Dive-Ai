# Agent Skills (ddaakk)

**Repo:** https://github.com/ddaakk/agent-skills

**Type:** skill-pack

## Why this is useful
Small, practical skill pack; sometimes tailored for Cursor/Claude usage.

## How to integrate with Antigravity + Vibe
Import selectively (avoid duplicating rules already covered by Vibe).

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
