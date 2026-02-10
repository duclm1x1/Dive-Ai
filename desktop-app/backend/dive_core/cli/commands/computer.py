#!/usr/bin/env python3
"""
Dive AI CLI - Computer Command
================================
Computer use via UI-TARS Desktop integration.
Supports: local operator, remote operator, browser operator.

This module bridges Dive AI with UI-TARS (ByteDance) for:
- GUI automation (click, type, scroll, drag)
- Screenshot and visual recognition
- Browser automation (navigate, fill forms, extract data)
- Cross-platform desktop control

Architecture:
    dive computer --task "..." 
        → UI-TARS CLI (agent-tars) 
        → Vision Language Model 
        → GUI/Browser actions
"""
import json
import os
import sys
import subprocess
import shutil
import tempfile
import base64
from datetime import datetime
from pathlib import Path


def check_uitars_installed(cli_path="agent-tars"):
    """Check if UI-TARS CLI is installed."""
    return shutil.which(cli_path) is not None


def check_node_installed():
    """Check if Node.js is installed (required for npx)."""
    return shutil.which("node") is not None


def take_screenshot(output_path=None):
    """Take a screenshot of the current screen."""
    try:
        import subprocess
        if not output_path:
            output_path = tempfile.mktemp(suffix=".png")

        # Try different screenshot methods
        methods = [
            ["scrot", output_path],
            ["gnome-screenshot", "-f", output_path],
            ["import", "-window", "root", output_path],
        ]

        for cmd in methods:
            if shutil.which(cmd[0]):
                subprocess.run(cmd, capture_output=True, timeout=10)
                if Path(output_path).exists():
                    return output_path

        return None
    except Exception:
        return None


def execute_via_uitars_cli(task, mode="local", provider="openai", model="gpt-4o",
                           api_key=None, cli_path="agent-tars"):
    """Execute a task via UI-TARS CLI."""
    cmd = [cli_path]

    # Add provider and model
    cmd.extend(["--provider", provider])
    cmd.extend(["--model", model])

    if api_key:
        cmd.extend(["--apiKey", api_key])

    # Add task as prompt
    cmd.extend(["--prompt", task])

    # Add mode-specific flags
    if mode == "browser":
        cmd.append("--browser")
    elif mode == "remote":
        cmd.append("--remote")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ}
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Task timed out (120s)", "success": False}
    except FileNotFoundError:
        return {"error": "UI-TARS CLI not found: " + cli_path, "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def execute_via_npx(task, mode="local", provider="openai", model="gpt-4o", api_key=None):
    """Execute via npx (no global install needed)."""
    cmd = ["npx", "@agent-tars/cli@latest"]

    cmd.extend(["--provider", provider])
    cmd.extend(["--model", model])

    if api_key:
        cmd.extend(["--apiKey", api_key])

    cmd.extend(["--prompt", task])

    if mode == "browser":
        cmd.append("--browser")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ}
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Task timed out (180s)", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def execute_via_llm_vision(task, config):
    """Fallback: Use LLM with vision capabilities for computer-use-like tasks."""
    from src.cli.llm_adapter import DiveLLM

    llm = DiveLLM(config)

    system = (
        "You are Dive AI Computer Assistant. The user wants to perform a computer task. "
        "Since direct GUI control is not available, provide detailed step-by-step "
        "instructions that can be executed via shell commands, keyboard shortcuts, "
        "or browser automation. Be specific and actionable."
    )

    result = llm.chat(task, system=system, model=llm.models["power"])

    return {
        "method": "llm_fallback",
        "instructions": result.get("content", ""),
        "model": result.get("model", ""),
        "usage": result.get("usage", {}),
        "note": "UI-TARS not available. Providing shell/CLI instructions instead.",
    }


def execute_task(task, mode="local", screenshot=False, provider="openai",
                 model="gpt-4o", config=None):
    """Main execution function - tries multiple methods."""
    from src.cli.config import DiveConfig
    if config is None:
        config = DiveConfig.load()

    result = {
        "task": task,
        "mode": mode,
    }

    # Method 1: UI-TARS CLI (global install)
    if check_uitars_installed(config.uitars.cli_path):
        uitars_result = execute_via_uitars_cli(
            task=task,
            mode=mode,
            provider=provider,
            model=model,
            api_key=config.uitars.api_key,
            cli_path=config.uitars.cli_path,
        )
        result["method"] = "uitars_cli"
        result.update(uitars_result)

    # Method 2: npx (no install needed)
    elif check_node_installed():
        npx_result = execute_via_npx(
            task=task,
            mode=mode,
            provider=provider,
            model=model,
            api_key=config.uitars.api_key,
        )
        result["method"] = "npx"
        result.update(npx_result)

    # Method 3: LLM fallback (always available)
    else:
        llm_result = execute_via_llm_vision(task, config)
        result["method"] = "llm_fallback"
        result.update(llm_result)

    # Take screenshot if requested
    if screenshot:
        ss_path = take_screenshot()
        if ss_path:
            result["screenshot"] = ss_path

    return result


def execute(args):
    """CLI entry point for computer command."""
    from src.cli.config import DiveConfig
    config = DiveConfig.load()

    result = execute_task(
        task=args.task,
        mode=args.mode,
        screenshot=args.screenshot,
        provider=args.provider,
        model=args.model,
        config=config,
    )

    output = {
        "status": "success" if not result.get("error") else "error",
        "command": "computer",
        **result,
        "timestamp": datetime.now().isoformat(),
    }

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
