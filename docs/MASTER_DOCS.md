# Dive AI v20 — MASTER DOCS (Unified)

## Quickstart
```bash
cd dive-ai/v20/coder
pip install -r requirements.txt
cd ..
python runtime/main.py
```

## Architecture
- **Coder** (`v20/coder`) is the heart: engine + workflows + tools + skills execution + UI.
- **Orchestrator** (`v20/orchestrator`) is thin: management + orchestration + multi-LLM client.
- **Skills** unified: `v20/skills/internal` and `v20/skills/external` (full catalog).

## Archive-safe guarantee
`archive/` is reference-only. v20 should run without it.
Checklist:
1) No runtime code/config references `archive/` or old version paths (v13/v15/v17/v19).
2) Smoke test: start system, load skills, run one workflow.
3) Delete `archive/` and repeat smoke test.
