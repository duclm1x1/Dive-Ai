# External Registry: Awesome Antigravity (ZhangYu-zjut)

Source: https://github.com/ZhangYu-zjut/awesome-Antigravity

## When to use
- Need more Antigravity-ready skills, workflows, configs, and examples.
- Need benchmarks / community conventions for Antigravity agents.

## How to integrate safely
- Treat as **registry**: do NOT vendor everything.
- Pick 1-3 skills relevant to current task, copy into `.agent/skills_external/`.
- If `skills.lock.json` enforcement is enabled, pin copied skills:
  - record `repo`, `commit`, `path`, `sha256`.

## Enterprise checks
- Verify license + provenance.
- Prefer single-purpose skills; avoid monolithic prompts.
- Ensure skills do not request unsafe tool calls.
