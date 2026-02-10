"""
🔌 FEATURE ALGORITHMS
Wrap all new features as algorithms for AlgorithmManager integration

Core Philosophy:
User Input → Algorithm Selection (single or combined) → Result Delivery
"""

import os
import sys
from typing import Dict, List, Any, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


def success_result(data: Dict = None) -> AlgorithmResult:
    """Helper to create success result"""
    return AlgorithmResult(status="success", data=data or {})


def error_result(error: str) -> AlgorithmResult:
    """Helper to create error result"""
    return AlgorithmResult(status="error", error=error)


# ═══════════════════════════════════════════════════════════════════════
# 1. REAL API EXECUTION ALGORITHM
# ═══════════════════════════════════════════════════════════════════════

class RealAPIExecutionAlgorithm(BaseAlgorithm):
    """Execute requests against real V98/AICoding APIs with rate limiting"""
    
    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            algorithm_id="RealAPIExecution",
            name="Real API Execution",
            level="operational",
            category="execution",
            version="1.0.0",
            description="Execute agent requests against V98/AICoding APIs",
            io=AlgorithmIOSpec(
                inputs=[IOField("action", "string", True, "Action to perform")],
                outputs=[IOField("result", "object", True, "Execution result")]
            ),
            tags=["api", "execution", "v98", "aicoding"]
        )
        self.executor = None
    
    def _init_executor(self):
        if self.executor is None:
            from core.execution.real_api_executor import get_executor
            self.executor = get_executor()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        self._init_executor()
        action = params.get("action", "get_stats")
        
        if action == "execute_v98":
            result = self.executor.execute_v98(
                agent_id=params.get("agent_id", 1),
                model=params.get("model", "gpt-4o-mini"),
                messages=params.get("messages", [])
            )
            return success_result({
                "response": result.response,
                "tokens": result.tokens_used,
                "cost": result.cost
            })
        
        elif action == "get_stats":
            return success_result(self.executor.get_stats())
        
        return error_result(f"Unknown action: {action}")


# ═══════════════════════════════════════════════════════════════════════
# 2. PERSISTENT MEMORY ALGORITHM
# ═══════════════════════════════════════════════════════════════════════

class PersistentMemoryAlgorithm(BaseAlgorithm):
    """SQLite-based storage for agent states, tasks, and history"""
    
    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            algorithm_id="PersistentMemory",
            name="Persistent Memory",
            level="operational",
            category="memory",
            version="1.0.0",
            description="Save and retrieve agent states, tasks, and history",
            io=AlgorithmIOSpec(
                inputs=[IOField("action", "string", True, "Action to perform")],
                outputs=[IOField("result", "object", True, "Memory result")]
            ),
            tags=["memory", "storage", "sqlite"]
        )
        self.memory = None
    
    def _init_memory(self):
        if self.memory is None:
            from core.memory.persistent_memory import get_memory
            self.memory = get_memory()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        self._init_memory()
        action = params.get("action", "get_stats")
        
        if action == "get_stats":
            return success_result(self.memory.get_dashboard_stats())
        
        elif action == "search":
            results = self.memory.search_memory(
                query=params.get("query", ""),
                limit=params.get("limit", 20)
            )
            return success_result({"results": results})
        
        return error_result(f"Unknown action: {action}")


# ═══════════════════════════════════════════════════════════════════════
# 3. TASK QUEUE ALGORITHM
# ═══════════════════════════════════════════════════════════════════════

class TaskQueueAlgorithm(BaseAlgorithm):
    """Priority queue with DAG dependencies for task scheduling"""
    
    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            algorithm_id="TaskQueue",
            name="Task Queue",
            level="operational",
            category="orchestration",
            version="1.0.0",
            description="Priority queue with DAG dependency support",
            io=AlgorithmIOSpec(
                inputs=[IOField("action", "string", True, "Action to perform")],
                outputs=[IOField("result", "object", True, "Queue result")]
            ),
            tags=["queue", "dag", "scheduling"]
        )
        self.queue = None
    
    def _init_queue(self):
        if self.queue is None:
            from core.execution.task_queue import TaskQueue
            self.queue = TaskQueue(max_parallel=10)
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        self._init_queue()
        action = params.get("action", "get_stats")
        
        if action == "add_task":
            task_id = self.queue.add_task(
                description=params.get("description", "Task"),
                priority=params.get("priority", 3),
                dependencies=params.get("dependencies", [])
            )
            return success_result({"task_id": task_id})
        
        elif action == "get_stats":
            return success_result(self.queue.get_stats())
        
        elif action == "detect_deadlock":
            return success_result({"has_deadlock": self.queue.detect_deadlock()})
        
        return error_result(f"Unknown action: {action}")


# ═══════════════════════════════════════════════════════════════════════
# 4. AUTO DEPLOY ALGORITHM
# ═══════════════════════════════════════════════════════════════════════

class AutoDeployAlgorithm(BaseAlgorithm):
    """Git integration for automated code deployment"""
    
    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            algorithm_id="AutoDeploy",
            name="Auto Deploy",
            level="operational",
            category="deployment",
            version="1.0.0",
            description="Automated Git commit, push, and PR creation",
            io=AlgorithmIOSpec(
                inputs=[IOField("action", "string", True, "Action to perform")],
                outputs=[IOField("result", "object", True, "Deploy result")]
            ),
            tags=["git", "deploy", "commit"]
        )
        self.deployer = None
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        repo_path = params.get("repo_path", ".")
        
        try:
            from core.deployment.auto_deployer import create_deployer
            deployer = create_deployer(repo_path)
        except Exception as e:
            return error_result(str(e))
        
        if action == "status":
            return success_result(deployer.get_status())
        
        elif action == "commit":
            result = deployer.commit(
                message=params.get("message", "Auto commit"),
                stage_all=params.get("stage_all", True)
            )
            return success_result({
                "success": result.success,
                "commit_hash": result.commit_hash
            })
        
        return error_result(f"Unknown action: {action}")


# ═══════════════════════════════════════════════════════════════════════
# 5. SELF IMPROVING ALGORITHM
# ═══════════════════════════════════════════════════════════════════════

class SelfImprovingAlgorithm(BaseAlgorithm):
    """Learn from mistakes and optimize agent performance"""
    
    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            algorithm_id="SelfImproving",
            name="Self Improving",
            level="operational",
            category="learning",
            version="1.0.0",
            description="Learn from execution feedback and optimize",
            io=AlgorithmIOSpec(
                inputs=[IOField("action", "string", True, "Action to perform")],
                outputs=[IOField("result", "object", True, "Learning result")]
            ),
            tags=["learning", "optimization", "feedback"]
        )
        self.improver = None
    
    def _init_improver(self):
        if self.improver is None:
            from core.learning.self_improving import get_self_improver
            self.improver = get_self_improver()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        self._init_improver()
        action = params.get("action", "get_summary")
        
        if action == "get_summary":
            return success_result(self.improver.get_summary())
        
        elif action == "get_recommendations":
            recs = self.improver.get_recommendations(params.get("agent_id", 1))
            return success_result(recs)
        
        return error_result(f"Unknown action: {action}")


# ═══════════════════════════════════════════════════════════════════════
# 6. MULTI PROJECT ALGORITHM
# ═══════════════════════════════════════════════════════════════════════

class MultiProjectAlgorithm(BaseAlgorithm):
    """Manage multiple codebases with project-specific agent pools"""
    
    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            algorithm_id="MultiProject",
            name="Multi Project",
            level="operational",
            category="project",
            version="1.0.0",
            description="Manage multiple projects with dedicated agent pools",
            io=AlgorithmIOSpec(
                inputs=[IOField("action", "string", True, "Action to perform")],
                outputs=[IOField("result", "object", True, "Project result")]
            ),
            tags=["project", "multi", "workspace"]
        )
        self.manager = None
    
    def _init_manager(self):
        if self.manager is None:
            from core.projects.multi_project import get_project_manager
            self.manager = get_project_manager()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        self._init_manager()
        action = params.get("action", "list_projects")
        
        if action == "list_projects":
            projects = self.manager.list_projects()
            return success_result({
                "projects": [
                    {"id": p.project_id, "name": p.name, "agents": p.allocated_agents}
                    for p in projects
                ]
            })
        
        elif action == "add_project":
            project = self.manager.add_project(
                name=params.get("name", "New Project"),
                path=params.get("path", "."),
                priority=params.get("priority", 3)
            )
            return success_result({
                "project_id": project.project_id,
                "allocated_agents": project.allocated_agents
            })
        
        elif action == "get_stats":
            return success_result(self.manager.get_project_stats())
        
        return error_result(f"Unknown action: {action}")


# ═══════════════════════════════════════════════════════════════════════
# AUTO-REGISTRATION
# ═══════════════════════════════════════════════════════════════════════

FEATURE_ALGORITHMS = [
    RealAPIExecutionAlgorithm,
    PersistentMemoryAlgorithm,
    TaskQueueAlgorithm,
    AutoDeployAlgorithm,
    SelfImprovingAlgorithm,
    MultiProjectAlgorithm
]


def register_feature_algorithms(algorithm_manager):
    """Register all feature algorithms with AlgorithmManager"""
    registered = 0
    
    for AlgoClass in FEATURE_ALGORITHMS:
        try:
            algo = AlgoClass()
            algorithm_manager.register(algo)
            print(f"✅ {algo.spec.name} registered")
            registered += 1
        except Exception as e:
            print(f"⚠️ {AlgoClass.__name__} failed: {e}")
    
    return registered


if __name__ == "__main__":
    print("\n🔌 Feature Algorithms Module")
    print("\nAvailable Algorithms:")
    for cls in FEATURE_ALGORITHMS:
        algo = cls()
        print(f"   - {algo.spec.algorithm_id}: {algo.spec.description}")
    
    print("\nTesting TaskQueue...")
    tq = TaskQueueAlgorithm()
    result = tq.execute({"action": "get_stats"})
    print(f"   Result: {result.status} - {result.data}")
