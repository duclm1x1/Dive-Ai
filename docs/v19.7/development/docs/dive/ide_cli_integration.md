# Dive Coder — IDE/CLI Integration (design spec)

Dive Coder is intended to be usable in:
- IDEs (VS Code, Cursor, JetBrains) via extension + local CLI
- CLI-only environments (Terminal) via `dive` commands
- Agent runtimes (Claude Code, Roo Code) via OpenAI-compatible gateway config

## Core integration primitives
1. **Project Rules / Agent Rules**
   - A single “Master Prompt” (V13) + per-mode templates.
2. **CLI entrypoint**
   - `dive mode apply <template>`
   - `dive mode run <template> --full`
   - `dive gates run ...`
3. **Workspace**
   - `.vibe/runs/<run_id>/` holds all artifacts, including E3 EvidencePack.
4. **Evidence**
   - E0–E3 Evidence Levels with claims ledger + validator outputs.

## Orbit-style installer (pattern)
Provide:
- `install.ps1` (Windows PowerShell)
- `install.sh` (macOS/Linux)
- `dive doctor` to verify toolchain & config

Installer responsibilities:
- install `git`, `python3`, `node` (optional), `semgrep` (optional)
- place `dive` binary (or python shim) on PATH
- write a **local** config file (never commit):
  - `~/.config/dive/config.json` (or OS equivalent)
- print next steps:
  - `dive doctor`
  - `dive mode run build-n8n --full`

## IDE wiring (VS Code / Cursor)
- Add a task runner that calls `dive mode run ...`
- Add a “Run EvidencePack” command that opens `.vibe/runs/<id>/evidencepack.json`

## Claude Code / Roo Code wiring
- Configure Base URL + Key + Model (OpenAI-compatible) via their provider settings.
