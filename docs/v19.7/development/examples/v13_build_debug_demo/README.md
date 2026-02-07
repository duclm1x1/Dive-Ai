# V13 Build + Baseline Gate Demo

This demo validates that **build** mode:
- emits EvidencePack (E3)
- initializes a baseline on first run (E3 artifact)
- fails on baseline regressions (new findings) on subsequent runs

## Run

```bash
python examples/v13_build_debug_demo/run_demo.py
```

Expected:
- First build exit code = 0 (baseline-init gate writes `.vibe/baseline.json`)
- Second build exit code != 0 (baseline-compare gate detects new finding)

Artifacts:
- `out/.vibe/baseline.json`
- `out/.vibe/reports/baseline-compare.json`
- `out/.vibe/reports/vibe-build.evidencepack.json`
