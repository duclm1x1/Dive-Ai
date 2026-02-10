#!/usr/bin/env python3
"""
Dive AI V25 - Voice-Controlled Orchestrator
Integrates continuous voice processing with UI-TARS automation
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

from core.dive_voice_continuous import ContinuousVoiceProcessor, VoiceCommandParser
from core.dive_uitars_client import UITARSClient

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class DiveVoiceOrchestrator:
    """
    Main orchestrator for voice-controlled computer automation
    Manages continuous voice conversation while executing UI-TARS tasks
    """
    
    def __init__(
        self,
        stt_provider: str = "google",
        tts_provider: str = "pyttsx3",
        wake_word: str = "hey dive",
        api_key: Optional[str] = None,
        uitars_path: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize components
        print("🚀 Initializing Dive Voice Orchestrator...")
        
        # Voice processor
        self.voice_processor = ContinuousVoiceProcessor(
            stt_provider=stt_provider,
            tts_provider=tts_provider,
            wake_word=wake_word,
            api_key=self.api_key
        )
        
        # UI-TARS client
        self.uitars_client = UITARSClient(uitars_path=uitars_path)
        
        # Command parser
        self.command_parser = VoiceCommandParser(
            llm_client=OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None
        )
        
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
        
        print("✓ Orchestrator initialized")
    
    def start(self):
        """Start the orchestrator"""
        print("\n" + "="*60)
        print("🎤 DIVE AI V25 - Voice-Controlled Computer Automation")
        print("="*60)
        print(f"Wake word: '{self.voice_processor.wake_word}'")
        print("Say the wake word to start interacting")
        print("="*60 + "\n")
        
        self.is_running = True
        
        # Start voice processor
        self.voice_processor.start()
        
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
        print("👋 Goodbye!")
    
    def handle_command(self, command: str):
        """
        Handle voice command
        Called by voice processor when a command is detected
        """
        print(f"\n🎯 Command: {command}")
        
        # Acknowledge command
        self.voice_processor.speak("Understood. Executing now.", priority=True)
        
        # Parse command
        parsed = self.command_parser.parse(command)
        
        # Add to task queue
        task = {
            "command": command,
            "parsed": parsed,
            "timestamp": time.time()
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
        Called by voice processor for non-command text
        """
        print(f"\n💬 Conversation: {text}")
        
        # Add to context
        self.conversation_context.append({
            "role": "user",
            "type": "conversation",
            "content": text
        })
        
        # Generate response
        response = self._generate_response(text)
        
        # Add response to context
        self.conversation_context.append({
            "role": "assistant",
            "type": "conversation",
            "content": response
        })
        
        return response
    
    def _generate_response(self, text: str) -> str:
        """Generate conversational response"""
        # Simple responses for now
        # In production, use LLM with full context
        
        if "how are you" in text.lower():
            return "I'm doing great! Ready to help you with any computer tasks."
        
        elif "what can you do" in text.lower():
            return "I can control your computer through voice commands. Try saying 'open Chrome' or 'search for something'."
        
        elif "status" in text.lower() or "progress" in text.lower():
            if self.current_task:
                return f"I'm currently working on: {self.current_task['command']}"
            else:
                return "No tasks running right now. I'm ready for your next command."
        
        elif "thank" in text.lower():
            return "You're welcome! Let me know if you need anything else."
        
        else:
            return "I'm here to help. You can ask me to open applications, search the web, or control your computer."
    
    def _task_executor(self):
        """
        Execute tasks from queue
        Runs in separate thread to not block voice processing
        """
        while self.is_running:
            try:
                # Get task from queue
                task = self.task_queue.get(timeout=1)
                self.current_task = task
                
                print(f"\n⚙️ Executing task: {task['command']}")
                
                # Execute through UI-TARS
                self._execute_task(task)
                
                # Mark as complete
                self.current_task = None
                self.task_history.append(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ Task execution error: {e}")
                self.voice_processor.speak(f"Sorry, I encountered an error: {str(e)}")
                self.current_task = None
    
    def _execute_task(self, task: Dict[str, Any]):
        """Execute a single task"""
        command = task["command"]
        parsed = task.get("parsed", {})
        
        # Provide feedback
        self.voice_processor.speak(f"Starting: {command}")
        
        # Execute through UI-TARS
        try:
            results = []
            for result in self.uitars_client.execute_command(command, stream_feedback=True):
                results.append(result)
                
                # Provide real-time feedback
                if result["status"] == "success":
                    action_type = result["action"]["type"]
                    self.voice_processor.speak(f"Completed {action_type}")
                elif result["status"] == "error":
                    self.voice_processor.speak(f"Error: {result.get('error', 'Unknown error')}")
            
            # Final feedback
            if all(r["status"] == "success" for r in results):
                self.voice_processor.speak(f"Task completed successfully!")
            else:
                self.voice_processor.speak(f"Task completed with some errors.")
            
            # Store results
            task["results"] = results
            task["completed_at"] = time.time()
            
        except Exception as e:
            print(f"⚠ Execution error: {e}")
            self.voice_processor.speak(f"Failed to execute: {str(e)}")
            task["error"] = str(e)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_running": self.is_running,
            "current_task": self.current_task,
            "queue_size": self.task_queue.qsize(),
            "tasks_completed": len(self.task_history),
            "conversation_turns": len(self.conversation_context)
        }
    
    def save_session(self, filepath: str):
        """Save session data"""
        session_data = {
            "task_history": self.task_history,
            "conversation_context": self.conversation_context,
            "timestamp": time.time()
        }
        
        with open(filepath, "w") as f:
            json.dump(session_data, f, indent=2)
        
        print(f"✓ Session saved to {filepath}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dive AI Voice-Controlled Orchestrator")
    parser.add_argument("--stt", default="google", choices=["whisper", "google", "sphinx"],
                       help="Speech-to-text provider")
    parser.add_argument("--tts", default="pyttsx3", choices=["pyttsx3", "openai"],
                       help="Text-to-speech provider")
    parser.add_argument("--wake-word", default="hey dive",
                       help="Wake word to activate voice control")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--uitars-path", help="Path to UI-TARS installation")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = DiveVoiceOrchestrator(
        stt_provider=args.stt,
        tts_provider=args.tts,
        wake_word=args.wake_word,
        api_key=args.api_key,
        uitars_path=args.uitars_path
    )
    
    # Start
    orchestrator.start()


if __name__ == "__main__":
    main()
