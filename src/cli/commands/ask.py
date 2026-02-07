#!/usr/bin/env python3
"""Dive AI CLI - Ask Command: Ask Dive AI a question with LLM + memory context."""
import json
import sys
from datetime import datetime
from pathlib import Path


def execute(args):
    question = " ".join(args.question)
    from src.cli.llm_adapter import DiveLLM
    from src.cli.config import DiveConfig

    config = DiveConfig.load()
    llm = DiveLLM(config)

    # Build context from memory if project specified
    memory_context = ""
    if args.project:
        try:
            from src.core.memory.dive_memory_3file_complete import DiveMemory3FileComplete
            memory = DiveMemory3FileComplete(base_dir=config.memory.storage_dir)
            recalled = memory.recall(args.project)
            if recalled:
                memory_context = "\n\nProject Memory (" + args.project + "):\n" + recalled[:2000]
        except Exception:
            pass

    file_context = ""
    if args.context and Path(args.context).exists():
        file_context = "\n\nFile Context:\n" + Path(args.context).read_text()[:3000]

    system = (
        "You are Dive AI, a fully automatic computer assistant. "
        "Answer questions accurately and concisely. "
        "If the question is about code, provide working examples. "
        "If the question requires multiple steps, provide a clear plan."
        + memory_context + file_context
    )

    result = llm.chat(question, system=system, model=args.model)

    output = {
        "status": "success",
        "command": "ask",
        "question": question,
        "answer": result.get("content", ""),
        "model": result.get("model", ""),
        "usage": result.get("usage", {}),
        "tier": result.get("tier", ""),
        "timestamp": datetime.now().isoformat(),
    }

    if result.get("error"):
        output["status"] = "error"
        output["error"] = result["error"]

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
