"""
Complexity Analyzer Algorithm
Analyze task complexity (1-10 scale)
"""

import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)

class ComplexityAnalyzerAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ComplexityAnalyzer",
            name="Complexity Analyzer",
            level="operational",
            category="routing",
            version="1.0",
            description="Analyze task complexity on 1-10 scale using heuristics.",
            io=AlgorithmIOSpec(
                inputs=[IOField("task", "string", True, "Task description")],
                outputs=[IOField("complexity", "integer", True, "1-10 complexity score"),
                        IOField("reasoning", "string", True, "Why this score"),
                        IOField("factors", "list", True, "Complexity factors")]
            ),
            steps=["Step 1: Extract keywords", "Step 2: Detect indicators",
                   "Step 3: Calculate score", "Step 4: Generate reasoning"],
            tags=["complexity", "analysis", "routing"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        task = params.get("task", "").lower()
        
        complexity = 5  # Default
        factors = []
        
        # Simple indicators
        if any(kw in task for kw in ["what", "define", "explain"]):
            complexity = 2
            factors.append("simple question")
        elif any(kw in task for kw in ["design", "architect", "system"]):
            complexity = 9
            factors.append("architecture/design")
        elif any(kw in task for kw in ["implement", "code", "build"]):
            complexity = 6
            factors.append("implementation task")
        
        reasoning = f"Complexity: {complexity}/10. Factors: {', '.join(factors) if factors else 'general task'}"
        
        return AlgorithmResult(status="success", data={
            "complexity": complexity,
            "reasoning": reasoning,
            "factors": factors
        })

def register(algorithm_manager):
    algorithm_manager.register("ComplexityAnalyzer", ComplexityAnalyzerAlgorithm())
    print("✅ ComplexityAnalyzer Algorithm registered")
