# expo_production: Release Management (versioning/changelog/rollback)

## Goal
Ship frequently with controlled risk: deterministic versioning, reproducible builds, fast rollback.

## Outputs
- `release/versioning.md` (scheme + rules)
- `release/changelog.md` (automation rules + format)
- `release/release_checklist.md`
- `release/rollback_plan.md`
- `release/build_provenance.md` (artifacts/hashes)
- `release/evidencepack.json` (E3)

## A–Z Checklist
1. Pick versioning scheme (SemVer + build metadata, or CalVer).
2. Automate changelog generation (PR labels → sections).
3. Define environments: dev/stage/prod + promotion rules.
4. Gate: typecheck + unit tests + build + security baseline compare.
5. Release artifact provenance: hashes + toolchain versions.
6. Rollback playbooks:
   - App store rollback path (if possible) and/or feature flags.
   - EAS update rollback (channel-based) for Expo Updates.
7. Post-release monitoring: crash spikes, auth failures, latency.
8. Release notes + comms template.
9. Incident link: releases must attach run_id/evidencepack id.

## Validators
- Release artifacts exist & hashed.
- Rollback procedure documented and tested in staging.
- Changelog includes breaking changes and migrations.

