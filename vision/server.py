"""Antigravity plugin server for Dive Coder.

This provides two transports:
- HTTP: local control plane + small dashboard (stdlib http.server)
- STDIO: minimal JSON-RPC style shim (for IDE tool runners)

Design constraints:
- offline-first
- dependency-light (stdlib only)

If you need full MCP protocol compatibility, add an adapter using the official MCP SDK.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Callable

# Import Dive Coder / V13 style modules
REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_path(repo_root: str | None) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    return REPO_ROOT


def _artifact_dir(repo_root: Path) -> Path:
    d = repo_root / '.vibe' / 'artifacts' / 'antigravity'
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append_ledger(repo_root: Path, entry: Dict[str, Any]) -> None:
    ledger = _artifact_dir(repo_root) / 'ledger.jsonl'
    entry = dict(entry)
    entry.setdefault('ts', time.time())
    with ledger.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[[Path, Dict[str, Any]], Dict[str, Any]]


def _tool_rag_query(repo_root: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    """Query the RAG engine.

    Args:
        query: str
        kb_path: optional (default .vibe/kb)
        top_k: int
    """
    query = args.get('query') or ''
    top_k = int(args.get('top_k', 5))
    kb_path = Path(args.get('kb_path') or (repo_root / '.vibe' / 'kb')).resolve()

    # Lazy import to keep server start fast
    sys.path.insert(0, str(repo_root / '.shared' / 'vibe-coder-v13'))
    from rag.engine import AdvancedRAG  # type: ignore

    rag = AdvancedRAG(kb_path=str(kb_path))
    result = rag.query(query=query, top_k=top_k)

    _append_ledger(repo_root, {
        'event': 'tool_call',
        'tool': 'rag.query',
        'args': {'query': query, 'top_k': top_k, 'kb_path': str(kb_path)},
        'ok': True,
    })
    return {'ok': True, 'result': result}


def _tool_rag_ingest(repo_root: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest documents into the KB."""
    input_path = Path(args.get('input_path') or repo_root).resolve()
    kb_path = Path(args.get('kb_path') or (repo_root / '.vibe' / 'kb')).resolve()

    sys.path.insert(0, str(repo_root / '.shared' / 'vibe-coder-v13'))
    from rag.engine import AdvancedRAG  # type: ignore

    rag = AdvancedRAG(kb_path=str(kb_path))
    stats = rag.ingest(path=str(input_path))

    _append_ledger(repo_root, {
        'event': 'tool_call',
        'tool': 'rag.ingest',
        'args': {'input_path': str(input_path), 'kb_path': str(kb_path)},
        'ok': True,
    })
    return {'ok': True, 'stats': stats}


TOOLS: list[Tool] = [
    Tool('rag.query', 'Query DiveCoder RAG', _tool_rag_query),
    Tool('rag.ingest', 'Ingest docs into DiveCoder KB', _tool_rag_ingest),
]


def _tool_map() -> Dict[str, Tool]:
    return {t.name: t for t in TOOLS}


class _Handler(BaseHTTPRequestHandler):
    server_version = 'DiveCoderAntigravity/0.1'

    def _json(self, code: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == '/health':
            return self._json(200, {'ok': True})
        if self.path == '/tools':
            return self._json(200, {
                'tools': [{'name': t.name, 'description': t.description} for t in TOOLS]
            })
        if self.path.startswith('/ui'):
            return self._serve_ui()
        return self._json(404, {'ok': False, 'error': 'not_found'})

    def _serve_ui(self):
        repo_root: Path = self.server.repo_root  # type: ignore[attr-defined]
        ledger = _artifact_dir(repo_root) / 'ledger.jsonl'
        rows = []
        if ledger.exists():
            rows = ledger.read_text(encoding='utf-8').splitlines()[-200:]

        html = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Dive Coder — Activity</title>
  <style>
    body{font-family:ui-sans-serif,system-ui;margin:16px;}
    pre{background:#f6f6f6;padding:12px;border-radius:8px;overflow:auto;}
    .hint{color:#666;margin-bottom:12px;}
  </style>
</head>
<body>
  <h2>Dive Coder (Antigravity Plugin) — Activity Ledger</h2>
  <div class='hint'>Source: .vibe/artifacts/antigravity/ledger.jsonl (last 200 lines)</div>
  <pre id='log'></pre>
  <script>
    const rows = %s;
    document.getElementById('log').textContent = rows.join('\n');
  </script>
</body>
</html>""" % (json.dumps(rows))

        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        if self.path != '/call':
            return self._json(404, {'ok': False, 'error': 'not_found'})

        length = int(self.headers.get('Content-Length', '0'))
        data = self.rfile.read(length) if length > 0 else b'{}'
        try:
            payload = json.loads(data.decode('utf-8'))
        except Exception:
            return self._json(400, {'ok': False, 'error': 'invalid_json'})

        tool = payload.get('tool')
        args = payload.get('args') or {}
        repo_root: Path = self.server.repo_root  # type: ignore[attr-defined]

        t = _tool_map().get(tool)
        if not t:
            return self._json(404, {'ok': False, 'error': f'unknown_tool: {tool}'})

        try:
            out = t.handler(repo_root, dict(args))
            return self._json(200, out)
        except Exception as e:
            _append_ledger(repo_root, {
                'event': 'tool_call',
                'tool': tool,
                'args': args,
                'ok': False,
                'error': str(e),
            })
            return self._json(500, {'ok': False, 'error': str(e)})


def serve_http(repo_root: Path, host: str, port: int) -> None:
    httpd = HTTPServer((host, port), _Handler)
    httpd.repo_root = repo_root  # type: ignore[attr-defined]
    print(f"[antigravity_plugin] HTTP listening on http://{host}:{port} (repo_root={repo_root})", file=sys.stderr)
    httpd.serve_forever()


def serve_stdio(repo_root: Path) -> None:
    """A *minimal* JSON-RPC-ish stdio shim.

    This is NOT full MCP, but works for simple 'tool list' and 'tool call' patterns.
    Message format:
        {"id": "1", "method": "tools/list", "params": {}}
        {"id": "2", "method": "tools/call", "params": {"name":"rag.query","arguments":{...}}}

    Response:
        {"id":"1","result":{...}}
        {"id":"2","result":{...}} or {"id":"2","error":{...}}
    """

    tools = [{'name': t.name, 'description': t.description} for t in TOOLS]
    _append_ledger(repo_root, {'event': 'server_start', 'transport': 'stdio'})

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue

        mid = msg.get('id')
        method = msg.get('method')
        params = msg.get('params') or {}

        try:
            if method in ('tools/list', 'list_tools'):
                out = {'tools': tools}
            elif method in ('tools/call', 'call_tool'):
                name = params.get('name')
                arguments = params.get('arguments') or {}
                t = _tool_map().get(name)
                if not t:
                    raise KeyError(f'unknown_tool: {name}')
                out = t.handler(repo_root, dict(arguments))
            else:
                raise KeyError(f'unknown_method: {method}')

            resp = {'id': mid, 'result': out}
        except Exception as e:
            resp = {'id': mid, 'error': {'message': str(e)}}

        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + '\n')
        sys.stdout.flush()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--transport', choices=['http','stdio'], default='http')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--repo_root', default=None)
    args = p.parse_args()

    repo_root = _ensure_repo_path(args.repo_root)

    if args.transport == 'http':
        serve_http(repo_root, args.host, args.port)
        return 0
    serve_stdio(repo_root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
