#!/usr/bin/env python3
"""
Dive AI CLI - Command Router
==============================
Routes CLI commands to the appropriate Dive AI engine modules.
Outputs JSON for easy parsing by Manus or any AI agent.

Commands:
    ask       - Ask Dive AI a question (uses LLM + memory + context)
    code      - Code generation, review, debug, refactor
    search    - Search codebase, web, or memory
    memory    - Store, recall, or search project memory
    computer  - Computer use via UI-TARS (GUI automation)
    skills    - List, run, or manage skills
    orchestrate - Run multi-step task via smart orchestrator
    serve     - Start HTTP API server
    status    - Show system status
"""
import sys
import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Project root
DIVE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(DIVE_ROOT))

# Configure logging
LOG_LEVEL = os.getenv("DIVE_LOG_LEVEL", "WARNING")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("dive-cli")

VERSION = "28.0.0"


def output_json(data: dict, pretty: bool = False):
    """Output JSON to stdout for machine consumption."""
    indent = 2 if pretty else None
    print(json.dumps(data, indent=indent, ensure_ascii=False, default=str))


def output_error(message: str, code: str = "ERROR"):
    """Output error in standard format."""
    output_json({
        "status": "error",
        "code": code,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    sys.exit(1)


def cmd_ask(args):
    """Ask Dive AI a question - uses LLM + memory context."""
    from src.cli.commands.ask import execute
    execute(args)


def cmd_code(args):
    """Code generation, review, debug, refactor."""
    from src.cli.commands.code import execute
    execute(args)


def cmd_search(args):
    """Search codebase, web, or memory."""
    from src.cli.commands.search import execute
    execute(args)


def cmd_memory(args):
    """Store, recall, or search project memory."""
    from src.cli.commands.memory import execute
    execute(args)


def cmd_computer(args):
    """Computer use via UI-TARS integration."""
    from src.cli.commands.computer import execute
    execute(args)


def cmd_skills(args):
    """List, run, or manage skills."""
    from src.cli.commands.skills import execute
    execute(args)


def cmd_orchestrate(args):
    """Run multi-step task via smart orchestrator."""
    from src.cli.commands.orchestrate import execute
    execute(args)


def cmd_serve(args):
    """Start HTTP API server."""
    from src.cli.commands.serve import execute
    execute(args)


def cmd_status(args):
    """Show system status."""
    from src.cli.commands.status import execute
    execute(args)


def build_parser():
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="dive",
        description=f"Dive AI V{VERSION} - Fully Automatic Computer Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dive ask "How to implement OAuth2 in FastAPI?"
  dive code --task "Create a REST API with CRUD" --lang python
  dive code --action review --file ./app.py
  dive search --query "memory leak" --scope codebase
  dive memory --action store --project myapp --content "API uses JWT tokens"
  dive memory --action recall --project myapp
  dive computer --task "Open VS Code and create new file"
  dive skills --list
  dive orchestrate --task "Build and deploy a todo app"
  dive serve --port 8000
  dive status
        """
    )
    parser.add_argument("--version", action="version", version=f"Dive AI V{VERSION}")
    parser.add_argument("--json", action="store_true", default=True,
                        help="Output in JSON format (default)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # === ASK ===
    p_ask = subparsers.add_parser("ask", help="Ask Dive AI a question")
    p_ask.add_argument("question", nargs="+", help="The question to ask")
    p_ask.add_argument("--model", default=None, help="LLM model to use")
    p_ask.add_argument("--context", default=None, help="Additional context file")
    p_ask.add_argument("--project", default=None, help="Project name for memory context")
    p_ask.set_defaults(func=cmd_ask)

    # === CODE ===
    p_code = subparsers.add_parser("code", help="Code generation, review, debug")
    p_code.add_argument("--action", choices=["generate", "review", "debug", "refactor", "test", "explain"],
                        default="generate", help="Coding action")
    p_code.add_argument("--task", help="Task description")
    p_code.add_argument("--file", help="Target file for review/debug/refactor")
    p_code.add_argument("--lang", default="python", help="Programming language")
    p_code.add_argument("--output", help="Output file path")
    p_code.set_defaults(func=cmd_code)

    # === SEARCH ===
    p_search = subparsers.add_parser("search", help="Search codebase, web, or memory")
    p_search.add_argument("--query", "-q", required=True, help="Search query")
    p_search.add_argument("--scope", choices=["codebase", "web", "memory", "all"],
                          default="all", help="Search scope")
    p_search.add_argument("--path", default=".", help="Codebase path for codebase search")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")
    p_search.set_defaults(func=cmd_search)

    # === MEMORY ===
    p_memory = subparsers.add_parser("memory", help="Project memory management")
    p_memory.add_argument("--action", choices=["store", "recall", "search", "list", "changelog"],
                          required=True, help="Memory action")
    p_memory.add_argument("--project", required=True, help="Project name")
    p_memory.add_argument("--content", help="Content to store")
    p_memory.add_argument("--query", help="Search query for memory")
    p_memory.add_argument("--category", default="knowledge",
                          help="Category: knowledge, criteria, decision, issue")
    p_memory.set_defaults(func=cmd_memory)

    # === COMPUTER ===
    p_computer = subparsers.add_parser("computer", help="Computer use via UI-TARS")
    p_computer.add_argument("--task", required=True, help="Task description in natural language")
    p_computer.add_argument("--mode", choices=["local", "remote", "browser"],
                            default="local", help="Operator mode")
    p_computer.add_argument("--screenshot", action="store_true",
                            help="Take screenshot after task")
    p_computer.add_argument("--provider", default="openai", help="VLM provider")
    p_computer.add_argument("--model", default="gpt-4o", help="VLM model")
    p_computer.set_defaults(func=cmd_computer)

    # === SKILLS ===
    p_skills = subparsers.add_parser("skills", help="Manage and run skills")
    p_skills.add_argument("--list", action="store_true", help="List available skills")
    p_skills.add_argument("--run", help="Run a specific skill by name")
    p_skills.add_argument("--input", help="Input for the skill")
    p_skills.set_defaults(func=cmd_skills)

    # === ORCHESTRATE ===
    p_orch = subparsers.add_parser("orchestrate", help="Multi-step task orchestration")
    p_orch.add_argument("--task", required=True, help="Complex task description")
    p_orch.add_argument("--project", help="Project context")
    p_orch.add_argument("--steps", type=int, default=0, help="Max steps (0=auto)")
    p_orch.set_defaults(func=cmd_orchestrate)

    # === SERVE ===
    p_serve = subparsers.add_parser("serve", help="Start HTTP API server")
    p_serve.add_argument("--port", type=int, default=8000, help="Server port")
    p_serve.add_argument("--host", default="0.0.0.0", help="Server host")
    p_serve.add_argument("--workers", type=int, default=1, help="Number of workers")
    p_serve.set_defaults(func=cmd_serve)

    # === STATUS ===
    p_status = subparsers.add_parser("status", help="Show system status")
    p_status.set_defaults(func=cmd_status)

    return parser


def main():
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except KeyboardInterrupt:
        output_error("Interrupted by user", "INTERRUPTED")
    except Exception as e:
        logger.exception("CLI error")
        output_error(str(e), "INTERNAL_ERROR")


if __name__ == "__main__":
    main()
