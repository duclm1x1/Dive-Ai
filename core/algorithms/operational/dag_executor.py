"""
📊 DAG EXECUTOR
Execute Directed Acyclic Graph workflows

Based on V28's vibe_engine/dag_executor.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """A node in the DAG"""
    id: str
    task: str
    dependencies: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    execution_time: float = 0.0


class DAGExecutorAlgorithm(BaseAlgorithm):
    """
    📊 DAG Executor
    
    Executes workflow DAGs:
    - Dependency resolution
    - Parallel execution
    - Error handling
    - Progress tracking
    
    From V28: vibe_engine/dag_executor.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="DAGExecutor",
            name="DAG Executor",
            level="operational",
            category="workflow",
            version="1.0",
            description="Execute DAG workflows with dependencies",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "build/execute/status"),
                    IOField("nodes", "array", False, "Nodes to add"),
                    IOField("executor", "function", False, "Node executor function")
                ],
                outputs=[
                    IOField("result", "object", True, "Execution result")
                ]
            ),
            steps=["Build DAG", "Topological sort", "Execute in order", "Handle failures"],
            tags=["dag", "workflow", "execution", "parallel"]
        )
        
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_order: List[str] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n📊 DAG Executor")
        
        if action == "build":
            return self._build_dag(params.get("nodes", []))
        elif action == "execute":
            return self._execute_dag(params.get("executor"))
        elif action == "status":
            return self._get_status()
        elif action == "reset":
            return self._reset()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _build_dag(self, nodes_data: List[Dict]) -> AlgorithmResult:
        for node_data in nodes_data:
            node = DAGNode(
                id=node_data.get("id", f"node_{len(self.nodes)}"),
                task=node_data.get("task", ""),
                dependencies=node_data.get("dependencies", [])
            )
            self.nodes[node.id] = node
        
        # Topological sort
        self.execution_order = self._topological_sort()
        
        print(f"   Built DAG: {len(self.nodes)} nodes")
        
        return AlgorithmResult(
            status="success",
            data={
                "nodes": len(self.nodes),
                "execution_order": self.execution_order
            }
        )
    
    def _topological_sort(self) -> List[str]:
        in_degree = {n: 0 for n in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[node.id] += 1
        
        queue = deque([n for n in self.nodes if in_degree[n] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for node_id, node in self.nodes.items():
                if current in node.dependencies:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)
        
        return result
    
    def _execute_dag(self, executor: Callable = None) -> AlgorithmResult:
        if not self.execution_order:
            self.execution_order = self._topological_sort()
        
        results = {}
        failed = []
        
        for node_id in self.execution_order:
            node = self.nodes[node_id]
            
            # Check dependencies
            deps_ok = all(
                self.nodes[d].status == NodeStatus.COMPLETED
                for d in node.dependencies if d in self.nodes
            )
            
            if not deps_ok:
                node.status = NodeStatus.SKIPPED
                continue
            
            # Execute
            node.status = NodeStatus.RUNNING
            start = time.time()
            
            try:
                if executor:
                    node.result = executor(node)
                else:
                    node.result = f"Executed: {node.task}"
                node.status = NodeStatus.COMPLETED
            except Exception as e:
                node.status = NodeStatus.FAILED
                node.result = str(e)
                failed.append(node_id)
            
            node.execution_time = time.time() - start
            results[node_id] = node.result
        
        completed = sum(1 for n in self.nodes.values() if n.status == NodeStatus.COMPLETED)
        print(f"   Executed: {completed}/{len(self.nodes)} completed")
        
        return AlgorithmResult(
            status="success" if not failed else "partial",
            data={
                "completed": completed,
                "failed": failed,
                "results": results,
                "total_time": sum(n.execution_time for n in self.nodes.values())
            }
        )
    
    def _get_status(self) -> AlgorithmResult:
        by_status = {}
        for node in self.nodes.values():
            status = node.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return AlgorithmResult(
            status="success",
            data={
                "total_nodes": len(self.nodes),
                "by_status": by_status,
                "execution_order": self.execution_order
            }
        )
    
    def _reset(self) -> AlgorithmResult:
        for node in self.nodes.values():
            node.status = NodeStatus.PENDING
            node.result = None
            node.execution_time = 0
        
        return AlgorithmResult(
            status="success",
            data={"reset": True, "nodes": len(self.nodes)}
        )


def register(algorithm_manager):
    algo = DAGExecutorAlgorithm()
    algorithm_manager.register("DAGExecutor", algo)
    print("✅ DAGExecutor registered")


if __name__ == "__main__":
    algo = DAGExecutorAlgorithm()
    algo.execute({"action": "build", "nodes": [
        {"id": "A", "task": "Setup", "dependencies": []},
        {"id": "B", "task": "Build", "dependencies": ["A"]},
        {"id": "C", "task": "Test", "dependencies": ["B"]},
        {"id": "D", "task": "Deploy", "dependencies": ["C"]}
    ]})
    result = algo.execute({"action": "execute"})
    print(f"Completed: {result.data['completed']}")
