#!/usr/bin/env python3
"""Dive AI CLI - Code Command: Code generation, review, debug, refactor, test, explain."""
import json
import sys
from datetime import datetime
from pathlib import Path


def execute(args):
    from src.cli.llm_adapter import DiveLLM
    from src.cli.config import DiveConfig

    config = DiveConfig.load()
    llm = DiveLLM(config)

    action = args.action
    task = args.task or ""
    language = args.lang

    # If file provided, read it as context
    context = None
    if args.file:
        filepath = Path(args.file)
        if filepath.exists():
            context = filepath.read_text()
            if not task:
                task = action + " this code"
        else:
            print(json.dumps({"status": "error", "message": "File not found: " + args.file}, indent=2))
            sys.exit(1)

    if not task:
        print(json.dumps({"status": "error", "message": "Either --task or --file is required"}, indent=2))
        sys.exit(1)

    result = llm.code(task=task, language=language, context=context, action=action)

    output = {
        "status": "success",
        "command": "code",
        "action": action,
        "language": language,
        "code": result.get("content", ""),
        "model": result.get("model", ""),
        "usage": result.get("usage", {}),
        "timestamp": datetime.now().isoformat(),
    }

    if result.get("error"):
        output["status"] = "error"
        output["error"] = result["error"]

    # Save to file if --output specified
    if args.output and output["status"] == "success":
        Path(args.output).write_text(output["code"])
        output["saved_to"] = args.output

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
