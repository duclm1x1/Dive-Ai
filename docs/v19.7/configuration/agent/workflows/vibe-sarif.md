# /vibe-sarif

Mục tiêu: xuất report sang **SARIF** để dùng với CI / GitHub code scanning.

## Steps

1. Đảm bảo đã có report JSON (từ `/vibe-review` hoặc `/vibe-pr`).

2. Export SARIF:

```bash
python3 .shared/vibe-coder-v13/vibe.py sarif --report .vibe/reports/vibe-report.json --out .vibe/reports/vibe.sarif
```

3. Output
- file `.vibe/reports/vibe.sarif`
