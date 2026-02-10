"""
📋 TASK DECOMPOSITION ALGORITHM (PTD)
Parallel Task Decomposition - Break complex tasks into manageable sub-tasks

Based on V28's layer1_paralleltaskdecomposition.py + Prompt Template Design
"""

import os
import sys
import re
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


@dataclass
class SubTask:
    """A decomposed sub-task"""
    id: int
    title: str
    description: str
    complexity: float  # 0.0 - 1.0
    dependencies: List[int] = field(default_factory=list)
    estimated_time: float = 0.0  # minutes
    category: str = "general"
    parallelizable: bool = True


class TaskDecompositionAlgorithm(BaseAlgorithm):
    """
    📋 Task Decomposition Algorithm (PTD)
    
    Breaks complex user requests into parallel, manageable sub-tasks.
    
    Features:
    - Identifies task complexity
    - Creates hierarchical decomposition
    - Detects dependencies
    - Enables parallel execution
    - Estimates completion time
    
    From V28: Prompt Template Design (PTD) + Parallel Task Decomposition
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="TaskDecomposition",
            name="Task Decomposition (PTD)",
            level="operational",
            category="planning",
            version="1.0",
            description="Break complex tasks into parallel sub-tasks",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("request", "string", True, "User request to decompose"),
                    IOField("max_depth", "integer", False, "Max decomposition depth (default: 3)"),
                    IOField("target_complexity", "number", False, "Target sub-task complexity (default: 0.3)")
                ],
                outputs=[
                    IOField("subtasks", "array", True, "List of decomposed sub-tasks"),
                    IOField("dependency_graph", "object", True, "Task dependency graph"),
                    IOField("total_estimated_time", "number", True, "Total estimated time")
                ]
            ),
            
            steps=[
                "1. Analyze request complexity",
                "2. Identify main components",
                "3. Break into sub-tasks recursively",
                "4. Detect dependencies between tasks",
                "5. Mark parallelizable tasks",
                "6. Estimate completion time",
                "7. Create execution plan"
            ],
            
            tags=["decomposition", "planning", "ptd", "parallel"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute task decomposition"""
        request = params.get("request", "")
        max_depth = params.get("max_depth", 3)
        target_complexity = params.get("target_complexity", 0.3)
        
        if not request:
            return AlgorithmResult(status="error", error="No request provided")
        
        print(f"\n📋 Task Decomposition (PTD)")
        print(f"   Request: {request[:80]}...")
        
        # Step 1: Analyze complexity
        overall_complexity = self._estimate_complexity(request)
        print(f"   Overall complexity: {overall_complexity:.2f}")
        
        # Step 2: Decompose
        subtasks = self._decompose_recursive(
            request, 
            current_depth=0,
            max_depth=max_depth,
            target_complexity=target_complexity
        )
        
        print(f"   Decomposed into {len(subtasks)} sub-tasks")
        
        # Step 3: Detect dependencies
        dependency_graph = self._detect_dependencies(subtasks)
        
        # Step 4: Estimate time
        total_time = sum(st.estimated_time for st in subtasks)
        parallel_time = self._calculate_parallel_time(subtasks, dependency_graph)
        
        print(f"   Estimated time: {total_time:.1f}min sequential, {parallel_time:.1f}min parallel")
        
        return AlgorithmResult(
            status="success",
            data={
                "subtasks": [self._subtask_to_dict(st) for st in subtasks],
                "dependency_graph": dependency_graph,
                "total_estimated_time": total_time,
                "parallel_estimated_time": parallel_time,
                "overall_complexity": overall_complexity,
                "parallelizable_count": sum(1 for st in subtasks if st.parallelizable)
            }
        )
    
    def _estimate_complexity(self, request: str) -> float:
        """Estimate task complexity (0.0 - 1.0)"""
        keywords_complex = [
            "create", "build", "develop", "implement", "design",
            "architecture", "system", "full", "complete", "entire"
        ]
        keywords_moderate = [
            "add", "update", "modify", "fix", "improve",
            "refactor", "optimize", "test"
        ]
        keywords_simple = [
            "show", "list", "get", "fetch", "display",
            "view", "check", "verify"
        ]
        
        request_lower = request.lower()
        
        # Count keyword matches
        complex_score = sum(1 for kw in keywords_complex if kw in request_lower)
        moderate_score = sum(1 for kw in keywords_moderate if kw in request_lower)
        simple_score = sum(1 for kw in keywords_simple if kw in request_lower)
        
        # Length factor
        length_factor = min(len(request) / 500, 1.0)
        
        # Combine scores
        if complex_score > 0:
            base_complexity = 0.7 + (complex_score * 0.1)
        elif moderate_score > 0:
            base_complexity = 0.4 + (moderate_score * 0.1)
        else:
            base_complexity = 0.2 + (simple_score * 0.05)
        
        return min(base_complexity + length_factor * 0.2, 1.0)
    
    def _decompose_recursive(self, task_text: str, current_depth: int, 
                            max_depth: int, target_complexity: float) -> List[SubTask]:
        """Recursively decompose task"""
        subtasks = []
        
        # Base case: max depth or already simple enough
        complexity = self._estimate_complexity(task_text)
        if current_depth >= max_depth or complexity <= target_complexity:
            subtasks.append(SubTask(
                id=len(subtasks) + 1,
                title=task_text[:50],
                description=task_text,
                complexity=complexity,
                estimated_time=self._estimate_time(task_text, complexity),
                category=self._categorize(task_text)
            ))
            return subtasks
        
        # Decompose based on patterns
        components = self._identify_components(task_text)
        
        for idx, component in enumerate(components):
            # Recursively decompose each component
            sub_subtasks = self._decompose_recursive(
                component,
                current_depth + 1,
                max_depth,
                target_complexity
            )
            
            # Renumber IDs
            for st in sub_subtasks:
                st.id = len(subtasks) + 1
                subtasks.append(st)
        
        return subtasks if subtasks else [SubTask(
            id=1,
            title=task_text[:50],
            description=task_text,
            complexity=complexity,
            estimated_time=self._estimate_time(task_text, complexity),
            category=self._categorize(task_text)
        )]
    
    def _identify_components(self, task_text: str) -> List[str]:
        """Identify task components"""
        task_lower = task_text.lower()
        
        # Pattern 1: "Create X, Y, and Z"
        if " and " in task_lower and ("create" in task_lower or "build" in task_lower):
            parts = re.split(r',\s*and\s+|,\s+|\s+and\s+', task_text)
            if len(parts) > 1:
                return parts
        
        # Pattern 2: "Do A. Do B. Do C."
        sentences = re.split(r'\.\s+', task_text)
        if len(sentences) > 2:
            return sentences
        
        # Pattern 3: Numbered/bulleted lists
        if re.search(r'\d+\.\s+', task_text):
            items = re.split(r'\d+\.\s+', task_text)
            return [item.strip() for item in items if item.strip()]
        
        # Pattern 4: Detect sub-tasks by action verbs
        action_verbs = ["create", "build", "implement", "add", "setup", "configure", "test"]
        components = []
        for verb in action_verbs:
            pattern = f"({verb}[^.]+)"
            matches = re.findall(pattern, task_lower)
            if matches:
                components.extend(matches)
        
        if components:
            return components[:5]  # Limit to 5 components
        
        # Default: split by length
        if len(task_text) > 200:
            mid = len(task_text) // 2
            return [task_text[:mid], task_text[mid:]]
        
        return [task_text]
    
    def _estimate_time(self, task_text: str, complexity: float) -> float:
        """Estimate completion time in minutes"""
        # Base time from complexity
        base_time = complexity * 30  # Max 30 minutes per task
        
        # Adjust for specific keywords
        if "create" in task_text.lower() or "build" in task_text.lower():
            base_time *= 1.5
        if "test" in task_text.lower():
            base_time *= 1.2
        if "simple" in task_text.lower() or "quick" in task_text.lower():
            base_time *= 0.5
        
        return max(base_time, 1.0)  # Minimum 1 minute
    
    def _categorize(self, task_text: str) -> str:
        """Categorize task"""
        task_lower = task_text.lower()
        
        if any(kw in task_lower for kw in ["code", "implement", "function", "class"]):
            return "coding"
        elif any(kw in task_lower for kw in ["test", "verify", "check"]):
            return "testing"
        elif any(kw in task_lower for kw in ["design", "architecture", "plan"]):
            return "design"
        elif any(kw in task_lower for kw in ["doc", "documentation", "readme"]):
            return "documentation"
        elif any(kw in task_lower for kw in ["setup", "install", "configure"]):
            return "setup"
        else:
            return "general"
    
    def _detect_dependencies(self, subtasks: List[SubTask]) -> Dict[int, List[int]]:
        """Detect dependencies between subtasks"""
        graph = {}
        
        for i, task_a in enumerate(subtasks):
            dependencies = []
            
            for j, task_b in enumerate(subtasks):
                if i == j:
                    continue
                
                # Heuristic: if task A mentions task B's category/title
                if (task_b.category in task_a.description.lower() or
                    any(word in task_a.description.lower() 
                        for word in task_b.title.lower().split()[:3])):
                    dependencies.append(task_b.id)
            
            # Category-based dependencies
            if task_a.category == "testing":
                # Testing depends on coding
                coding_tasks = [st.id for st in subtasks if st.category == "coding" and st.id != task_a.id]
                dependencies.extend(coding_tasks)
            
            if task_a.category == "documentation":
                # Docs depend on implementation
                impl_tasks = [st.id for st in subtasks 
                             if st.category in ["coding", "design"] and st.id != task_a.id]
                dependencies.extend(impl_tasks[:2])  # Limit dependencies
            
            task_a.dependencies = list(set(dependencies))
            graph[task_a.id] = task_a.dependencies
            
            # Mark as non-parallelizable if has dependencies
            if dependencies:
                task_a.parallelizable = False
        
        return graph
    
    def _calculate_parallel_time(self, subtasks: List[SubTask], graph: Dict) -> float:
        """Calculate time if tasks run in parallel"""
        # Simple heuristic: max path length in dependency graph
        # This is a simplified critical path calculation
        
        if not subtasks:
            return 0.0
        
        # Tasks with no dependencies can run immediately
        independent = [st for st in subtasks if not st.dependencies]
        dependent = [st for st in subtasks if st.dependencies]
        
        if not dependent:
            # All parallel
            return max(st.estimated_time for st in subtasks) if subtasks else 0.0
        
        # Sequential path through dependencies (simplified)
        max_sequential_time = sum(st.estimated_time for st in dependent)
        max_parallel_time = max(st.estimated_time for st in independent) if independent else 0.0
        
        return max_sequential_time + max_parallel_time
    
    def _subtask_to_dict(self, subtask: SubTask) -> Dict:
        """Convert SubTask to dict"""
        return {
            "id": subtask.id,
            "title": subtask.title,
            "description": subtask.description,
            "complexity": subtask.complexity,
            "dependencies": subtask.dependencies,
            "estimated_time": subtask.estimated_time,
            "category": subtask.category,
            "parallelizable": subtask.parallelizable
        }


def register(algorithm_manager):
    """Register Task Decomposition Algorithm"""
    algo = TaskDecompositionAlgorithm()
    algorithm_manager.register("TaskDecomposition", algo)
    print("✅ TaskDecomposition Algorithm registered")


# ========================================
# TEST
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📋 TASK DECOMPOSITION TEST")
    print("="*60)
    
    algo = TaskDecompositionAlgorithm()
    
    result = algo.execute({
        "request": "Create a full-stack React todo app with authentication, database, and testing",
        "max_depth": 2,
        "target_complexity": 0.4
    })
    
    print(f"\n📊 Result: {result.status}")
    if result.status == "success":
        print(f"   Sub-tasks: {len(result.data['subtasks'])}")
        print(f"   Parallelizable: {result.data['parallelizable_count']}")
        print(f"\n   Tasks:")
        for st in result.data['subtasks'][:5]:
            deps = f" (depends on {st['dependencies']})" if st['dependencies'] else ""
            print(f"   {st['id']}. [{st['category']}] {st['title']}{deps}")
    
    print("\n" + "="*60)
