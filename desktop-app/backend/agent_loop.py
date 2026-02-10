"""
Dive AI - Agent Loop
Autonomous screenshot→think→act→verify cycle inspired by UI-TARS GUIAgent.
Runs tasks autonomously by observing the screen, deciding actions, and executing them.
"""

import asyncio
import time
import traceback
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStep:
    """One step of the agent loop."""
    def __init__(self, step_num: int):
        self.step_num = step_num
        self.screenshot_b64: Optional[str] = None
        self.thinking: str = ""
        self.actions_text: str = ""
        self.action_results: List[Dict] = []
        self.timestamp: float = time.time()
        self.duration_ms: float = 0
    
    def to_dict(self) -> Dict:
        return {
            "step": self.step_num,
            "thinking": self.thinking[:500],
            "actions": self.actions_text[:500],
            "results": self.action_results[:5],
            "has_screenshot": self.screenshot_b64 is not None,
            "duration_ms": round(self.duration_ms, 2),
            "timestamp": self.timestamp
        }


class AgentLoop:
    """
    Autonomous agent loop that can complete tasks by controlling the PC.
    
    Cycle:
    1. screenshot() — capture current screen state
    2. think() — send screenshot + instruction + history to LLM
    3. parse() — extract actions from LLM response
    4. execute() — run actions via pc_operator/action_executor
    5. verify() — check if task is progressing or complete
    """
    
    def __init__(self, pc_operator, action_executor, llm_chat_fn):
        self.pc_operator = pc_operator
        self.action_executor = action_executor
        self.llm_chat_fn = llm_chat_fn  # async fn(message, system) -> dict
        
        self.status = AgentStatus.IDLE
        self.current_task: str = ""
        self.steps: List[AgentStep] = []
        self.max_steps: int = 20
        self.callbacks: List[Callable] = []  # Progress callbacks
        self._stop_flag = False
        self._pause_flag = False
    
    async def run(self, instruction: str, max_steps: int = 20) -> Dict[str, Any]:
        """
        Run the autonomous agent loop.
        Returns final status and step history.
        """
        self.current_task = instruction
        self.max_steps = max_steps
        self.steps = []
        self.status = AgentStatus.RUNNING
        self._stop_flag = False
        self._pause_flag = False
        
        try:
            # Check PC control permission
            if not self.pc_operator.allowed:
                return {
                    "success": False,
                    "error": "PC control is disabled. Press F3 to enable before running agent.",
                    "status": "failed"
                }
            
            for step_num in range(1, max_steps + 1):
                if self._stop_flag:
                    self.status = AgentStatus.STOPPED
                    break
                
                # Handle pause
                while self._pause_flag:
                    await asyncio.sleep(0.5)
                    if self._stop_flag:
                        self.status = AgentStatus.STOPPED
                        break
                
                if self.status == AgentStatus.STOPPED:
                    break
                
                step = AgentStep(step_num)
                start = time.time()
                
                # 1. Screenshot
                ss_result = self.pc_operator.screenshot()
                if ss_result["success"]:
                    step.screenshot_b64 = ss_result["screenshot"]
                
                # 2. Think — ask LLM what to do
                history_summary = self._build_history_summary()
                
                think_prompt = f"""You are controlling a Windows PC to complete a task.

TASK: {instruction}

CURRENT STEP: {step_num} of {max_steps}

PREVIOUS ACTIONS:
{history_summary}

Based on the current screen state, decide what action to take next.
If the task is COMPLETE, respond with: <task_complete/>
If you need to perform an action, use these tags:

<click x="100" y="200"/>
<type_text>text</type_text>
<hotkey>ctrl+v</hotkey>
<scroll amount="-3"/>
<open_app>chrome</open_app>
<execute_command>dir</execute_command>

Explain your reasoning briefly, then perform ONE action."""

                think_system = "You are an autonomous PC agent. Observe the screen, think, act. Be precise with coordinates. ALWAYS respond in English."
                
                result = await self.llm_chat_fn(
                    message=think_prompt,
                    system=think_system
                )
                
                response_text = result.get("content", "")
                step.thinking = response_text
                
                # 3. Check if task complete
                if "<task_complete/>" in response_text or "<task_complete>" in response_text:
                    step.actions_text = "Task marked as complete by AI"
                    step.duration_ms = (time.time() - start) * 1000
                    self.steps.append(step)
                    self.status = AgentStatus.COMPLETED
                    self._notify(step)
                    break
                
                # 4. Parse and execute actions
                if self.action_executor.has_actions(response_text):
                    step.actions_text = response_text
                    action_results = self.action_executor.parse_and_execute(
                        response_text,
                        automation_allowed=self.pc_operator.allowed
                    )
                    step.action_results = [r.to_dict() for r in action_results]
                else:
                    step.actions_text = "No actions found in response"
                
                step.duration_ms = (time.time() - start) * 1000
                self.steps.append(step)
                self._notify(step)
                
                # Brief pause between steps
                await asyncio.sleep(0.5)
            
            if self.status == AgentStatus.RUNNING:
                self.status = AgentStatus.COMPLETED
            
            return {
                "success": self.status == AgentStatus.COMPLETED,
                "status": self.status.value,
                "task": instruction,
                "steps_taken": len(self.steps),
                "steps": [s.to_dict() for s in self.steps[-10:]],  # Last 10 steps
            }
        
        except Exception as e:
            self.status = AgentStatus.FAILED
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "steps_taken": len(self.steps)
            }
    
    def stop(self):
        """Emergency stop."""
        self._stop_flag = True
        self.status = AgentStatus.STOPPED
    
    def pause(self):
        """Pause agent loop."""
        self._pause_flag = True
        self.status = AgentStatus.PAUSED
    
    def resume(self):
        """Resume agent loop."""
        self._pause_flag = False
        self.status = AgentStatus.RUNNING
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        current_step = self.steps[-1].to_dict() if self.steps else None
        return {
            "status": self.status.value,
            "task": self.current_task,
            "steps_taken": len(self.steps),
            "max_steps": self.max_steps,
            "current_step": current_step
        }
    
    def _build_history_summary(self) -> str:
        """Build summary of recent steps for context."""
        if not self.steps:
            return "No previous actions. This is the first step."
        
        lines = []
        for step in self.steps[-5:]:  # Last 5 steps
            results_str = ""
            if step.action_results:
                results_str = " → " + ", ".join(
                    f"{r['action']}: {'✓' if r['success'] else '✗ ' + r.get('error', '')}"
                    for r in step.action_results
                )
            lines.append(f"Step {step.step_num}: {step.actions_text[:100]}{results_str}")
        
        return "\n".join(lines)
    
    def _notify(self, step: AgentStep):
        """Notify callbacks of step completion."""
        for cb in self.callbacks:
            try:
                cb(step.to_dict())
            except Exception:
                pass
    
    def on_step(self, callback: Callable):
        """Register step completion callback."""
        self.callbacks.append(callback)


# Global agent instance (created in gateway_server.py)
agent_loop: Optional[AgentLoop] = None
