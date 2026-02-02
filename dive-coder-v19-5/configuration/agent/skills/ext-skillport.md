# Skillport (registry / load-on-demand)

**Repo:** https://github.com/gotalab/skillport

**Type:** registry

## Why this is useful
Skill catalog + discovery for agent skills; helpful for scaling skill libraries.

## How to integrate with Antigravity + Vibe
Use as inspiration for indexing/searching skills inside Antigravity.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
