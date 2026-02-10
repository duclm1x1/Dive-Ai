# /vibe-build

Build project từ spec theo phương pháp Vibe Coder (P0+P1):

1) Validate input spec (BẮT BUỘC PHẢI CÓ)
2) Scaffold repo thật (Next/Nest/Tailwind/n8n)
3) Run gates (theo vibe.config.yml)
4) Xuất report JSON/MD/SARIF

## Command

```bash
python3 .shared/vibe-coder-v13/vibe.py build \
  --kind <nextjs|nestjs|tailwind|website|n8n> \
  --spec <path/to/spec.yml> \
  --outdir <path/to/output_repo> \
  --run-gates \
  --out <path/to/report.json> \
  --md-out <path/to/report.md> \
  --sarif-out <path/to/report.sarif.json>
```
