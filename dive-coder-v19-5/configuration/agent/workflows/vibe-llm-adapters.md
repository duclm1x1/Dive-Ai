# Vibe Workflow: LLM Adapters (Claude / Antigravity / Any LLM) — v13

> Goal: run the **same Vibe Coder v13 OS** across different LLMs with *minimal drift*.
> This workflow provides **provider-ready system prompts**, **output contracts**, and **tooling expectations**.

---

## Core invariants (must hold on every model)

1) **Single mode per response** (`MODE: architect|coder|debugger|build`)
2) **No hallucinated repo facts** (paths/symbols/tests/tools)
3) **Preflight fail** when missing inputs
4) **Evidence levels** E0–E3 and **claims ledger** discipline
5) **Pointers** for code references: `relpath + symbol + start_line–end_line`

If a model cannot reliably satisfy these invariants in free-form chat, force it to output **structured JSON** (see below).

---

## Provider prompt packs

### A) Universal System Prompt (recommended default)
Use the **Vibe Coder v13 Master Prompt** as your system prompt (or first message) and add:

- **Always output** the 6-section format:
  `MODE / CONTEXT / PLAN / ACTION / VERIFICATION / OUTPUT`
- **Never claim tool runs** unless the tool output/artifact is present.

### B) Claude (Anthropic) adapter notes
Claude is strong at long-context planning; enforce determinism via:

- Keep the V13 Master Prompt in the **system** message.
- Put task-specific instructions in the **user** message.
- Require JSON when executing workflows that must be machine-checked (build, security).

**Recommended: Structured Output Envelope**
Ask Claude to wrap outputs in:

```json
{
  "mode": "debugger",
  "context": { "understanding": "...", "assumptions": [] },
  "plan": ["..."],
  "action": { "pointers": [], "changes": [], "artifacts": [] },
  "verification": { "gates": [], "evidence_level": "E2" },
  "output": { "result": "...", "next_steps": [] }
}
```

### C) Antigravity adapter notes
Antigravity orchestrators typically support **skill execution pipelines**.
Ensure:
- The orchestrator passes `repo_root`, `outdir`, and `policy` to tools.
- The orchestrator captures artifacts into `.vibe/` and includes them in EvidencePack.

---

## “Any LLM” fallback: strict JSON protocol (zero ambiguity)
When model reliability is uncertain, **force a strict JSON response**:

```json
{
  "mode": "architect",
  "preflight": {
    "missing_inputs": [],
    "ready": true
  },
  "pointers": [
    { "path": "src/x.py", "symbol": "Foo.bar", "start": 10, "end": 42 }
  ],
  "evidence": {
    "level": "E0",
    "artifacts": []
  },
  "actions": [],
  "verification": [],
  "next_steps": []
}
```

If `preflight.ready=false`, the model must stop.

---

## Tooling expectations
- **Search/Index**: use V13 hybrid retrieval (symbol + FTS + vector) where available.
- **Build/Gates**: tools produce artifacts, hashed into EvidencePack.
- **Baseline gate (E3)**: build fails on regressions unless explicitly allowed.

---

## Common failure modes & mitigations
- **Governance theater** (claiming tool runs without artifacts) → enforce claims ledger + CI validator.
- **Pointer hallucination** → require grounded pointers or fail.
- **Over-broad patches** → enforce patch safety (max files, no formatting churn).

