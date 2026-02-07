# /vibe-baseline

Mục tiêu: thiết lập baseline và phát hiện regression (chỉ report new findings).

## Option A: Set baseline

```bash
python3 .shared/vibe-coder-v13/vibe.py baseline set --repo . --mode balanced --filename baseline.json
```

## Option B: Compare against baseline

```bash
python3 .shared/vibe-coder-v13/vibe.py baseline compare --repo . --mode balanced \
  --baseline .vibe/baseline.json \
  --out .vibe/reports/vibe-new-findings.json \
  --md-out docs/vibe-new-findings.md
```

## Output

- Nếu `new_findings` rỗng => OK.
- Nếu có => prioritize theo severity và confidence.
