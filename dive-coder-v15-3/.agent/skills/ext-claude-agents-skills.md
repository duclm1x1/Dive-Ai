# Claude Agents & Skills

**Repo:** https://github.com/agentsoflearning/claude-agents-skills

**Type:** agent-pack

## Why this is useful
Agent personas + workflows for SDLC; useful for orchestration patterns.

## How to integrate with Antigravity + Vibe
Port workflows to .agent/workflows where useful.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
