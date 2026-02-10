"""
🔗 CROSS-LAYER LEARNING
Learn from interactions between system layers

Based on V28's layer6_crosslayerlearning.py
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class LayerInteraction:
    """Interaction between layers"""
    source_layer: str
    target_layer: str
    interaction_type: str
    data: Dict
    success: bool
    latency_ms: float
    timestamp: float


class CrossLayerLearningAlgorithm(BaseAlgorithm):
    """
    🔗 Cross-Layer Learning
    
    Learns from layer interactions:
    - Inter-layer patterns
    - Bottleneck detection
    - Flow optimization
    - Feedback propagation
    
    From V28: layer6_crosslayerlearning.py
    """
    
    LAYERS = ["decomposition", "allocation", "context", "multiagent", "verification", "learning"]
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="CrossLayerLearning",
            name="Cross-Layer Learning",
            level="operational",
            category="learning",
            version="1.0",
            description="Learn from layer interactions",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "record/analyze/optimize"),
                    IOField("interaction", "object", False, "Interaction to record")
                ],
                outputs=[
                    IOField("result", "object", True, "Learning result")
                ]
            ),
            steps=["Record interaction", "Analyze patterns", "Identify bottlenecks", "Suggest optimizations"],
            tags=["cross-layer", "learning", "optimization"]
        )
        
        self.interactions: List[LayerInteraction] = []
        self.layer_stats: Dict[str, Dict] = {layer: {"calls": 0, "errors": 0, "total_latency": 0} for layer in self.LAYERS}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "analyze")
        
        print(f"\n🔗 Cross-Layer Learning")
        
        if action == "record":
            return self._record_interaction(params.get("interaction", {}))
        elif action == "analyze":
            return self._analyze_patterns()
        elif action == "optimize":
            return self._suggest_optimizations()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _record_interaction(self, data: Dict) -> AlgorithmResult:
        interaction = LayerInteraction(
            source_layer=data.get("source", ""),
            target_layer=data.get("target", ""),
            interaction_type=data.get("type", "call"),
            data=data.get("data", {}),
            success=data.get("success", True),
            latency_ms=data.get("latency_ms", 0),
            timestamp=time.time()
        )
        self.interactions.append(interaction)
        
        # Update stats
        for layer in [interaction.source_layer, interaction.target_layer]:
            if layer in self.layer_stats:
                self.layer_stats[layer]["calls"] += 1
                self.layer_stats[layer]["total_latency"] += interaction.latency_ms
                if not interaction.success:
                    self.layer_stats[layer]["errors"] += 1
        
        return AlgorithmResult(
            status="success",
            data={"recorded": True, "total_interactions": len(self.interactions)}
        )
    
    def _analyze_patterns(self) -> AlgorithmResult:
        if not self.interactions:
            return AlgorithmResult(status="success", data={"analysis": "No interactions recorded"})
        
        # Flow analysis
        flows = {}
        for inter in self.interactions:
            key = f"{inter.source_layer}->{inter.target_layer}"
            if key not in flows:
                flows[key] = {"count": 0, "errors": 0, "avg_latency": 0, "latencies": []}
            flows[key]["count"] += 1
            flows[key]["latencies"].append(inter.latency_ms)
            if not inter.success:
                flows[key]["errors"] += 1
        
        # Calculate averages
        for flow in flows.values():
            flow["avg_latency"] = sum(flow["latencies"]) / len(flow["latencies"]) if flow["latencies"] else 0
            del flow["latencies"]
        
        # Find bottlenecks (high latency)
        bottlenecks = [k for k, v in flows.items() if v["avg_latency"] > 100]
        
        # Error-prone paths
        error_paths = [k for k, v in flows.items() if v["errors"] / v["count"] > 0.1]
        
        return AlgorithmResult(
            status="success",
            data={
                "flows": flows,
                "bottlenecks": bottlenecks,
                "error_paths": error_paths,
                "layer_stats": self.layer_stats
            }
        )
    
    def _suggest_optimizations(self) -> AlgorithmResult:
        analysis = self._analyze_patterns().data
        suggestions = []
        
        # Suggest for bottlenecks
        for bottleneck in analysis.get("bottlenecks", []):
            suggestions.append({
                "target": bottleneck,
                "suggestion": "Consider caching or async processing",
                "priority": "high"
            })
        
        # Suggest for errors
        for error_path in analysis.get("error_paths", []):
            suggestions.append({
                "target": error_path,
                "suggestion": "Add retry logic or fallback handlers",
                "priority": "medium"
            })
        
        return AlgorithmResult(
            status="success",
            data={
                "suggestions": suggestions,
                "analyzed_interactions": len(self.interactions)
            }
        )


def register(algorithm_manager):
    algo = CrossLayerLearningAlgorithm()
    algorithm_manager.register("CrossLayerLearning", algo)
    print("✅ CrossLayerLearning registered")


if __name__ == "__main__":
    algo = CrossLayerLearningAlgorithm()
    algo.execute({"action": "record", "interaction": {"source": "decomposition", "target": "context", "latency_ms": 50}})
    algo.execute({"action": "record", "interaction": {"source": "context", "target": "verification", "latency_ms": 150}})
    result = algo.execute({"action": "analyze"})
    print(f"Bottlenecks: {result.data.get('bottlenecks', [])}")
