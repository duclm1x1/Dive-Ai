"""
Input Control - Mouse and keyboard automation

Wraps pyautogui with safety features.
"""

import time
from typing import List, Tuple, Optional

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


class InputController:
    """Safe mouse and keyboard control"""
    
    def __init__(self, fail_safe: bool = True):
        if AVAILABLE:
            pyautogui.FAILSAFE = fail_safe
        self.action_log: List[dict] = []
    
    def _log(self, action: str, **kwargs):
        """Log action"""
        self.action_log.append({
            "action": action,
            "timestamp": time.time(),
            **kwargs
        })
    
    # Mouse actions
    
    def click(self, x: int, y: int, button: str = "left", clicks: int = 1):
        """Click at position"""
        if not AVAILABLE:
            return False
        pyautogui.click(x, y, button=button, clicks=clicks)
        self._log("click", x=x, y=y, button=button)
        return True
    
    def double_click(self, x: int, y: int):
        """Double click"""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: int, y: int):
        """Right click"""
        return self.click(x, y, button="right")
    
    def move(self, x: int, y: int, duration: float = 0.2):
        """Move mouse"""
        if not AVAILABLE:
            return False
        pyautogui.moveTo(x, y, duration=duration)
        self._log("move", x=x, y=y)
        return True
    
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5):
        """Drag from one point to another"""
        if not AVAILABLE:
            return False
        pyautogui.moveTo(x1, y1)
        pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
        self._log("drag", from_=(x1, y1), to=(x2, y2))
        return True
    
    def scroll(self, clicks: int, x: int = None, y: int = None):
        """Scroll wheel"""
        if not AVAILABLE:
            return False
        pyautogui.scroll(clicks, x=x, y=y)
        self._log("scroll", clicks=clicks)
        return True
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        if not AVAILABLE:
            return (0, 0)
        pos = pyautogui.position()
        return (pos.x, pos.y)
    
    # Keyboard actions
    
    def type_text(self, text: str, interval: float = 0.05):
        """Type text"""
        if not AVAILABLE:
            return False
        pyautogui.write(text, interval=interval)
        self._log("type", chars=len(text))
        return True
    
    def press(self, key: str):
        """Press single key"""
        if not AVAILABLE:
            return False
        pyautogui.press(key)
        self._log("press", key=key)
        return True
    
    def hotkey(self, *keys):
        """Press key combination"""
        if not AVAILABLE:
            return False
        pyautogui.hotkey(*keys)
        self._log("hotkey", keys=keys)
        return True
    
    def hold(self, key: str, duration: float = 0.5):
        """Hold key for duration"""
        if not AVAILABLE:
            return False
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        self._log("hold", key=key, duration=duration)
        return True
    
    # Utility
    
    def wait(self, seconds: float):
        """Wait between actions"""
        time.sleep(seconds)
        self._log("wait", seconds=seconds)
    
    def get_log(self) -> List[dict]:
        """Get action log"""
        return self.action_log.copy()
    
    def clear_log(self):
        """Clear action log"""
        self.action_log.clear()


# Singleton
_controller = None

def get_controller() -> InputController:
    """Get input controller"""
    global _controller
    if _controller is None:
        _controller = InputController()
    return _controller
