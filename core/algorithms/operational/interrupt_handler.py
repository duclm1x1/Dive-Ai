"""
⏸️ INTERRUPT HANDLER
Handle interrupts and task switching gracefully

Based on V28's core_engine/interrupt_handler.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class InterruptPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Interrupt:
    """An interrupt request"""
    id: str
    source: str
    priority: InterruptPriority
    reason: str
    timestamp: float
    handled: bool = False


@dataclass
class TaskContext:
    """Context for a paused task"""
    task_id: str
    state: Dict
    progress: float
    paused_at: float


class InterruptHandlerAlgorithm(BaseAlgorithm):
    """
    ⏸️ Interrupt Handler
    
    Graceful interrupt handling:
    - Priority-based handling
    - Context preservation
    - Task resumption
    - Graceful degradation
    
    From V28: core_engine/interrupt_handler.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="InterruptHandler",
            name="Interrupt Handler",
            level="operational",
            category="control",
            version="1.0",
            description="Handle interrupts and task switching",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "interrupt/resume/status"),
                    IOField("interrupt", "object", False, "Interrupt details"),
                    IOField("task_id", "string", False, "Task to interrupt/resume")
                ],
                outputs=[
                    IOField("result", "object", True, "Handler result")
                ]
            ),
            steps=["Evaluate priority", "Save context", "Handle interrupt", "Resume if needed"],
            tags=["interrupt", "control", "context", "resume"]
        )
        
        self.pending_interrupts: List[Interrupt] = []
        self.paused_tasks: Dict[str, TaskContext] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n⏸️ Interrupt Handler")
        
        if action == "interrupt":
            return self._handle_interrupt(params.get("interrupt", {}), params.get("task_id", ""))
        elif action == "resume":
            return self._resume_task(params.get("task_id", ""))
        elif action == "status":
            return self._get_status()
        elif action == "clear":
            return self._clear_interrupts()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _handle_interrupt(self, interrupt_data: Dict, task_id: str) -> AlgorithmResult:
        interrupt = Interrupt(
            id=f"int_{len(self.pending_interrupts)}",
            source=interrupt_data.get("source", "unknown"),
            priority=InterruptPriority(interrupt_data.get("priority", 2)),
            reason=interrupt_data.get("reason", ""),
            timestamp=time.time()
        )
        
        self.pending_interrupts.append(interrupt)
        
        # If task specified, pause it
        if task_id:
            context = TaskContext(
                task_id=task_id,
                state=interrupt_data.get("state", {}),
                progress=interrupt_data.get("progress", 0),
                paused_at=time.time()
            )
            self.paused_tasks[task_id] = context
            print(f"   Paused task: {task_id}")
        
        # Handle based on priority
        if interrupt.priority == InterruptPriority.CRITICAL:
            action = "immediate_handle"
        elif interrupt.priority == InterruptPriority.HIGH:
            action = "queue_front"
        else:
            action = "queue_back"
        
        interrupt.handled = True
        
        print(f"   Interrupt: {interrupt.reason} ({interrupt.priority.name})")
        
        return AlgorithmResult(
            status="success",
            data={
                "interrupt_id": interrupt.id,
                "action_taken": action,
                "task_paused": task_id if task_id else None,
                "pending_count": len([i for i in self.pending_interrupts if not i.handled])
            }
        )
    
    def _resume_task(self, task_id: str) -> AlgorithmResult:
        if not task_id:
            return AlgorithmResult(status="error", error="No task ID provided")
        
        if task_id not in self.paused_tasks:
            return AlgorithmResult(status="error", error="Task not found in paused tasks")
        
        context = self.paused_tasks.pop(task_id)
        pause_duration = time.time() - context.paused_at
        
        print(f"   Resumed: {task_id} (paused {pause_duration:.1f}s)")
        
        return AlgorithmResult(
            status="success",
            data={
                "task_id": task_id,
                "resumed": True,
                "pause_duration": pause_duration,
                "progress": context.progress,
                "state": context.state
            }
        )
    
    def _get_status(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "pending_interrupts": len([i for i in self.pending_interrupts if not i.handled]),
                "total_interrupts": len(self.pending_interrupts),
                "paused_tasks": len(self.paused_tasks),
                "paused_task_ids": list(self.paused_tasks.keys())
            }
        )
    
    def _clear_interrupts(self) -> AlgorithmResult:
        count = len(self.pending_interrupts)
        self.pending_interrupts.clear()
        
        return AlgorithmResult(
            status="success",
            data={"cleared": count}
        )


def register(algorithm_manager):
    algo = InterruptHandlerAlgorithm()
    algorithm_manager.register("InterruptHandler", algo)
    print("✅ InterruptHandler registered")


if __name__ == "__main__":
    algo = InterruptHandlerAlgorithm()
    algo.execute({
        "action": "interrupt",
        "interrupt": {"source": "user", "priority": 3, "reason": "Urgent request"},
        "task_id": "task_001"
    })
    result = algo.execute({"action": "status"})
    print(f"Paused tasks: {result.data['paused_tasks']}")
    algo.execute({"action": "resume", "task_id": "task_001"})
