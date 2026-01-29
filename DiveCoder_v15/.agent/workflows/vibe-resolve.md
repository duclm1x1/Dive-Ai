# /vibe-resolve

Verification loop mặc định (review → resolve → gates → SARIF → PR-ready summary).

## Command

```bash
python3 .shared/vibe-coder-v13/vibe.py resolve \
  --repo . \
  --confidence 80 \
  --run-gates \
  --patch-out .vibe/reports/vibe-resolve.patch \
  --out .vibe/reports/vibe-resolve.json \
  --md-out .vibe/reports/vibe-resolve.md \
  --sarif-out .vibe/reports/vibe-resolve.sarif.json
```

- Default: chỉ generate patch. Apply patch khi policy cho phép `--apply`.
