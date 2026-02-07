#!/usr/bin/env python3
"""
Dive AI V25.3 - Multimodal Orchestrator
Coordinates voice + vision + actions for intelligent computer control
"""

import os
import asyncio
import threading
import queue
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    from core.dive_realtime_voice import RealtimeVoiceProcessor, RealtimeConfig
    from core.dive_vision import DiveVisionProcessor, VisionConfig
    from core.dive_wake_word_enhanced import EnhancedWakeWordDetector, PhoneticTranscriptionFixer
    from core.dive_agent_fleet import AgentFleet
except ImportError:
    print("⚠ Some modules not available, using stubs")
    RealtimeVoiceProcessor = None
    DiveVisionProcessor = None
    EnhancedWakeWordDetector = None
    AgentFleet = None


class InputMode(Enum):
    """Input processing mode"""
    VOICE_ONLY = "voice_only"
    VISION_REQUIRED = "vision_required"
    MULTIMODAL = "multimodal"


@dataclass
class MultimodalConfig:
    """Configuration for multimodal orchestrator"""
    # Voice settings
    voice_model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice_enabled: bool = True
    wake_word: str = "hey dive"
    wake_word_confidence: float = 0.7
    
    # Vision settings
    vision_model: str = "gpt-4-vision-preview"
    vision_enabled: bool = True
    auto_capture_screen: bool = True
    
    # Orchestration
    session_timeout: int = 30  # seconds
    enable_continuous_mode: bool = True
    enable_function_calling: bool = True


class MultimodalOrchestrator:
    """
    Orchestrates voice and vision inputs for intelligent computer control
    Maintains V25.1 features while adding multimodal capabilities
    """
    
    def __init__(
        self,
        config: Optional[MultimodalConfig] = None,
        agent_fleet: Optional[Any] = None
    ):
        self.config = config or MultimodalConfig()
        self.agent_fleet = agent_fleet
        
        # Initialize components
        self._init_voice()
        self._init_vision()
        self._init_wake_word()
        
        # State
        self.session_active = False
        self.last_interaction_time = 0
        self.conversation_history = []
        
        # Queues
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        print("✓ Multimodal Orchestrator initialized")
        print(f"  Voice: {'Enabled' if self.config.voice_enabled else 'Disabled'}")
        print(f"  Vision: {'Enabled' if self.config.vision_enabled else 'Disabled'}")
        print(f"  Wake word: '{self.config.wake_word}'")
    
    def _init_voice(self):
        """Initialize voice processor"""
        if self.config.voice_enabled and RealtimeVoiceProcessor:
            voice_config = RealtimeConfig(
                model=self.config.voice_model,
                instructions=self._get_system_instructions()
            )
            
            self.voice_processor = RealtimeVoiceProcessor(
                config=voice_config,
                on_response=self._handle_voice_response,
                on_audio=self._handle_audio_output,
                on_function_call=self._handle_function_call
            )
            print("✓ Voice processor initialized")
        else:
            self.voice_processor = None
            print("⚠ Voice processor not available")
    
    def _init_vision(self):
        """Initialize vision processor"""
        if self.config.vision_enabled and DiveVisionProcessor:
            vision_config = VisionConfig(
                model=self.config.vision_model,
                auto_capture=self.config.auto_capture_screen
            )
            
            self.vision_processor = DiveVisionProcessor(config=vision_config)
            print("✓ Vision processor initialized")
        else:
            self.vision_processor = None
            print("⚠ Vision processor not available")
    
    def _init_wake_word(self):
        """Initialize wake word detector"""
        if EnhancedWakeWordDetector:
            self.wake_word_detector = EnhancedWakeWordDetector(
                wake_word=self.config.wake_word,
                confidence_threshold=self.config.wake_word_confidence
            )
            self.transcription_fixer = PhoneticTranscriptionFixer()
            print("✓ Wake word detector initialized")
        else:
            self.wake_word_detector = None
            self.transcription_fixer = None
            print("⚠ Wake word detector not available")
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for voice model"""
        return """
        You are Dive AI, an intelligent voice assistant with computer vision capabilities.
        
        Your role:
        - Help users control their computer through voice commands
        - Understand what's on the user's screen when needed
        - Execute tasks using available functions
        - Maintain natural, conversational interaction
        
        Capabilities:
        - Voice interaction (you can hear and speak)
        - Screen vision (you can see what's on screen)
        - Computer control (open apps, click, type, navigate)
        - Task execution (via 128 agent fleet)
        
        Guidelines:
        - Be concise but helpful
        - Ask for screen vision when context is needed
        - Confirm before destructive actions
        - Narrate actions as you perform them
        - Handle Vietnamese-accented English gracefully
        
        Available functions:
        - open_application(app_name)
        - click_element(description)
        - type_text(text)
        - navigate_browser(url)
        - search_web(query)
        - capture_screen()
        - analyze_screen(prompt)
        - execute_task(task_description)
        """
    
    def _determine_input_mode(self, text: str) -> InputMode:
        """
        Determine if command requires vision
        
        Args:
            text: Command text
        
        Returns:
            InputMode enum
        """
        vision_keywords = [
            "see", "look", "screen", "what's", "show", "find",
            "click", "button", "window", "element", "visible",
            "read", "text", "error", "message"
        ]
        
        text_lower = text.lower()
        
        # Check if vision is needed
        needs_vision = any(keyword in text_lower for keyword in vision_keywords)
        
        if needs_vision and self.config.vision_enabled:
            return InputMode.VISION_REQUIRED
        else:
            return InputMode.VOICE_ONLY
    
    def _handle_voice_response(self, text: str):
        """Handle text response from voice model"""
        print(f"🤖 AI: {text}")
        self.conversation_history.append({
            "role": "assistant",
            "content": text
        })
    
    def _handle_audio_output(self, audio_data: bytes):
        """Handle audio output from voice model"""
        # Audio is automatically played by RealtimeVoiceProcessor
        pass
    
    def _handle_function_call(self, name: str, args: dict) -> Dict[str, Any]:
        """
        Handle function calls from voice model
        
        Args:
            name: Function name
            args: Function arguments
        
        Returns:
            Function result
        """
        print(f"🔧 Function call: {name}({args})")
        
        try:
            # Route to appropriate handler
            if name == "open_application":
                return self._open_application(args.get("app_name"))
            
            elif name == "click_element":
                return self._click_element(args.get("description"))
            
            elif name == "type_text":
                return self._type_text(args.get("text"))
            
            elif name == "navigate_browser":
                return self._navigate_browser(args.get("url"))
            
            elif name == "search_web":
                return self._search_web(args.get("query"))
            
            elif name == "capture_screen":
                return self._capture_screen()
            
            elif name == "analyze_screen":
                return self._analyze_screen(args.get("prompt"))
            
            elif name == "execute_task":
                return self._execute_task(args.get("task_description"))
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown function: {name}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def _open_application(self, app_name: str) -> Dict[str, Any]:
        """Open application"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            
            if system == "Windows":
                subprocess.Popen(["start", app_name], shell=True)
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux
                subprocess.Popen([app_name.lower()])
            
            return {
                "success": True,
                "message": f"Opened {app_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open {app_name}: {str(e)}"
            }
    
    def _click_element(self, description: str) -> Dict[str, Any]:
        """Click element using vision"""
        if not self.vision_processor:
            return {"success": False, "message": "Vision not available"}
        
        success = self.vision_processor.click_element(description)
        
        return {
            "success": success,
            "message": f"Clicked '{description}'" if success else f"Could not find '{description}'"
        }
    
    def _type_text(self, text: str) -> Dict[str, Any]:
        """Type text"""
        import pyautogui
        
        try:
            pyautogui.write(text, interval=0.05)
            return {
                "success": True,
                "message": f"Typed: {text}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to type: {str(e)}"
            }
    
    def _navigate_browser(self, url: str) -> Dict[str, Any]:
        """Navigate browser to URL"""
        import webbrowser
        
        try:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            
            webbrowser.open(url)
            return {
                "success": True,
                "message": f"Navigating to {url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to navigate: {str(e)}"
            }
    
    def _search_web(self, query: str) -> Dict[str, Any]:
        """Search web"""
        import webbrowser
        import urllib.parse
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(url)
            return {
                "success": True,
                "message": f"Searching for: {query}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to search: {str(e)}"
            }
    
    def _capture_screen(self) -> Dict[str, Any]:
        """Capture screenshot"""
        if not self.vision_processor:
            return {"success": False, "message": "Vision not available"}
        
        image = self.vision_processor.capture_screen()
        
        if image:
            return {
                "success": True,
                "message": f"Screenshot captured: {image.width}x{image.height}",
                "image_size": (image.width, image.height)
            }
        else:
            return {
                "success": False,
                "message": "Failed to capture screenshot"
            }
    
    def _analyze_screen(self, prompt: str) -> Dict[str, Any]:
        """Analyze screen with vision"""
        if not self.vision_processor:
            return {"success": False, "message": "Vision not available"}
        
        result = self.vision_processor.analyze_image(prompt=prompt)
        
        return {
            "success": True,
            "message": "Screen analyzed",
            "analysis": result
        }
    
    def _execute_task(self, task_description: str) -> Dict[str, Any]:
        """Execute task using agent fleet"""
        if not self.agent_fleet:
            return {"success": False, "message": "Agent fleet not available"}
        
        # Delegate to agent fleet
        try:
            result = self.agent_fleet.execute_task(task_description)
            return {
                "success": True,
                "message": "Task executed",
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Task execution failed: {str(e)}"
            }
    
    async def run(self):
        """Main run loop"""
        if not self.voice_processor:
            print("⚠ Cannot run without voice processor")
            return
        
        print("\n" + "="*70)
        print("🎤 Dive AI V25.3 - Multimodal Voice Assistant")
        print("="*70)
        print(f"\nSay '{self.config.wake_word}' to activate")
        print("Press Ctrl+C to stop\n")
        
        # Run voice processor
        await self.voice_processor.run()


# Example usage
if __name__ == "__main__":
    # Create orchestrator
    config = MultimodalConfig(
        voice_enabled=True,
        vision_enabled=True,
        wake_word="hey dive",
        enable_continuous_mode=True
    )
    
    orchestrator = MultimodalOrchestrator(config=config)
    
    # Run
    asyncio.run(orchestrator.run())
