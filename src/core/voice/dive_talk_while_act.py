#!/usr/bin/env python3
"""
Dive AI V25 - Talk-While-Act Module
Real-time narration of UI-TARS actions as they execute
"""

import time
import threading
import queue
from typing import Optional, Dict, Any, Callable
from enum import Enum


class ActionStatus(Enum):
    """Action execution status"""
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TalkWhileActNarrator:
    """
    Narrates UI-TARS actions in real-time as they execute
    Provides continuous voice feedback during automation
    """
    
    def __init__(
        self,
        tts_controller,
        narration_style: str = "detailed",  # detailed, concise, minimal
        narrate_progress: bool = True
    ):
        self.tts = tts_controller
        self.narration_style = narration_style
        self.narrate_progress = narrate_progress
        
        # Event queue for narration
        self.event_queue = queue.Queue()
        
        # Narration thread
        self.is_running = False
        self.narration_thread = None
        
        # Action templates
        self.action_templates = self._load_action_templates()
        
        print(f"✓ Talk-While-Act Narrator initialized (style: {narration_style})")
    
    def _load_action_templates(self) -> Dict[str, Dict[str, str]]:
        """Load narration templates for different actions"""
        return {
            "open_app": {
                "starting": "Opening {app_name}",
                "in_progress": "Launching {app_name}",
                "completed": "{app_name} is now open",
                "failed": "Failed to open {app_name}"
            },
            "close_app": {
                "starting": "Closing {app_name}",
                "completed": "{app_name} closed",
                "failed": "Could not close {app_name}"
            },
            "navigate": {
                "starting": "Navigating to {url}",
                "in_progress": "Loading {url}",
                "completed": "Page loaded successfully",
                "failed": "Failed to navigate to {url}"
            },
            "click": {
                "starting": "Clicking on {element}",
                "completed": "Clicked {element}",
                "failed": "Could not click {element}"
            },
            "type": {
                "starting": "Typing text",
                "in_progress": "Entering: {text}",
                "completed": "Text entered",
                "failed": "Failed to type text"
            },
            "search": {
                "starting": "Searching for {query}",
                "in_progress": "Looking up {query}",
                "completed": "Search results found",
                "failed": "Search failed"
            },
            "screenshot": {
                "starting": "Taking screenshot",
                "completed": "Screenshot captured",
                "failed": "Screenshot failed"
            },
            "scroll": {
                "starting": "Scrolling {direction}",
                "completed": "Scrolled {direction}",
                "failed": "Could not scroll"
            },
            "wait": {
                "starting": "Waiting {seconds} seconds",
                "in_progress": "Still waiting",
                "completed": "Wait complete"
            }
        }
    
    def start(self):
        """Start narration thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.narration_thread = threading.Thread(target=self._narration_loop, daemon=True)
        self.narration_thread.start()
        
        print("🗣️ Talk-While-Act narration started")
    
    def stop(self):
        """Stop narration"""
        self.is_running = False
        if self.narration_thread:
            self.narration_thread.join(timeout=1)
        print("🛑 Talk-While-Act narration stopped")
    
    def narrate_action(
        self,
        action_type: str,
        status: ActionStatus,
        params: Optional[Dict[str, Any]] = None,
        progress: Optional[float] = None
    ):
        """
        Queue an action for narration
        
        Args:
            action_type: Type of action (open_app, click, etc.)
            status: Current status of action
            params: Action parameters for template filling
            progress: Optional progress percentage (0-100)
        """
        event = {
            "action_type": action_type,
            "status": status,
            "params": params or {},
            "progress": progress,
            "timestamp": time.time()
        }
        
        self.event_queue.put(event)
    
    def _narration_loop(self):
        """Main narration loop"""
        while self.is_running:
            try:
                event = self.event_queue.get(timeout=0.1)
                self._narrate_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ Narration error: {e}")
    
    def _narrate_event(self, event: Dict[str, Any]):
        """Narrate a single event"""
        action_type = event["action_type"]
        status = event["status"]
        params = event["params"]
        progress = event.get("progress")
        
        # Get narration text
        text = self._generate_narration(action_type, status, params, progress)
        
        if text:
            # Speak narration
            self.tts.speak(text, priority=False)
            print(f"🗣️ Narrating: {text}")
    
    def _generate_narration(
        self,
        action_type: str,
        status: ActionStatus,
        params: Dict[str, Any],
        progress: Optional[float]
    ) -> Optional[str]:
        """Generate narration text from template"""
        
        # Get template
        templates = self.action_templates.get(action_type, {})
        template = templates.get(status.value)
        
        if not template:
            return None
        
        # Apply narration style
        if self.narration_style == "minimal" and status != ActionStatus.COMPLETED:
            return None  # Only narrate completion in minimal mode
        
        # Fill template with params
        try:
            text = template.format(**params)
        except KeyError:
            text = template
        
        # Add progress if available
        if progress is not None and self.narrate_progress:
            text += f" ({int(progress)}% complete)"
        
        # Adjust for concise style
        if self.narration_style == "concise":
            text = self._make_concise(text)
        
        return text
    
    def _make_concise(self, text: str) -> str:
        """Make narration more concise"""
        # Remove filler words
        text = text.replace("is now", "")
        text = text.replace("successfully", "")
        text = text.replace("complete", "done")
        return text.strip()


class UITARSEventNarrator:
    """
    Listens to UI-TARS event stream and narrates actions
    Integrates with UI-TARS event system
    """
    
    def __init__(
        self,
        narrator: TalkWhileActNarrator,
        uitars_client
    ):
        self.narrator = narrator
        self.uitars_client = uitars_client
        
        # Current action tracking
        self.current_action = None
        self.action_start_time = None
        
        print("✓ UI-TARS Event Narrator initialized")
    
    def execute_with_narration(self, command: str):
        """
        Execute UI-TARS command with real-time narration
        
        Args:
            command: Natural language command
        """
        print(f"🎯 Executing with narration: {command}")
        
        # Start narration
        self.narrator.start()
        
        try:
            # Execute command and narrate each step
            for result in self.uitars_client.execute_command(command, stream_feedback=True):
                self._process_result(result)
        
        except Exception as e:
            print(f"⚠ Execution error: {e}")
            self.narrator.narrate_action(
                "error",
                ActionStatus.FAILED,
                {"error": str(e)}
            )
        
        finally:
            # Wait for narration to complete
            time.sleep(0.5)
    
    def _process_result(self, result: Dict[str, Any]):
        """Process UI-TARS result and narrate"""
        action = result.get("action", {})
        status = result.get("status", "unknown")
        progress = result.get("progress", "")
        
        action_type = action.get("type", "unknown")
        params = action.get("params", {})
        
        # Calculate progress percentage
        progress_pct = None
        if progress:
            try:
                current, total = progress.split("/")
                progress_pct = (int(current) / int(total)) * 100
            except:
                pass
        
        # Map status to ActionStatus
        if status == "success":
            action_status = ActionStatus.COMPLETED
        elif status == "error":
            action_status = ActionStatus.FAILED
        else:
            action_status = ActionStatus.IN_PROGRESS
        
        # Narrate action
        self.narrator.narrate_action(
            action_type,
            action_status,
            params,
            progress_pct
        )


class ProgressiveNarrator(TalkWhileActNarrator):
    """
    Enhanced narrator with progressive updates for long-running actions
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_update_interval = 5.0  # seconds
        self.long_running_actions = {}
    
    def start_long_action(self, action_id: str, action_type: str, params: Dict[str, Any]):
        """Start tracking a long-running action"""
        self.long_running_actions[action_id] = {
            "action_type": action_type,
            "params": params,
            "start_time": time.time(),
            "last_update": time.time()
        }
        
        # Initial narration
        self.narrate_action(action_type, ActionStatus.STARTING, params)
        
        # Start progress thread
        threading.Thread(
            target=self._progress_updater,
            args=(action_id,),
            daemon=True
        ).start()
    
    def end_long_action(self, action_id: str, success: bool = True):
        """End tracking of a long-running action"""
        if action_id not in self.long_running_actions:
            return
        
        action_data = self.long_running_actions.pop(action_id)
        status = ActionStatus.COMPLETED if success else ActionStatus.FAILED
        
        # Final narration
        self.narrate_action(
            action_data["action_type"],
            status,
            action_data["params"]
        )
    
    def _progress_updater(self, action_id: str):
        """Provide periodic progress updates"""
        while action_id in self.long_running_actions:
            time.sleep(self.progress_update_interval)
            
            if action_id not in self.long_running_actions:
                break
            
            action_data = self.long_running_actions[action_id]
            elapsed = time.time() - action_data["start_time"]
            
            # Narrate progress
            self.narrate_action(
                action_data["action_type"],
                ActionStatus.IN_PROGRESS,
                {**action_data["params"], "elapsed": f"{int(elapsed)}s"}
            )


# Example usage
if __name__ == "__main__":
    # Mock TTS
    class MockTTS:
        def speak(self, text, priority=False):
            print(f"🔊 TTS: {text}")
    
    # Mock UI-TARS client
    class MockUITARS:
        def execute_command(self, command, stream_feedback=True):
            # Simulate multi-step execution
            steps = [
                {"action": {"type": "open_app", "params": {"app_name": "Chrome"}}, "status": "success", "progress": "1/3"},
                {"action": {"type": "navigate", "params": {"url": "github.com"}}, "status": "success", "progress": "2/3"},
                {"action": {"type": "search", "params": {"query": "UI-TARS"}}, "status": "success", "progress": "3/3"}
            ]
            
            for step in steps:
                time.sleep(1)
                yield step
    
    # Test narrator
    tts = MockTTS()
    narrator = TalkWhileActNarrator(tts, narration_style="detailed")
    
    uitars = MockUITARS()
    event_narrator = UITARSEventNarrator(narrator, uitars)
    
    print("\n🎬 Testing Talk-While-Act narration...\n")
    event_narrator.execute_with_narration("open Chrome and search for UI-TARS")
    
    print("\n✅ Test complete")
