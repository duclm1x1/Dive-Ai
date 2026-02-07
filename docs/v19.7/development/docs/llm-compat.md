# LLM Compatibility — Vibe Coder v13

This repo is designed to run consistently across:

- Claude (Anthropic)
- Antigravity orchestrators
- Any other LLM that can follow deterministic contracts

Key idea: **artifact-first governance**.
When the model cannot be trusted to be precise, force **strict JSON** outputs and validate artifacts with the CLI.

See: `.agent/workflows/vibe-llm-adapters.md`
