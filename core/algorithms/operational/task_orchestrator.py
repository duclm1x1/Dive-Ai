"""
🎯 TASK ORCHESTRATOR
Orchestrate complex multi-step tasks

Based on V28's core_engine/task_orchestrator.py
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


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestratedTask:
    """A task in the orchestration"""
    id: str
    name: str
    handler: str
    params: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    state: TaskState = TaskState.PENDING
    result: Any = None


class TaskOrchestratorAlgorithm(BaseAlgorithm):
    """
    🎯 Task Orchestrator
    
    Orchestrates complex tasks:
    - Task graph management
    - Dependency resolution
    - Parallel execution
    - Progress tracking
    
    From V28: core_engine/task_orchestrator.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="TaskOrchestrator",
            name="Task Orchestrator",
            level="operational",
            category="orchestration",
            version="1.0",
            description="Orchestrate complex multi-step tasks",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "define/execute/status"),
                    IOField("tasks", "array", False, "Tasks to orchestrate"),
                    IOField("task_id", "string", False, "Specific task ID")
                ],
                outputs=[
                    IOField("result", "object", True, "Orchestration result")
                ]
            ),
            steps=["Define tasks", "Resolve dependencies", "Execute in order", "Track progress"],
            tags=["orchestration", "tasks", "workflow"]
        )
        
        self.tasks: Dict[str, OrchestratedTask] = {}
        self.execution_log: List[Dict] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n🎯 Task Orchestrator")
        
        if action == "define":
            return self._define_tasks(params.get("tasks", []))
        elif action == "execute":
            return self._execute_orchestration()
        elif action == "status":
            return self._get_status()
        elif action == "cancel":
            return self._cancel_task(params.get("task_id", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _define_tasks(self, tasks_data: List[Dict]) -> AlgorithmResult:
        for task_data in tasks_data:
            task = OrchestratedTask(
                id=task_data.get("id", f"task_{len(self.tasks)}"),
                name=task_data.get("name", "Untitled"),
                handler=task_data.get("handler", "default"),
                params=task_data.get("params", {}),
                dependencies=task_data.get("dependencies", [])
            )
            self.tasks[task.id] = task
        
        print(f"   Defined: {len(tasks_data)} tasks")
        
        return AlgorithmResult(
            status="success",
            data={"defined": len(tasks_data), "total_tasks": len(self.tasks)}
        )
    
    def _execute_orchestration(self) -> AlgorithmResult:
        if not self.tasks:
            return AlgorithmResult(status="error", error="No tasks defined")
        
        # Get execution order
        order = self._get_execution_order()
        completed = []
        failed = []
        
        for task_id in order:
            task = self.tasks[task_id]
            
            # Check dependencies
            deps_ok = all(
                self.tasks[d].state == TaskState.COMPLETED
                for d in task.dependencies if d in self.tasks
            )
            
            if not deps_ok:
                task.state = TaskState.FAILED
                task.result = "Dependencies not met"
                failed.append(task_id)
                continue
            
            # Execute task
            task.state = TaskState.RUNNING
            try:
                # Simulate execution
                task.result = f"Executed: {task.name}"
                task.state = TaskState.COMPLETED
                completed.append(task_id)
                
                self.execution_log.append({
                    "task_id": task_id,
                    "state": "completed",
                    "timestamp": time.time()
                })
            except Exception as e:
                task.state = TaskState.FAILED
                task.result = str(e)
                failed.append(task_id)
        
        print(f"   Executed: {len(completed)}/{len(self.tasks)} completed")
        
        return AlgorithmResult(
            status="success" if not failed else "partial",
            data={
                "completed": completed,
                "failed": failed,
                "total": len(self.tasks)
            }
        )
    
    def _get_execution_order(self) -> List[str]:
        """Topological sort of tasks"""
        visited = set()
        order = []
        
        def visit(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)
            task = self.tasks.get(task_id)
            if task:
                for dep in task.dependencies:
                    visit(dep)
                order.append(task_id)
        
        for task_id in self.tasks:
            visit(task_id)
        
        return order
    
    def _get_status(self) -> AlgorithmResult:
        by_state = {}
        for task in self.tasks.values():
            state = task.state.value
            by_state[state] = by_state.get(state, 0) + 1
        
        return AlgorithmResult(
            status="success",
            data={
                "total_tasks": len(self.tasks),
                "by_state": by_state,
                "tasks": [
                    {"id": t.id, "name": t.name, "state": t.state.value}
                    for t in self.tasks.values()
                ]
            }
        )
    
    def _cancel_task(self, task_id: str) -> AlgorithmResult:
        if task_id not in self.tasks:
            return AlgorithmResult(status="error", error="Task not found")
        
        task = self.tasks[task_id]
        if task.state in [TaskState.PENDING, TaskState.RUNNING]:
            task.state = TaskState.CANCELLED
            return AlgorithmResult(status="success", data={"cancelled": task_id})
        
        return AlgorithmResult(status="error", error="Task cannot be cancelled")


def register(algorithm_manager):
    algo = TaskOrchestratorAlgorithm()
    algorithm_manager.register("TaskOrchestrator", algo)
    print("✅ TaskOrchestrator registered")


if __name__ == "__main__":
    algo = TaskOrchestratorAlgorithm()
    algo.execute({"action": "define", "tasks": [
        {"id": "setup", "name": "Setup Environment", "dependencies": []},
        {"id": "build", "name": "Build Project", "dependencies": ["setup"]},
        {"id": "test", "name": "Run Tests", "dependencies": ["build"]},
        {"id": "deploy", "name": "Deploy", "dependencies": ["test"]}
    ]})
    result = algo.execute({"action": "execute"})
    print(f"Completed: {len(result.data['completed'])}")
