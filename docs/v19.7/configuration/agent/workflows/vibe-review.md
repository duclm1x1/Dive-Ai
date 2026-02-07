# /vibe-review

Mục tiêu: chạy Vibe Coder v11 review **repo-level** và trả về action plan.

## Steps

1. Chạy tool:

```bash
python3 .shared/vibe-coder-v13/vibe.py review --repo . --mode balanced \
  --out .vibe/reports/vibe-report.json \
  --md-out docs/vibe-report.md
```

2. Đọc `.vibe/reports/vibe-report.json` và `docs/vibe-report.md`.

3. Output cho user:
- Score + top 10 action items.
- Nhóm theo: Security / Bug / Architecture / Style.
- Đề xuất gates cần chạy tiếp.

4. Nếu có finding `high/critical`: propose patch plan + test plan.


## Skill usage (auto)

Before writing the final answer:
1. Read the relevant **always-on base skills** from `.agent/skills/`.
2. If `detected_stacks` is non-empty, read the matching stack skills (React/Next/Nest/Tailwind/Python).
3. If any finding severity >= high, consult security-oriented external entries from `.agent/skills/vibe-external-skills-catalog.md`.

In the final response, include a short section:
- **Skills Used**: list skill markdown files that were used.
