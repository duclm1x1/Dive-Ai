#!/usr/bin/env python3
"""
Dive AI V25 - Continuous Voice Processing Module
Enables non-blocking voice interaction during task execution
"""

import os
import queue
import threading
import time
from typing import Optional, Callable, Dict, Any
import json

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from core.dive_audio_adapter import SpeechRecognitionAdapter
except ImportError:
    SpeechRecognitionAdapter = None


class ContinuousVoiceProcessor:
    """
    Continuous voice processing with non-blocking TTS and STT
    Maintains conversation while executing background tasks
    """
    
    def __init__(
        self,
        stt_provider: str = "whisper",  # whisper, google, sphinx
        tts_provider: str = "pyttsx3",  # pyttsx3, openai, elevenlabs
        wake_word: str = "hey dive",
        language: str = "en-US",
        api_key: Optional[str] = None
    ):
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self.wake_word = wake_word.lower()
        self.language = language
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Threading components
        self.voice_queue = queue.Queue()
        self.tts_queue = queue.Queue()
        self.is_listening = False
        self.is_speaking = False
        self.conversation_active = True
        
        # Initialize components
        self._init_stt()
        self._init_tts()
        
        # Conversation state
        self.last_speech_time = 0
        self.conversation_timeout = 30  # Seconds of silence before requiring wake word again
        
        # Callbacks
        self.on_command: Optional[Callable[[str], None]] = None
        self.on_conversation: Optional[Callable[[str], str]] = None
        
        print(f"✓ Voice Processor initialized (STT: {stt_provider}, TTS: {tts_provider})")
    
    def _init_stt(self):
        """Initialize Speech-to-Text"""
        if self.stt_provider == "whisper" and OpenAI:
            self.openai_client = OpenAI(api_key=self.api_key)
            try:
                self.recognizer = sr.Recognizer() if sr else None
                self.microphone = sr.Microphone() if sr else None
                if self.microphone:
                    print("✓ Whisper STT initialized")
            except (AttributeError, Exception) as e:
                print(f"⚠ Microphone not available for Whisper: {e}")
                if SpeechRecognitionAdapter:
                    print("⚙ Using sounddevice adapter for Whisper")
                    self.recognizer = sr.Recognizer() if sr else None
                    self.microphone = SpeechRecognitionAdapter()
                else:
                    self.recognizer = sr.Recognizer() if sr else None
                    self.microphone = None
        elif sr:
            try:
                self.recognizer = sr.Recognizer()
                # Tuning for better responsiveness
                self.recognizer.energy_threshold = 4000  # Default is 300, higher is less sensitive to noise
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8    # Seconds of silence to consider a phrase ended (default 0.8)
                self.recognizer.non_speaking_duration = 0.5 # Seconds of non-speaking to consider silence
                
                self.microphone = sr.Microphone()
                print(f"✓ {self.stt_provider} STT initialized")
            except (AttributeError, Exception) as e:
                print(f"⚠ {self.stt_provider} STT hardware not available: {e}")
                if SpeechRecognitionAdapter:
                    print("⚙ Using sounddevice adapter")
                    self.recognizer = sr.Recognizer()
                    # Apply same tuning to adapter mode
                    self.recognizer.energy_threshold = 1000 # Different threshold for sounddevice often needed
                    self.recognizer.dynamic_energy_threshold = True
                    self.recognizer.pause_threshold = 0.6
                    
                    self.microphone = SpeechRecognitionAdapter()
                else:
                    self.recognizer = sr.Recognizer()
                    self.microphone = None
        else:
            print("⚠ Speech recognition not available. Install: pip install SpeechRecognition pyaudio")
            self.recognizer = None
            self.microphone = None
    
    def _init_tts(self):
        """Initialize Text-to-Speech"""
        if self.tts_provider == "pyttsx3" and pyttsx3:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 175)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            print("✓ pyttsx3 TTS initialized")
        elif self.tts_provider == "openai" and OpenAI:
            self.openai_client = OpenAI(api_key=self.api_key)
            print("✓ OpenAI TTS initialized")
        else:
            print("⚠ TTS not available. Install: pip install pyttsx3")
            self.tts_engine = None
    
    def start(self):
        """Start continuous voice processing"""
        if not self.recognizer or not self.microphone:
            print("⚠ Cannot start voice processing - STT not available")
            return
        
        # Start threads
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.tts_thread = threading.Thread(target=self._tts_loop, daemon=True)
        
        self.listen_thread.start()
        self.process_thread.start()
        self.tts_thread.start()
        
        print("🎤 Voice processing started. Say '{}' to activate.".format(self.wake_word))
    
    def stop(self):
        """Stop voice processing"""
        self.conversation_active = False
        print("🛑 Voice processing stopped")
    
    def _listen_loop(self):
        """Continuous listening loop"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while self.conversation_active:
            try:
                with self.microphone as source:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    self.voice_queue.put(audio)
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"⚠ Listen error: {e}")
                time.sleep(1)
    
    def _process_loop(self):
        """Process voice input with session management"""
        wake_word_detected = False
        
        while self.conversation_active:
            try:
                # Check for session timeout
                if wake_word_detected and time.time() - self.last_speech_time > self.conversation_timeout:
                    wake_word_detected = False
                    print("💤 Session timed out. Say '{}' to reactivate.".format(self.wake_word))
                    self.speak("Going into standby mode.")

                audio = self.voice_queue.get(timeout=1)
                
                # Transcribe
                text = self._transcribe(audio)
                if not text:
                    continue
                
                print(f"🎤 Heard: {text}")
                text_lower = text.lower()
                
                # Check for wake word or if already in session
                is_wake = self.wake_word in text_lower
                
                if is_wake:
                    wake_word_detected = True
                    self.last_speech_time = time.time()
                    # Strip wake word for cleaner processing
                    process_text = text.lower().replace(self.wake_word, "").strip()
                    if not process_text:
                        self.speak("Yes, I'm listening.")
                        continue
                    text = process_text
                
                # Check for exit commands
                if wake_word_detected and any(cmd in text_lower for cmd in ["go to sleep", "goodbye", "stop listening"]):
                    wake_word_detected = False
                    self.speak("Understood. I'll be here if you need me.")
                    print("💤 Session ended by user.")
                    continue

                # Process if wake word was detected or already in conversation
                if wake_word_detected:
                    self.last_speech_time = time.time()
                    # Classify intent
                    if self._is_command(text):
                        # Execute command
                        if self.on_command:
                            self.on_command(text)
                    else:
                        # Continue conversation
                        if self.on_conversation:
                            response = self.on_conversation(text)
                            self.speak(response)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ Process error: {e}")
    
    def _transcribe(self, audio) -> Optional[str]:
        """Transcribe audio to text"""
        try:
            if self.stt_provider == "whisper" and self.openai_client:
                # Save audio to temp file for Whisper API
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio.get_wav_data())
                    temp_path = f.name
                
                with open(temp_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=self.language.split("-")[0]
                    )
                
                os.unlink(temp_path)
                return transcript.text
            
            elif self.stt_provider == "google":
                try:
                    return self.recognizer.recognize_google(audio, language=self.language)
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    return None
                except sr.RequestError as e:
                    print(f"⚠ Google STT Request Error: {e}")
                    return None
            
            elif self.stt_provider == "sphinx":
                return self.recognizer.recognize_sphinx(audio)
            
        except Exception as e:
            import traceback
            print(f"⚠ Transcription system error: {e}")
            traceback.print_exc()
            return None
    
    def _is_command(self, text: str) -> bool:
        """Classify if text is a command or conversation"""
        command_keywords = [
            "open", "close", "start", "stop", "launch", "run",
            "click", "type", "search", "navigate", "go to",
            "install", "download", "upload", "save", "delete",
            "create", "make", "build", "execute", "perform"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in command_keywords)
    
    def speak(self, text: str, priority: bool = False):
        """Add text to TTS queue"""
        if priority:
            # Insert at front of queue
            temp_queue = queue.Queue()
            temp_queue.put(text)
            while not self.tts_queue.empty():
                temp_queue.put(self.tts_queue.get())
            self.tts_queue = temp_queue
        else:
            self.tts_queue.put(text)
    
    def _tts_loop(self):
        """Text-to-Speech loop (non-blocking)"""
        while self.conversation_active:
            try:
                text = self.tts_queue.get(timeout=1)
                self._synthesize(text)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ TTS error: {e}")
    
    def _synthesize(self, text: str):
        """Synthesize text to speech"""
        try:
            self.is_speaking = True
            print(f"🔊 Speaking: {text}")
            
            if self.tts_provider == "pyttsx3" and self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            elif self.tts_provider == "openai" and self.openai_client:
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text
                )
                
                # Play audio (requires additional library like pygame or playsound)
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(response.content)
                    temp_path = f.name
                
                # Play audio file
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except ImportError:
                    print("⚠ pygame not available for audio playback")
                
                os.unlink(temp_path)
            
            self.is_speaking = False
            
        except Exception as e:
            print(f"⚠ Synthesis error: {e}")
            self.is_speaking = False


class VoiceCommandParser:
    """Parse natural language voice commands into structured actions"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def parse(self, command: str) -> Dict[str, Any]:
        """
        Parse voice command into structured action
        
        Example:
            Input: "open Chrome and go to GitHub"
            Output: {
                "actions": [
                    {"type": "open_app", "app": "Chrome"},
                    {"type": "navigate", "url": "https://github.com"}
                ]
            }
        """
        if self.llm_client:
            return self._parse_with_llm(command)
        else:
            return self._parse_with_rules(command)
    
    def _parse_with_llm(self, command: str) -> Dict[str, Any]:
        """Use LLM to parse command"""
        prompt = f"""
Parse this voice command into structured actions for computer control:

Command: "{command}"

Available action types:
- open_app: Open an application (params: app_name)
- close_app: Close an application (params: app_name)
- click: Click at location (params: x, y, element_name)
- type: Type text (params: text)
- navigate: Navigate browser (params: url)
- search: Search for something (params: query, engine)
- screenshot: Take screenshot
- wait: Wait for duration (params: seconds)

Return JSON format:
{{
    "intent": "brief description",
    "actions": [
        {{"type": "action_type", "params": {{...}}}}
    ]
}}
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠ LLM parsing error: {e}")
            return self._parse_with_rules(command)
    
    def _parse_with_rules(self, command: str) -> Dict[str, Any]:
        """Simple rule-based parsing"""
        command_lower = command.lower()
        actions = []
        
        # Open application
        if "open" in command_lower:
            app_name = self._extract_app_name(command_lower)
            if app_name:
                actions.append({"type": "open_app", "params": {"app_name": app_name}})
        
        # Navigate
        if "go to" in command_lower or "navigate to" in command_lower:
            url = self._extract_url(command)
            if url:
                actions.append({"type": "navigate", "params": {"url": url}})
        
        # Search
        if "search for" in command_lower or "search" in command_lower:
            query = self._extract_search_query(command)
            if query:
                actions.append({"type": "search", "params": {"query": query, "engine": "google"}})
        
        return {
            "intent": command,
            "actions": actions
        }
    
    def _extract_app_name(self, command: str) -> Optional[str]:
        """Extract application name from command"""
        apps = ["chrome", "firefox", "safari", "edge", "vscode", "code", "terminal", "notepad"]
        for app in apps:
            if app in command:
                return app.capitalize()
        return None
    
    def _extract_url(self, command: str) -> Optional[str]:
        """Extract URL from command"""
        words = command.split()
        for word in words:
            if "." in word and not word.startswith("."):
                # Simple URL detection
                if not word.startswith("http"):
                    return f"https://{word}"
                return word
        return None
    
    def _extract_search_query(self, command: str) -> Optional[str]:
        """Extract search query from command"""
        if "search for" in command.lower():
            return command.lower().split("search for")[-1].strip()
        elif "search" in command.lower():
            return command.lower().split("search")[-1].strip()
        return None


# Example usage
if __name__ == "__main__":
    def handle_command(command: str):
        print(f"\n🎯 Command received: {command}")
        parser = VoiceCommandParser()
        parsed = parser.parse(command)
        print(f"📋 Parsed: {json.dumps(parsed, indent=2)}")
    
    def handle_conversation(text: str) -> str:
        print(f"\n💬 Conversation: {text}")
        return f"I heard you say: {text}. How can I help?"
    
    # Initialize voice processor
    processor = ContinuousVoiceProcessor(
        stt_provider="google",  # Use google for testing (free)
        tts_provider="pyttsx3",
        wake_word="hey dive"
    )
    
    processor.on_command = handle_command
    processor.on_conversation = handle_conversation
    
    # Start processing
    processor.start()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop()
        print("\n👋 Goodbye!")
