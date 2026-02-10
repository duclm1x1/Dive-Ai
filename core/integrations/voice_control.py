"""
🎤 VOICE CONTROL
Speech recognition and voice commands for Dive AI
"""

import os
import sys
import json
import threading
import queue
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# Speech recognition will be imported if available
SPEECH_AVAILABLE = False
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    pass

# Text-to-speech will be imported if available
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


@dataclass
class VoiceCommand:
    """Parsed voice command"""
    raw_text: str
    intent: str
    priority: int = 3
    task_description: str = ""
    confidence: float = 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class VoiceCommandParser:
    """
    🔍 Parse voice commands into actionable intents
    """
    
    # Command patterns
    PATTERNS = {
        "status": ["status", "how are you", "what's happening", "report"],
        "agents": ["agents", "how many agents", "show agents", "agent status"],
        "task": ["create", "build", "make", "implement", "add", "fix", "update", "do"],
        "plan": ["plan", "schedule", "what's next", "24 hour", "today"],
        "stop": ["stop", "cancel", "abort", "halt"],
        "help": ["help", "what can you do", "commands"]
    }
    
    # Priority keywords
    PRIORITY_KEYWORDS = {
        "urgent": 5, "critical": 5, "important": 4, "high priority": 4,
        "asap": 5, "now": 4, "quick": 4, "later": 2, "low priority": 1
    }
    
    def parse(self, text: str) -> VoiceCommand:
        """Parse voice command text"""
        text_lower = text.lower().strip()
        
        # Detect intent
        intent = "unknown"
        for cmd, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    intent = cmd
                    break
            if intent != "unknown":
                break
        
        # Extract priority
        priority = 3
        for keyword, level in self.PRIORITY_KEYWORDS.items():
            if keyword in text_lower:
                priority = level
                break
        
        # Extract task description (for task intent)
        task_description = ""
        if intent == "task":
            # Remove command words
            task_description = text
            for pattern in self.PATTERNS["task"]:
                task_description = task_description.replace(pattern, "")
            task_description = task_description.strip()
        
        return VoiceCommand(
            raw_text=text,
            intent=intent,
            priority=priority,
            task_description=task_description
        )


class TextToSpeech:
    """
    🔊 Text-to-Speech engine
    """
    
    def __init__(self):
        self.engine = None
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 175)  # Speed
                self.engine.setProperty('volume', 0.9)
                print("✅ TTS engine initialized")
            except Exception as e:
                print(f"⚠️ TTS init failed: {e}")
    
    def speak(self, text: str, block: bool = False):
        """Speak text"""
        if self.engine:
            self.engine.say(text)
            if block:
                self.engine.runAndWait()
            else:
                threading.Thread(target=self.engine.runAndWait, daemon=True).start()
    
    def set_voice(self, voice_id: int = 0):
        """Set voice (0 = male, 1 = female typically)"""
        if self.engine:
            voices = self.engine.getProperty('voices')
            if voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
    
    def set_rate(self, rate: int = 175):
        """Set speech rate (words per minute)"""
        if self.engine:
            self.engine.setProperty('rate', rate)


class VoiceController:
    """
    🎤 Voice Control System for Dive AI
    
    Features:
    - Speech recognition
    - Wake word detection
    - Command parsing
    - Text-to-speech responses
    """
    
    WAKE_WORDS = ["hey dive", "dive ai", "dive", "ok dive"]
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts = TextToSpeech()
        self.parser = VoiceCommandParser()
        self.coordinator = None
        self.running = False
        self.command_queue = queue.Queue()
        self.callbacks: Dict[str, Callable] = {}
        
        if SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            print("✅ Voice Controller initialized")
        else:
            print("⚠️ SpeechRecognition not installed. Run: pip install SpeechRecognition")
    
    def set_coordinator(self, coordinator):
        """Set coordinator reference"""
        self.coordinator = coordinator
    
    def set_callback(self, intent: str, callback: Callable):
        """Set callback for intent"""
        self.callbacks[intent] = callback
    
    def _detect_wake_word(self, text: str) -> bool:
        """Check if wake word was spoken"""
        text_lower = text.lower()
        for wake_word in self.WAKE_WORDS:
            if wake_word in text_lower:
                return True
        return False
    
    def _strip_wake_word(self, text: str) -> str:
        """Remove wake word from text"""
        text_lower = text.lower()
        for wake_word in self.WAKE_WORDS:
            text_lower = text_lower.replace(wake_word, "")
        return text_lower.strip()
    
    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech once"""
        if not SPEECH_AVAILABLE:
            return None
        
        try:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"   Heard: '{text}'")
                    return text
                except sr.UnknownValueError:
                    return None
                except sr.RequestError as e:
                    print(f"   ❌ Recognition error: {e}")
                    return None
        except Exception as e:
            print(f"   ❌ Microphone error: {e}")
            return None
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """Process voice command"""
        command = self.parser.parse(text)
        
        result = {
            "command": command,
            "response": "",
            "executed": False
        }
        
        # Execute based on intent
        if command.intent == "status" and self.coordinator:
            status = self.coordinator.execute({"action": "get_status"})
            agents_idle = status.data.get("agents_idle", 0)
            agents_busy = status.data.get("agents_busy", 0)
            result["response"] = f"Coordinator online. {agents_idle} agents idle, {agents_busy} agents busy."
            result["executed"] = True
        
        elif command.intent == "agents" and self.coordinator:
            agents = self.coordinator.execute({"action": "spawn_agents"})
            total = agents.data.get("total_agents", 0)
            result["response"] = f"I have {total} Dive Coder agents ready."
            result["executed"] = True
        
        elif command.intent == "task" and self.coordinator:
            if command.task_description:
                self.coordinator.execute({
                    "action": "autonomous_execute",
                    "task": command.task_description,
                    "priority": command.priority
                })
                result["response"] = f"Task received with priority {command.priority}. Executing autonomously."
                result["executed"] = True
            else:
                result["response"] = "What task would you like me to do?"
        
        elif command.intent == "plan" and self.coordinator:
            plan = self.coordinator.execute({"action": "generate_24h_plan"})
            plan_date = plan.data.get("plan_date", "today")
            result["response"] = f"24-hour plan generated for {plan_date}. Check the dashboard for details."
            result["executed"] = True
        
        elif command.intent == "stop":
            result["response"] = "Stopping current operations."
            result["executed"] = True
        
        elif command.intent == "help":
            result["response"] = "You can ask me for status, agents, create tasks, or generate plans."
            result["executed"] = True
        
        else:
            result["response"] = "I didn't understand that command."
        
        # Speak response
        if result["response"]:
            self.tts.speak(result["response"])
        
        # Call custom callback if registered
        if command.intent in self.callbacks:
            self.callbacks[command.intent](command, result)
        
        return result
    
    def start_listening(self):
        """Start continuous listening loop"""
        if not SPEECH_AVAILABLE:
            print("⚠️ Cannot start: SpeechRecognition not installed")
            return
        
        self.running = True
        
        self.tts.speak("Dive AI voice control activated.")
        
        print("\n🎤 Voice Control Active")
        print(f"   Wake words: {', '.join(self.WAKE_WORDS)}")
        print("   Say 'stop' to end\n")
        
        while self.running:
            text = self.listen_once(timeout=5)
            
            if text:
                # Check for wake word or direct command
                if self._detect_wake_word(text):
                    command_text = self._strip_wake_word(text)
                    if command_text:
                        self.process_command(command_text)
                    else:
                        self.tts.speak("Yes?")
                        # Wait for follow-up command
                        follow_up = self.listen_once(timeout=5)
                        if follow_up:
                            self.process_command(follow_up)
                
                # Check for stop command
                if "stop listening" in text.lower() or "exit" in text.lower():
                    self.tts.speak("Voice control deactivated.")
                    self.running = False
    
    def stop_listening(self):
        """Stop listening loop"""
        self.running = False
    
    def start_listening_async(self):
        """Start listening in background thread"""
        thread = threading.Thread(target=self.start_listening, daemon=True)
        thread.start()
        return thread


# Convenience functions
def create_voice_controller() -> VoiceController:
    """Create voice controller"""
    return VoiceController()


if __name__ == "__main__":
    print("\n🎤 Voice Control Module")
    print(f"\n   SpeechRecognition: {'✅' if SPEECH_AVAILABLE else '❌ pip install SpeechRecognition'}")
    print(f"   pyttsx3 (TTS): {'✅' if TTS_AVAILABLE else '❌ pip install pyttsx3'}")
    
    if SPEECH_AVAILABLE and TTS_AVAILABLE:
        print("\n🧪 Quick test...")
        
        controller = VoiceController()
        
        # Test TTS
        controller.tts.speak("Dive AI voice control ready.", block=True)
        
        # Test single listen
        print("\n🎤 Say something (5 second timeout)...")
        text = controller.listen_once(timeout=5)
        if text:
            result = controller.process_command(text)
            print(f"   Result: {result}")
