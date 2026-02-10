"""
🤖 AUTONOMOUS EXECUTOR - OpenClaw Style
Self-running execution that doesn't ask - just does it!
With Security Guardrails for protection.

Usage:
    executor = AutonomousExecutorAlgorithm()
    result = executor.execute({
        "task": "generate code",
        "params": {"requirements": "hello world"}
    })
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)

from core.algorithms.operational.security_guardrail import (
    SecurityGuardrail,
    SecurityLevel,
    SENSITIVE_DATA_PATTERNS,
    DANGEROUS_ACTIONS
)


@dataclass
class ExecutionTask:
    """A task queued for execution"""
    task_id: str
    algorithm_id: str
    params: Dict[str, Any]
    security_level: SecurityLevel
    status: str = "pending"
    requires_confirmation: bool = False
    result: Optional[AlgorithmResult] = None
    created_at: float = field(default_factory=time.time)


class AutonomousExecutorAlgorithm(BaseAlgorithm):
    """
    🤖 OpenClaw-Style Autonomous Executor
    
    RUNS AUTOMATICALLY without asking user!
    Only stops for:
    - CRITICAL security (passwords, API keys, financial)
    - Personal data exposure risk
    - Dangerous system operations
    
    Everything else: AUTO-EXECUTE! 🚀
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AutonomousExecutor",
            name="Autonomous Executor",
            level="operational",
            category="orchestration",
            version="1.0",
            description="OpenClaw-style self-running executor. Auto-executes safe tasks, only asks for dangerous ones.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("task", "string", True, "Task/Algorithm to execute"),
                    IOField("params", "object", False, "Parameters for the task"),
                    IOField("force_ask", "boolean", False, "Force asking user"),
                    IOField("batch", "list", False, "Batch of tasks to execute")
                ],
                outputs=[
                    IOField("executed", "list", True, "Tasks that were auto-executed"),
                    IOField("pending", "list", True, "Tasks pending confirmation"),
                    IOField("results", "object", True, "Execution results")
                ]
            ),
            
            steps=[
                "Step 1: Receive task(s)",
                "Step 2: Security classification",
                "Step 3: Auto-execute safe tasks",
                "Step 4: Queue dangerous tasks for confirmation",
                "Step 5: Return execution report"
            ],
            
            tags=["autonomous", "executor", "openclaw", "self-running"]
        )
        
        self.guardrail = SecurityGuardrail()
        self.execution_queue: List[ExecutionTask] = []
        self.execution_history: List[ExecutionTask] = []
        self.algorithm_manager = None
    
    def set_algorithm_manager(self, manager):
        """Set the algorithm manager for executing sub-tasks"""
        self.algorithm_manager = manager
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """
        Execute tasks autonomously
        
        Auto-executes everything that's safe
        Queues dangerous tasks for confirmation
        """
        
        task = params.get("task", "")
        task_params = params.get("params", {})
        force_ask = params.get("force_ask", False)
        batch = params.get("batch", [])
        
        executed = []
        pending = []
        results = {}
        
        # Process single task or batch
        tasks_to_process = []
        
        if task:
            tasks_to_process.append({"task": task, "params": task_params})
        
        if batch:
            tasks_to_process.extend(batch)
        
        print(f"\n🤖 Autonomous Executor: {len(tasks_to_process)} task(s)")
        
        for i, task_spec in enumerate(tasks_to_process):
            task_name = task_spec.get("task", f"task_{i}")
            task_params = task_spec.get("params", {})
            
            # Security check
            can_execute, reason = self.guardrail.can_auto_execute(task_name, task_params)
            level, security_reasons = self.guardrail.classify_action(task_name, task_params)
            
            # Force ask overrides auto-execute
            if force_ask:
                can_execute = False
                reason = "User forced confirmation"
            
            if can_execute:
                # 🚀 AUTO-EXECUTE!
                print(f"   ✅ [{level.name}] Auto-executing: {task_name}")
                
                result = self._execute_task(task_name, task_params)
                
                executed.append({
                    "task": task_name,
                    "security_level": level.name,
                    "status": result.status if result else "unknown"
                })
                
                results[task_name] = {
                    "status": result.status if result else "error",
                    "data": result.data if result else None
                }
            else:
                # 🔒 NEEDS CONFIRMATION
                print(f"   🔒 [{level.name}] Queued for confirmation: {task_name}")
                print(f"      Reason: {reason}")
                
                # Create execution task
                exec_task = ExecutionTask(
                    task_id=f"task_{int(time.time() * 1000)}_{i}",
                    algorithm_id=task_name,
                    params=task_params,
                    security_level=level,
                    requires_confirmation=True
                )
                
                self.execution_queue.append(exec_task)
                
                pending.append({
                    "task_id": exec_task.task_id,
                    "task": task_name,
                    "security_level": level.name,
                    "reasons": security_reasons,
                    "confirmation_required": self.guardrail.request_user_confirmation(task_name, task_params)
                })
        
        # Summary
        print(f"\n   📊 Summary:")
        print(f"      Auto-executed: {len(executed)}")
        print(f"      Pending confirmation: {len(pending)}")
        
        return AlgorithmResult(
            status="success",
            data={
                "executed": executed,
                "pending": pending,
                "results": results,
                "summary": {
                    "total_tasks": len(tasks_to_process),
                    "auto_executed": len(executed),
                    "pending_confirmation": len(pending)
                }
            },
            metadata={
                "execution_mode": "autonomous",
                "security_enabled": True
            }
        )
    
    def _execute_task(self, task: str, params: Dict[str, Any]) -> Optional[AlgorithmResult]:
        """Internal task execution"""
        
        if self.algorithm_manager:
            # Try to execute via algorithm manager
            algo = self.algorithm_manager.get_algorithm(task)
            if algo:
                return self.algorithm_manager.execute(task, params)
        
        # Fallback: simulate execution
        return AlgorithmResult(
            status="success",
            data={"task": task, "params": params, "simulated": True}
        )
    
    def confirm_pending(self, task_id: str, confirmed: bool) -> AlgorithmResult:
        """
        Confirm a pending task
        
        Args:
            task_id: ID of the pending task
            confirmed: True to execute, False to cancel
        """
        
        # Find task in queue
        task = None
        for t in self.execution_queue:
            if t.task_id == task_id:
                task = t
                break
        
        if not task:
            return AlgorithmResult(
                status="error",
                error=f"Task {task_id} not found in queue"
            )
        
        if confirmed:
            # Execute the task
            print(f"   ✅ User confirmed: {task.algorithm_id}")
            result = self._execute_task(task.algorithm_id, task.params)
            task.status = "executed"
            task.result = result
            
            # Move to history
            self.execution_queue.remove(task)
            self.execution_history.append(task)
            
            return AlgorithmResult(
                status="success",
                data={
                    "task_id": task_id,
                    "executed": True,
                    "result": result.data if result else None
                }
            )
        else:
            # Cancel the task
            print(f"   ❌ User cancelled: {task.algorithm_id}")
            task.status = "cancelled"
            
            self.execution_queue.remove(task)
            self.execution_history.append(task)
            
            return AlgorithmResult(
                status="cancelled",
                data={
                    "task_id": task_id,
                    "executed": False,
                    "reason": "User cancelled"
                }
            )
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks requiring confirmation"""
        
        return [
            {
                "task_id": t.task_id,
                "task": t.algorithm_id,
                "security_level": t.security_level.name,
                "params_keys": list(t.params.keys()),
                "created_at": t.created_at
            }
            for t in self.execution_queue
        ]


# ================================
# SAFE ACTIONS LIST (Auto-execute)
# ================================

SAFE_ACTIONS = [
    # Memory operations
    "HighPerformanceMemory",
    "MemoryLoop",
    "SemanticSearch",
    "ContextRetrieval",
    
    # Routing & Analysis
    "SmartModelRouter",
    "ComplexityAnalyzer",
    "SemanticRouting",
    
    # Code Generation (read-only outputs)
    "CodeGenerator",
    "CodeReviewer",
    "TestWriter",
    "DocumentationGenerator",
    
    # Skills (no external effects)
    "FormalVerification",
    "DynamicNeuralArchitecture",
    "GradientAwareRouting",
    "HierarchicalExperts",
    
    # Orchestration (planning only)
    "TaskDecomposition",
    "SmartOrchestrator",
    
    # Prompting
    "HybridPrompting",
    "PromptTemplate",
    "ChainOfThought",
    
    # Formatting
    "InputValidation",
    "OutputFormatting",
    "ResponseFormatting"
]

# ================================
# DANGEROUS ACTIONS LIST (Always ask)
# ================================

DANGEROUS_ACTIONS_LIST = [
    # Network operations
    "ConnectionV98",
    "ConnectionAICoding",
    "ConnectionOpenAI",
    "LLMQuery",  # Sends data externally
    
    # Computer control
    "ComputerOperator",
    "MouseControl",
    "KeyboardControl",
    "WindowManagement",
    
    # File operations
    "write_file",
    "delete_file",
    "upload_file",
    
    # System operations
    "run_command",
    "install_package",
    "modify_config"
]


def register(algorithm_manager):
    """Register Autonomous Executor"""
    try:
        algo = AutonomousExecutorAlgorithm()
        algo.set_algorithm_manager(algorithm_manager)
        algorithm_manager.register("AutonomousExecutor", algo)
        print("✅ AutonomousExecutor registered (OPENCLAW-STYLE)")
    except Exception as e:
        print(f"❌ Failed to register AutonomousExecutor: {e}")
