#!/usr/bin/env python3
"""Dive AI CLI - Status Command: Show system status and component health."""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

DIVE_ROOT = Path(__file__).parent.parent.parent.parent


def check_component(name, import_path):
    """Check if a component is available."""
    try:
        parts = import_path.rsplit(".", 1)
        mod = __import__(parts[0], fromlist=[parts[1]] if len(parts) > 1 else [])
        return {"status": "ok", "name": name}
    except Exception as e:
        return {"status": "unavailable", "name": name, "reason": str(e)[:100]}


def execute(args):
    from src.cli.config import DiveConfig
    config = DiveConfig.load()

    # Check components
    components = []

    # CLI
    components.append({"name": "CLI Router", "status": "ok"})

    # LLM
    try:
        from src.cli.llm_adapter import DiveLLM
        llm = DiveLLM(config)
        components.append({"name": "LLM Adapter", "status": "ok", "model": config.llm.model})
    except Exception as e:
        components.append({"name": "LLM Adapter", "status": "error", "reason": str(e)[:100]})

    # Memory
    mem_dir = Path(config.memory.storage_dir)
    if mem_dir.exists():
        projects = [d.name for d in mem_dir.iterdir() if d.is_dir()]
        components.append({"name": "Memory System", "status": "ok", "projects": len(projects)})
    else:
        components.append({"name": "Memory System", "status": "ok", "projects": 0, "note": "No data yet"})

    # Skills
    skills_dir = DIVE_ROOT / "src" / "skills"
    if skills_dir.exists():
        skill_count = len(list(skills_dir.rglob("*.py"))) - len(list(skills_dir.rglob("__init__.py")))
        components.append({"name": "Skills Engine", "status": "ok", "skills": skill_count})
    else:
        components.append({"name": "Skills Engine", "status": "unavailable"})

    # Core modules
    core_dir = DIVE_ROOT / "src" / "core"
    if core_dir.exists():
        core_modules = [d.name for d in core_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]
        components.append({"name": "Core Engine", "status": "ok", "modules": core_modules})
    else:
        components.append({"name": "Core Engine", "status": "unavailable"})

    # UI-TARS
    if config.uitars.enabled:
        import shutil
        if shutil.which(config.uitars.cli_path):
            components.append({"name": "UI-TARS (Computer Use)", "status": "ok", "mode": config.uitars.mode})
        else:
            components.append({"name": "UI-TARS (Computer Use)", "status": "not installed",
                              "note": "Install: npm install @agent-tars/cli@latest -g"})
    else:
        components.append({"name": "UI-TARS (Computer Use)", "status": "disabled",
                          "note": "Enable: DIVE_UITARS_ENABLED=true"})

    # Coder engine
    coder_dir = DIVE_ROOT / "src" / "coder"
    if coder_dir.exists():
        components.append({"name": "Dive Coder Engine", "status": "ok"})
    else:
        components.append({"name": "Dive Coder Engine", "status": "unavailable"})

    # Count files
    total_files = len(list(DIVE_ROOT.rglob("*"))) - len(list(DIVE_ROOT.rglob(".*")))

    output = {
        "status": "success",
        "command": "status",
        "version": config.version,
        "config": config.to_dict(),
        "components": components,
        "health": {
            "ok": sum(1 for c in components if c["status"] == "ok"),
            "total": len(components),
        },
        "project_root": str(DIVE_ROOT),
        "total_files": total_files,
        "timestamp": datetime.now().isoformat(),
    }

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
