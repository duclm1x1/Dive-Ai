"""
Dive AI V29 - Hierarchical Task Decomposition with A* Selection
Upgrade from: task_decomposition.py

Features:
- A* heuristic for algorithm selection: f(A) = g(A) + h(A)
  - g(A): Historical cost from Memory V5
  - h(A): Estimated future cost based on task complexity
- 3-Tier decomposition: Strategy → Tactic → Operation
- Integration with Algorithm Suggester
- Memory-aware planning
"""

import os
import sys
import re
import heapq
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


# ==========================================
# DATA CLASSES
# ==========================================

@dataclass
class SubTask:
    """A decomposed sub-task"""
    id: int
    title: str
    description: str
    tier: str  # strategy, tactic, operation
    complexity: float  # 0.0 - 1.0
    dependencies: List[int] = field(default_factory=list)
    estimated_time: float = 0.0
    category: str = "general"
    parallelizable: bool = True
    suggested_algorithm: str = ""
    f_score: float = 0.0  # A* score
    g_score: float = 0.0  # Historical cost
    h_score: float = 0.0  # Heuristic estimate


@dataclass
class AlgorithmNode:
    """Node for A* search in algorithm space"""
    algorithm_id: str
    f_score: float  # f(A) = g(A) + h(A)
    g_score: float  # Historical cost
    h_score: float  # Estimated future cost
    parent: Optional[str] = None
    
    def __lt__(self, other):
        return self.f_score < other.f_score


@dataclass
class DecompositionPlan:
    """Complete decomposition plan"""
    request: str
    overall_complexity: float
    strategy_tasks: List[SubTask]
    tactic_tasks: List[SubTask]
    operation_tasks: List[SubTask]
    execution_order: List[int]
    estimated_total_time: float
    parallel_time: float
    algorithm_assignments: Dict[int, str]


# ==========================================
# A* ALGORITHM SELECTOR
# ==========================================

class AStarAlgorithmSelector:
    """
    A* based algorithm selection
    
    f(A) = g(A) + h(A)
    - g(A): Historical cost from past executions
    - h(A): Heuristic estimate based on task-algorithm fit
    """
    
    def __init__(self, memory=None):
        self.memory = memory
        self.algorithm_catalog = self._load_catalog()
    
    def _load_catalog(self) -> Dict[str, Dict]:
        """Load algorithm catalog with base costs"""
        return {
            # Strategy tier
            "DevelopWebApp": {"tier": "strategy", "base_cost": 0.3, "domains": ["web", "app"]},
            "AnalyzeData": {"tier": "strategy", "base_cost": 0.35, "domains": ["data", "analysis"]},
            "RefactorCodebase": {"tier": "strategy", "base_cost": 0.4, "domains": ["refactor", "code"]},
            "ConductResearch": {"tier": "strategy", "base_cost": 0.3, "domains": ["research", "learn"]},
            
            # Tactic tier
            "WritePythonCode": {"tier": "tactic", "base_cost": 0.2, "domains": ["python", "code"]},
            "DebugAndFix": {"tier": "tactic", "base_cost": 0.25, "domains": ["debug", "fix", "bug"]},
            "SearchAndSynthesize": {"tier": "tactic", "base_cost": 0.15, "domains": ["search", "find"]},
            "WriteTests": {"tier": "tactic", "base_cost": 0.2, "domains": ["test", "testing"]},
            "DocumentCode": {"tier": "tactic", "base_cost": 0.15, "domains": ["doc", "readme"]},
            "ReviewCode": {"tier": "tactic", "base_cost": 0.2, "domains": ["review", "quality"]},
            
            # Operation tier
            "CodeGenerator": {"tier": "operation", "base_cost": 0.1, "domains": ["generate", "code"]},
            "TestGenerator": {"tier": "operation", "base_cost": 0.1, "domains": ["test", "generate"]},
            "AdvancedSearch": {"tier": "operation", "base_cost": 0.08, "domains": ["search", "find"]},
            "LLMQuery": {"tier": "operation", "base_cost": 0.12, "domains": ["llm", "query", "ai"]},
            "FileOperation": {"tier": "operation", "base_cost": 0.05, "domains": ["file", "read", "write"]},
            "CommandExecution": {"tier": "operation", "base_cost": 0.08, "domains": ["command", "shell"]},
        }
    
    def calculate_g(self, algorithm_id: str) -> float:
        """
        Calculate g(A) - historical cost
        Based on past execution data
        """
        if self.memory:
            try:
                return self.memory.calculate_historical_cost(algorithm_id)
            except:
                pass
        
        # Default: base cost from catalog
        algo = self.algorithm_catalog.get(algorithm_id, {})
        return algo.get("base_cost", 0.5)
    
    def calculate_h(self, algorithm_id: str, task_text: str, complexity: float) -> float:
        """
        Calculate h(A) - heuristic future cost estimate
        Based on task-algorithm fit
        """
        algo = self.algorithm_catalog.get(algorithm_id, {})
        domains = algo.get("domains", [])
        
        # Domain match bonus (lower cost if matches)
        task_lower = task_text.lower()
        domain_match = sum(1 for d in domains if d in task_lower)
        domain_bonus = min(domain_match * 0.1, 0.3)
        
        # Complexity penalty
        complexity_cost = complexity * 0.3
        
        # Tier bonus (lower tier = less overhead)
        tier = algo.get("tier", "operation")
        tier_cost = {"strategy": 0.2, "tactic": 0.1, "operation": 0.05}.get(tier, 0.1)
        
        return max(0.1, complexity_cost + tier_cost - domain_bonus)
    
    def select_best_algorithm(
        self,
        task_text: str,
        complexity: float,
        tier_filter: Optional[str] = None
    ) -> Tuple[str, AlgorithmNode]:
        """
        Use A* to select best algorithm for task
        
        Returns:
            (algorithm_id, AlgorithmNode with scores)
        """
        candidates = []
        
        for algo_id, spec in self.algorithm_catalog.items():
            if tier_filter and spec["tier"] != tier_filter:
                continue
            
            g = self.calculate_g(algo_id)
            h = self.calculate_h(algo_id, task_text, complexity)
            f = g + h
            
            node = AlgorithmNode(
                algorithm_id=algo_id,
                f_score=f,
                g_score=g,
                h_score=h
            )
            heapq.heappush(candidates, node)
        
        if not candidates:
            return None, None
        
        best = heapq.heappop(candidates)
        return best.algorithm_id, best


# ==========================================
# HIERARCHICAL TASK DECOMPOSITION
# ==========================================

class HierarchicalTaskDecomposition(BaseAlgorithm):
    """
    📋 Hierarchical Task Decomposition with A* Selection
    
    Features:
    - 3-tier decomposition: Strategy → Tactic → Operation
    - A* algorithm selection for each subtask
    - Memory-aware planning using historical costs
    - Parallel execution optimization
    """
    
    def __init__(self, memory=None):
        self.spec = AlgorithmSpec(
            algorithm_id="HierarchicalTaskDecomposition",
            name="Hierarchical Task Decomposition",
            level="strategy",
            category="planning",
            version="2.0",
            description="Hierarchical task decomposition with A* algorithm selection",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("request", "string", True, "User request"),
                    IOField("context", "object", False, "Additional context"),
                    IOField("max_depth", "integer", False, "Max decomposition depth")
                ],
                outputs=[
                    IOField("plan", "object", True, "Decomposition plan"),
                    IOField("subtasks", "array", True, "List of subtasks"),
                    IOField("algorithm_assignments", "object", True, "Task to algorithm mapping")
                ]
            ),
            
            steps=[
                "1. Analyze request complexity",
                "2. Decompose into Strategy tier",
                "3. Break down into Tactic tier",
                "4. Expand to Operation tier",
                "5. Apply A* to select algorithms",
                "6. Build dependency graph",
                "7. Calculate execution order",
                "8. Return decomposition plan"
            ],
            
            tags=["decomposition", "planning", "hierarchical", "a*", "algorithm_selection"]
        )
        
        self.memory = memory
        self.a_star_selector = AStarAlgorithmSelector(memory)
        
        # Task patterns for decomposition
        self.strategy_patterns = {
            "web app": "DevelopWebApp",
            "website": "DevelopWebApp",
            "application": "DevelopWebApp",
            "analyze": "AnalyzeData",
            "data": "AnalyzeData",
            "refactor": "RefactorCodebase",
            "research": "ConductResearch",
            "learn": "ConductResearch"
        }
        
        self.tactic_patterns = {
            "python": "WritePythonCode",
            "code": "WritePythonCode",
            "debug": "DebugAndFix",
            "fix": "DebugAndFix",
            "bug": "DebugAndFix",
            "search": "SearchAndSynthesize",
            "find": "SearchAndSynthesize",
            "test": "WriteTests",
            "document": "DocumentCode",
            "review": "ReviewCode"
        }
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute hierarchical decomposition"""
        request = params.get("request", "")
        context = params.get("context", {})
        max_depth = params.get("max_depth", 3)
        
        try:
            # 1. Analyze complexity
            complexity = self._estimate_complexity(request)
            
            # 2. Decompose by tier
            strategy_tasks = self._decompose_strategy(request, complexity)
            tactic_tasks = self._decompose_tactics(request, strategy_tasks, complexity)
            operation_tasks = self._decompose_operations(request, tactic_tasks, complexity)
            
            # 3. Apply A* to select algorithms
            all_tasks = strategy_tasks + tactic_tasks + operation_tasks
            algorithm_assignments = self._assign_algorithms(all_tasks)
            
            # 4. Build dependency graph and execution order
            execution_order = self._calculate_execution_order(all_tasks)
            
            # 5. Calculate times
            total_time = sum(t.estimated_time for t in all_tasks)
            parallel_time = self._calculate_parallel_time(all_tasks, execution_order)
            
            # 6. Build result
            plan = DecompositionPlan(
                request=request,
                overall_complexity=complexity,
                strategy_tasks=strategy_tasks,
                tactic_tasks=tactic_tasks,
                operation_tasks=operation_tasks,
                execution_order=execution_order,
                estimated_total_time=total_time,
                parallel_time=parallel_time,
                algorithm_assignments=algorithm_assignments
            )
            
            return AlgorithmResult(
                status="success",
                data={
                    "plan": {
                        "request": plan.request,
                        "complexity": plan.overall_complexity,
                        "estimated_time": plan.estimated_total_time,
                        "parallel_time": plan.parallel_time,
                        "tier_counts": {
                            "strategy": len(strategy_tasks),
                            "tactic": len(tactic_tasks),
                            "operation": len(operation_tasks)
                        }
                    },
                    "subtasks": [self._task_to_dict(t) for t in all_tasks],
                    "algorithm_assignments": algorithm_assignments,
                    "execution_order": execution_order
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=str(e))
    
    def _estimate_complexity(self, request: str) -> float:
        """Estimate task complexity (0-1)"""
        words = request.split()
        
        # Base on length
        length_factor = min(len(words) / 30, 1.0)
        
        # Check for complexity indicators
        complex_keywords = ["full", "complete", "comprehensive", "production", "scale", "optimize"]
        complex_count = sum(1 for w in words if w.lower() in complex_keywords)
        
        # Multi-step indicators
        multi_keywords = ["and", "then", "also", "with", "including"]
        multi_count = sum(1 for w in words if w.lower() in multi_keywords)
        
        complexity = length_factor * 0.4 + min(complex_count * 0.15, 0.3) + min(multi_count * 0.1, 0.3)
        return min(complexity, 1.0)
    
    def _decompose_strategy(self, request: str, complexity: float) -> List[SubTask]:
        """Decompose into Strategy tier tasks"""
        tasks = []
        request_lower = request.lower()
        
        # Identify main strategy
        for pattern, strategy in self.strategy_patterns.items():
            if pattern in request_lower:
                task = SubTask(
                    id=len(tasks) + 1,
                    title=f"Strategy: {strategy}",
                    description=f"High-level approach using {strategy}",
                    tier="strategy",
                    complexity=complexity,
                    estimated_time=complexity * 30,  # minutes
                    category="strategy",
                    suggested_algorithm=strategy
                )
                tasks.append(task)
                break
        
        # If no specific strategy found, create generic one
        if not tasks:
            tasks.append(SubTask(
                id=1,
                title="Strategy: Generic Approach",
                description="General problem-solving strategy",
                tier="strategy",
                complexity=complexity,
                estimated_time=complexity * 20,
                category="strategy",
                suggested_algorithm="ConductResearch"
            ))
        
        return tasks
    
    def _decompose_tactics(
        self,
        request: str,
        strategy_tasks: List[SubTask],
        complexity: float
    ) -> List[SubTask]:
        """Decompose into Tactic tier tasks"""
        tasks = []
        request_lower = request.lower()
        base_id = max(t.id for t in strategy_tasks) if strategy_tasks else 0
        
        # Identify relevant tactics
        for pattern, tactic in self.tactic_patterns.items():
            if pattern in request_lower:
                task = SubTask(
                    id=base_id + len(tasks) + 1,
                    title=f"Tactic: {tactic}",
                    description=f"Mid-level action: {tactic}",
                    tier="tactic",
                    complexity=complexity * 0.7,
                    dependencies=[strategy_tasks[0].id] if strategy_tasks else [],
                    estimated_time=complexity * 15,
                    category="tactic",
                    suggested_algorithm=tactic
                )
                tasks.append(task)
        
        # Ensure at least one tactic
        if not tasks:
            tasks.append(SubTask(
                id=base_id + 1,
                title="Tactic: Execute Plan",
                description="Execute the strategy",
                tier="tactic",
                complexity=complexity * 0.6,
                dependencies=[strategy_tasks[0].id] if strategy_tasks else [],
                estimated_time=complexity * 10,
                category="tactic",
                suggested_algorithm="WritePythonCode"
            ))
        
        return tasks
    
    def _decompose_operations(
        self,
        request: str,
        tactic_tasks: List[SubTask],
        complexity: float
    ) -> List[SubTask]:
        """Decompose into Operation tier tasks"""
        tasks = []
        base_id = max(t.id for t in tactic_tasks) if tactic_tasks else 0
        
        # For each tactic, create supporting operations
        for tactic in tactic_tasks:
            # Code generation operation
            tasks.append(SubTask(
                id=base_id + len(tasks) + 1,
                title=f"Op: Generate for {tactic.title}",
                description="Generate code/content",
                tier="operation",
                complexity=complexity * 0.4,
                dependencies=[tactic.id],
                estimated_time=complexity * 5,
                category="operation",
                suggested_algorithm="CodeGenerator"
            ))
            
            # Verification operation
            tasks.append(SubTask(
                id=base_id + len(tasks) + 1,
                title=f"Op: Verify {tactic.title}",
                description="Verify output",
                tier="operation",
                complexity=complexity * 0.3,
                dependencies=[base_id + len(tasks)],  # Depends on generate
                estimated_time=complexity * 3,
                category="operation",
                suggested_algorithm="TestGenerator",
                parallelizable=False
            ))
        
        return tasks
    
    def _assign_algorithms(self, tasks: List[SubTask]) -> Dict[int, str]:
        """Use A* to assign best algorithm to each task"""
        assignments = {}
        
        for task in tasks:
            if task.suggested_algorithm:
                # Already has suggestion, validate with A*
                algo_id, node = self.a_star_selector.select_best_algorithm(
                    task.description,
                    task.complexity,
                    tier_filter=task.tier
                )
                
                if node:
                    task.f_score = node.f_score
                    task.g_score = node.g_score
                    task.h_score = node.h_score
                    assignments[task.id] = algo_id
                else:
                    assignments[task.id] = task.suggested_algorithm
            else:
                # Use A* to find best
                algo_id, node = self.a_star_selector.select_best_algorithm(
                    task.description,
                    task.complexity,
                    tier_filter=task.tier
                )
                
                if algo_id:
                    task.f_score = node.f_score
                    task.g_score = node.g_score
                    task.h_score = node.h_score
                    task.suggested_algorithm = algo_id
                    assignments[task.id] = algo_id
        
        return assignments
    
    def _calculate_execution_order(self, tasks: List[SubTask]) -> List[int]:
        """Calculate execution order using topological sort"""
        # Build adjacency list
        graph = {t.id: t.dependencies for t in tasks}
        in_degree = {t.id: len(t.dependencies) for t in tasks}
        
        # Kahn's algorithm
        order = []
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        
        while queue:
            current = queue.pop(0)
            order.append(current)
            
            for tid, deps in graph.items():
                if current in deps:
                    in_degree[tid] -= 1
                    if in_degree[tid] == 0:
                        queue.append(tid)
        
        return order
    
    def _calculate_parallel_time(self, tasks: List[SubTask], order: List[int]) -> float:
        """Calculate parallel execution time"""
        task_map = {t.id: t for t in tasks}
        finish_times = {}
        
        for tid in order:
            task = task_map.get(tid)
            if not task:
                continue
            
            # Start time is max finish time of dependencies
            start = max((finish_times.get(d, 0) for d in task.dependencies), default=0)
            finish_times[tid] = start + task.estimated_time
        
        return max(finish_times.values()) if finish_times else 0
    
    def _task_to_dict(self, task: SubTask) -> Dict:
        """Convert SubTask to dict"""
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "tier": task.tier,
            "complexity": task.complexity,
            "dependencies": task.dependencies,
            "estimated_time": task.estimated_time,
            "category": task.category,
            "parallelizable": task.parallelizable,
            "algorithm": task.suggested_algorithm,
            "scores": {
                "f": task.f_score,
                "g": task.g_score,
                "h": task.h_score
            }
        }


# ==========================================
# REGISTRATION
# ==========================================

def register(algorithm_manager):
    """Register Hierarchical Task Decomposition"""
    algo = HierarchicalTaskDecomposition()
    algorithm_manager.register("HierarchicalTaskDecomposition", algo)
    print("✅ HierarchicalTaskDecomposition registered (A* algorithm selection)")


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📋 HIERARCHICAL TASK DECOMPOSITION TEST")
    print("=" * 60)
    
    decomp = HierarchicalTaskDecomposition()
    
    # Test complex request
    result = decomp.execute({
        "request": "Build a complete web application with React frontend and Python backend, including user authentication, database, and deploy to production"
    })
    
    if result.status == "success":
        plan = result.data["plan"]
        print(f"\n📊 Decomposition Results:")
        print(f"   Complexity: {plan['complexity']:.2f}")
        print(f"   Estimated Time: {plan['estimated_time']:.1f} min")
        print(f"   Parallel Time: {plan['parallel_time']:.1f} min")
        print(f"   Tiers: Strategy={plan['tier_counts']['strategy']}, "
              f"Tactic={plan['tier_counts']['tactic']}, "
              f"Operation={plan['tier_counts']['operation']}")
        
        print(f"\n📋 Subtasks:")
        for task in result.data["subtasks"][:8]:
            deps = f" ← {task['dependencies']}" if task['dependencies'] else ""
            scores = task['scores']
            print(f"   {task['id']}. [{task['tier'][:3].upper()}] {task['title']}")
            print(f"      Algorithm: {task['algorithm']} | f={scores['f']:.2f} g={scores['g']:.2f} h={scores['h']:.2f}{deps}")
        
        print(f"\n📌 Execution Order: {result.data['execution_order'][:10]}...")
    else:
        print(f"Error: {result.error}")
    
    print("\n" + "=" * 60)
    print("✅ Hierarchical decomposition test completed!")
