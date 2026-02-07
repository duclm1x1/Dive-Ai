# /vibe-dag

Run a deterministic DAG (policy-gated shell commands) for CI-like flows.

Spec format (YAML/JSON):
```yaml
nodes:
  - id: lint
    type: shell
    cmd: ["npm","run","lint"]
  - id: test
    deps: [lint]
    type: shell
    cmd: ["npm","test"]
```

Run:
```bash
python3 .shared/vibe-coder-v13/vibe.py dag-run --repo . --spec .vibe/dag.yml --out .vibe/reports/vibe-dag.json
```
