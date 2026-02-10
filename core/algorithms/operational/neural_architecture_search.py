"""
🧠 NEURAL ARCHITECTURE SEARCH (DNAS)
Dynamic Neural Architecture Search for optimal model selection

Based on V28's layer2_dynamicneuralarchitecturesearch.py + dnas/
"""

import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class ModelArchitecture:
    """Model architecture configuration"""
    name: str
    params: int  # Parameters count
    layers: int
    context_window: int
    strengths: List[str]
    cost_per_token: float
    latency_ms: float
    quality_score: float  # 0-1


class NeuralArchitectureSearchAlgorithm(BaseAlgorithm):
    """
    🧠 Dynamic Neural Architecture Search (DNAS)
    
    Automatically selects optimal model architecture based on:
    - Task complexity
    - Latency requirements
    - Cost constraints
    - Quality needs
    
    From V28: DNAS module (10/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="NeuralArchitectureSearch",
            name="Neural Architecture Search (DNAS)",
            level="operational",
            category="optimization",
            version="1.0",
            description="Optimal model selection for tasks",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("task", "string", True, "Task description"),
                    IOField("constraints", "object", False, "Latency/cost/quality constraints")
                ],
                outputs=[
                    IOField("selected_model", "object", True, "Best model"),
                    IOField("alternatives", "array", True, "Alternative models")
                ]
            ),
            steps=["Analyze task", "Evaluate architectures", "Rank by fitness", "Select optimal"],
            tags=["dnas", "optimization", "model-selection"]
        )
        
        # Available architectures
        self.architectures = [
            ModelArchitecture("claude-opus-4.6", 200_000_000_000, 96, 200000, 
                            ["reasoning", "coding", "planning"], 0.015, 2000, 0.98),
            ModelArchitecture("gpt-5.2-codex", 175_000_000_000, 96, 128000,
                            ["coding", "review", "debugging"], 0.008, 1500, 0.95),
            ModelArchitecture("glm-4.6v", 130_000_000_000, 64, 128000,
                            ["multimodal", "vision", "frontend"], 0.003, 800, 0.90),
            ModelArchitecture("claude-sonnet-4", 70_000_000_000, 48, 200000,
                            ["balanced", "fast", "coding"], 0.003, 500, 0.88),
            ModelArchitecture("gpt-4o-mini", 8_000_000_000, 32, 128000,
                            ["fast", "cheap", "simple"], 0.0001, 200, 0.75),
        ]
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        task = params.get("task", "")
        constraints = params.get("constraints", {})
        
        if not task:
            return AlgorithmResult(status="error", error="No task provided")
        
        print(f"\n🧠 Neural Architecture Search (DNAS)")
        
        # Score each architecture
        scored = []
        for arch in self.architectures:
            score = self._evaluate_fitness(arch, task, constraints)
            scored.append((score, arch))
        
        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)
        
        best = scored[0][1]
        print(f"   Selected: {best.name} (score: {scored[0][0]:.2f})")
        
        return AlgorithmResult(
            status="success",
            data={
                "selected_model": self._arch_to_dict(best),
                "alternatives": [self._arch_to_dict(a) for _, a in scored[1:3]],
                "scores": {a.name: s for s, a in scored}
            }
        )
    
    def _evaluate_fitness(self, arch: ModelArchitecture, task: str, constraints: Dict) -> float:
        score = arch.quality_score * 100
        task_lower = task.lower()
        
        # Strength matching
        for strength in arch.strengths:
            if strength in task_lower:
                score += 20
        
        # Apply constraints
        max_latency = constraints.get("max_latency_ms", 5000)
        max_cost = constraints.get("max_cost_per_token", 0.1)
        min_quality = constraints.get("min_quality", 0.7)
        
        if arch.latency_ms > max_latency:
            score -= 30
        if arch.cost_per_token > max_cost:
            score -= 20
        if arch.quality_score < min_quality:
            score -= 40
        
        return max(0, score)
    
    def _arch_to_dict(self, arch: ModelArchitecture) -> Dict:
        return {
            "name": arch.name, "params": arch.params, "context_window": arch.context_window,
            "strengths": arch.strengths, "cost_per_token": arch.cost_per_token,
            "latency_ms": arch.latency_ms, "quality_score": arch.quality_score
        }


def register(algorithm_manager):
    algo = NeuralArchitectureSearchAlgorithm()
    algorithm_manager.register("NeuralArchitectureSearch", algo)
    print("✅ NeuralArchitectureSearch registered")


if __name__ == "__main__":
    algo = NeuralArchitectureSearchAlgorithm()
    result = algo.execute({"task": "Complex coding with code review", "constraints": {"max_latency_ms": 3000}})
    print(f"Result: {result.data['selected_model']['name']}")
