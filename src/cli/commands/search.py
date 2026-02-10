#!/usr/bin/env python3
"""Dive AI CLI - Search Command: Search codebase, web, or memory."""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def search_codebase(query, path=".", limit=10):
    """Search local codebase using grep-like matching."""
    results = []
    search_path = Path(path).resolve()

    if not search_path.exists():
        return {"error": "Path not found: " + str(search_path)}

    extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".json", ".yaml", ".yml", ".toml", ".cfg", ".html", ".css"}

    for root, dirs, files in os.walk(search_path):
        # Skip hidden dirs and common excludes
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".git")]

        for fname in files:
            if len(results) >= limit:
                break
            fpath = Path(root) / fname
            if fpath.suffix not in extensions:
                continue
            try:
                content = fpath.read_text(errors="ignore")
                for i, line in enumerate(content.split("\n"), 1):
                    if query.lower() in line.lower():
                        results.append({
                            "file": str(fpath.relative_to(search_path)),
                            "line": i,
                            "content": line.strip()[:200],
                        })
                        if len(results) >= limit:
                            break
            except Exception:
                continue

    return results


def search_memory(query, config):
    """Search project memory files."""
    results = []
    memory_dir = Path(config.memory.storage_dir)
    if not memory_dir.exists():
        return results

    for md_file in memory_dir.glob("**/*.md"):
        try:
            content = md_file.read_text()
            if query.lower() in content.lower():
                # Find matching lines
                for i, line in enumerate(content.split("\n"), 1):
                    if query.lower() in line.lower():
                        results.append({
                            "file": str(md_file.relative_to(memory_dir)),
                            "line": i,
                            "content": line.strip()[:200],
                        })
        except Exception:
            continue

    return results


def search_web(query, llm):
    """Use LLM to answer web-like queries (knowledge-based)."""
    result = llm.chat(
        "Answer this search query concisely with factual information: " + query,
        system="You are a search engine. Provide factual, concise answers with sources when possible.",
        model=llm.models["fast"],
        max_tokens=500,
    )
    return result.get("content", "No results")


def execute(args):
    from src.cli.llm_adapter import DiveLLM
    from src.cli.config import DiveConfig

    config = DiveConfig.load()
    query = args.query
    scope = args.scope
    limit = args.limit

    output = {
        "status": "success",
        "command": "search",
        "query": query,
        "scope": scope,
        "results": {},
        "timestamp": datetime.now().isoformat(),
    }

    if scope in ("codebase", "all"):
        output["results"]["codebase"] = search_codebase(query, args.path, limit)

    if scope in ("memory", "all"):
        output["results"]["memory"] = search_memory(query, config)

    if scope in ("web", "all"):
        try:
            llm = DiveLLM(config)
            output["results"]["web"] = search_web(query, llm)
        except Exception as e:
            output["results"]["web"] = {"error": str(e)}

    # Count total results
    total = 0
    for key, val in output["results"].items():
        if isinstance(val, list):
            total += len(val)
        elif isinstance(val, str):
            total += 1
    output["total_results"] = total

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
