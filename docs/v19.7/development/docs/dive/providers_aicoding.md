# Dive Coder — Primary LLM Provider: aicoding.io.vn (Antigravity)

This repository can route requests to many LLMs via an **OpenAI-compatible gateway**.

## Gateway
- Base URL (OpenAI-compatible): `https://aicoding.io.vn/v1`
- Models: discover via `GET /v1/models`

> The gateway also exposes an **Anthropic-native** endpoint at `POST /v1/messages` via base `https://aicoding.io.vn` for clients that support it.

## Why this is primary
- OpenAI-compatible format enables broad IDE/CLI compatibility (Roo Code / Cline / Kilo Code-style clients).
- Supports multiple model families behind one key (model selection in config).

## Client configuration (generic)
Environment:
- `DIVE_BASE_URL=https://aicoding.io.vn/v1`
- `DIVE_API_KEY=YOUR_API_KEY`
- `DIVE_MODEL=claude-sonnet-4-5-20250929` (example)

## Security note
Never embed API keys in install commands or committed files. Use env vars or OS secret stores.
