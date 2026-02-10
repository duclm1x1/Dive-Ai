"""
🎭 MODEL ENSEMBLE
Combine multiple models for better results

Based on V28's vibe_engine/model_ensemble.py
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class EnsembleMethod(Enum):
    VOTING = "voting"
    AVERAGING = "averaging"
    WEIGHTED = "weighted"
    STACKING = "stacking"
    BEST_OF = "best_of"


@dataclass
class ModelResponse:
    """Response from a model"""
    model_id: str
    response: str
    confidence: float
    latency_ms: float


class ModelEnsembleAlgorithm(BaseAlgorithm):
    """
    🎭 Model Ensemble
    
    Combines multiple models:
    - Parallel execution
    - Response aggregation
    - Confidence weighting
    - Best-of selection
    
    From V28: vibe_engine/model_ensemble.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ModelEnsemble",
            name="Model Ensemble",
            level="operational",
            category="llm",
            version="1.0",
            description="Combine multiple models for better results",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "query/configure"),
                    IOField("prompt", "string", False, "Prompt to send"),
                    IOField("method", "string", False, "Ensemble method")
                ],
                outputs=[
                    IOField("result", "object", True, "Ensemble result")
                ]
            ),
            steps=["Query all models", "Collect responses", "Apply ensemble method", "Return best"],
            tags=["ensemble", "models", "aggregation"]
        )
        
        self.models: List[str] = ["claude", "gpt", "gemini"]
        self.weights: Dict[str, float] = {"claude": 1.0, "gpt": 1.0, "gemini": 1.0}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "query")
        
        print(f"\n🎭 Model Ensemble")
        
        if action == "query":
            return self._query_ensemble(
                params.get("prompt", ""),
                EnsembleMethod(params.get("method", "voting"))
            )
        elif action == "configure":
            return self._configure(params.get("models", []), params.get("weights", {}))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _query_ensemble(self, prompt: str, method: EnsembleMethod) -> AlgorithmResult:
        if not prompt:
            return AlgorithmResult(status="error", error="No prompt provided")
        
        # Simulate model responses
        responses = self._simulate_responses(prompt)
        
        # Apply ensemble method
        if method == EnsembleMethod.VOTING:
            result = self._voting_ensemble(responses)
        elif method == EnsembleMethod.AVERAGING:
            result = self._averaging_ensemble(responses)
        elif method == EnsembleMethod.WEIGHTED:
            result = self._weighted_ensemble(responses)
        elif method == EnsembleMethod.BEST_OF:
            result = self._best_of_ensemble(responses)
        else:
            result = self._voting_ensemble(responses)
        
        print(f"   Method: {method.value}, Models: {len(responses)}")
        
        return AlgorithmResult(
            status="success",
            data={
                "final_response": result["response"],
                "confidence": result["confidence"],
                "method": method.value,
                "model_count": len(responses),
                "individual_responses": [
                    {"model": r.model_id, "confidence": r.confidence}
                    for r in responses
                ]
            }
        )
    
    def _simulate_responses(self, prompt: str) -> List[ModelResponse]:
        """Simulate responses from different models"""
        responses = []
        
        # Simulate varying responses and confidences
        for i, model in enumerate(self.models):
            responses.append(ModelResponse(
                model_id=model,
                response=f"Response from {model}: {prompt[:50]}...",
                confidence=0.7 + (i * 0.05),  # Varying confidence
                latency_ms=100 + (i * 50)
            ))
        
        return responses
    
    def _voting_ensemble(self, responses: List[ModelResponse]) -> Dict:
        # In real impl, would compare semantic similarity
        # Here, pick response with highest confidence
        best = max(responses, key=lambda r: r.confidence)
        return {"response": best.response, "confidence": best.confidence}
    
    def _averaging_ensemble(self, responses: List[ModelResponse]) -> Dict:
        avg_confidence = sum(r.confidence for r in responses) / len(responses)
        # Combine responses (simplified)
        combined = " | ".join(r.response[:50] for r in responses)
        return {"response": combined, "confidence": avg_confidence}
    
    def _weighted_ensemble(self, responses: List[ModelResponse]) -> Dict:
        total_weight = sum(self.weights.get(r.model_id, 1.0) * r.confidence for r in responses)
        weights_sum = sum(self.weights.get(r.model_id, 1.0) for r in responses)
        
        weighted_confidence = total_weight / weights_sum if weights_sum > 0 else 0
        
        # Pick highest weighted response
        best = max(responses, key=lambda r: self.weights.get(r.model_id, 1.0) * r.confidence)
        return {"response": best.response, "confidence": weighted_confidence}
    
    def _best_of_ensemble(self, responses: List[ModelResponse]) -> Dict:
        best = max(responses, key=lambda r: r.confidence)
        return {"response": best.response, "confidence": best.confidence}
    
    def _configure(self, models: List[str], weights: Dict[str, float]) -> AlgorithmResult:
        if models:
            self.models = models
        if weights:
            self.weights.update(weights)
        
        return AlgorithmResult(
            status="success",
            data={"models": self.models, "weights": self.weights}
        )


def register(algorithm_manager):
    algo = ModelEnsembleAlgorithm()
    algorithm_manager.register("ModelEnsemble", algo)
    print("✅ ModelEnsemble registered")


if __name__ == "__main__":
    algo = ModelEnsembleAlgorithm()
    result = algo.execute({
        "action": "query",
        "prompt": "Explain the concept of recursion",
        "method": "weighted"
    })
    print(f"Confidence: {result.data['confidence']:.2f}")
