"""
Dive AI V29 - Meta-Algorithm Base Class
Foundation for Cognitive Layer Strategies

Features:
- Standardized execution flow: Decompose -> Execute -> Evaluate -> Learn
- State management via WorkflowState
- Integration with Memory V5, Reasoning, and Evaluation
- Error handling and self-correction
"""

import os
import sys
import time
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import asdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult, AlgorithmSpec
from core.memory_v2.memory_v5 import get_memory_v5, MemoryV5, ExecutionRecord
from core.evaluation.workflow_scorer import get_workflow_scorer, WorkflowScorer


class WorkflowState:
    """
    Tracks the state of a Meta-Algorithm execution
    """
    def __init__(self, workflow_id: str, goal: str):
        self.workflow_id = workflow_id
        self.goal = goal
        self.status = "running"  # running, completed, failed, paused
        self.current_step_index = 0
        self.steps: List[Dict] = []
        self.context: Dict[str, Any] = {}
        self.history: List[Dict] = []
        self.artifacts: Dict[str, str] = {}
        self.start_time = time.time()
        self.end_time = 0.0
    
    def add_step(self, step: Dict):
        """Add a step to the plan"""
        self.steps.append(step)
    
    def update_context(self, key: str, value: Any):
        """Update context variable"""
        self.context[key] = value
    
    def log_history(self, action: str, result: Any, success: bool):
        """Log action history"""
        self.history.append({
            "timestamp": time.time(),
            "action": action,
            "result": str(result)[:500],  # Truncate for log
            "success": success
        })
    
    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "goal": self.goal,
            "status": self.status,
            "current_step": self.current_step_index,
            "total_steps": len(self.steps),
            "context_keys": list(self.context.keys()),
            "duration": (self.end_time or time.time()) - self.start_time
        }


class BaseMetaAlgorithm(BaseAlgorithm, ABC):
    """
    Base class for V29 Meta-Algorithms
    
    A Meta-Algorithm is a high-level strategy that:
    1. Decomposes a goal into steps
    2. Executes standard algorithms for each step
    3. Evaluates progress and corrects course
    """
    
    def __init__(self):
        super().__init__()
        self.memory: MemoryV5 = get_memory_v5()
        self.scorer: WorkflowScorer = get_workflow_scorer()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """
        Execute the meta-algorithm
        
        Args:
            params: Must contain 'goal' or 'request'
        
        Returns:
            AlgorithmResult with execution summary and artifacts
        """
        goal = params.get("goal") or params.get("request")
        if not goal:
            return AlgorithmResult(status="error", error="Missing 'goal' in params")
        
        workflow_id = str(uuid.uuid4())
        state = WorkflowState(workflow_id, goal)
        execution_recorder = self.scorer.start_execution(workflow_id, self.spec.algorithm_id, goal)
        
        print(f"\n🚀 STARTING META-ALGORITHM: {self.spec.name}")
        print(f"   Goal: {goal}")
        print(f"   ID: {workflow_id}")
        
        try:
            # 1. Initialize
            self._initialize(state, params)
            
            # 2. Decompose / Plan
            if not state.steps:
                plan = self.decompose(state)
                if not plan:
                    raise Exception("Decomposition failed to produce steps")
                state.steps = plan
            
            # 3. Execution Loop
            while state.current_step_index < len(state.steps):
                step = state.steps[state.current_step_index]
                print(f"\n   👉 Step {state.current_step_index + 1}/{len(state.steps)}: {step.get('title', 'Unknown')}")
                
                # Execute step
                step_result = self._execute_step(step, state)
                
                # Log to scorer
                self.scorer.log_action(
                    workflow_id,
                    step.get("title", "unknown"),
                    success=step_result.get("success", False),
                    details=step_result
                )
                
                # Evaluate & Decide
                decision = self._evaluate_and_decide(step, step_result, state)
                
                if decision == "continue":
                    state.current_step_index += 1
                elif decision == "retry":
                    print("   🔄 Retrying step...")
                    # Don't increment index
                elif decision == "abort":
                    raise Exception(f"Step failed: {step_result.get('error', 'Unknown error')}")
                elif decision == "done":
                    break
            
            # 4. Finalize
            self._finalize(state)
            state.status = "completed"
            
            # Scorer completion
            kpis = self.scorer.complete_execution(workflow_id, success=True)
            
            # Record execution in Memory
            self._record_execution(state, kpis, True)
            
            execution_time = state.end_time - state.start_time
            print(f"\n✅ COMPLETED in {execution_time:.2f}s")
            print(f"   KPI Score: {kpis.overall_score:.2f}")
            
            return AlgorithmResult(
                status="success",
                data={
                    "workflow_id": workflow_id,
                    "state": state.to_dict(),
                    "artifacts": state.artifacts,
                    "kpis": asdict(kpis) if kpis else {}
                }
            )
            
        except Exception as e:
            print(f"\n❌ FAILED: {str(e)}")
            state.status = "failed"
            self.scorer.complete_execution(workflow_id, success=False)
            self._record_execution(state, None, False)
            
            return AlgorithmResult(status="error", error=str(e))
    
    @abstractmethod
    def decompose(self, state: WorkflowState) -> List[Dict]:
        """
        Decompose goal into steps.
        Must be implemented by subclasses.
        """
        pass
    
    def _initialize(self, state: WorkflowState, params: Dict):
        """Optional initialization hook"""
        state.context.update(params.get("context", {}))
    
    def _execute_step(self, step: Dict, state: WorkflowState) -> Dict:
        """
        Execute a single step.
        Can be overridden, but default implementation looks for method matching step 'type'
        """
        step_type = step.get("type", "action")
        method_name = f"step_{step_type}"
        
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            try:
                result = method(step, state)
                state.log_history(step.get("title"), result, True)
                return {"success": True, "data": result}
            except Exception as e:
                state.log_history(step.get("title"), str(e), False)
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Unknown step type: {step_type}"}
    
    def _evaluate_and_decide(self, step: Dict, result: Dict, state: WorkflowState) -> str:
        """
        Evaluate step result and decide next action.
        Returns: continue, retry, abort, done
        """
        if not result["success"]:
            # Simple retry logic (can be enhanced)
            retry_count = state.context.get(f"retry_{state.current_step_index}", 0)
            if retry_count < 2:
                state.context[f"retry_{state.current_step_index}"] = retry_count + 1
                return "retry"
            return "abort"
        
        return "continue"
    
    def _finalize(self, state: WorkflowState):
        """Optional finalization hook"""
        state.end_time = time.time()
    
    def _record_execution(self, state: WorkflowState, kpis: Any, success: bool):
        """Save execution record to Memory V5"""
        try:
            record = ExecutionRecord(
                execution_id=state.workflow_id,
                algorithm_id=self.spec.algorithm_id,
                task_type="meta-algorithm",
                task_description=state.goal,
                input_data={"context_keys": list(state.context.keys())},
                output_data={"status": state.status, "steps": len(state.history)},
                gpa_score=kpis.overall_score if kpis else 0.0,
                goal_alignment=0.0, # Filled by manual review or advanced scorer
                plan_alignment=kpis.final_success_rate if kpis else 0.0,
                action_quality=kpis.overall_score if kpis else 0.0,
                execution_time_ms=(time.time() - state.start_time) * 1000,
                resources_used={},
                success=success
            )
            self.memory.save_execution(record)
        except Exception as e:
            print(f"   ⚠️ Failed to save execution history: {e}")

