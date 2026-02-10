"""
🎯 CRUEL EVALUATOR
Strict evaluation of code and responses

Based on V28's vibe_engine/cruel_evaluator/ + cruel_system.py
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


class EvaluationCategory(Enum):
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    EFFICIENCY = "efficiency"
    READABILITY = "readability"
    SECURITY = "security"


@dataclass
class EvaluationCriterion:
    """A single evaluation criterion"""
    category: EvaluationCategory
    score: float  # 0-10
    feedback: str
    critical: bool = False


class CruelEvaluatorAlgorithm(BaseAlgorithm):
    """
    🎯 Cruel Evaluator
    
    Provides strict, honest evaluation:
    - Zero-tolerance for errors
    - Brutally honest feedback
    - No sugar-coating
    - Actionable improvements
    
    From V28: vibe_engine/cruel_evaluator/
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="CruelEvaluator",
            name="Cruel Evaluator",
            level="operational",
            category="evaluation",
            version="1.0",
            description="Strict, honest code and response evaluation",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("content", "string", True, "Content to evaluate"),
                    IOField("content_type", "string", False, "code/response/plan"),
                    IOField("criteria", "array", False, "Specific criteria to evaluate")
                ],
                outputs=[
                    IOField("score", "number", True, "Overall score (0-10)"),
                    IOField("evaluations", "array", True, "Per-criterion evaluations"),
                    IOField("verdict", "string", True, "PASS/FAIL/NEEDS_WORK")
                ]
            ),
            steps=["Parse content", "Apply criteria", "Score ruthlessly", "Generate feedback"],
            tags=["evaluation", "cruel", "strict", "quality"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        content = params.get("content", "")
        content_type = params.get("content_type", "code")
        
        if not content:
            return AlgorithmResult(status="error", error="No content to evaluate")
        
        print(f"\n🎯 Cruel Evaluator")
        
        evaluations = []
        
        if content_type == "code":
            evaluations = self._evaluate_code(content)
        elif content_type == "response":
            evaluations = self._evaluate_response(content)
        else:
            evaluations = self._evaluate_general(content)
        
        # Calculate overall score
        scores = [e.score for e in evaluations]
        overall = sum(scores) / len(scores) if scores else 0
        
        # Determine verdict (cruel - no mercy)
        has_critical = any(e.critical for e in evaluations)
        if has_critical or overall < 5:
            verdict = "FAIL"
        elif overall < 8:
            verdict = "NEEDS_WORK"
        else:
            verdict = "PASS"
        
        print(f"   Score: {overall:.1f}/10 - {verdict}")
        
        return AlgorithmResult(
            status="success",
            data={
                "score": round(overall, 1),
                "verdict": verdict,
                "evaluations": [
                    {"category": e.category.value, "score": e.score, "feedback": e.feedback, "critical": e.critical}
                    for e in evaluations
                ],
                "summary": self._generate_cruel_summary(verdict, evaluations)
            }
        )
    
    def _evaluate_code(self, code: str) -> List[EvaluationCriterion]:
        evaluations = []
        
        # Correctness - syntax check
        try:
            compile(code, '<string>', 'exec')
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.CORRECTNESS, 8.0, "Code compiles. That's a start.", False
            ))
        except SyntaxError as e:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.CORRECTNESS, 0.0, f"Syntax error: {e}. Unacceptable.", True
            ))
        
        # Completeness
        if len(code.strip()) < 50:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.COMPLETENESS, 3.0, "Is this all? Looks incomplete.", False
            ))
        else:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.COMPLETENESS, 7.0, "Appears complete, but verify thoroughly.", False
            ))
        
        # Security
        dangerous = ["eval(", "exec(", "os.system(", "subprocess.call("]
        found = [d for d in dangerous if d in code]
        if found:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.SECURITY, 2.0, f"Security nightmare: {found}. Fix immediately.", True
            ))
        else:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.SECURITY, 8.0, "No obvious security holes. Don't get cocky.", False
            ))
        
        # Readability
        lines = code.split('\n')
        long_lines = sum(1 for l in lines if len(l) > 100)
        if long_lines > 3:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.READABILITY, 4.0, f"{long_lines} lines too long. Did you forget about readability?", False
            ))
        else:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.READABILITY, 7.0, "Readable. Could be better.", False
            ))
        
        # Efficiency (basic heuristics)
        if "for " in code and "for " in code[code.find("for ") + 5:]:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.EFFICIENCY, 5.0, "Nested loops detected. Justify this.", False
            ))
        else:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.EFFICIENCY, 7.0, "Efficiency seems acceptable.", False
            ))
        
        return evaluations
    
    def _evaluate_response(self, response: str) -> List[EvaluationCriterion]:
        evaluations = []
        
        # Completeness
        word_count = len(response.split())
        if word_count < 20:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.COMPLETENESS, 3.0, "Too brief. Elaborate or don't bother.", False
            ))
        else:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.COMPLETENESS, 7.0, "Adequate length.", False
            ))
        
        # Clarity
        if "TODO" in response or "FIXME" in response:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.CORRECTNESS, 4.0, "Contains unresolved TODOs. Finish the job.", False
            ))
        else:
            evaluations.append(EvaluationCriterion(
                EvaluationCategory.CORRECTNESS, 8.0, "No obvious placeholders.", False
            ))
        
        return evaluations
    
    def _evaluate_general(self, content: str) -> List[EvaluationCriterion]:
        return [EvaluationCriterion(
            EvaluationCategory.COMPLETENESS, 5.0, "Generic evaluation. Provide specific content type for better feedback.", False
        )]
    
    def _generate_cruel_summary(self, verdict: str, evaluations: List[EvaluationCriterion]) -> str:
        if verdict == "PASS":
            return "Acceptable. Don't let it go to your head."
        elif verdict == "NEEDS_WORK":
            weak = [e for e in evaluations if e.score < 6]
            areas = ", ".join(e.category.value for e in weak[:3])
            return f"Mediocre. Fix: {areas}."
        else:
            critical = [e for e in evaluations if e.critical]
            if critical:
                return f"Failed. Critical issues: {critical[0].feedback}"
            return "Failed. This needs significant work."


def register(algorithm_manager):
    algo = CruelEvaluatorAlgorithm()
    algorithm_manager.register("CruelEvaluator", algo)
    print("✅ CruelEvaluator registered")


if __name__ == "__main__":
    algo = CruelEvaluatorAlgorithm()
    result = algo.execute({
        "content": "def add(a, b):\n    return eval(f'{a} + {b}')\n",
        "content_type": "code"
    })
    print(f"Verdict: {result.data['verdict']}")
    print(f"Summary: {result.data['summary']}")
