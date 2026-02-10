"""
📝 USER FEEDBACK LEARNING (UFBL)
Learn from user feedback to improve responses

Based on V28's layer6_userfeedbackbasedlearning.py + ufbl/
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class FeedbackType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"


@dataclass
class FeedbackEntry:
    """A user feedback entry"""
    id: str
    feedback_type: FeedbackType
    context: str
    response: str
    correction: str = ""
    score: float = 0.0
    timestamp: float = 0.0


class FeedbackLearningAlgorithm(BaseAlgorithm):
    """
    📝 User Feedback-Based Learning (UFBL)
    
    Improves from user feedback:
    - Rating-based learning
    - Correction learning
    - Preference modeling
    - Quality calibration
    
    From V28: UFBL module (8/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="FeedbackLearning",
            name="Feedback Learning (UFBL)",
            level="operational",
            category="learning",
            version="1.0",
            description="Learn from user feedback",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "record/analyze/apply"),
                    IOField("feedback", "object", False, "Feedback entry")
                ],
                outputs=[
                    IOField("result", "object", True, "Feedback learning result")
                ]
            ),
            steps=["Record feedback", "Analyze patterns", "Extract improvements", "Apply learnings"],
            tags=["feedback", "user", "learning", "improvement"]
        )
        
        self.feedback_log: List[FeedbackEntry] = []
        self.learned_preferences: Dict[str, float] = {}
        self.corrections_applied: int = 0
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "record")
        
        print(f"\n📝 Feedback Learning (UFBL)")
        
        if action == "record":
            return self._record_feedback(params.get("feedback", {}))
        elif action == "analyze":
            return self._analyze_feedback()
        elif action == "apply":
            return self._apply_learnings(params.get("context", {}))
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _record_feedback(self, data: Dict) -> AlgorithmResult:
        entry = FeedbackEntry(
            id=f"fb_{len(self.feedback_log)}",
            feedback_type=FeedbackType(data.get("type", "positive")),
            context=data.get("context", ""),
            response=data.get("response", ""),
            correction=data.get("correction", ""),
            score=data.get("score", 0.5),
            timestamp=time.time()
        )
        self.feedback_log.append(entry)
        
        # Immediate learning for corrections
        if entry.feedback_type == FeedbackType.CORRECTION and entry.correction:
            self._learn_from_correction(entry)
        
        print(f"   Recorded: {entry.feedback_type.value} feedback")
        
        return AlgorithmResult(
            status="success",
            data={"recorded": entry.id, "total_feedback": len(self.feedback_log)}
        )
    
    def _learn_from_correction(self, entry: FeedbackEntry):
        # Extract pattern from correction
        words = entry.correction.lower().split()
        for word in words:
            if len(word) > 4:
                self.learned_preferences[word] = self.learned_preferences.get(word, 0) + 1
        self.corrections_applied += 1
    
    def _analyze_feedback(self) -> AlgorithmResult:
        if not self.feedback_log:
            return AlgorithmResult(
                status="success",
                data={"analysis": "No feedback to analyze"}
            )
        
        # Analyze by type
        by_type = {}
        for entry in self.feedback_log:
            t = entry.feedback_type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        # Calculate metrics
        total = len(self.feedback_log)
        positive_rate = by_type.get("positive", 0) / total
        avg_score = sum(e.score for e in self.feedback_log) / total
        
        # Recent trend
        recent = self.feedback_log[-10:]
        recent_avg = sum(e.score for e in recent) / len(recent) if recent else 0
        trend = "improving" if recent_avg > avg_score else "stable" if recent_avg == avg_score else "declining"
        
        print(f"   Analysis: {positive_rate:.1%} positive, trend: {trend}")
        
        return AlgorithmResult(
            status="success",
            data={
                "total_feedback": total,
                "by_type": by_type,
                "positive_rate": positive_rate,
                "average_score": avg_score,
                "recent_average": recent_avg,
                "trend": trend,
                "top_preferences": dict(sorted(self.learned_preferences.items(), key=lambda x: -x[1])[:10])
            }
        )
    
    def _apply_learnings(self, context: Dict) -> AlgorithmResult:
        # Apply learned preferences
        adjustments = []
        
        context_text = context.get("text", "").lower()
        for pref, weight in self.learned_preferences.items():
            if weight > 2 and pref in context_text:
                adjustments.append({"preference": pref, "weight": weight})
        
        return AlgorithmResult(
            status="success",
            data={
                "adjustments_applied": len(adjustments),
                "adjustments": adjustments,
                "learned_from": len(self.feedback_log)
            }
        )
    
    def _get_stats(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "total_feedback": len(self.feedback_log),
                "corrections_applied": self.corrections_applied,
                "preferences_learned": len(self.learned_preferences),
                "average_score": sum(e.score for e in self.feedback_log) / len(self.feedback_log) if self.feedback_log else 0
            }
        )


def register(algorithm_manager):
    algo = FeedbackLearningAlgorithm()
    algorithm_manager.register("FeedbackLearning", algo)
    print("✅ FeedbackLearning registered")


if __name__ == "__main__":
    algo = FeedbackLearningAlgorithm()
    algo.execute({"action": "record", "feedback": {"type": "positive", "score": 0.9}})
    algo.execute({"action": "record", "feedback": {"type": "correction", "correction": "Use shorter variable names"}})
    result = algo.execute({"action": "analyze"})
    print(f"Positive rate: {result.data['positive_rate']:.1%}")
