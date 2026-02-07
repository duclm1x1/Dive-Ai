# Agent Skills (spec + SDK)

**Repo:** https://github.com/agentskills/agentskills

**Type:** spec/sdk

## Why this is useful
Reference spec + tooling for skills as portable, composable capability units.

## How to integrate with Antigravity + Vibe
Use as a standard for skill metadata + installation conventions.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
