# kitwork-engine (integration skill)

## Classification
- **Type:** Integration Skill (external runtime/workflow engine), not a Base Skill.
- **Why:** Dive Coder is an AI coding OS; Kitwork Engine is a high-performance DSL/VM runtime for executing business logic and workflows.

## What it enables in Dive Coder
- Embed a programmable workflow runtime behind `build-n8n`-like automation without requiring n8n.
- Use as an optional execution backend for “workflow-mode” templates (server-side execution, HTTP router triggers).
- Integrate as a target in templates: generate Kitwork scripts + Go host + tests + benchmarks.

## Constraints
- License is **AGPL-3.0** (impacts distribution and SaaS usage).
- Treat as optional plugin; require explicit opt-in.

## Minimal adapter plan
- `dive provider workflow-engine kitwork`:
  - scaffold `cmd/server` + `work` scripts
  - run `go test -bench` for evidence (E2)
  - pack EvidencePack (E3)
