# /vibe-docs

Mục tiêu: sinh docs markdown từ report JSON.

## Steps

```bash
python3 .shared/vibe-coder-v13/vibe.py docs --report .vibe/reports/vibe-report.json --out docs/vibe-report.md
```

Output:
- `docs/vibe-report.md`


## Skill usage (auto)

Before writing the final answer:
1. Read the relevant **always-on base skills** from `.agent/skills/`.
2. If `detected_stacks` is non-empty, read the matching stack skills (React/Next/Nest/Tailwind/Python).
3. If any finding severity >= high, consult security-oriented external entries from `.agent/skills/vibe-external-skills-catalog.md`.

In the final response, include a short section:
- **Skills Used**: list skill markdown files that were used.
