# External Skills & Tooling Catalog

This catalog is a *drop-in index* of external GitHub repos you can plug into Antigravity + Vibe Coder.

- Vibe Coder does **not vendor** these repos.
- Each entry is represented as a lightweight skill note so agents can discover and reference it consistently.

## How to use
- Copy a specific entry into your project skill stack (or fetch via an installer like add-skill).
- Keep Vibe as the *quality gate + review engine* and use these repos as *domain skill packs*.

## Entries

- **AgentScope (multi-agent framework)** — https://github.com/agentscope-ai/agentscope
  Type: `multi-agent-framework` • Developer-centric framework for building multi-agent systems (ReAct agents, memory, planning, RAG, MCP/A2A integrations).

- **Agent Skills (spec + SDK)** — https://github.com/agentskills/agentskills  
  Type: `spec/sdk` • Reference spec + tooling for skills as portable, composable capability units.

- **Vercel add-skill (installer)** — https://github.com/vercel-labs/add-skill  
  Type: `installer` • One-command installer (npx) to pull skill content from a Git repo into your agent skill directory.
- **n8n-skills (workflow automation skillset)** — https://github.com/czlonkowski/n8n-skills  
  Type: `skills-pack` • Claude Code skills for building production-ready n8n workflows using the n8n-mcp MCP server.

- **AIClient-2-API (provider gateway)** — https://github.com/justlovemaki/AIClient-2-API  
  Type: `provider-gateway` • Self-hosted OpenAI-compatible API gateway/proxy with protocol adapters and (advertised) pool + health/failover features. Prefer integrating as a separate service; do not vendor due to GPL-3.0.


- **Skillport (registry / load-on-demand)** — https://github.com/gotalab/skillport  
  Type: `registry` • Skill catalog + discovery for agent skills; helpful for scaling skill libraries.

- **Awesome Agent Skills (skillmatic-ai)** — https://github.com/skillmatic-ai/awesome-agent-skills  
  Type: `curated-list` • Curated list of skill packs + best practices; good source for continuous expansion.

- **Awesome Agent Skills (heilcheng)** — https://github.com/heilcheng/awesome-agent-skills  
  Type: `curated-list` • Another curated list with overlap + extra pointers.

- **Anthropic Skills** — https://github.com/anthropics/skills  
  Type: `skill-pack` • High-quality skills library (software + ops).

- **Vercel Agent Skills** — https://github.com/vercel-labs/agent-skills  
  Type: `skill-pack` • Engineering-grade skills, including React/Next.js best practices and web workflows.

- **Agent Skills for Context Engineering** — https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering  
  Type: `skill-pack` • Practices/templates for context shaping, routing, and reliable agent behavior.

- **AI Skills (strativd)** — https://github.com/strativd/ai-skills  
  Type: `skill-pack` • Starter pack of skills in markdown; simple to copy into Antigravity.

- **Claude Agents & Skills** — https://github.com/agentsoflearning/claude-agents-skills  
  Type: `agent-pack` • Agent personas + workflows for SDLC; useful for orchestration patterns.

- **Agents (wshobson)** — https://github.com/wshobson/agents  
  Type: `agent-ecosystem` • Large plugin ecosystem for agents; good reference for modularity.

- **UI/UX Pro Max Skill** — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill  
  Type: `design-skill` • Style vault + UX patterns; aligns with “Design Intelligence”.

- **React Agent Skills (jturner421)** — https://github.com/jturner421/react-agent-skills  
  Type: `frontend-skill-pack` • React-focused skills; complements Next.js workflows.

- **Agent Skills (ddaakk)** — https://github.com/ddaakk/agent-skills  
  Type: `skill-pack` • Small, practical skill pack; sometimes tailored for Cursor/Claude usage.

- **Cursor Skills (cursor-skills)** — https://github.com/chrisboden/cursor-skills  
  Type: `skills-infra` • Skill discovery/invoke tooling + MCP server concepts; useful for scaling skill libraries.

- **Sentry Skill: code-review** — https://github.com/getsentry/code-review  
  Type: `workflow-skill` • Repeatable review workflow; good patterns for PR feedback.

- **Sentry Skill: commit** — https://github.com/getsentry/commit  
  Type: `workflow-skill` • Commit quality conventions; helps reduce review churn.

- **Sentry Skill: create-pr** — https://github.com/getsentry/create-pr  
  Type: `workflow-skill` • PR hygiene; templates and checklists.

- **Sentry Skill: find-bugs** — https://github.com/getsentry/find-bugs  
  Type: `workflow-skill` • Bug discovery workflow; aligns with QA/Debugging.

- **Sentry Skill: deslop** — https://github.com/getsentry/deslop  
  Type: `workflow-skill` • Cleanup sloppy code; pairs well with diff-aware autopatch.

- **Sentry Skill: agents-md** — https://github.com/getsentry/agents-md  
  Type: `workflow-skill` • Standardizes agent instructions (AGENTS.md) across repos.

- **Trail of Bits: static-analysis** — https://github.com/trailofbits/static-analysis  
  Type: `tooling` • Practical guidance/tools for static analysis pipelines.

- **Trail of Bits: semgrep-rule-creator** — https://github.com/trailofbits/semgrep-rule-creator  
  Type: `tooling` • Helps build/refine Semgrep rules—useful for your stack rule packs.

- **Trail of Bits: differential-review** — https://github.com/trailofbits/differential-review  
  Type: `security-workflow` • Security-focused differential review; aligns with PR-mode scanning.

- **Trail of Bits: sharp-edges** — https://github.com/trailofbits/sharp-edges  
  Type: `security-knowledge-base` • Catalog of dangerous APIs/configs; great source for “policy” rules.

- **Trail of Bits: property-based-testing** — https://github.com/trailofbits/property-based-testing  
  Type: `testing-knowledge-base` • PBT patterns and guidance; improves test generation quality.

- **Anthropic: webapp-testing** — https://github.com/anthropics/webapp-testing  
  Type: `testing-skill` • Playwright-centric testing workflows; helps enterprise QA automation.

- **Awesome Antigravity (ZhangYu-zjut)** — https://github.com/ZhangYu-zjut/awesome-Antigravity  
  Curated Antigravity skills/resources registry.
