"""
📊 RESPONSE RANKER
Rank and filter model responses by quality

Based on V28's vibe_engine/response_ranker.py
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class RankedResponse:
    """A ranked response"""
    id: str
    content: str
    scores: Dict[str, float]
    total_score: float
    rank: int = 0


class ResponseRankerAlgorithm(BaseAlgorithm):
    """
    📊 Response Ranker
    
    Ranks responses by quality:
    - Multi-criteria scoring
    - Quality filtering
    - Best response selection
    - Confidence calibration
    
    From V28: vibe_engine/response_ranker.py
    """
    
    CRITERIA = ["relevance", "completeness", "clarity", "accuracy", "helpfulness"]
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ResponseRanker",
            name="Response Ranker",
            level="operational",
            category="evaluation",
            version="1.0",
            description="Rank and filter model responses",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("responses", "array", True, "Responses to rank"),
                    IOField("query", "string", False, "Original query for relevance"),
                    IOField("criteria", "array", False, "Custom criteria weights")
                ],
                outputs=[
                    IOField("ranked", "array", True, "Ranked responses")
                ]
            ),
            steps=["Score each response", "Apply weights", "Rank", "Filter"],
            tags=["ranking", "quality", "evaluation", "responses"]
        )
        
        self.weights: Dict[str, float] = {c: 1.0 for c in self.CRITERIA}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        responses = params.get("responses", [])
        query = params.get("query", "")
        custom_weights = params.get("criteria", {})
        
        if not responses:
            return AlgorithmResult(status="error", error="No responses to rank")
        
        print(f"\n📊 Response Ranker")
        
        # Apply custom weights
        weights = {**self.weights, **custom_weights}
        
        # Score each response
        ranked = []
        for i, resp in enumerate(responses):
            content = resp if isinstance(resp, str) else resp.get("content", "")
            scores = self._score_response(content, query)
            
            # Calculate weighted total
            total = sum(scores[c] * weights.get(c, 1.0) for c in scores)
            
            ranked.append(RankedResponse(
                id=f"resp_{i}",
                content=content,
                scores=scores,
                total_score=total
            ))
        
        # Sort by total score
        ranked.sort(key=lambda r: r.total_score, reverse=True)
        
        # Assign ranks
        for i, r in enumerate(ranked):
            r.rank = i + 1
        
        print(f"   Ranked {len(ranked)} responses")
        
        return AlgorithmResult(
            status="success",
            data={
                "ranked": [
                    {
                        "rank": r.rank,
                        "id": r.id,
                        "total_score": round(r.total_score, 2),
                        "scores": r.scores,
                        "preview": r.content[:100]
                    }
                    for r in ranked
                ],
                "best": ranked[0].content if ranked else None,
                "best_score": ranked[0].total_score if ranked else 0
            }
        )
    
    def _score_response(self, content: str, query: str) -> Dict[str, float]:
        scores = {}
        
        # Relevance (based on query overlap)
        if query:
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            overlap = len(query_words & content_words) / len(query_words) if query_words else 0
            scores["relevance"] = min(1.0, overlap * 2)
        else:
            scores["relevance"] = 0.5
        
        # Completeness (based on length)
        word_count = len(content.split())
        scores["completeness"] = min(1.0, word_count / 100)
        
        # Clarity (simple heuristic - sentence structure)
        sentences = content.count('.') + content.count('!') + content.count('?')
        scores["clarity"] = min(1.0, sentences / 5) if sentences > 0 else 0.3
        
        # Accuracy (placeholder - would need fact-checking)
        scores["accuracy"] = 0.7  # Default moderate
        
        # Helpfulness (code blocks, examples, etc.)
        has_code = "```" in content or "    " in content
        has_examples = "example" in content.lower() or "e.g." in content.lower()
        scores["helpfulness"] = 0.5 + (0.25 if has_code else 0) + (0.25 if has_examples else 0)
        
        return scores


def register(algorithm_manager):
    algo = ResponseRankerAlgorithm()
    algorithm_manager.register("ResponseRanker", algo)
    print("✅ ResponseRanker registered")


if __name__ == "__main__":
    algo = ResponseRankerAlgorithm()
    result = algo.execute({
        "responses": [
            "Python is a programming language.",
            "Python is a versatile programming language known for its readability. For example, you can write 'print(hello)' to output text.",
            "Programming can be done with various languages including Python, Java, and JavaScript."
        ],
        "query": "What is Python?"
    })
    print(f"Best response score: {result.data['best_score']:.2f}")
