"""Dive Coder MCP server (minimal, offline-first).

This implements a *small* subset of MCP-like behavior for Antigravity integration.

Design goals:
- Python stdlib only (no heavy deps)
- Supports stdio JSON-RPC (line-delimited JSON) OR HTTP JSON-RPC
- Exposes tool calls that shell out to the existing Dive/V13 CLI

NOTE: This is a compatibility shim. If you prefer the official MCP SDK, create an
adapter under `antigravity_plugin/mcp/sdk_server.py` and keep this as fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional


def _write_event(log_path: str, event: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        # Never crash tool execution because UI logging failed.
        pass


def _run_cmd(cmd: list[str], cwd: Optional[str], env: Optional[Dict[str, str]]) -> Dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return {
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def _tool_dive_rag_ingest(args: Dict[str, Any]) -> Dict[str, Any]:
    repo = args.get("repo", ".")
    spec = args.get("spec", ".vibe/inputs/v13/rag_spec.yml")
    cmd = ["python3", ".shared/vibe-coder-v13/vibe.py", "rag", "ingest", "--repo", repo, "--spec", spec]
    return _run_cmd(cmd, cwd=repo, env=os.environ.copy())


def _tool_dive_rag_query(args: Dict[str, Any]) -> Dict[str, Any]:
    repo = args.get("repo", ".")
    kb = args.get("kb", ".vibe/kb")
    query = args.get("query")
    if not query:
        return {"error": "Missing required field: query"}
    cmd = ["python3", ".shared/vibe-coder-v13/vibe.py", "rag", "query", "--repo", repo, "--kb", kb, "--query", query]
    return _run_cmd(cmd, cwd=repo, env=os.environ.copy())


def _tool_dive_rag_eval(args: Dict[str, Any]) -> Dict[str, Any]:
    repo = args.get("repo", ".")
    eval_spec = args.get("eval_spec", ".vibe/inputs/v13/rag_eval.yml")
    cmd = ["python3", ".shared/vibe-coder-v13/vibe.py", "rag", "eval", "--repo", repo, "--eval", eval_spec]
    return _run_cmd(cmd, cwd=repo, env=os.environ.copy())


TOOLS = {
    "dive_rag_ingest": _tool_dive_rag_ingest,
    "dive_rag_query": _tool_dive_rag_query,
    "dive_rag_eval": _tool_dive_rag_eval,
}


def handle_rpc(req: Dict[str, Any], log_path: str) -> Dict[str, Any]:
    method = req.get("method")
    rpc_id = req.get("id")

    if method == "tools/list":
        result = [{"name": name, "description": fn.__doc__ or ""} for name, fn in TOOLS.items()]
        return {"jsonrpc": "2.0", "id": rpc_id, "result": result}

    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Unknown tool: {name}"}}

        _write_event(log_path, {"type": "tool_call", "tool": name, "arguments": arguments})
        out = TOOLS[name](arguments)
        _write_event(log_path, {"type": "tool_result", "tool": name, "result": out})
        return {"jsonrpc": "2.0", "id": rpc_id, "result": out}

    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def run_stdio(log_path: str) -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        resp = handle_rpc(req, log_path)
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


class _Handler(BaseHTTPRequestHandler):
    server_version = "DiveCoderMCP/0.1"

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        try:
            req = json.loads(body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"invalid json")
            return

        resp = handle_rpc(req, self.server.log_path)
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):  # noqa: A003
        return


def run_http(host: str, port: int, log_path: str) -> None:
    httpd = HTTPServer((host, port), _Handler)
    httpd.log_path = log_path
    httpd.serve_forever()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transport", choices=["stdio", "http"], default=os.getenv("DIVE_MCP_TRANSPORT", "stdio"))
    ap.add_argument("--host", default=os.getenv("DIVE_MCP_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("DIVE_MCP_PORT", "8765")))
    ap.add_argument("--log", default=os.getenv("DIVE_MCP_LOG", ".vibe/logs/dive_mcp_events.jsonl"))
    args = ap.parse_args()

    if args.transport == "stdio":
        run_stdio(args.log)
        return 0

    run_http(args.host, args.port, args.log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
