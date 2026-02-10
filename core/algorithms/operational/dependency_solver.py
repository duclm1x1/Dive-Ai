"""
🔗 DEPENDENCY SOLVER
Hierarchical Dependency Solver for task ordering

Based on V28's layer2_hierarchicaldependencysolver.py
"""

import os
import sys
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class DependencyNode:
    """A node in the dependency graph"""
    id: str
    name: str
    dependencies: List[str]
    level: int = 0
    resolved: bool = False


class DependencySolverAlgorithm(BaseAlgorithm):
    """
    🔗 Hierarchical Dependency Solver
    
    Resolves task dependencies using topological sort.
    Handles circular dependencies gracefully.
    
    From V28: layer2_hierarchicaldependencysolver.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="DependencySolver",
            name="Dependency Solver",
            level="operational",
            category="planning",
            version="1.0",
            description="Resolve task dependencies for execution order",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("tasks", "array", True, "Tasks with dependencies"),
                ],
                outputs=[
                    IOField("execution_order", "array", True, "Ordered task list"),
                    IOField("levels", "object", True, "Tasks grouped by level")
                ]
            ),
            steps=["Build graph", "Detect cycles", "Topological sort", "Assign levels"],
            tags=["dependencies", "planning", "dag"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        tasks = params.get("tasks", [])
        
        if not tasks:
            return AlgorithmResult(status="error", error="No tasks provided")
        
        print(f"\n🔗 Dependency Solver")
        print(f"   Tasks: {len(tasks)}")
        
        # Build nodes
        nodes = {}
        for task in tasks:
            node = DependencyNode(
                id=task.get("id", str(len(nodes))),
                name=task.get("name", ""),
                dependencies=task.get("dependencies", [])
            )
            nodes[node.id] = node
        
        # Detect cycles
        cycles = self._detect_cycles(nodes)
        if cycles:
            print(f"   ⚠️ Circular dependencies detected: {cycles}")
        
        # Topological sort
        order = self._topological_sort(nodes)
        
        # Assign levels
        levels = self._assign_levels(nodes, order)
        
        print(f"   Levels: {len(levels)}")
        print(f"   Order: {' → '.join(order[:5])}{'...' if len(order) > 5 else ''}")
        
        return AlgorithmResult(
            status="success",
            data={
                "execution_order": order,
                "levels": levels,
                "cycles": cycles,
                "parallel_groups": self._get_parallel_groups(levels)
            }
        )
    
    def _detect_cycles(self, nodes: Dict[str, DependencyNode]) -> List[List[str]]:
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str, path: List[str]) -> bool:
            if node_id in rec_stack:
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            if node_id in nodes:
                for dep in nodes[node_id].dependencies:
                    if dep in nodes:
                        dfs(dep, path.copy())
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in nodes:
            if node_id not in visited:
                dfs(node_id, [])
        
        return cycles
    
    def _topological_sort(self, nodes: Dict[str, DependencyNode]) -> List[str]:
        in_degree = defaultdict(int)
        for node in nodes.values():
            for dep in node.dependencies:
                if dep in nodes:
                    in_degree[node.id] += 1
        
        queue = [n for n in nodes if in_degree[n] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for node in nodes.values():
                if current in node.dependencies:
                    in_degree[node.id] -= 1
                    if in_degree[node.id] == 0 and node.id not in result:
                        queue.append(node.id)
        
        # Add any remaining (cycle members)
        for node_id in nodes:
            if node_id not in result:
                result.append(node_id)
        
        return result
    
    def _assign_levels(self, nodes: Dict[str, DependencyNode], order: List[str]) -> Dict[int, List[str]]:
        levels = defaultdict(list)
        node_levels = {}
        
        for node_id in order:
            if node_id not in nodes:
                continue
            node = nodes[node_id]
            
            # Level is max of dependencies + 1
            if not node.dependencies:
                level = 0
            else:
                dep_levels = [node_levels.get(d, 0) for d in node.dependencies if d in nodes]
                level = max(dep_levels) + 1 if dep_levels else 0
            
            node_levels[node_id] = level
            levels[level].append(node_id)
        
        return dict(levels)
    
    def _get_parallel_groups(self, levels: Dict[int, List[str]]) -> List[List[str]]:
        return [tasks for level, tasks in sorted(levels.items())]


def register(algorithm_manager):
    algo = DependencySolverAlgorithm()
    algorithm_manager.register("DependencySolver", algo)
    print("✅ DependencySolver registered")


if __name__ == "__main__":
    algo = DependencySolverAlgorithm()
    result = algo.execute({
        "tasks": [
            {"id": "A", "name": "Design", "dependencies": []},
            {"id": "B", "name": "Implement", "dependencies": ["A"]},
            {"id": "C", "name": "Test", "dependencies": ["B"]},
            {"id": "D", "name": "Deploy", "dependencies": ["C"]},
            {"id": "E", "name": "Docs", "dependencies": ["A"]}
        ]
    })
    print(f"Order: {result.data['execution_order']}")
