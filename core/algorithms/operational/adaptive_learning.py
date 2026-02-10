"""
🎓 ADAPTIVE LEARNING
Self-improving learning from execution results

Based on V28's layer6_adaptivelearning.py
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class LearningExample:
    """A learning example"""
    input_data: Dict
    output_data: Dict
    success: bool
    timestamp: float
    feedback_score: float = 0.0


@dataclass
class LearnedPattern:
    """A pattern learned from examples"""
    pattern_id: str
    pattern_type: str
    confidence: float
    examples_count: int
    last_updated: float


class AdaptiveLearningAlgorithm(BaseAlgorithm):
    """
    🎓 Adaptive Learning System
    
    Learns from execution to improve:
    - Pattern recognition
    - Parameter tuning
    - Strategy selection
    - Confidence calibration
    
    From V28: layer6_adaptivelearning.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AdaptiveLearning",
            name="Adaptive Learning",
            level="operational",
            category="learning",
            version="1.0",
            description="Self-improving learning from results",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "learn/predict/adjust"),
                    IOField("example", "object", False, "Learning example"),
                    IOField("query", "object", False, "Query for prediction")
                ],
                outputs=[
                    IOField("result", "object", True, "Learning result")
                ]
            ),
            steps=["Process example", "Update patterns", "Adjust weights", "Store learning"],
            tags=["learning", "adaptive", "self-improving"]
        )
        
        self.examples: List[LearningExample] = []
        self.patterns: Dict[str, LearnedPattern] = {}
        self.parameters: Dict[str, float] = {"learning_rate": 0.1, "decay": 0.99}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "learn")
        
        print(f"\n🎓 Adaptive Learning")
        
        if action == "learn":
            return self._learn(params.get("example", {}))
        elif action == "predict":
            return self._predict(params.get("query", {}))
        elif action == "adjust":
            return self._adjust_parameters(params.get("feedback", {}))
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _learn(self, example_data: Dict) -> AlgorithmResult:
        example = LearningExample(
            input_data=example_data.get("input", {}),
            output_data=example_data.get("output", {}),
            success=example_data.get("success", True),
            timestamp=time.time(),
            feedback_score=example_data.get("feedback", 0.5)
        )
        self.examples.append(example)
        
        # Extract pattern
        pattern_type = self._identify_pattern(example)
        if pattern_type:
            if pattern_type not in self.patterns:
                self.patterns[pattern_type] = LearnedPattern(
                    pattern_id=f"p_{len(self.patterns)}",
                    pattern_type=pattern_type,
                    confidence=0.5,
                    examples_count=0,
                    last_updated=time.time()
                )
            
            pattern = self.patterns[pattern_type]
            pattern.examples_count += 1
            pattern.confidence = min(0.99, pattern.confidence + self.parameters["learning_rate"] * (1 if example.success else -0.5))
            pattern.last_updated = time.time()
        
        print(f"   Learned from example ({len(self.examples)} total)")
        
        return AlgorithmResult(
            status="success",
            data={
                "learned": True,
                "pattern": pattern_type,
                "total_examples": len(self.examples),
                "total_patterns": len(self.patterns)
            }
        )
    
    def _identify_pattern(self, example: LearningExample) -> str:
        # Simple pattern identification
        input_keys = list(example.input_data.keys())
        if input_keys:
            return f"pattern_{input_keys[0]}"
        return "pattern_generic"
    
    def _predict(self, query: Dict) -> AlgorithmResult:
        if not self.patterns:
            return AlgorithmResult(
                status="success",
                data={"prediction": None, "confidence": 0, "reason": "No patterns learned"}
            )
        
        # Find best matching pattern
        best_pattern = max(self.patterns.values(), key=lambda p: p.confidence)
        
        # Generate prediction based on similar examples
        similar = [e for e in self.examples if e.success][-5:]
        
        prediction = {
            "recommended_action": "continue",
            "confidence": best_pattern.confidence,
            "based_on": len(similar)
        }
        
        return AlgorithmResult(
            status="success",
            data={
                "prediction": prediction,
                "confidence": best_pattern.confidence,
                "pattern_used": best_pattern.pattern_type
            }
        )
    
    def _adjust_parameters(self, feedback: Dict) -> AlgorithmResult:
        score = feedback.get("score", 0.5)
        
        # Adjust learning rate based on feedback
        if score > 0.7:
            self.parameters["learning_rate"] *= 1.1
        elif score < 0.3:
            self.parameters["learning_rate"] *= 0.9
        
        self.parameters["learning_rate"] = max(0.01, min(0.5, self.parameters["learning_rate"]))
        
        return AlgorithmResult(
            status="success",
            data={
                "adjusted": True,
                "new_parameters": self.parameters
            }
        )
    
    def _get_stats(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "total_examples": len(self.examples),
                "total_patterns": len(self.patterns),
                "success_rate": sum(1 for e in self.examples if e.success) / len(self.examples) if self.examples else 0,
                "parameters": self.parameters,
                "top_patterns": [
                    {"type": p.pattern_type, "confidence": p.confidence}
                    for p in sorted(self.patterns.values(), key=lambda x: -x.confidence)[:5]
                ]
            }
        )


def register(algorithm_manager):
    algo = AdaptiveLearningAlgorithm()
    algorithm_manager.register("AdaptiveLearning", algo)
    print("✅ AdaptiveLearning registered")


if __name__ == "__main__":
    algo = AdaptiveLearningAlgorithm()
    algo.execute({"action": "learn", "example": {"input": {"task": "code"}, "success": True}})
    algo.execute({"action": "learn", "example": {"input": {"task": "code"}, "success": True}})
    result = algo.execute({"action": "predict", "query": {"task": "code"}})
    print(f"Prediction confidence: {result.data['confidence']:.2f}")
