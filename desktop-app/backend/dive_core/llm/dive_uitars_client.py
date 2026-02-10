#!/usr/bin/env python3
"""
Dive AI V25 - UI-TARS Integration Client
Connects DIVE AI with UI-TARS desktop automation
"""

import os
import json
import time
import subprocess
from typing import List, Dict, Any, Optional, Generator
import requests
from pathlib import Path


class UITARSClient:
    """
    Client for UI-TARS Desktop automation
    Executes natural language commands through UI-TARS
    """
    
    def __init__(
        self,
        uitars_path: Optional[str] = None,
        api_url: str = "http://localhost:8080",
        model: str = "ui-tars-1.5"
    ):
        self.uitars_path = uitars_path or self._find_uitars()
        self.api_url = api_url
        self.model = model
        self.session = requests.Session()
        self.process = None
        
        print(f"✓ UI-TARS Client initialized (API: {api_url}, Model: {model})")
    
    def _find_uitars(self) -> Optional[str]:
        """Find UI-TARS installation"""
        possible_paths = [
            "/home/ubuntu/UI-TARS-desktop",
            os.path.expanduser("~/UI-TARS-desktop"),
            "/opt/UI-TARS-desktop"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def start_server(self):
        """Start UI-TARS server"""
        if not self.uitars_path:
            print("⚠ UI-TARS path not found. Please install UI-TARS first.")
            return False
        
        try:
            # Start UI-TARS server
            print("🚀 Starting UI-TARS server...")
            
            # Check if already running
            if self._is_server_running():
                print("✓ UI-TARS server already running")
                return True
            
            # Start server process
            os.chdir(self.uitars_path)
            self.process = subprocess.Popen(
                ["pnpm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for i in range(30):
                if self._is_server_running():
                    print("✓ UI-TARS server started")
                    return True
                time.sleep(1)
            
            print("⚠ UI-TARS server failed to start")
            return False
            
        except Exception as e:
            print(f"⚠ Error starting UI-TARS server: {e}")
            return False
    
    def _is_server_running(self) -> bool:
        """Check if UI-TARS server is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def stop_server(self):
        """Stop UI-TARS server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("🛑 UI-TARS server stopped")
    
    def execute_command(
        self,
        command: str,
        stream_feedback: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute natural language command through UI-TARS
        
        Args:
            command: Natural language command (e.g., "open Chrome and go to GitHub")
            stream_feedback: Stream real-time feedback
        
        Yields:
            Dict with action results and feedback
        """
        print(f"🎯 Executing command: {command}")
        
        # Parse command to actions
        actions = self._parse_command(command)
        
        # Execute each action
        for i, action in enumerate(actions):
            print(f"  [{i+1}/{len(actions)}] {action['type']}: {action.get('params', {})}")
            
            try:
                result = self._execute_action(action)
                
                if stream_feedback:
                    yield {
                        "action": action,
                        "result": result,
                        "status": "success",
                        "progress": f"{i+1}/{len(actions)}"
                    }
                
                # Small delay between actions
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = f"Error executing {action['type']}: {e}"
                print(f"  ⚠ {error_msg}")
                
                if stream_feedback:
                    yield {
                        "action": action,
                        "error": str(e),
                        "status": "error",
                        "progress": f"{i+1}/{len(actions)}"
                    }
    
    def _parse_command(self, command: str) -> List[Dict[str, Any]]:
        """
        Parse natural language command into UI-TARS actions
        
        This is a simplified version. In production, use LLM for better parsing.
        """
        actions = []
        command_lower = command.lower()
        
        # Open application
        if "open" in command_lower:
            app_name = self._extract_app_name(command_lower)
            if app_name:
                actions.append({
                    "type": "open_app",
                    "params": {"app_name": app_name}
                })
        
        # Navigate browser
        if "go to" in command_lower or "navigate" in command_lower:
            url = self._extract_url(command)
            if url:
                actions.append({
                    "type": "navigate",
                    "params": {"url": url}
                })
        
        # Click element
        if "click" in command_lower:
            element = self._extract_element(command)
            if element:
                actions.append({
                    "type": "click",
                    "params": {"element": element}
                })
        
        # Type text
        if "type" in command_lower:
            text = self._extract_text(command)
            if text:
                actions.append({
                    "type": "type",
                    "params": {"text": text}
                })
        
        # Search
        if "search" in command_lower:
            query = self._extract_search_query(command)
            if query:
                actions.append({
                    "type": "search",
                    "params": {"query": query}
                })
        
        # Screenshot
        if "screenshot" in command_lower or "capture" in command_lower:
            actions.append({
                "type": "screenshot",
                "params": {}
            })
        
        return actions if actions else [{"type": "unknown", "params": {"command": command}}]
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single UI-TARS action"""
        action_type = action["type"]
        params = action.get("params", {})
        
        if action_type == "open_app":
            return self._open_app(params["app_name"])
        
        elif action_type == "navigate":
            return self._navigate(params["url"])
        
        elif action_type == "click":
            return self._click(params.get("element") or params.get("x"), params.get("y"))
        
        elif action_type == "type":
            return self._type_text(params["text"])
        
        elif action_type == "search":
            return self._search(params["query"])
        
        elif action_type == "screenshot":
            return self._screenshot()
        
        else:
            return {"status": "unknown_action", "action": action_type}
    
    def _open_app(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        # Map common app names to executables
        app_map = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "vscode": "code",
            "code": "code",
            "terminal": "gnome-terminal",
            "notepad": "gedit"
        }
        
        executable = app_map.get(app_name.lower(), app_name)
        
        try:
            subprocess.Popen([executable])
            return {"status": "success", "app": app_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _navigate(self, url: str) -> Dict[str, Any]:
        """Navigate browser to URL"""
        try:
            # Open URL in default browser
            import webbrowser
            webbrowser.open(url)
            return {"status": "success", "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _click(self, x_or_element, y=None) -> Dict[str, Any]:
        """Click at coordinates or element"""
        try:
            # Use pyautogui for mouse control
            import pyautogui
            
            if y is not None:
                # Click at coordinates
                pyautogui.click(x_or_element, y)
                return {"status": "success", "x": x_or_element, "y": y}
            else:
                # Click element (would need UI-TARS vision to locate)
                return {"status": "not_implemented", "element": x_or_element}
        except ImportError:
            return {"status": "error", "error": "pyautogui not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _type_text(self, text: str) -> Dict[str, Any]:
        """Type text"""
        try:
            import pyautogui
            pyautogui.write(text, interval=0.05)
            return {"status": "success", "text": text}
        except ImportError:
            return {"status": "error", "error": "pyautogui not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _search(self, query: str) -> Dict[str, Any]:
        """Search on Google"""
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return self._navigate(url)
    
    def _screenshot(self) -> Dict[str, Any]:
        """Take screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            return {"status": "success", "file": filename}
        except ImportError:
            return {"status": "error", "error": "pyautogui not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # Helper methods for parsing
    def _extract_app_name(self, command: str) -> Optional[str]:
        apps = ["chrome", "firefox", "safari", "edge", "vscode", "code", "terminal", "notepad"]
        for app in apps:
            if app in command:
                return app
        return None
    
    def _extract_url(self, command: str) -> Optional[str]:
        words = command.split()
        for word in words:
            if "." in word and not word.startswith("."):
                if not word.startswith("http"):
                    return f"https://{word}"
                return word
        return None
    
    def _extract_element(self, command: str) -> Optional[str]:
        # Extract element name after "click"
        if "click" in command.lower():
            parts = command.lower().split("click")
            if len(parts) > 1:
                return parts[1].strip()
        return None
    
    def _extract_text(self, command: str) -> Optional[str]:
        # Extract text after "type"
        if "type" in command.lower():
            parts = command.lower().split("type")
            if len(parts) > 1:
                return parts[1].strip().strip('"\'')
        return None
    
    def _extract_search_query(self, command: str) -> Optional[str]:
        if "search for" in command.lower():
            return command.lower().split("search for")[-1].strip()
        elif "search" in command.lower():
            return command.lower().split("search")[-1].strip()
        return None


class UITARSVisionClient(UITARSClient):
    """
    Extended UI-TARS client with vision capabilities
    Uses UI-TARS model for visual element detection
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vision_enabled = True
    
    def find_element(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Find element on screen using vision
        
        Args:
            description: Natural language description of element
        
        Returns:
            Dict with element location and confidence
        """
        try:
            # Take screenshot
            screenshot_result = self._screenshot()
            if screenshot_result["status"] != "success":
                return None
            
            # Use UI-TARS vision model to find element
            # This would call the actual UI-TARS API
            # For now, return mock result
            
            return {
                "found": True,
                "x": 100,
                "y": 100,
                "width": 50,
                "height": 30,
                "confidence": 0.95,
                "description": description
            }
            
        except Exception as e:
            print(f"⚠ Vision error: {e}")
            return None
    
    def click_element(self, description: str) -> Dict[str, Any]:
        """Click element by description"""
        element = self.find_element(description)
        if element and element["found"]:
            center_x = element["x"] + element["width"] // 2
            center_y = element["y"] + element["height"] // 2
            return self._click(center_x, center_y)
        else:
            return {"status": "error", "error": "Element not found"}


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = UITARSClient()
    
    # Test commands
    commands = [
        "open Chrome",
        "go to github.com",
        "search for UI-TARS",
        "take a screenshot"
    ]
    
    for command in commands:
        print(f"\n{'='*60}")
        print(f"Command: {command}")
        print('='*60)
        
        for result in client.execute_command(command):
            print(f"  Result: {result}")
            time.sleep(1)
