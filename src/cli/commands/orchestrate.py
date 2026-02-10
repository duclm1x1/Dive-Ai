#!/usr/bin/env python3
"""Dive AI CLI - Orchestrate Command: Multi-step task orchestration via LLM."""
import json
import sys
from datetime import datetime
from pathlib import Path


def execute(args):
    from src.cli.llm_adapter import DiveLLM
    from src.cli.config import DiveConfig

    config = DiveConfig.load()
    llm = DiveLLM(config)

    task = args.task
    project = args.project or "default"
    max_steps = args.steps if args.steps > 0 else 10

    # Step 1: Plan the task
    plan_prompt = (
        "You are Dive AI Smart Orchestrator. Break down this complex task into "
        "a numbered list of concrete, executable steps. Each step should be "
        "actionable and specific. Output as JSON with keys: "
        '"steps" (array of {step_number, action, description, tool}).\n\n'
        "Task: " + task
    )

    plan_result = llm.chat(
        plan_prompt,
        system="You are a task planning AI. Output valid JSON only.",
        model=llm.models["power"],
        json_mode=True,
    )

    # Parse plan
    steps = []
    try:
        plan_data = json.loads(plan_result.get("content", "{}"))
        steps = plan_data.get("steps", [])
    except (json.JSONDecodeError, TypeError):
        # If JSON parsing fails, try to extract steps from text
        content = plan_result.get("content", "")
        steps = [{"step_number": 1, "action": "execute", "description": content, "tool": "llm"}]

    # Limit steps
    if len(steps) > max_steps:
        steps = steps[:max_steps]

    # Store plan in memory
    try:
        from src.cli.commands.memory import DiveMemoryCLI
        mem = DiveMemoryCLI(config.memory.storage_dir)
        mem.store(project, "Task: " + task + "\nPlan: " + json.dumps(steps, indent=2), "orchestration")
    except Exception:
        pass

    output = {
        "status": "success",
        "command": "orchestrate",
        "task": task,
        "project": project,
        "plan": {
            "total_steps": len(steps),
            "steps": steps,
        },
        "model": plan_result.get("model", ""),
        "usage": plan_result.get("usage", {}),
        "note": "Plan generated. Execute each step using: dive code/search/computer/ask",
        "timestamp": datetime.now().isoformat(),
    }

    if plan_result.get("error"):
        output["status"] = "error"
        output["error"] = plan_result["error"]

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
