# /vibe-autopatch

Mục tiêu: tạo patch an toàn (safe autopatch).

- **Full-file whitespace/newline EOF**: có thể `--apply` (policy cho phép).
- **Diff-aware**: nếu set `--diff-base`, autopatch chỉ generate patch cho các hunk đã thay đổi (không auto-apply).

## Generate patches (no write)

```bash
python3 .shared/vibe-coder-v13/vibe.py autopatch --repo . --mode balanced \
  --out .vibe/reports/vibe-autopatch.json
```

## Diff-aware patch (reviewdog / git apply)

```bash
python3 .shared/vibe-coder-v13/vibe.py autopatch --repo . --mode balanced --diff-base origin/main \
  --out .vibe/reports/vibe-autopatch.json \
  --patch-out .vibe/reports/vibe-autopatch.patch
```

## Apply patches (requires policy allow_write + allow_autofix)

1. Copy policy sample và bật write/autofix:

```bash
cp .shared/vibe-coder-v13/policy.sample.json .shared/vibe-coder-v13/policy.json
# edit file: set allow_write=true, allow_autofix=true
```

2. Apply:

```bash
python3 .shared/vibe-coder-v13/vibe.py autopatch --repo . --mode balanced --apply \
  --policy .shared/vibe-coder-v13/policy.json \
  --out .vibe/reports/vibe-autopatch-applied.json
```

3. Run gates (manual):
- Python: `ruff check && pytest`
- Node: `npm run lint && npm test && npm run build`


## Skill usage (auto)

Before writing the final answer:
1. Read the relevant **always-on base skills** from `.agent/skills/`.
2. If `detected_stacks` is non-empty, read the matching stack skills (React/Next/Nest/Tailwind/Python).
3. If any finding severity >= high, consult security-oriented external entries from `.agent/skills/vibe-external-skills-catalog.md`.

In the final response, include a short section:
- **Skills Used**: list skill markdown files that were used.
