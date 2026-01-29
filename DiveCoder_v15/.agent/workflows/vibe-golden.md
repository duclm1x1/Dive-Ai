# /vibe-golden

Mục tiêu: tạo **golden config scaffolds** cực conservative (create-only) cho repo.

- Không overwrite file đang tồn tại.
- Output patch dạng unified diff để apply qua `git apply` hoặc reviewdog.

## Generate patch

```bash
python3 .shared/vibe-coder-v13/vibe.py golden --repo . \
  --out .vibe/reports/vibe-golden.json \
  --patch-out .vibe/reports/vibe-golden.patch
```

## Apply patch manually

```bash
git apply .vibe/reports/vibe-golden.patch
```

## Apply via CLI (requires policy allow_write + allow_autofix)

```bash
cp .shared/vibe-coder-v13/policy.sample.json .shared/vibe-coder-v13/policy.json
# edit: allow_write=true, allow_autofix=true

python3 .shared/vibe-coder-v13/vibe.py golden --repo . --apply \
  --policy .shared/vibe-coder-v13/policy.json \
  --out .vibe/reports/vibe-golden-applied.json
```
