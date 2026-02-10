#!/usr/bin/env python3
"""Dive AI CLI - Serve Command: Start FastAPI HTTP server for API access."""
import json
import sys
from datetime import datetime


def execute(args):
    """Start the FastAPI server."""
    try:
        import uvicorn
    except ImportError:
        print(json.dumps({
            "status": "error",
            "message": "uvicorn required. Install: pip install uvicorn fastapi"
        }, indent=2))
        sys.exit(1)

    from src.cli.api_server import create_app

    app = create_app()

    print(json.dumps({
        "status": "starting",
        "command": "serve",
        "host": args.host,
        "port": args.port,
        "workers": args.workers,
        "endpoints": [
            "POST /api/ask",
            "POST /api/code",
            "POST /api/search",
            "POST /api/memory",
            "POST /api/computer",
            "POST /api/skills",
            "POST /api/orchestrate",
            "GET  /api/status",
            "GET  /health",
        ],
        "timestamp": datetime.now().isoformat(),
    }, indent=2))

    uvicorn.run(app, host=args.host, port=args.port, workers=args.workers)
