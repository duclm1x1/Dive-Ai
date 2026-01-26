# Agents (wshobson)

**Repo:** https://github.com/wshobson/agents

**Type:** agent-ecosystem

## Why this is useful
Large plugin ecosystem for agents; good reference for modularity.

## How to integrate with Antigravity + Vibe
Use as inspiration for plug-in boundaries; import selectively.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
