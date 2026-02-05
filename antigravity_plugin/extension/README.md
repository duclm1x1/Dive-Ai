# Dive Coder Panel (Antigravity / VS Code compatible)

Antigravity can install VS Code extensions via VSIX, and many community extensions ship a **Webview dashboard** tab. citeturn1search1turn1search4

This folder is a skeleton placeholder.

## What you implement next

- Command: `Dive Coder: Open Panel`
- Webview UI:
  - tail log from `.vibe/logs/dive_mcp_events.jsonl`
  - show: last tool call, status, last eval report path, EvidencePack links
- Optional: buttons to run `dive_rag_ingest/eval` via MCP

Because VSIX builds require Node tooling, we keep this skeleton separate from the Python-only core.
