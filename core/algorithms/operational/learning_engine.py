"""
🧠 LEARNING ENGINE
Continuous learning from interactions

Based on V28's vibe_engine/learning_engine.py
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
class LearningEntry:
    """A learning entry"""
    id: str
    category: str
    insight: str
    confidence: float
    source: str
    timestamp: float


class LearningEngineAlgorithm(BaseAlgorithm):
    """
    🧠 Learning Engine
    
    Continuous learning system:
    - Pattern extraction
    - Insight generation
    - Knowledge consolidation
    - Skill improvement
    
    From V28: vibe_engine/learning_engine.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="LearningEngine",
            name="Learning Engine",
            level="operational",
            category="learning",
            version="1.0",
            description="Continuous learning from interactions",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "learn/recall/consolidate"),
                    IOField("data", "object", False, "Data to learn from")
                ],
                outputs=[
                    IOField("result", "object", True, "Learning result")
                ]
            ),
            steps=["Extract patterns", "Generate insights", "Store knowledge", "Improve"],
            tags=["learning", "continuous", "improvement"]
        )
        
        self.entries: List[LearningEntry] = []
        self.categories: Dict[str, int] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "learn")
        
        print(f"\n🧠 Learning Engine")
        
        if action == "learn":
            return self._learn(params.get("data", {}))
        elif action == "recall":
            return self._recall(params.get("query", ""))
        elif action == "consolidate":
            return self._consolidate()
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _learn(self, data: Dict) -> AlgorithmResult:
        category = data.get("category", "general")
        insight = data.get("insight", "")
        
        if not insight:
            # Extract insight from data
            insight = str(data)[:200]
        
        entry = LearningEntry(
            id=f"learn_{len(self.entries)}",
            category=category,
            insight=insight,
            confidence=data.get("confidence", 0.7),
            source=data.get("source", "interaction"),
            timestamp=time.time()
        )
        self.entries.append(entry)
        self.categories[category] = self.categories.get(category, 0) + 1
        
        print(f"   Learned: {category}")
        
        return AlgorithmResult(
            status="success",
            data={"learned": entry.id, "total_entries": len(self.entries)}
        )
    
    def _recall(self, query: str) -> AlgorithmResult:
        if not query:
            # Return recent learnings
            recent = self.entries[-10:]
            return AlgorithmResult(
                status="success",
                data={"results": [{"id": e.id, "insight": e.insight} for e in recent]}
            )
        
        # Search
        query_lower = query.lower()
        matches = [
            e for e in self.entries
            if query_lower in e.insight.lower() or query_lower in e.category.lower()
        ]
        
        return AlgorithmResult(
            status="success",
            data={"results": [{"id": e.id, "insight": e.insight, "category": e.category} for e in matches[:10]]}
        )
    
    def _consolidate(self) -> AlgorithmResult:
        """Consolidate learnings into patterns"""
        patterns = {}
        
        for entry in self.entries:
            if entry.category not in patterns:
                patterns[entry.category] = {"count": 0, "high_confidence": 0}
            patterns[entry.category]["count"] += 1
            if entry.confidence > 0.8:
                patterns[entry.category]["high_confidence"] += 1
        
        return AlgorithmResult(
            status="success",
            data={"patterns": patterns, "total_entries": len(self.entries)}
        )
    
    def _get_stats(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "total_entries": len(self.entries),
                "categories": self.categories,
                "avg_confidence": sum(e.confidence for e in self.entries) / len(self.entries) if self.entries else 0
            }
        )


def register(algorithm_manager):
    algo = LearningEngineAlgorithm()
    algorithm_manager.register("LearningEngine", algo)
    print("✅ LearningEngine registered")


if __name__ == "__main__":
    algo = LearningEngineAlgorithm()
    algo.execute({"action": "learn", "data": {"category": "coding", "insight": "Use type hints for clarity"}})
    algo.execute({"action": "learn", "data": {"category": "coding", "insight": "Write tests first"}})
    result = algo.execute({"action": "recall", "query": "coding"})
    print(f"Found: {len(result.data['results'])} learnings")
