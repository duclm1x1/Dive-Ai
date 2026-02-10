#!/usr/bin/env python3
"""
Dive AI V25 - Full-Duplex Voice Orchestrator
Integrates streaming TTS, VAD barge-in, talk-while-act, and 128 agents
"""

import os
import sys
import time
import queue
import threading
from typing import Optional, Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dive_streaming_tts import StreamingTTS, LLMStreamingTTS
from core.dive_vad_bargein import VADBargeIn, BargeInController
from core.dive_talk_while_act import TalkWhileActNarrator, UITARSEventNarrator, ActionStatus
from core.dive_uitars_client import UITARSClient
from core.dive_voice_continuous import ContinuousVoiceProcessor, VoiceCommandParser

try:
    from core.dive_agent_fleet import DiveAgentFleet
except ImportError:
    DiveAgentFleet = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class FullDuplexVoiceOrchestrator:
    """
    Full-duplex voice orchestrator with:
    - Streaming TTS (speak while generating)
    - VAD barge-in (interrupt AI speech)
    - Talk-while-act (narrate actions in real-time)
    - 128 agent integration
    """
    
    def __init__(
        self,
        stt_provider: str = "google",
        tts_provider: str = "pyttsx3",
        wake_word: str = "hey dive",
        api_key: Optional[str] = None,
        uitars_path: Optional[str] = None,
        enable_barge_in: bool = True,
        narration_style: str = "detailed"
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.enable_barge_in = enable_barge_in
        
        print("="*70)
        print("🚀 Initializing Dive AI V25 Full-Duplex Voice Orchestrator")
        print("="*70)
        
        # 1. Initialize Streaming TTS
        print("\n[1/7] Initializing Streaming TTS...")
        self.streaming_tts = StreamingTTS(
            provider=tts_provider,
            api_key=self.api_key,
            chunk_size=50
        )
        
        # 2. Initialize VAD Barge-in
        print("\n[2/7] Initializing VAD Barge-in...")
        if enable_barge_in:
            try:
                self.vad = VADBargeIn(
                    sensitivity=2,
                    trigger_threshold=3
                )
                self.barge_in_controller = BargeInController(
                    vad=self.vad,
                    tts_controller=self.streaming_tts,
                    abort_tasks_on_interrupt=False  # Don't abort by default
                )
            except ImportError as e:
                print(f"⚠ VAD not available: {e}")
                print("  Install with: pip install webrtcvad pyaudio")
                self.vad = None
                self.barge_in_controller = None
        else:
            self.vad = None
            self.barge_in_controller = None
        
        # 3. Initialize Talk-While-Act Narrator
        print("\n[3/7] Initializing Talk-While-Act Narrator...")
        self.narrator = TalkWhileActNarrator(
            tts_controller=self.streaming_tts,
            narration_style=narration_style,
            narrate_progress=True
        )
        
        # 4. Initialize UI-TARS Client
        print("\n[4/7] Initializing UI-TARS Client...")
        self.uitars_client = UITARSClient(uitars_path=uitars_path)
        self.event_narrator = UITARSEventNarrator(
            narrator=self.narrator,
            uitars_client=self.uitars_client
        )
        
        # 5. Initialize Voice Processor
        print("\n[5/7] Initializing Voice Processor...")
        self.voice_processor = ContinuousVoiceProcessor(
            stt_provider=stt_provider,
            tts_provider=tts_provider,  # Won't be used, we use streaming_tts instead
            wake_word=wake_word,
            api_key=self.api_key
        )
        
        # Override TTS with streaming version
        self.voice_processor.tts_engine = None  # Disable built-in TTS
        
        # 6. Initialize 128 Agent Fleet
        print("\n[6/7] Initializing 128 Agent Fleet...")
        if DiveAgentFleet:
            try:
                self.agent_fleet = DiveAgentFleet()
                print(f"✓ Loaded {len(self.agent_fleet.agents)} agents")
            except Exception as e:
                print(f"⚠ Agent fleet error: {e}")
                self.agent_fleet = None
        else:
            print("⚠ Agent fleet not available")
            self.agent_fleet = None
        
        # 7. Initialize LLM Client
        print("\n[7/7] Initializing LLM Client...")
        if OpenAI and self.api_key:
            self.llm_client = OpenAI(api_key=self.api_key)
            self.llm_streaming_tts = LLMStreamingTTS(
                llm_client=self.llm_client,
                tts=self.streaming_tts,
                model="gpt-4"
            )
        else:
            print("⚠ LLM client not available (no API key)")
            self.llm_client = None
            self.llm_streaming_tts = None
        
        # Task management
        self.task_queue = queue.Queue()
        self.current_task = None
        self.task_history = []
        
        # State
        self.is_running = False
        self.conversation_context = []
        
        # Set up callbacks
        self.voice_processor.on_command = self.handle_command
        self.voice_processor.on_conversation = self.handle_conversation
        
        print("\n" + "="*70)
        print("✅ Full-Duplex Voice Orchestrator Ready!")
        print("="*70)
    
    def start(self):
        """Start the full-duplex orchestrator"""
        print("\n" + "="*70)
        print("🎤 DIVE AI V25 - Full-Duplex Voice Control")
        print("="*70)
        print(f"Wake word: '{self.voice_processor.wake_word}'")
        print("Features:")
        print("  ✓ Streaming TTS (speak while generating)")
        print(f"  {'✓' if self.barge_in_controller else '✗'} VAD Barge-in (interrupt AI)")
        print("  ✓ Talk-While-Act (real-time narration)")
        print(f"  ✓ 128 Agent Fleet")
        print("\nSay the wake word to start interacting")
        print("="*70 + "\n")
        
        self.is_running = True
        
        # Start components
        self.voice_processor.start()
        self.narrator.start()
        
        if self.barge_in_controller:
            self.barge_in_controller.start()
        
        # Start task executor thread
        self.task_thread = threading.Thread(target=self._task_executor, daemon=True)
        self.task_thread.start()
        
        # Keep running
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        print("\n🛑 Stopping orchestrator...")
        self.is_running = False
        
        self.voice_processor.stop()
        self.narrator.stop()
        
        if self.barge_in_controller:
            self.barge_in_controller.stop()
        
        print("👋 Goodbye!")
    
    def handle_command(self, command: str):
        """
        Handle voice command
        Uses streaming TTS for acknowledgment
        """
        print(f"\n🎯 Command: {command}")
        
        # Acknowledge with streaming TTS
        self.streaming_tts.speak("Understood. Executing now.", priority=True)
        
        # Add to task queue
        task = {
            "command": command,
            "timestamp": time.time(),
            "type": "command"
        }
        self.task_queue.put(task)
        
        # Update context
        self.conversation_context.append({
            "role": "user",
            "type": "command",
            "content": command
        })
    
    def handle_conversation(self, text: str) -> str:
        """
        Handle conversational input
        Uses LLM streaming + TTS for response
        """
        print(f"\n💬 Conversation: {text}")
        
        # Add to context
        self.conversation_context.append({
            "role": "user",
            "type": "conversation",
            "content": text
        })
        
        # Generate response with streaming
        if self.llm_streaming_tts:
            response = self._generate_streaming_response(text)
        else:
            response = self._generate_simple_response(text)
            self.streaming_tts.speak(response)
        
        # Add response to context
        self.conversation_context.append({
            "role": "assistant",
            "type": "conversation",
            "content": response
        })
        
        return response
    
    def _generate_streaming_response(self, text: str) -> str:
        """Generate response with LLM streaming + TTS"""
        system_prompt = """You are Dive AI, a helpful voice assistant that controls computers.
You are currently having a conversation while potentially executing tasks in the background.
Be concise, friendly, and informative. Keep responses under 2 sentences when possible."""
        
        def on_chunk(chunk):
            print(chunk, end='', flush=True)
        
        response = self.llm_streaming_tts.generate_and_speak(
            prompt=text,
            system_prompt=system_prompt,
            on_chunk=on_chunk
        )
        
        print()  # New line after streaming
        return response
    
    def _generate_simple_response(self, text: str) -> str:
        """Simple rule-based response"""
        text_lower = text.lower()
        
        if "how are you" in text_lower:
            return "I'm doing great! Ready to help you with any computer tasks."
        elif "what can you do" in text_lower:
            return "I can control your computer through voice. Try asking me to open apps or search the web."
        elif "status" in text_lower or "progress" in text_lower:
            if self.current_task:
                return f"I'm currently working on: {self.current_task['command']}"
            else:
                return "No tasks running. I'm ready for your next command."
        elif "thank" in text_lower:
            return "You're welcome! Let me know if you need anything else."
        else:
            return "I'm here to help. You can ask me to control your computer or just chat."
    
    def _task_executor(self):
        """
        Execute tasks from queue
        Uses talk-while-act narration
        """
        while self.is_running:
            try:
                task = self.task_queue.get(timeout=1)
                self.current_task = task
                
                print(f"\n⚙️ Executing task: {task['command']}")
                
                # Execute with narration
                self._execute_task_with_narration(task)
                
                # Mark as complete
                self.current_task = None
                self.task_history.append(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ Task execution error: {e}")
                self.streaming_tts.speak(f"Sorry, I encountered an error: {str(e)}")
                self.current_task = None
    
    def _execute_task_with_narration(self, task: Dict[str, Any]):
        """Execute task with real-time narration"""
        command = task["command"]
        
        # Initial feedback
        self.streaming_tts.speak(f"Starting: {command}")
        
        # Execute through UI-TARS with narration
        try:
            self.event_narrator.execute_with_narration(command)
            
            # Success feedback
            self.streaming_tts.speak("Task completed successfully!")
            
        except Exception as e:
            print(f"⚠ Execution error: {e}")
            self.streaming_tts.speak(f"Failed to execute: {str(e)}")
            task["error"] = str(e)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_running": self.is_running,
            "current_task": self.current_task,
            "queue_size": self.task_queue.qsize(),
            "tasks_completed": len(self.task_history),
            "conversation_turns": len(self.conversation_context),
            "tts_active": self.streaming_tts.is_active(),
            "barge_in_enabled": self.barge_in_controller is not None,
            "agents_available": len(self.agent_fleet.agents) if self.agent_fleet else 0
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dive AI Full-Duplex Voice Orchestrator")
    parser.add_argument("--stt", default="google", choices=["whisper", "google", "sphinx"],
                       help="Speech-to-text provider")
    parser.add_argument("--tts", default="pyttsx3", choices=["pyttsx3", "openai"],
                       help="Text-to-speech provider")
    parser.add_argument("--wake-word", default="hey dive",
                       help="Wake word to activate")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--uitars-path", help="Path to UI-TARS installation")
    parser.add_argument("--no-barge-in", action="store_true",
                       help="Disable VAD barge-in")
    parser.add_argument("--narration", default="detailed",
                       choices=["detailed", "concise", "minimal"],
                       help="Narration style")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = FullDuplexVoiceOrchestrator(
        stt_provider=args.stt,
        tts_provider=args.tts,
        wake_word=args.wake_word,
        api_key=args.api_key,
        uitars_path=args.uitars_path,
        enable_barge_in=not args.no_barge_in,
        narration_style=args.narration
    )
    
    # Start
    orchestrator.start()


if __name__ == "__main__":
    main()
