#!/usr/bin/env python3
"""
Dive AI v24 - Main Entry Point
Vision + Reasoning Computer Assistant

Usage:
    python main.py                    # Start interactive mode
    python main.py --api              # Start API server
    python main.py --task "..."       # Execute single task
    python main.py --test             # Run tests
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def print_banner():
    """Print welcome banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ██████╗ ██╗██╗   ██╗███████╗     █████╗ ██╗    ██╗   ██╗██████╗ ║
║     ██╔══██╗██║██║   ██║██╔════╝    ██╔══██╗██║    ██║   ██║╚════██╗║
║     ██║  ██║██║██║   ██║█████╗      ███████║██║    ██║   ██║ █████╔╝║
║     ██║  ██║██║╚██╗ ██╔╝██╔══╝      ██╔══██║██║    ╚██╗ ██╔╝██╔═══╝ ║
║     ██████╔╝██║ ╚████╔╝ ███████╗    ██║  ██║██║     ╚████╔╝ ███████╗║
║     ╚═════╝ ╚═╝  ╚═══╝  ╚══════╝    ╚═╝  ╚═╝╚═╝      ╚═══╝  ╚══════╝║
║                                                                  ║
║              Vision + Reasoning Computer Assistant               ║
║                        Version 24.0.0                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold blue")


def print_features():
    """Print feature list"""
    table = Table(title="🚀 Features", show_header=True, header_style="bold magenta")
    table.add_column("Feature", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    
    features = [
        ("👁️ Vision Model", "Qwen2.5-VL / UI-TARS-1.5-7B integration", "✅ Ready"),
        ("🧠 128 Agents", "Specialized reasoning agents", "✅ Ready"),
        ("💾 Memory V4", "13.9x faster learning system", "✅ Ready"),
        ("⚡ Automation", "Click, type, scroll, drag", "✅ Ready"),
        ("🔌 WebSocket", "Real-time streaming", "✅ Ready"),
        ("🌐 API Server", "FastAPI REST + WebSocket", "✅ Ready"),
        ("🖥️ Desktop App", "Electron wrapper", "✅ Ready"),
        ("🇻🇳 Bilingual", "English / Vietnamese", "✅ Ready"),
    ]
    
    for feature, desc, status in features:
        table.add_row(feature, desc, status)
    
    console.print(table)


async def interactive_mode():
    """Run interactive mode"""
    from core.orchestrator.v24_orchestrator import DiveAIv24Orchestrator
    
    print_banner()
    print_features()
    
    console.print("\n[bold green]Initializing Dive AI v24...[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Loading orchestrator...", total=None)
        
        orchestrator = DiveAIv24Orchestrator(
            project_name="dive-ai-v24",
            vision_model="ui-tars-1.5-7b",
            enable_learning=True
        )
        
        progress.update(task, description="✅ Orchestrator ready!")
    
    console.print(f"\n[bold]Session ID:[/bold] {orchestrator.session_id}")
    console.print(f"[bold]Agents:[/bold] {len(orchestrator.agents)}")
    console.print(f"[bold]Vision Model:[/bold] ui-tars-1.5-7b")
    
    console.print("\n[bold yellow]Commands:[/bold yellow]")
    console.print("  • Type your task to execute")
    console.print("  • 'stats' - Show statistics")
    console.print("  • 'agents' - List agents")
    console.print("  • 'help' - Show help")
    console.print("  • 'quit' - Exit")
    
    while True:
        try:
            console.print()
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                console.print("\n[bold]Goodbye! 👋[/bold]")
                break
            
            if user_input.lower() == 'stats':
                stats = orchestrator.get_stats()
                console.print(Panel(
                    json.dumps(stats, indent=2),
                    title="📊 Statistics",
                    border_style="blue"
                ))
                continue
            
            if user_input.lower() == 'agents':
                agents = list(orchestrator.agents.keys())
                console.print(Panel(
                    "\n".join(f"• {a}" for a in agents[:20]) + f"\n... and {len(agents)-20} more",
                    title=f"🤖 Agents ({len(agents)} total)",
                    border_style="green"
                ))
                continue
            
            if user_input.lower() == 'help':
                console.print(Panel(
                    """
**Available Commands:**
- Type any task to execute (e.g., "Click the submit button")
- `stats` - Show system statistics
- `agents` - List all 128 agents
- `help` - Show this help
- `quit` - Exit the program

**Task Examples:**
- "Click the submit button"
- "Type 'Hello World' in the input field"
- "Scroll down the page"
- "Take a screenshot"
- "Open Chrome browser"
                    """,
                    title="❓ Help",
                    border_style="yellow"
                ))
                continue
            
            # Process task
            console.print(f"\n[bold magenta]Dive AI:[/bold magenta]")
            
            async for event in orchestrator.process_task(user_input):
                event_type = event.type
                content = event.content
                confidence = event.confidence
                
                if event_type == "thinking":
                    stage = content.get("stage", "")
                    message = content.get("message", "")
                    explanation = content.get("explanation", "")
                    
                    console.print(f"  💭 [dim]{message}[/dim]")
                    if explanation:
                        console.print(f"     [italic dim]{explanation}[/italic dim]")
                
                elif event_type == "action":
                    stage = content.get("stage", "")
                    message = content.get("message", "")
                    
                    console.print(f"  ⚡ [yellow]{message}[/yellow]")
                
                elif event_type == "result":
                    success = content.get("success", False)
                    message = content.get("message", "")
                    
                    if success:
                        console.print(f"  ✅ [green]{message}[/green]")
                    else:
                        console.print(f"  ❌ [red]{message}[/red]")
                
                elif event_type == "learning":
                    message = content.get("message", "")
                    console.print(f"  📚 [blue]{message}[/blue]")
                
                elif event_type == "error":
                    message = content.get("message", "")
                    console.print(f"  ❌ [red]Error: {message}[/red]")
            
            console.print(f"\n  [dim]Confidence: {confidence:.1%}[/dim]")
            
        except KeyboardInterrupt:
            console.print("\n\n[bold]Interrupted. Goodbye! 👋[/bold]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


async def run_api():
    """Run API server"""
    print_banner()
    
    console.print("[bold green]Starting API Server...[/bold green]\n")
    
    import uvicorn
    from api.main import app
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_task(task: str, screenshot: str = None):
    """Run a single task"""
    from core.orchestrator.v24_orchestrator import DiveAIv24Orchestrator
    
    console.print(f"[bold]Task:[/bold] {task}")
    if screenshot:
        console.print(f"[bold]Screenshot:[/bold] {screenshot}")
    
    orchestrator = DiveAIv24Orchestrator()
    
    async for event in orchestrator.process_task(task, screenshot):
        console.print(f"[{event.type}] {event.content.get('message', event.content)}")


def run_tests():
    """Run tests"""
    import pytest
    pytest.main(["-v", "tests/"])


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dive AI v24 - Vision + Reasoning Computer Assistant"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="Execute a single task"
    )
    
    parser.add_argument(
        "--screenshot",
        type=str,
        help="Screenshot path for task"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version"
    )
    
    args = parser.parse_args()
    
    if args.version:
        console.print("Dive AI v24.0.0")
        return
    
    if args.test:
        run_tests()
        return
    
    if args.api:
        asyncio.run(run_api())
        return
    
    if args.task:
        asyncio.run(run_task(args.task, args.screenshot))
        return
    
    # Default: interactive mode
    asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
