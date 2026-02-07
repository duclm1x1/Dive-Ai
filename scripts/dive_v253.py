#!/usr/bin/env python3
"""
Dive AI V25.3 - Main Entry Point
Multimodal AI Assistant with Voice + Vision
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.dive_multimodal_orchestrator import MultimodalOrchestrator, MultimodalConfig
from core.dive_agent_fleet import AgentFleet


def load_config() -> MultimodalConfig:
    """Load configuration from environment"""
    return MultimodalConfig(
        # Voice settings
        voice_model=os.getenv("VOICE_MODEL", "gpt-4o-realtime-preview-2024-10-01"),
        voice_enabled=os.getenv("ENABLE_REALTIME_VOICE", "true").lower() == "true",
        wake_word=os.getenv("VOICE_WAKE_WORD", "hey dive"),
        wake_word_confidence=float(os.getenv("VOICE_CONFIDENCE_THRESHOLD", "0.7")),
        
        # Vision settings
        vision_model=os.getenv("VISION_MODEL", "gpt-4-vision-preview"),
        vision_enabled=os.getenv("ENABLE_VISION", "true").lower() == "true",
        auto_capture_screen=os.getenv("VISION_AUTO_CAPTURE", "true").lower() == "true",
        
        # Orchestration
        session_timeout=int(os.getenv("SESSION_TIMEOUT", "30")),
        enable_continuous_mode=os.getenv("ENABLE_CONTINUOUS_MODE", "true").lower() == "true",
        enable_function_calling=os.getenv("ENABLE_FUNCTION_CALLING", "true").lower() == "true"
    )


def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    🎤 DIVE AI V25.3 🎤                          ║
║                                                                  ║
║              Multimodal Voice + Vision Assistant                ║
║                                                                  ║
║  ✓ OpenAI Realtime API (GPT-4o) - Ultra-low latency voice     ║
║  ✓ GPT-4 Vision - Screen understanding & visual grounding      ║
║  ✓ Enhanced Wake Word - Phonetic matching for accuracy        ║
║  ✓ 128 Agent Fleet - Powerful task execution                  ║
║  ✓ Full-Duplex Voice - Continuous conversation mode           ║
║  ✓ UI-TARS Integration - Computer control automation          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not found!")
        print("\nPlease configure your API key in the .env file:")
        print("  1. Open .env file")
        print("  2. Add: OPENAI_API_KEY=sk-your-key-here")
        print("  3. Save and restart\n")
        return False
    
    print(f"✓ API Key configured: {api_key[:20]}...")
    return True


def print_usage():
    """Print usage instructions"""
    print("\n" + "="*70)
    print("USAGE INSTRUCTIONS")
    print("="*70)
    print(f"\n1. Say the wake word: 'hey dive'")
    print("2. Speak your command naturally")
    print("3. AI will respond with voice and execute actions")
    print("\nExample commands:")
    print("  • 'hey dive open chrome'")
    print("  • 'hey dive what's on my screen?'")
    print("  • 'hey dive click the blue button'")
    print("  • 'hey dive search for python tutorials'")
    print("\nContinuous mode:")
    print("  • After activation, you can keep talking for 30 seconds")
    print("  • Say 'go to sleep' or 'goodbye' to end session")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")


async def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Dive AI V25.3 - Multimodal Voice Assistant")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice input")
    parser.add_argument("--no-vision", action="store_true", help="Disable vision capabilities")
    parser.add_argument("--wake-word", type=str, help="Custom wake word")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check API key
    if not check_api_key():
        if not args.test:
            return
    
    # Load configuration
    config = load_config()
    
    # Apply command line overrides
    if args.no_voice:
        config.voice_enabled = False
    if args.no_vision:
        config.vision_enabled = False
    if args.wake_word:
        config.wake_word = args.wake_word
    
    # Print configuration
    print("\nConfiguration:")
    print(f"  Voice: {'Enabled' if config.voice_enabled else 'Disabled'} ({config.voice_model})")
    print(f"  Vision: {'Enabled' if config.vision_enabled else 'Disabled'} ({config.vision_model})")
    print(f"  Wake word: '{config.wake_word}' (confidence: {config.wake_word_confidence})")
    print(f"  Continuous mode: {'Enabled' if config.enable_continuous_mode else 'Disabled'}")
    print(f"  Session timeout: {config.session_timeout}s")
    
    # Initialize agent fleet (optional)
    agent_fleet = None
    try:
        print("\nInitializing agent fleet...")
        agent_fleet = AgentFleet()
        print("✓ Agent fleet ready")
    except Exception as e:
        print(f"⚠ Agent fleet not available: {e}")
    
    # Create orchestrator
    print("\nInitializing multimodal orchestrator...")
    orchestrator = MultimodalOrchestrator(
        config=config,
        agent_fleet=agent_fleet
    )
    
    # Print usage
    print_usage()
    
    # Run
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Goodbye!\n")


if __name__ == "__main__":
    # Run main
    asyncio.run(main())
