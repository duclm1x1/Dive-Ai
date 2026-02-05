# External integrations (Git repos worth plugging in)

Vibe Coder v11.x is designed to be a **quality gate + review engine**.
This file indexes external repos you can *plug in* (skills, workflows, tooling) without vendoring them.

- Full catalog: `vibe-external-skills-catalog.md`
- Individual lightweight notes: `ext-*.md`

## Quick guidance
- Prefer *copying only the needed skill markdown* into your repo’s `.agent/skills/`.
- If you need a one-command installer, use `vercel-labs/add-skill`.
- Treat security/testing tools (Semgrep, etc.) as **gates** that output SARIF and get merged.

- Registry: https://github.com/ZhangYu-zjut/awesome-Antigravity (curated Antigravity skills/resources)

- **n8n-skills (workflow automation)** — https://github.com/czlonkowski/n8n-skills  
  Use when building or reviewing n8n workflow automation; pairs well with n8n-mcp for node-level documentation.

- **AIClient-2-API (provider gateway / OpenAI-compatible)** — https://github.com/justlovemaki/AIClient-2-API  
  Use when you want a self-hosted gateway that presents a single OpenAI-compatible base URL while fronting multiple upstream providers. Treat it as an external service/provider and apply Dive Engine provider validation + EvidencePack governance.
