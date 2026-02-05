# Documentation Auto

## Nguyên tắc

- Code thay đổi => docs thay đổi.
- Mỗi module public có: mục tiêu, input/output, error cases.

## Tự động hoá với Vibe v11

Workflow `/vibe-docs` sẽ:

- Đọc JSON report.
- Sinh `docs/vibe-report.md`.
- Nếu chỉ cần new findings: sinh `docs/vibe-new-findings.md`.

## Gợi ý thêm (optional)

- MkDocs / Docusaurus cho docs site.
- TypeDoc (TS) / Compodoc (NestJS).
