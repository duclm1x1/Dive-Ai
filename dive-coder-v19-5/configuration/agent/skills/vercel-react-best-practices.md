---
name: vercel-react-best-practices
version: 1.0
category: react,nextjs,performance,best-practices
source_repo: vercel-labs/agent-skills
source_path: skills/react-best-practices
---

# Vercel: React Best Practices (Agent Skills)

## What this adds
A high-signal ruleset from Vercel Engineering focused on **React + Next.js performance and best practices**. Use it as a *reference skill* when reviewing or generating React code.

## Install (Agent Skills compatible)
If your agent environment supports `add-skill`:

```bash
npx add-skill vercel-labs/agent-skills
```

Then ensure the agent can load the skill folder:
- `skills/react-best-practices/`

## How Vibe Coder should use it
- During React/Next review, when encountering:
  - cascading or redundant `useEffect`
  - heavy client-side imports / large bundles
  - unnecessary re-renders
  - client/server boundary misuse
- Prefer recommendations grounded in this skill.

## Output contract
When referencing this skill, include in findings:
- `reference.skill = "vercel-react-best-practices"`
- `reference.source = "vercel-labs/agent-skills/skills/react-best-practices"`
