"""
UI-TARS Integration - Natural language desktop automation

Uses Claude models to understand instructions and
generate pyautogui actions.
"""

import io
import base64
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    import pyautogui
    from PIL import ImageGrab
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

from ..llm.connections import get_manager, CLAUDE_OPUS_46_THINKING


@dataclass
class UIAction:
    """Single UI action"""
    action: str  # click, type, keypress, wait
    params: Dict[str, Any]
    description: str


@dataclass
class ExecutionResult:
    """Result of UI-TARS execution"""
    success: bool
    actions: List[UIAction]
    screenshots: List[str]  # Base64 before/after
    error: Optional[str] = None
    duration_ms: float = 0


class UITarsEngine:
    """
    UI-TARS-like engine using Claude for understanding
    
    Flow:
    1. Capture screenshot
    2. Send to Claude with instruction
    3. Parse actions from response
    4. Execute actions
    5. Capture result screenshot
    """
    
    SYSTEM_PROMPT = """You are a UI automation assistant. Given a screenshot and instruction,
output a JSON array of actions to perform.

Each action should be:
{"action": "click", "x": 100, "y": 200, "description": "Click on button"}
{"action": "type", "text": "hello", "description": "Type text"}
{"action": "keypress", "key": "enter", "description": "Press enter"}
{"action": "wait", "seconds": 1, "description": "Wait 1 second"}

Only output the JSON array, no explanation."""
    
    def __init__(self):
        self.manager = get_manager()
        self.last_screenshot: Optional[bytes] = None
    
    def capture_screen(self) -> str:
        """Capture and return base64 screenshot"""
        if not AVAILABLE:
            return ""
        
        img = ImageGrab.grab()
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        self.last_screenshot = buffer.getvalue()
        return base64.b64encode(self.last_screenshot).decode()
    
    def execute(self, instruction: str) -> ExecutionResult:
        """Execute natural language instruction"""
        start_time = time.time()
        actions = []
        screenshots = []
        
        if not AVAILABLE:
            return ExecutionResult(
                success=False,
                actions=[],
                screenshots=[],
                error="pyautogui not available"
            )
        
        try:
            # 1. Capture before screenshot
            before = self.capture_screen()
            screenshots.append(before)
            
            # 2. Ask Claude to analyze and generate actions
            prompt = f"""Instruction: {instruction}

[Screenshot is attached - analyze it and generate actions]

Generate actions as JSON array."""
            
            response = self.manager.chat(
                prompt,
                system=self.SYSTEM_PROMPT
            )
            
            if not response.success:
                return ExecutionResult(
                    success=False,
                    actions=[],
                    screenshots=screenshots,
                    error=response.error
                )
            
            # 3. Parse actions (simplified - in production use proper JSON parsing)
            parsed_actions = self._parse_actions(response.content)
            
            # 4. Execute actions
            for action_data in parsed_actions:
                action = UIAction(
                    action=action_data.get("action", ""),
                    params=action_data,
                    description=action_data.get("description", "")
                )
                actions.append(action)
                self._execute_action(action)
            
            # 5. Capture after screenshot
            time.sleep(0.5)  # Wait for UI to update
            after = self.capture_screen()
            screenshots.append(after)
            
            duration = (time.time() - start_time) * 1000
            
            return ExecutionResult(
                success=True,
                actions=actions,
                screenshots=screenshots,
                duration_ms=duration
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                actions=actions,
                screenshots=screenshots,
                error=str(e)
            )
    
    def _parse_actions(self, content: str) -> List[Dict]:
        """Parse actions from Claude response"""
        import json
        
        # Try to extract JSON from response
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON array in content
            import re
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
        
        return []
    
    def _execute_action(self, action: UIAction):
        """Execute single action"""
        if action.action == "click":
            x = action.params.get("x", 0)
            y = action.params.get("y", 0)
            pyautogui.click(x, y)
        
        elif action.action == "type":
            text = action.params.get("text", "")
            pyautogui.write(text, interval=0.05)
        
        elif action.action == "keypress":
            key = action.params.get("key", "enter")
            pyautogui.press(key)
        
        elif action.action == "wait":
            seconds = action.params.get("seconds", 1)
            time.sleep(seconds)


# Singleton
_engine = None

def get_engine() -> UITarsEngine:
    """Get UI-TARS engine"""
    global _engine
    if _engine is None:
        _engine = UITarsEngine()
    return _engine


def execute_instruction(instruction: str) -> ExecutionResult:
    """Quick execute helper"""
    return get_engine().execute(instruction)
