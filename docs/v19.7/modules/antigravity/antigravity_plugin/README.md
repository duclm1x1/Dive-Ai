# Dive Coder v14.4 — Antigravity Plugin (skeleton)

Goal: package Dive Coder as a **separate plugin** that Antigravity can load / call.

This is a *production-oriented skeleton*:
- offline-first by default
- can be used as a **local tool server** (HTTP) and/or **MCP server** (stdio)
- writes an **activity ledger** + links to EvidencePack/claims outputs so UI can render runs

## 1) Why this exists
Antigravity usually needs 2 things:
1. **Tool surface**: functions it can call (ingest/query/eval/run pipelines)
2. **Observability/UI surface**: a tab or view to see what Dive Coder is doing

This plugin provides both (tool server + run ledger). UI embedding depends on Antigravity's extension API;
if Antigravity supports embedding a URL or a WebView tab, point it at the dashboard.

## 2) Start (HTTP mode)
```bash
python -m antigravity_plugin.server --transport http --port 8765 --repo_root .
# then open:
# http://127.0.0.1:8765/ui
```

Endpoints:
- `GET /health`
- `GET /tools`
- `POST /call`  `{ "tool": "rag.query", "args": {...} }`
- `GET /ui`  small dashboard (read-only)

## 3) Start (MCP stdio mode)
This is a thin shim intended to be wired into Antigravity's MCP client.
```bash
python -m antigravity_plugin.server --transport stdio --repo_root .
```

> Note: this repository ships a **minimal MCP compatibility shim** (no heavy deps). If your Antigravity runtime
> expects full MCP semantics, install the official MCP SDK and switch the adapter (TODO in code).

## 4) Where logs go
- Run ledger (JSONL): `.vibe/artifacts/antigravity/ledger.jsonl`
- EvidencePack + claims: whatever your existing v13-rag report output writes (linked from ledger entries)

## 5) Next steps (what you still need)
- Decide transport used by Antigravity (stdio vs http) based on deployment constraints.
- (If you want a native Antigravity tab) implement an Antigravity extension that renders `ledger.jsonl` + latest EvidencePack.
