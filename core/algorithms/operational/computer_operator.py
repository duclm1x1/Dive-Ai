"""
Computer Operator Algorithm  
Execute computer control actions (screenshot, mouse, keyboard, window)

Algorithm = CODE + STEPS
⭐ CRITICAL for UI-TARS integration
"""

import os
import sys
from typing import Dict, Any
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class ComputerOperatorAlgorithm(BaseAlgorithm):
    """
    Computer Operator - Desktop Automation
    
    ⭐ CRITICAL: Core algorithm for UI-TARS computer control
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ComputerOperator",
            name="Computer Operator",
            level="operational",
            category="computer-control",
            version="1.0",
            description="Execute computer control actions: screenshot, mouse move/click, keyboard type, window management.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "screenshot/mouse/keyboard/window"),
                    IOField("params", "object", True, "Action-specific parameters")
                ],
                outputs=[
                    IOField("success", "boolean", True, "Action succeeded"),
                    IOField("result", "object", False, "Action result"),
                    IOField("screenshot", "string", False, "Base64 screenshot if captured")
                ]
            ),
            
            steps=[
                "Step 1: Validate action and params",
                "Step 2: Execute action via appropriate library:",
                "  - screenshot: pyautogui.screenshot()",
                "  - mouse: pyautogui.move/click()",
                "  - keyboard: keyboard.type()",
                "  - window: win32gui functions",
                "Step 3: Capture result",
                "Step 4: Return success + result"
            ],
            
            tags=["computer-control", "automation", "ui-tars", "CRITICAL"]
        )
        
        # Initialize libraries
        self._init_libraries()
    
    def _init_libraries(self):
        """Initialize computer control libraries"""
        try:
            import pyautogui
            import keyboard
            import mouse
            import win32gui
            import win32con
            from PIL import Image
            import io
            
            self.pyautogui = pyautogui
            self.keyboard = keyboard
            self.mouse = mouse
            self.win32gui = win32gui
            self.win32con = win32con
            self.Image = Image
            self.io = io
            
            print("   ✅ Computer control libraries loaded")
            
        except ImportError as e:
            print(f"   ⚠️  Computer control libraries not available: {e}")
            print("      Run: pip install pyautogui keyboard mouse pillow pywin32")
            self.pyautogui = None
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute computer control action"""
        
        action = params.get("action", "")
        action_params = params.get("params", {})
        
        print(f"\n🖥️  Computer Operator: {action}")
        
        if not self.pyautogui:
            return AlgorithmResult(
                status="error",
                error="Computer control libraries not installed. Run: pip install pyautogui keyboard mouse pillow pywin32"
            )
        
        try:
            # Step 1: Validate
            if action not in ["screenshot", "mouse", "keyboard", "window"]:
                return AlgorithmResult(status="error", error=f"Unknown action: {action}")
            
            # Step 2: Execute based on action
            if action == "screenshot":
                return self._screenshot(action_params)
            elif action == "mouse":
                return self._mouse(action_params)
            elif action == "keyboard":
                return self._keyboard(action_params)
            elif action == "window":
                return self._window(action_params)
        
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Action failed: {str(e)}")
    
    def _screenshot(self, params: Dict) -> AlgorithmResult:
        """Capture screenshot"""
        
        screenshot = self.pyautogui.screenshot()
        
        # Convert to base64
        buffer = self.io.BytesIO()
        screenshot.save(buffer, format="PNG")
        screenshot_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        print(f"   📸 Screenshot captured ({len(screenshot_b64)} bytes)")
        
        return AlgorithmResult(
            status="success",
            data={
                "success": True,
                "screenshot": screenshot_b64,
                "size": screenshot.size
            }
        )
    
    def _mouse(self, params: Dict) -> AlgorithmResult:
        """Mouse control"""
        
        sub_action = params.get("sub_action", "move")  # move/click/drag
        x = params.get("x", 0)
        y = params.get("y", 0)
        
        if sub_action == "move":
            self.pyautogui.moveTo(x, y, duration=0.2)
            print(f"   🖱️  Moved to ({x}, {y})")
        elif sub_action == "click":
            self.pyautogui.click(x, y)
            print(f"   🖱️  Clicked at ({x}, {y})")
        elif sub_action == "drag":
            to_x = params.get("to_x", x)
            to_y = params.get("to_y", y)
            self.pyautogui.dragTo(to_x, to_y, duration=0.5)
            print(f"   🖱️  Dragged to ({to_x}, {to_y})")
        
        return AlgorithmResult(
            status="success",
            data={"success": True, "action": sub_action, "position": (x, y)}
        )
    
    def _keyboard(self, params: Dict) -> AlgorithmResult:
        """Keyboard control"""
        
        text = params.get("text", "")
        press_key = params.get("press", None)
        
        if text:
            self.keyboard.write(text)
            print(f"   ⌨️  Typed: '{text[:50]}...'")
        
        if press_key:
            self.keyboard.press_and_release(press_key)
            print(f"   ⌨️  Pressed: {press_key}")
        
        return AlgorithmResult(
            status="success",
            data={"success": True, "text": text, "key": press_key}
        )
    
    def _window(self, params: Dict) -> AlgorithmResult:
        """Window management"""
        
        sub_action = params.get("sub_action", "focus")  # focus/minimize/maximize
        window_title = params.get("title", "")
        
        # Find window by title
        def callback(hwnd, windows):
            if self.win32gui.IsWindowVisible(hwnd):
                title = self.win32gui.GetWindowText(hwnd)
                if window_title.lower() in title.lower():
                    windows.append(hwnd)
        
        windows = []
        self.win32gui.EnumWindows(callback, windows)
        
        if not windows:
            return AlgorithmResult(
                status="error",
                error=f"Window not found: {window_title}"
            )
        
        hwnd = windows[0]
        
        if sub_action == "focus":
            self.win32gui.SetForegroundWindow(hwnd)
            print(f"   🪟 Focused window: {window_title}")
        elif sub_action == "minimize":
            self.win32gui.ShowWindow(hwnd, self.win32con.SW_MINIMIZE)
            print(f"   🪟 Minimized: {window_title}")
        elif sub_action == "maximize":
            self.win32gui.ShowWindow(hwnd, self.win32con.SW_MAXIMIZE)
            print(f"   🪟 Maximized: {window_title}")
        
        return AlgorithmResult(
            status="success",
            data={"success": True, "action": sub_action, "window": window_title}
        )


def register(algorithm_manager):
    """Register Computer Operator Algorithm"""
    try:
        algo = ComputerOperatorAlgorithm()
        algorithm_manager.register("ComputerOperator", algo)
        print("✅ Computer Operator Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register ComputerOperator: {e}")
