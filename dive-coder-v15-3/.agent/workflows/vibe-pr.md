# /vibe-pr

Mục tiêu: review theo **git diff** (tập trung vào thay đổi trong PR/branch).

## Steps

1. Xác định base branch (ưu tiên `origin/main`, fallback `main`):

```bash
git rev-parse --verify origin/main >/dev/null 2>&1 && echo origin/main || echo main
```

2. Chạy diff review:

```bash
BASE=$(git rev-parse --verify origin/main >/dev/null 2>&1 && echo origin/main || echo main)
python3 .shared/vibe-coder-v13/vibe.py review --repo . --mode balanced --diff-base "$BASE" \
  --out .vibe/reports/vibe-pr-report.json \
  --md-out docs/vibe-pr-report.md
```

3. Output:
- Chỉ tập trung vào findings thuộc changed files
- Propose small diffs + unit tests


## Skill usage (auto)

Before writing the final answer:
1. Read the relevant **always-on base skills** from `.agent/skills/`.
2. If `detected_stacks` is non-empty, read the matching stack skills (React/Next/Nest/Tailwind/Python).
3. If any finding severity >= high, consult security-oriented external entries from `.agent/skills/vibe-external-skills-catalog.md`.

In the final response, include a short section:
- **Skills Used**: list skill markdown files that were used.
