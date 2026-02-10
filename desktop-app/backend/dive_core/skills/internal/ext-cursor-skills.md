# Cursor Skills (cursor-skills)

**Repo:** https://github.com/chrisboden/cursor-skills

**Type:** skills-infra

## Why this is useful
Skill discovery/invoke tooling + MCP server concepts; useful for scaling skill libraries.

## How to integrate with Antigravity + Vibe
Use as reference if you turn Vibe into an MCP tool server.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
