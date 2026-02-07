# Antigravity integration (plugin-style)

This repo ships a **plugin-style bundle** under `antigravity_plugin/`:

- `mcp/server.py`: local MCP-like server (stdlib-only) exposing Dive RAG tools.
- `configs/mcp_servers.json`: template you can copy into your Antigravity workspace.
- `extension/`: optional UI tab (VSIX skeleton) to visualize Dive Coder activity.

## 1) MCP transport: stdio vs http

Antigravity supports `stdio` and `http` transports for MCP servers. `stdio` is best for local tools; `http` is best for remote/containerized services. The config schema typically includes `transport`, `command/args` for stdio, and `url` for http. See Antigravity MCP docs and common templates. citeturn2view0turn1search6

## 2) Quick start (stdio)

From repo root:

```bash
export PYTHONPATH=.
python3 antigravity_plugin/mcp/server.py --transport stdio
```

In Antigravity, add an MCP server pointing to that command (or use the provided `mcp_servers.json`).

## 3) Quick start (http)

```bash
export PYTHONPATH=.
python3 antigravity_plugin/mcp/server.py --transport http --host 127.0.0.1 --port 8765
```

Then configure Antigravity with `transport: "http"` and `url: "http://127.0.0.1:8765"`.

## 4) Tools exposed

- `tools/list`
- `tools/call` with tool names:
  - `dive_rag_ingest`
  - `dive_rag_query`
  - `dive_rag_eval`

Each call appends to `.vibe/logs/dive_mcp_events.jsonl` for UI visualization.
