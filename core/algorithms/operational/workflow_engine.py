"""
⚙️ WORKFLOW ENGINE
Define and execute complex workflows

Based on V28's vibe_engine/workflow_engine.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class StepType(Enum):
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    WAIT = "wait"


@dataclass
class WorkflowStep:
    """A step in the workflow"""
    id: str
    type: StepType
    action: str
    config: Dict = field(default_factory=dict)
    next_step: str = None
    on_error: str = None


@dataclass
class WorkflowInstance:
    """An instance of a running workflow"""
    id: str
    workflow_id: str
    current_step: str
    status: str = "running"
    context: Dict = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)


class WorkflowEngineAlgorithm(BaseAlgorithm):
    """
    ⚙️ Workflow Engine
    
    Complex workflow execution:
    - Step definitions
    - Conditional branching
    - Parallel execution
    - Error handling
    
    From V28: vibe_engine/workflow_engine.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="WorkflowEngine",
            name="Workflow Engine",
            level="operational",
            category="workflow",
            version="1.0",
            description="Define and execute complex workflows",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "define/execute/status"),
                    IOField("workflow", "object", False, "Workflow definition"),
                    IOField("workflow_id", "string", False, "Workflow to execute")
                ],
                outputs=[
                    IOField("result", "object", True, "Workflow result")
                ]
            ),
            steps=["Define workflow", "Parse steps", "Execute sequence", "Handle branching"],
            tags=["workflow", "automation", "execution"]
        )
        
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.action_handlers: Dict[str, Callable] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n⚙️ Workflow Engine")
        
        if action == "define":
            return self._define_workflow(params.get("workflow", {}))
        elif action == "execute":
            return self._execute_workflow(params.get("workflow_id", ""), params.get("context", {}))
        elif action == "status":
            return self._get_status(params.get("instance_id", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _define_workflow(self, workflow_data: Dict) -> AlgorithmResult:
        workflow_id = workflow_data.get("id", f"wf_{len(self.workflows)}")
        steps_data = workflow_data.get("steps", [])
        
        steps = []
        for step_data in steps_data:
            step = WorkflowStep(
                id=step_data.get("id", f"step_{len(steps)}"),
                type=StepType(step_data.get("type", "action")),
                action=step_data.get("action", ""),
                config=step_data.get("config", {}),
                next_step=step_data.get("next"),
                on_error=step_data.get("on_error")
            )
            steps.append(step)
        
        self.workflows[workflow_id] = steps
        
        print(f"   Defined: {workflow_id} ({len(steps)} steps)")
        
        return AlgorithmResult(
            status="success",
            data={"workflow_id": workflow_id, "steps": len(steps)}
        )
    
    def _execute_workflow(self, workflow_id: str, context: Dict) -> AlgorithmResult:
        if workflow_id not in self.workflows:
            return AlgorithmResult(status="error", error="Workflow not found")
        
        steps = self.workflows[workflow_id]
        if not steps:
            return AlgorithmResult(status="error", error="Workflow has no steps")
        
        # Create instance
        instance = WorkflowInstance(
            id=f"inst_{len(self.instances)}",
            workflow_id=workflow_id,
            current_step=steps[0].id,
            context=context
        )
        self.instances[instance.id] = instance
        
        # Execute steps
        step_index = 0
        while step_index < len(steps):
            step = steps[step_index]
            instance.current_step = step.id
            
            try:
                result = self._execute_step(step, instance)
                instance.history.append({
                    "step": step.id,
                    "status": "completed",
                    "result": result
                })
                
                # Handle branching
                if step.next_step:
                    next_idx = next((i for i, s in enumerate(steps) if s.id == step.next_step), None)
                    if next_idx is not None:
                        step_index = next_idx
                        continue
                
                step_index += 1
                
            except Exception as e:
                instance.history.append({
                    "step": step.id,
                    "status": "error",
                    "error": str(e)
                })
                
                if step.on_error:
                    err_idx = next((i for i, s in enumerate(steps) if s.id == step.on_error), None)
                    if err_idx is not None:
                        step_index = err_idx
                        continue
                
                instance.status = "failed"
                break
        else:
            instance.status = "completed"
        
        print(f"   Executed: {instance.id} → {instance.status}")
        
        return AlgorithmResult(
            status="success",
            data={
                "instance_id": instance.id,
                "workflow_id": workflow_id,
                "status": instance.status,
                "steps_completed": len(instance.history),
                "context": instance.context
            }
        )
    
    def _execute_step(self, step: WorkflowStep, instance: WorkflowInstance) -> Any:
        """Execute a single workflow step"""
        if step.type == StepType.ACTION:
            # Simulate action execution
            return f"Executed: {step.action}"
        
        elif step.type == StepType.WAIT:
            wait_time = step.config.get("seconds", 1)
            time.sleep(min(wait_time, 2))  # Cap at 2s for safety
            return f"Waited {wait_time}s"
        
        elif step.type == StepType.CONDITION:
            # Evaluate condition
            condition = step.config.get("condition", "true")
            result = eval(condition, {"context": instance.context})
            return {"condition": condition, "result": result}
        
        return None
    
    def _get_status(self, instance_id: str) -> AlgorithmResult:
        if instance_id:
            if instance_id not in self.instances:
                return AlgorithmResult(status="error", error="Instance not found")
            
            inst = self.instances[instance_id]
            return AlgorithmResult(
                status="success",
                data={
                    "instance_id": instance_id,
                    "workflow_id": inst.workflow_id,
                    "status": inst.status,
                    "current_step": inst.current_step,
                    "history": inst.history
                }
            )
        
        return AlgorithmResult(
            status="success",
            data={
                "total_workflows": len(self.workflows),
                "total_instances": len(self.instances),
                "running": sum(1 for i in self.instances.values() if i.status == "running")
            }
        )


def register(algorithm_manager):
    algo = WorkflowEngineAlgorithm()
    algorithm_manager.register("WorkflowEngine", algo)
    print("✅ WorkflowEngine registered")


if __name__ == "__main__":
    algo = WorkflowEngineAlgorithm()
    algo.execute({"action": "define", "workflow": {
        "id": "deploy",
        "steps": [
            {"id": "build", "type": "action", "action": "npm run build"},
            {"id": "test", "type": "action", "action": "npm test"},
            {"id": "deploy", "type": "action", "action": "deploy to prod"}
        ]
    }})
    result = algo.execute({"action": "execute", "workflow_id": "deploy"})
    print(f"Status: {result.data['status']}")
