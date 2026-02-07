# Vercel Agent Skills

**Repo:** https://github.com/vercel-labs/agent-skills

**Type:** skill-pack

## Why this is useful
Engineering-grade skills, including React/Next.js best practices and web workflows.

## How to integrate with Antigravity + Vibe
Copy skill markdowns into .agent/skills/ or use add-skill to fetch subpaths.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
