"""
Dive AI - Action Executor
Parses AI response for action XML tags and executes them.
This is the bridge between the LLM's intentions and real system actions.
"""

import re
import os
import subprocess
import traceback
import time
from typing import Dict, Any, List, Optional
from pathlib import Path


class ActionResult:
    """Result of executing an action."""
    def __init__(self, action: str, success: bool, output: str = "", error: str = ""):
        self.action = action
        self.success = success
        self.output = output
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "success": self.success,
            "output": self.output[:2000],  # Truncate large outputs
            "error": self.error
        }


class ActionExecutor:
    """
    Parses LLM response text for action XML tags and executes them.
    
    Supported actions:
    - <execute_command>command</execute_command>
    - <read_file>path</read_file>
    - <write_file path="path">content</write_file>
    - <screenshot/>
    - <click x="100" y="200" button="left"/>
    - <type_text>text to type</type_text>
    - <hotkey>ctrl+c</hotkey>
    - <scroll amount="3"/>
    - <open_app>chrome</open_app>
    - <self_debug target="file.py" issue="description"/>
    """
    
    # Regex patterns for action tags
    PATTERNS = {
        "execute_command": re.compile(
            r'<execute_command>(.*?)</execute_command>', re.DOTALL
        ),
        "read_file": re.compile(
            r'<read_file>(.*?)</read_file>', re.DOTALL
        ),
        "write_file": re.compile(
            r'<write_file\s+path=["\']([^"\']+)["\']>(.*?)</write_file>', re.DOTALL
        ),
        "screenshot": re.compile(
            r'<screenshot\s*/>', re.DOTALL
        ),
        "click": re.compile(
            r'<click\s+x=["\'](\d+)["\']\s+y=["\'](\d+)["\']\s*(?:button=["\'](\w+)["\'])?\s*/>', re.DOTALL
        ),
        "type_text": re.compile(
            r'<type_text>(.*?)</type_text>', re.DOTALL
        ),
        "hotkey": re.compile(
            r'<hotkey>(.*?)</hotkey>', re.DOTALL
        ),
        "scroll": re.compile(
            r'<scroll\s+amount=["\'](-?\d+)["\']\s*/>', re.DOTALL
        ),
        "open_app": re.compile(
            r'<open_app>(.*?)</open_app>', re.DOTALL
        ),
        "self_debug": re.compile(
            r'<self_debug\s+target=["\']([^"\']+)["\']\s+issue=["\']([^"\']+)["\']\s*/>', re.DOTALL
        ),
        "move_to": re.compile(
            r'<move_to\s+x=["\'](\d+)["\']\s+y=["\'](\d+)["\']\s*/>', re.DOTALL
        ),
    }
    
    def __init__(self, pc_operator=None, app_path: str = "", llm_chat_fn=None):
        self.pc_operator = pc_operator
        self.app_path = app_path
        self.llm_chat_fn = llm_chat_fn  # For self-debug LLM calls
        self._execution_log: List[Dict] = []
        
        # Detect venv paths for smart command rewriting
        self._venv_python = self._find_venv_python()
        self._venv_pip = self._find_venv_pip()
    
    def _find_venv_python(self) -> str:
        """Find the venv python executable."""
        candidates = [
            "D:/Antigravity/Dive AI/.venv/Scripts/python.exe",
            os.path.join(self.app_path, "..", ".venv", "Scripts", "python.exe"),
            os.path.join(self.app_path, ".venv", "Scripts", "python.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return "python"
    
    def _find_venv_pip(self) -> str:
        """Find the venv pip executable."""
        candidates = [
            "D:/Antigravity/Dive AI/.venv/Scripts/pip.exe",
            os.path.join(self.app_path, "..", ".venv", "Scripts", "pip.exe"),
            os.path.join(self.app_path, ".venv", "Scripts", "pip.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return "pip"
    
    def _rewrite_command(self, command: str) -> str:
        """Rewrite commands to use venv paths when appropriate."""
        cmd_lower = command.strip().lower()
        
        # pip install → use venv pip
        if cmd_lower.startswith("pip "):
            return f'"{self._venv_pip}" {command[4:]}'
        
        # python → use venv python
        if cmd_lower.startswith("python "):
            return f'"{self._venv_python}" {command[7:]}'
        
        return command
    
    def has_actions(self, text: str) -> bool:
        """Check if text contains any action tags."""
        for pattern in self.PATTERNS.values():
            if pattern.search(text):
                return True
        return False
    
    def parse_and_execute(self, text: str, automation_allowed: bool = False) -> List[ActionResult]:
        """
        Parse all action tags from text and execute them in order.
        Returns list of ActionResults.
        """
        results = []
        
        # Process each action type
        for action_type, pattern in self.PATTERNS.items():
            matches = pattern.finditer(text)
            for match in matches:
                try:
                    result = self._execute_action(action_type, match, automation_allowed)
                    results.append(result)
                    self._execution_log.append(result.to_dict())
                except Exception as e:
                    results.append(ActionResult(
                        action=action_type,
                        success=False,
                        error=f"Execution error: {str(e)}\n{traceback.format_exc()}"
                    ))
        
        return results
    
    def _execute_action(self, action_type: str, match, automation_allowed: bool) -> ActionResult:
        """Execute a single action based on its type."""
        
        if action_type == "execute_command":
            return self._exec_command(match.group(1).strip())
        
        elif action_type == "read_file":
            return self._exec_read_file(match.group(1).strip())
        
        elif action_type == "write_file":
            path = match.group(1).strip()
            content = match.group(2)
            return self._exec_write_file(path, content)
        
        elif action_type == "screenshot":
            return self._exec_screenshot()
        
        elif action_type == "click":
            if not automation_allowed:
                return ActionResult("click", False, error="PC control disabled. Press F3 to enable.")
            x = int(match.group(1))
            y = int(match.group(2))
            button = match.group(3) or "left"
            return self._exec_click(x, y, button)
        
        elif action_type == "type_text":
            if not automation_allowed:
                return ActionResult("type_text", False, error="PC control disabled. Press F3 to enable.")
            return self._exec_type_text(match.group(1))
        
        elif action_type == "hotkey":
            if not automation_allowed:
                return ActionResult("hotkey", False, error="PC control disabled. Press F3 to enable.")
            return self._exec_hotkey(match.group(1).strip())
        
        elif action_type == "scroll":
            if not automation_allowed:
                return ActionResult("scroll", False, error="PC control disabled. Press F3 to enable.")
            amount = int(match.group(1))
            return self._exec_scroll(amount)
        
        elif action_type == "open_app":
            if not automation_allowed:
                return ActionResult("open_app", False, error="PC control disabled. Press F3 to enable.")
            return self._exec_open_app(match.group(1).strip())
        
        elif action_type == "move_to":
            if not automation_allowed:
                return ActionResult("move_to", False, error="PC control disabled. Press F3 to enable.")
            x = int(match.group(1))
            y = int(match.group(2))
            return self._exec_move_to(x, y)
        
        elif action_type == "self_debug":
            target = match.group(1).strip()
            issue = match.group(2).strip()
            return self._exec_self_debug(target, issue)
        
        return ActionResult(action_type, False, error=f"Unknown action: {action_type}")
    
    # ── Individual Action Executors ──────────────────────────
    
    def _exec_command(self, command: str) -> ActionResult:
        """Execute a terminal command with smart venv path rewriting."""
        try:
            # Security: block dangerous commands
            dangerous = ["rm -rf /", "format c:", "del /f /s /q c:\\"]
            if any(d in command.lower() for d in dangerous):
                return ActionResult("execute_command", False, error="Blocked: dangerous command")
            
            # Smart rewrite: pip/python → use venv paths
            original_cmd = command
            command = self._rewrite_command(command)
            rewritten = command != original_cmd
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.app_path or None,
                capture_output=True,
                text=True,
                timeout=60  # Increased for pip install
            )
            
            output = result.stdout
            if rewritten:
                output = f"[Auto-rewritten: {command}]\n{output}"
            if result.stderr:
                output += f"\n[STDERR]: {result.stderr}"
            
            return ActionResult(
                "execute_command",
                result.returncode == 0,
                output=output,
                error=result.stderr if result.returncode != 0 else ""
            )
        except subprocess.TimeoutExpired:
            return ActionResult("execute_command", False, error="Command timed out (60s)")
        except Exception as e:
            return ActionResult("execute_command", False, error=str(e))
    
    def _exec_read_file(self, path: str) -> ActionResult:
        """Read file contents."""
        try:
            # Resolve relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.app_path, path)
            
            if not os.path.exists(path):
                return ActionResult("read_file", False, error=f"File not found: {path}")
            
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return ActionResult("read_file", True, output=content[:5000])
        except Exception as e:
            return ActionResult("read_file", False, error=str(e))
    
    def _exec_write_file(self, path: str, content: str) -> ActionResult:
        """Write content to file with backup."""
        try:
            if not os.path.isabs(path):
                path = os.path.join(self.app_path, path)
            
            # Create backup if file exists
            if os.path.exists(path):
                backup = path + ".backup"
                with open(path, 'r', encoding='utf-8') as f:
                    orig = f.read()
                with open(backup, 'w', encoding='utf-8') as f:
                    f.write(orig)
            
            # Create directories if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ActionResult("write_file", True, output=f"Written {len(content)} bytes to {path}")
        except Exception as e:
            return ActionResult("write_file", False, error=str(e))
    
    def _exec_screenshot(self) -> ActionResult:
        """Take a screenshot."""
        if self.pc_operator:
            result = self.pc_operator.screenshot()
            if result["success"]:
                return ActionResult("screenshot", True, output=f"Screenshot captured: {result['width']}x{result['height']}")
            return ActionResult("screenshot", False, error=result.get("error", ""))
        return ActionResult("screenshot", False, error="PC operator not available")
    
    def _exec_click(self, x: int, y: int, button: str = "left") -> ActionResult:
        """Click at screen position."""
        if self.pc_operator:
            result = self.pc_operator.click(x, y, button)
            if result["success"]:
                return ActionResult("click", True, output=f"Clicked at ({x}, {y}) [{button}]")
            return ActionResult("click", False, error=result.get("error", ""))
        return ActionResult("click", False, error="PC operator not available")
    
    def _exec_type_text(self, text: str) -> ActionResult:
        """Type text."""
        if self.pc_operator:
            result = self.pc_operator.type_text(text)
            if result["success"]:
                return ActionResult("type_text", True, output=f"Typed {len(text)} characters")
            return ActionResult("type_text", False, error=result.get("error", ""))
        return ActionResult("type_text", False, error="PC operator not available")
    
    def _exec_hotkey(self, keys_str: str) -> ActionResult:
        """Execute keyboard shortcut (e.g. 'ctrl+c')."""
        if self.pc_operator:
            keys = [k.strip() for k in keys_str.split('+')]
            result = self.pc_operator.hotkey(*keys)
            if result["success"]:
                return ActionResult("hotkey", True, output=f"Pressed: {keys_str}")
            return ActionResult("hotkey", False, error=result.get("error", ""))
        return ActionResult("hotkey", False, error="PC operator not available")
    
    def _exec_scroll(self, amount: int) -> ActionResult:
        """Scroll screen."""
        if self.pc_operator:
            result = self.pc_operator.scroll(amount)
            if result["success"]:
                direction = "up" if amount > 0 else "down"
                return ActionResult("scroll", True, output=f"Scrolled {direction} by {abs(amount)}")
            return ActionResult("scroll", False, error=result.get("error", ""))
        return ActionResult("scroll", False, error="PC operator not available")
    
    def _exec_open_app(self, app_name: str) -> ActionResult:
        """Open application."""
        if self.pc_operator:
            result = self.pc_operator.open_application(app_name)
            if result["success"]:
                return ActionResult("open_app", True, output=f"Opened: {app_name}")
            return ActionResult("open_app", False, error=result.get("error", ""))
        return ActionResult("open_app", False, error="PC operator not available")
    
    def _exec_move_to(self, x: int, y: int) -> ActionResult:
        """Move cursor."""
        if self.pc_operator:
            result = self.pc_operator.move_to(x, y)
            if result["success"]:
                return ActionResult("move_to", True, output=f"Moved to ({x}, {y})")
            return ActionResult("move_to", False, error=result.get("error", ""))
        return ActionResult("move_to", False, error="PC operator not available")
    
    def _exec_self_debug(self, target: str, issue: str) -> ActionResult:
        """Self-debug: read own source, analyze with LLM, suggest fix."""
        try:
            if not os.path.isabs(target):
                target = os.path.join(self.app_path, target)
            
            if not os.path.exists(target):
                return ActionResult("self_debug", False, error=f"Target not found: {target}")
            
            with open(target, 'r', encoding='utf-8') as f:
                code = f.read()
            
            analysis = f"[Self-Debug] Read {target} ({len(code)} bytes)\nIssue: {issue}\n"
            analysis += f"File contents:\n```\n{code[:3000]}\n```\n"
            analysis += "\nAnalysis: File loaded for debugging. Use LLM to analyze and fix."
            
            return ActionResult("self_debug", True, output=analysis)
        except Exception as e:
            return ActionResult("self_debug", False, error=str(e))
    
    def get_execution_log(self) -> List[Dict]:
        """Get history of all executed actions."""
        return self._execution_log[-50:]
    
    def clear_log(self):
        self._execution_log = []
    
    def format_results_for_display(self, results: List[ActionResult]) -> str:
        """Format action results for display in chat."""
        if not results:
            return ""
        
        output_parts = ["\n\n---\n**🔧 Actions Executed:**\n"]
        
        for r in results:
            icon = "✅" if r.success else "❌"
            output_parts.append(f"\n{icon} **{r.action}**")
            
            if r.output:
                # Truncate long outputs
                display = r.output[:500]
                if len(r.output) > 500:
                    display += f"\n... ({len(r.output) - 500} more characters)"
                output_parts.append(f"\n```\n{display}\n```")
            
            if r.error:
                output_parts.append(f"\n⚠️ {r.error}")
        
        return "\n".join(output_parts)
