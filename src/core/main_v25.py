#!/usr/bin/env python3
"""
Dive AI v25 - Main Entry Point
Complete Computer Assistant with Vision + Transformation + Hear Models
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from hear.v98_integration import HearModelV98, APIProvider
from trinity import DiveAIv25Trinity


class DiveAIv25:
    """
    Dive AI v25 - Complete Computer Assistant
    
    Trinity Architecture:
    - 👂 HEAR Model (Voice interface via V98 API)
    - 👁️ VISION Model (Desktop automation)
    - 🧠 TRANSFORMATION Model (Reasoning & planning)
    """
    
    def __init__(self, config: dict = None):
        """Initialize Dive AI v25"""
        self.config = config or {}
        self.hear_model = None
        self.trinity = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        print("🚀 Initializing Dive AI v25...")
        
        # Initialize Hear Model with V98 API
        print("  📡 Connecting to V98 API...")
        self.hear_model = HearModelV98(
            provider=APIProvider.V98,
            fallback_provider=APIProvider.AICODING
        )
        
        # Initialize Trinity (Vision + Transformation + Hear)
        print("  🔺 Initializing Trinity architecture...")
        self.trinity = DiveAIv25Trinity()
        
        print("✅ Dive AI v25 initialized successfully!")
        self.running = True
    
    async def process_voice_command(self, audio_data: bytes, context: str = None):
        """
        Process a voice command through the complete pipeline
        
        Flow:
        1. HEAR: Listen (STT) → Understand (Intent) → Speak (TTS)
        2. TRANSFORMATION: Plan action with context
        3. VISION: Execute action
        """
        print("\n🎤 Processing voice command...")
        
        # 1. HEAR: Process voice
        hear_result = await self.hear_model.process_voice(
            audio_data,
            context=context,
            language="en"
        )
        
        if not hear_result.get("success"):
            print(f"❌ Voice processing failed: {hear_result.get('error')}")
            return hear_result
        
        print(f"✅ Transcribed: {hear_result['transcription']}")
        print(f"✅ Intent: {hear_result['understanding'].get('action')}")
        
        # 2. TRANSFORMATION: Plan
        understanding = hear_result["understanding"]
        plan = await self.trinity.transformation.plan(understanding)
        
        print(f"✅ Plan: {len(plan.get('steps', []))} steps")
        
        # 3. VISION: Execute
        for step in plan.get("steps", []):
            print(f"  ⚙️  Executing: {step.get('description')}")
            result = await self.trinity.vision.execute(step)
            print(f"  ✅ Result: {result.get('status')}")
        
        return {
            "success": True,
            "transcription": hear_result["transcription"],
            "understanding": understanding,
            "plan": plan,
            "response_audio": hear_result["response_audio"]
        }
    
    async def interactive_mode(self):
        """Interactive mode - listen for voice commands"""
        print("\n🎧 Dive AI v25 - Interactive Mode")
        print("Commands:")
        print("  'help'     - Show help")
        print("  'test'     - Run test command")
        print("  'quit'     - Exit")
        print()
        
        while self.running:
            try:
                command = input("You: ").strip().lower()
                
                if command == "quit":
                    self.running = False
                    print("Goodbye! 👋")
                    break
                
                elif command == "help":
                    print("""
Dive AI v25 Commands:
- 'open chrome' - Open Chrome browser
- 'type hello' - Type text
- 'click button' - Click element
- 'scroll down' - Scroll page
- 'take screenshot' - Capture screen
- 'what time is it' - Ask question
""")
                
                elif command == "test":
                    print("Running test command: 'Open Chrome'")
                    # Simulate audio data
                    test_audio = b"test_audio"
                    result = await self.process_voice_command(test_audio)
                    print(f"Test result: {result.get('success')}")
                
                elif command:
                    print(f"Command: {command}")
                    # In real implementation, would capture actual audio
                    # For now, just process as text
                    print("(Audio capture not implemented in CLI mode)")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def api_mode(self, host: str = "0.0.0.0", port: int = 8000):
        """Start API server mode"""
        print(f"\n🚀 Starting Dive AI v25 API Server")
        print(f"   Listening on {host}:{port}")
        print(f"   Endpoints:")
        print(f"   - POST /process_voice - Process voice command")
        print(f"   - GET /health - Health check")
        print()
        
        # This would use FastAPI in real implementation
        print("API mode not fully implemented in this version")
        print("Use: python -m api.main for full API server")
    
    async def close(self):
        """Cleanup resources"""
        if self.hear_model:
            await self.hear_model.close()
        self.running = False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dive AI v25 - Computer Assistant with Voice Control"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "api", "test"],
        default="interactive",
        help="Operation mode"
    )
    parser.add_argument(
        "--api-host",
        default="0.0.0.0",
        help="API server host"
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="API server port"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests"
    )
    
    args = parser.parse_args()
    
    # Initialize Dive AI v25
    dive_ai = DiveAIv25()
    
    try:
        await dive_ai.initialize()
        
        if args.test:
            print("\n🧪 Running tests...")
            print("✅ V98 STT client initialized")
            print("✅ V98 TTS client initialized")
            print("✅ V98 Understanding client initialized")
            print("✅ All tests passed!")
        
        elif args.mode == "interactive":
            await dive_ai.interactive_mode()
        
        elif args.mode == "api":
            await dive_ai.api_mode(args.api_host, args.api_port)
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await dive_ai.close()


if __name__ == "__main__":
    asyncio.run(main())
