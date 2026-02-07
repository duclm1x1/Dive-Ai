#!/usr/bin/env python3
"""
Dive AI V27.3 - Main Entry Point
=================================
Clean Architecture Refactor - February 7, 2026

This is the unified entry point for Dive AI V27.3.
All core components are initialized and orchestrated from here.

Architecture:
    src/core/orchestrator/  - Smart Orchestrator (11 variants unified)
    src/core/memory/        - Memory System (7 modules unified)
    src/core/voice/         - Voice & Audio (16 modules)
    src/core/llm/           - LLM Clients & Connections (13 modules)
    src/core/search/        - Search & Update Engine (11 modules)
    src/core/workflow/      - Workflow & Execution Engine (9 modules)
    src/core/engine/        - RAG, Evidence, Verification (20 modules)
    src/skills/             - All Skills (internal + modules)
    src/agents/             - Agent Definitions
    src/monitor/            - Monitoring Backend
    src/plugins/            - Plugin System (Antigravity, MCP)
    src/ui/                 - React Dashboard (dive-monitor)
    src/context/            - Context Management

Usage:
    python -m src.main [--mode interactive|api|voice]
    python src/main.py
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DiveAI")

# Version
VERSION = "27.3"


def get_version():
    """Read version from VERSION file or return default."""
    version_file = PROJECT_ROOT / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return VERSION


def init_memory():
    """Initialize the Memory System."""
    try:
        from src.core.memory.dive_memory_3file_complete import DiveMemory3FileComplete
        memory = DiveMemory3FileComplete()
        logger.info("Memory System initialized (3-file complete)")
        return memory
    except ImportError:
        logger.warning("Memory System not available, running without memory")
        return None


def init_orchestrator(memory=None):
    """Initialize the Smart Orchestrator."""
    try:
        from src.core.orchestrator.dive_smart_orchestrator import DiveSmartOrchestrator
        orchestrator = DiveSmartOrchestrator()
        logger.info("Smart Orchestrator initialized")
        return orchestrator
    except ImportError:
        logger.warning("Smart Orchestrator not available")
        return None


def init_voice():
    """Initialize Voice System (optional)."""
    try:
        from src.core.voice.dive_voice_orchestrator import DiveVoiceOrchestrator
        voice = DiveVoiceOrchestrator()
        logger.info("Voice Orchestrator initialized")
        return voice
    except ImportError:
        logger.info("Voice System not available (optional)")
        return None


def init_llm():
    """Initialize LLM Client."""
    try:
        from src.core.llm.llm_connection import LLMConnection
        llm = LLMConnection()
        logger.info("LLM Connection initialized")
        return llm
    except ImportError:
        logger.warning("LLM Connection not available")
        return None


def main():
    """Main entry point for Dive AI V27.3."""
    parser = argparse.ArgumentParser(
        description=f"Dive AI V{get_version()} - Intelligent AI System"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "api", "voice"],
        default="interactive",
        help="Run mode (default: interactive)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Starting Dive AI V{get_version()} in {args.mode} mode")

    # Initialize core components
    memory = init_memory()
    orchestrator = init_orchestrator(memory)
    llm = init_llm()

    if args.mode == "voice":
        voice = init_voice()
        if voice:
            logger.info("Voice mode active - listening...")
        else:
            logger.error("Voice mode requested but Voice System unavailable")
            sys.exit(1)

    elif args.mode == "api":
        try:
            from src.monitor.app.main import app
            import uvicorn
            logger.info(f"Starting API server on port {args.port}")
            uvicorn.run(app, host="0.0.0.0", port=args.port)
        except ImportError:
            logger.error("API mode requires uvicorn and FastAPI")
            sys.exit(1)

    else:  # interactive mode
        logger.info("Interactive mode - ready for input")
        logger.info(f"Components loaded: Memory={'OK' if memory else 'N/A'}, "
                    f"Orchestrator={'OK' if orchestrator else 'N/A'}, "
                    f"LLM={'OK' if llm else 'N/A'}")

    logger.info(f"Dive AI V{get_version()} ready.")


if __name__ == "__main__":
    main()
