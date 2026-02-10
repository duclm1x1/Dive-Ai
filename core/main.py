#!/usr/bin/env python3
"""
Dive AI v25 - Trinity Computer Assistant

Main entry point for the Trinity system.

Usage:
    python main.py              # Interactive mode
    python main.py --api        # API server mode
    python main.py --text       # Text-only mode
    python main.py --language vi  # Vietnamese language
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Reduce noise from libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)


def print_banner():
    """Print Dive AI v25 banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🔺 DIVE AI v25 - TRINITY COMPUTER ASSISTANT                 ║
║                                                               ║
║   👂 HEAR    - Listen, Understand, Speak                      ║
║   👁️ VISION  - See, Detect, Act                               ║
║   🧠 THINK   - Reason, Plan, Execute                          ║
║                                                               ║
║   "Your Computer, Your Voice, Your Assistant"                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_interactive(language: str = "en"):
    """Run interactive mode"""
    from trinity import DiveAIv25Trinity, TrinityConfig
    
    print_banner()
    print("🚀 Starting Trinity in Interactive Mode...")
    print(f"   Language: {language}")
    print()
    
    # Initialize Trinity
    config = TrinityConfig(
        language=language,
        device="cuda"
    )
    
    trinity = DiveAIv25Trinity(config)
    
    try:
        await trinity.initialize()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("   Falling back to CPU mode...")
        config.device = "cpu"
        trinity = DiveAIv25Trinity(config)
        await trinity.initialize()
    
    print()
    print("✅ Trinity ready!")
    print("=" * 60)
    print()
    print("💡 Commands:")
    print("   - Type a command (e.g., 'Open Chrome')")
    print("   - Type 'voice' to enable voice mode")
    print("   - Type 'status' to see statistics")
    print("   - Type 'quit' or 'exit' to stop")
    print()
    
    while True:
        try:
            # Get input
            user_input = input("🎤 You: ").strip()
            
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
                
            if user_input.lower() == 'status':
                stats = trinity.stats
                print(f"\n📊 Statistics:")
                print(f"   Commands: {stats['commands_processed']}")
                print(f"   Actions: {stats['actions_executed']}")
                print(f"   Errors: {stats['errors']}")
                if stats['commands_processed'] > 0:
                    print(f"   Avg Latency: {stats['avg_latency_ms']:.0f}ms")
                print()
                continue
                
            if user_input.lower() == 'voice':
                print("\n🎙️ Voice mode requires audio input/output setup.")
                print("   Please use the API server for voice mode:")
                print("   python main.py --api")
                print()
                continue
                
            # Process command
            print(f"🧠 Processing...")
            
            result = await trinity.process_text(user_input)
            
            print(f"\n🤖 Dive AI: {result.get('response', 'Done!')}")
            
            if result.get('intent'):
                intent = result['intent']
                print(f"   Intent: {intent.get('action', 'unknown')}")
                if intent.get('target'):
                    print(f"   Target: {intent.get('target')}")
                    
            if result.get('actions'):
                print(f"   Actions: {len(result['actions'])} executed")
                
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


async def run_api_server(host: str = "0.0.0.0", port: int = 8000, language: str = "en"):
    """Run API server mode"""
    print_banner()
    print("🚀 Starting Trinity API Server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Language: {language}")
    print()
    
    try:
        from api.main import create_app
        import uvicorn
        
        app = create_app(language=language)
        
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except ImportError:
        print("❌ API server requires uvicorn and fastapi")
        print("   pip install uvicorn fastapi")
        sys.exit(1)


async def run_text_mode(language: str = "en"):
    """Run text-only mode (no audio)"""
    from hear.hear_model import HearModel, HearModelConfig
    
    print_banner()
    print("🚀 Starting Text Mode...")
    print(f"   Language: {language}")
    print()
    
    # Initialize Hear Model only
    config = HearModelConfig(
        language=language,
        stt_device="cpu",
        enable_duplex=False
    )
    
    hear = HearModel(config)
    await hear.initialize()
    
    print("✅ Ready!")
    print("=" * 60)
    print()
    print("💡 Type a command (e.g., 'Open Chrome')")
    print("   Type 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("🎤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
                
            # Analyze intent
            intent = await hear.understand(user_input)
            response = hear._generate_response(intent)
            
            print(f"\n🤖 Dive AI: {response}")
            print(f"   Intent: {intent.action.value}")
            if intent.target:
                print(f"   Target: {intent.target}")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


async def run_test():
    """Run system tests"""
    print_banner()
    print("🧪 Running System Tests...")
    print()
    
    # Test Hear Model
    print("1️⃣ Testing Hear Model...")
    try:
        from hear.hear_model import test_hear_model
        await test_hear_model()
        print("   ✅ Hear Model: PASSED")
    except Exception as e:
        print(f"   ❌ Hear Model: FAILED - {e}")
        
    print()
    
    # Test Trinity
    print("2️⃣ Testing Trinity...")
    try:
        from trinity import test_trinity
        await test_trinity()
        print("   ✅ Trinity: PASSED")
    except Exception as e:
        print(f"   ❌ Trinity: FAILED - {e}")
        
    print()
    print("=" * 60)
    print("✅ Tests complete!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dive AI v25 - Trinity Computer Assistant"
    )
    
    parser.add_argument(
        '--api',
        action='store_true',
        help='Run as API server'
    )
    
    parser.add_argument(
        '--text',
        action='store_true',
        help='Run in text-only mode (no audio)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run system tests'
    )
    
    parser.add_argument(
        '--language', '-l',
        type=str,
        default='en',
        choices=['en', 'vi', 'auto'],
        help='Language (default: en)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='API server host (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Run appropriate mode
    if args.test:
        asyncio.run(run_test())
    elif args.api:
        asyncio.run(run_api_server(args.host, args.port, args.language))
    elif args.text:
        asyncio.run(run_text_mode(args.language))
    else:
        asyncio.run(run_interactive(args.language))


if __name__ == "__main__":
    main()
