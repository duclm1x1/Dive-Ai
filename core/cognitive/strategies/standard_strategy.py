"""
Dive AI V29 - Standard Strategy
Generic Meta-Algorithm for handling standard requests

Features:
- Uses HierarchicalTaskDecomposition for planning
- Executes Tactic-tier algorithms for steps
- Self-corrects using GPA Scorer
"""

from typing import Dict, Any, List
import time

from core.cognitive.meta_algorithm_base import BaseMetaAlgorithm, WorkflowState
from core.algorithms.base_algorithm import AlgorithmSpec, AlgorithmIOSpec, IOField
from core.reasoning.hierarchical_decomposition import HierarchicalTaskDecomposition

# Import memory correctly
from core.memory_v2.memory_v5 import get_memory_v5, MemoryV5

class StandardStrategy(BaseMetaAlgorithm):
    """
    Standard Strategy: 
    A generic meta-algorithm that plans and executes using V29 components.
    """
    
    def __init__(self):
        super().__init__()
        self.decomposer = HierarchicalTaskDecomposition(self.memory)
        
        self.spec = AlgorithmSpec(
            algorithm_id="StandardStrategy",
            name="Standard Execution Strategy",
            level="strategy",
            category="general",
            version="1.0",
            description="Generic strategy that decomposes requests and executes them using best-fit algorithms",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("request", "string", True, "User request"),
                    IOField("context", "object", False, "Context")
                ],
                outputs=[
                    IOField("result", "object", True, "Execution key results")
                ]
            ),
            
            steps=[
                "1. Decompose request using HierarchicalTaskDecomposition",
                "2. Execute each subtask",
                "3. Aggregate results"
            ],
            
            tags=["strategy", "general", "planning", "decomposition", "build", "create", "app", "dev"]
        )
    
    def decompose(self, state: WorkflowState) -> List[Dict]:
        """
        Decomposes the goal into actionable steps using the Reasoning Engine
        """
        print(f"   🧠 Reasoning: Decomposing goal '{state.goal}'...")
        
        result = self.decomposer.execute({
            "request": state.goal,
            "context": state.context
        })
        
        if result.status != "success":
            print(f"   ❌ Decomposition failed: {result.error}")
            return []
            
        plan = result.data.get("subtasks", [])
        
        # Convert plan to workflow steps
        steps = []
        for task in plan:
            steps.append({
                "id": str(task["id"]),
                "title": task["title"],
                "type": "action",
                "algorithm": task.get("algorithm", "Unknown"),
                "params": {
                    "request": task["description"],
                    "context": state.context
                }
            })
            
        print(f"   📋 Plan created: {len(steps)} steps")
        return steps

    def step_action(self, step: Dict, state: WorkflowState) -> Any:
        """
        Execute an action step
        """
        algo_name = step.get("algorithm")
        print(f"      ⚙️ Executing: {algo_name}")
        
        # Simulate execution for now (until we connect to real AlgorithmManager)
        # In full system: AlgorithmManager.execute(algo_name, step["params"])
        
        time.sleep(0.5) # Simulate work
        
        return {
            "status": "success", 
            "output": f"Executed {algo_name} for {step['title']}"
        }

# Registration
def register(manager):
    algo = StandardStrategy()
    manager.register("StandardStrategy", algo)
