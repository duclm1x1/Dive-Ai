# Workflow: EvidencePack

Generate a deterministic EvidencePack from CI/CD or Canary.

## Local (developer)

```bash
python3 .shared/vibe-coder-v13/vibe.py review --repo . --mode accuracy --run-gates \
  --out .vibe/reports/vibe-report.json --md-out .vibe/reports/vibe-report.md --sarif-out .vibe/reports/vibe.sarif.json

python3 .shared/vibe-coder-v13/vibe.py evidencepack --repo . --issue-id IKO-123 --outdir .vibe/evidence --ci-run-id local
```

## CI/CD

Use the template workflow `.github/workflows/vibe-evidencepack.yml`.

## Notes

- EvidencePack is a pointer bundle + checksums. Do not stuff huge logs into the JSON.
- Gatekeeper requires EvidencePack for state changes beyond INVESTIGATING.
