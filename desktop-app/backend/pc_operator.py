"""
Dive AI - PC Operator
Desktop control module inspired by UI-TARS NutJSOperator.
Uses pyautogui for mouse/keyboard control.
"""

import io
import base64
import time
import subprocess
from typing import Optional, Tuple, Dict, Any

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.1
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class PCOperator:
    """Desktop control operator for Dive AI autonomous agent."""
    
    def __init__(self):
        self.allowed = False  # Must be explicitly enabled via F3
        self._last_screenshot: Optional[str] = None
        self._action_log: list = []
    
    def set_allowed(self, allowed: bool):
        self.allowed = allowed
    
    def _check_permission(self) -> Dict[str, Any]:
        """Check if PC control is allowed."""
        if not self.allowed:
            return {"success": False, "error": "PC control is DISABLED. Press F3 to enable."}
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not installed. Run: pip install pyautogui"}
        return {"success": True}
    
    def screenshot(self) -> Dict[str, Any]:
        """Capture screenshot and return as base64 PNG."""
        if not HAS_PYAUTOGUI or not HAS_PIL:
            return {"success": False, "error": "pyautogui/Pillow not installed"}
        try:
            img = pyautogui.screenshot()
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            b64 = base64.b64encode(buffer.getvalue()).decode()
            self._last_screenshot = b64
            return {
                "success": True,
                "screenshot": b64,
                "width": img.width,
                "height": img.height
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """Click at position."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            if button == "right":
                pyautogui.rightClick(x, y)
            elif button == "double":
                pyautogui.doubleClick(x, y)
            else:
                pyautogui.click(x, y)
            self._log("click", {"x": x, "y": y, "button": button})
            return {"success": True, "action": "click", "x": x, "y": y, "button": button}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def type_text(self, text: str, interval: float = 0.02) -> Dict[str, Any]:
        """Type text. Supports Unicode via clipboard fallback."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            # For ASCII, use typewrite; for Unicode, use clipboard
            if all(ord(c) < 128 for c in text):
                pyautogui.typewrite(text, interval=interval)
            else:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.1)
            self._log("type_text", {"text": text[:50]})
            return {"success": True, "action": "type_text", "length": len(text)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def hotkey(self, *keys: str) -> Dict[str, Any]:
        """Press keyboard shortcut."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            pyautogui.hotkey(*keys)
            self._log("hotkey", {"keys": list(keys)})
            return {"success": True, "action": "hotkey", "keys": list(keys)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def key_press(self, key: str) -> Dict[str, Any]:
        """Press a single key."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            pyautogui.press(key)
            self._log("key_press", {"key": key})
            return {"success": True, "action": "key_press", "key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scroll(self, amount: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Scroll up (positive) or down (negative)."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            if x is not None and y is not None:
                pyautogui.scroll(amount, x=x, y=y)
            else:
                pyautogui.scroll(amount)
            self._log("scroll", {"amount": amount})
            return {"success": True, "action": "scroll", "amount": amount}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def move_to(self, x: int, y: int, duration: float = 0.3) -> Dict[str, Any]:
        """Move cursor to position."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            pyautogui.moveTo(x, y, duration=duration)
            self._log("move_to", {"x": x, "y": y})
            return {"success": True, "action": "move_to", "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_screen_size(self) -> Dict[str, Any]:
        """Get screen resolution."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            w, h = pyautogui.size()
            return {"success": True, "width": w, "height": h}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_cursor_position(self) -> Dict[str, Any]:
        """Get current cursor position."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            x, y = pyautogui.position()
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application by name (Windows)."""
        check = self._check_permission()
        if not check["success"]:
            return check
        try:
            # Common app mappings for Windows
            app_map = {
                "chrome": "chrome",
                "google chrome": "chrome", 
                "firefox": "firefox",
                "notepad": "notepad",
                "calculator": "calc",
                "explorer": "explorer",
                "file explorer": "explorer",
                "cmd": "cmd",
                "terminal": "wt",
                "vscode": "code",
                "vs code": "code",
            }
            cmd = app_map.get(app_name.lower(), app_name)
            subprocess.Popen(cmd, shell=True)
            time.sleep(1)
            self._log("open_app", {"app": app_name, "cmd": cmd})
            return {"success": True, "action": "open_app", "app": app_name}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log(self, action: str, params: Dict):
        """Log action for history."""
        self._action_log.append({
            "action": action,
            "params": params,
            "timestamp": time.time()
        })
        # Keep last 100 actions
        if len(self._action_log) > 100:
            self._action_log = self._action_log[-100:]
    
    def get_action_log(self) -> list:
        return self._action_log
    
    def clear_log(self):
        self._action_log = []


# Global operator instance
pc_operator = PCOperator()
