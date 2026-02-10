"""
🔄 SELF IMPROVER
Self-improvement through reflection and meta-learning

Based on V28's core_engine/self_improver.py
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
class ImprovementCandidate:
    """A potential improvement"""
    id: str
    category: str
    description: str
    expected_impact: float
    implementation_effort: str
    priority_score: float


class SelfImproverAlgorithm(BaseAlgorithm):
    """
    🔄 Self Improver
    
    Enables self-improvement:
    - Performance reflection
    - Weakness identification
    - Improvement suggestions
    - Meta-learning
    
    From V28: core_engine/self_improver.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="SelfImprover",
            name="Self Improver",
            level="operational",
            category="meta",
            version="1.0",
            description="Self-improvement through reflection",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "reflect/identify/suggest/apply"),
                    IOField("performance_data", "object", False, "Performance data to analyze")
                ],
                outputs=[
                    IOField("result", "object", True, "Improvement result")
                ]
            ),
            steps=["Collect performance", "Analyze weaknesses", "Generate improvements", "Prioritize"],
            tags=["self-improvement", "meta-learning", "reflection"]
        )
        
        self.performance_history: List[Dict] = []
        self.improvements: List[ImprovementCandidate] = []
        self.applied_improvements: List[str] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "reflect")
        
        print(f"\n🔄 Self Improver")
        
        if action == "reflect":
            return self._reflect(params.get("performance_data", {}))
        elif action == "identify":
            return self._identify_weaknesses()
        elif action == "suggest":
            return self._suggest_improvements()
        elif action == "apply":
            return self._apply_improvement(params.get("improvement_id", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _reflect(self, data: Dict) -> AlgorithmResult:
        # Record performance
        entry = {
            "timestamp": time.time(),
            "success_rate": data.get("success_rate", 0.5),
            "response_time": data.get("response_time", 0),
            "error_count": data.get("errors", 0),
            "task_types": data.get("task_types", [])
        }
        self.performance_history.append(entry)
        
        # Basic reflection
        avg_success = sum(e["success_rate"] for e in self.performance_history) / len(self.performance_history)
        trend = "improving" if len(self.performance_history) > 1 and entry["success_rate"] > avg_success else "stable"
        
        return AlgorithmResult(
            status="success",
            data={
                "reflection": {
                    "current_success_rate": entry["success_rate"],
                    "historical_average": avg_success,
                    "trend": trend,
                    "data_points": len(self.performance_history)
                }
            }
        )
    
    def _identify_weaknesses(self) -> AlgorithmResult:
        if not self.performance_history:
            return AlgorithmResult(status="success", data={"weaknesses": []})
        
        weaknesses = []
        
        # Success rate analysis
        recent = self.performance_history[-5:]
        avg_success = sum(e["success_rate"] for e in recent) / len(recent)
        
        if avg_success < 0.8:
            weaknesses.append({
                "area": "success_rate",
                "severity": "high" if avg_success < 0.5 else "medium",
                "description": f"Recent success rate is {avg_success:.1%}"
            })
        
        # Response time analysis
        avg_time = sum(e["response_time"] for e in recent) / len(recent)
        if avg_time > 5000:  # 5 seconds
            weaknesses.append({
                "area": "response_time",
                "severity": "medium",
                "description": f"Average response time is {avg_time:.0f}ms"
            })
        
        # Error analysis
        total_errors = sum(e["error_count"] for e in recent)
        if total_errors > 5:
            weaknesses.append({
                "area": "error_handling",
                "severity": "high",
                "description": f"Recent error count: {total_errors}"
            })
        
        print(f"   Identified {len(weaknesses)} weaknesses")
        
        return AlgorithmResult(
            status="success",
            data={"weaknesses": weaknesses}
        )
    
    def _suggest_improvements(self) -> AlgorithmResult:
        weaknesses = self._identify_weaknesses().data.get("weaknesses", [])
        
        suggestions = []
        for i, weakness in enumerate(weaknesses):
            improvement = ImprovementCandidate(
                id=f"imp_{i}",
                category=weakness["area"],
                description=self._get_improvement_for(weakness["area"]),
                expected_impact=0.8 if weakness["severity"] == "high" else 0.5,
                implementation_effort="medium",
                priority_score=0.9 if weakness["severity"] == "high" else 0.6
            )
            suggestions.append(improvement)
            self.improvements.append(improvement)
        
        print(f"   Generated {len(suggestions)} improvement suggestions")
        
        return AlgorithmResult(
            status="success",
            data={
                "suggestions": [
                    {"id": s.id, "category": s.category, "description": s.description, "priority": s.priority_score}
                    for s in suggestions
                ]
            }
        )
    
    def _get_improvement_for(self, area: str) -> str:
        improvements_map = {
            "success_rate": "Enhance error handling and add validation checks",
            "response_time": "Implement caching and async processing",
            "error_handling": "Add comprehensive try-catch blocks and fallback logic"
        }
        return improvements_map.get(area, "Review and optimize implementation")
    
    def _apply_improvement(self, improvement_id: str) -> AlgorithmResult:
        improvement = next((i for i in self.improvements if i.id == improvement_id), None)
        
        if not improvement:
            return AlgorithmResult(status="error", error="Improvement not found")
        
        self.applied_improvements.append(improvement_id)
        
        return AlgorithmResult(
            status="success",
            data={
                "applied": improvement_id,
                "description": improvement.description,
                "total_applied": len(self.applied_improvements)
            }
        )


def register(algorithm_manager):
    algo = SelfImproverAlgorithm()
    algorithm_manager.register("SelfImprover", algo)
    print("✅ SelfImprover registered")


if __name__ == "__main__":
    algo = SelfImproverAlgorithm()
    algo.execute({"action": "reflect", "performance_data": {"success_rate": 0.7, "errors": 3}})
    result = algo.execute({"action": "suggest"})
    print(f"Suggestions: {len(result.data.get('suggestions', []))}")
