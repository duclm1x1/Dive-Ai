"""
Dive AI V29 - GPA Scorer
Goal-Plan-Action Scoring for Action Evaluation

Upgrade from: cruel_evaluator.py + feedback_learning.py

GPA Score Formula:
    overall = goal_alignment * 0.4 + plan_alignment * 0.3 + action_quality * 0.3

Features:
- Goal Alignment (0-1): How well does action achieve goal?
- Plan Alignment (0-1): Does action follow the plan?
- Action Quality (0-1): Code quality, efficiency, security
- Feedback generation for learning
- Integration with Memory V5 for history
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


# ==========================================
# ENUMS & DATA CLASSES
# ==========================================

class ScoreLevel(Enum):
    EXCELLENT = "excellent"  # 0.8-1.0
    GOOD = "good"           # 0.6-0.8
    ACCEPTABLE = "acceptable"  # 0.4-0.6
    POOR = "poor"           # 0.2-0.4
    FAIL = "fail"           # 0.0-0.2


class EvaluationDimension(Enum):
    GOAL_ALIGNMENT = "goal_alignment"
    PLAN_ALIGNMENT = "plan_alignment"
    ACTION_QUALITY = "action_quality"
    CODE_CORRECTNESS = "code_correctness"
    CODE_EFFICIENCY = "code_efficiency"
    CODE_SECURITY = "code_security"
    CODE_READABILITY = "code_readability"


@dataclass
class GPAScore:
    """GPA Score result"""
    goal_alignment: float
    plan_alignment: float
    action_quality: float
    overall: float
    level: ScoreLevel
    
    @staticmethod
    def calculate(goal: float, plan: float, action: float) -> 'GPAScore':
        overall = goal * 0.4 + plan * 0.3 + action * 0.3
        
        if overall >= 0.8:
            level = ScoreLevel.EXCELLENT
        elif overall >= 0.6:
            level = ScoreLevel.GOOD
        elif overall >= 0.4:
            level = ScoreLevel.ACCEPTABLE
        elif overall >= 0.2:
            level = ScoreLevel.POOR
        else:
            level = ScoreLevel.FAIL
        
        return GPAScore(goal, plan, action, overall, level)


@dataclass
class DimensionScore:
    """Score for a single dimension"""
    dimension: EvaluationDimension
    score: float
    feedback: str
    critical_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation result"""
    gpa_score: GPAScore
    dimension_scores: List[DimensionScore]
    overall_feedback: str
    tactical_feedback: str  # Short-term improvements
    strategic_feedback: str  # Long-term patterns
    strengths: List[str]
    weaknesses: List[str]
    improvement_actions: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "gpa_score": {
                "goal_alignment": self.gpa_score.goal_alignment,
                "plan_alignment": self.gpa_score.plan_alignment,
                "action_quality": self.gpa_score.action_quality,
                "overall": self.gpa_score.overall,
                "level": self.gpa_score.level.value
            },
            "dimension_scores": [
                {
                    "dimension": ds.dimension.value,
                    "score": ds.score,
                    "feedback": ds.feedback,
                    "critical_issues": ds.critical_issues,
                    "suggestions": ds.suggestions
                }
                for ds in self.dimension_scores
            ],
            "overall_feedback": self.overall_feedback,
            "tactical_feedback": self.tactical_feedback,
            "strategic_feedback": self.strategic_feedback,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "improvement_actions": self.improvement_actions
        }


# ==========================================
# GPA SCORER ALGORITHM
# ==========================================

class GPAScorerAlgorithm(BaseAlgorithm):
    """
    📊 GPA Scorer Algorithm
    
    Evaluates actions using Goal-Plan-Action framework:
    - Goal Alignment (40%): Does action achieve the goal?
    - Plan Alignment (30%): Does action follow the plan?
    - Action Quality (30%): Quality of implementation
    
    Generates:
    - Tactical Feedback: Immediate improvements
    - Strategic Feedback: Long-term patterns
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="GPAScorer",
            name="GPA Scorer",
            level="tactic",
            category="evaluation",
            version="1.0",
            description="Goal-Plan-Action scoring for action evaluation",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("goal", "string", True, "The intended goal"),
                    IOField("plan", "string", True, "The execution plan"),
                    IOField("action", "string", True, "The action taken"),
                    IOField("action_type", "string", False, "Type: code/response/general"),
                    IOField("context", "object", False, "Additional context")
                ],
                outputs=[
                    IOField("gpa_score", "object", True, "GPA score object"),
                    IOField("evaluation", "object", True, "Full evaluation result")
                ]
            ),
            
            steps=[
                "1. Analyze goal alignment",
                "2. Analyze plan alignment",
                "3. Evaluate action quality",
                "4. Calculate GPA score",
                "5. Generate tactical feedback",
                "6. Generate strategic feedback",
                "7. Return evaluation result"
            ],
            
            tags=["evaluation", "scoring", "feedback", "learning", "gpa"]
        )
        
        # Patterns for code quality detection
        self.security_issues = [
            (r'eval\s*\(', "eval() is dangerous"),
            (r'exec\s*\(', "exec() is dangerous"),
            (r'subprocess\..*shell\s*=\s*True', "shell=True is risky"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'pickle\.loads', "pickle.loads is insecure"),
            (r'os\.system\s*\(', "os.system is dangerous"),
        ]
        
        self.efficiency_issues = [
            (r'for .+ in .+:\s*for .+ in .+:\s*for .+ in .+:', "Triple nested loop"),
            (r'time\.sleep\s*\(\s*\d{2,}\s*\)', "Long sleep"),
            (r'while\s+True:', "Infinite loop risk"),
        ]
        
        self.readability_issues = [
            (r'[a-z]\s*=\s*', "Single letter variable"),
            (r'def\s+[a-z]\s*\(', "Single letter function"),
            (r'#', "Has comments", True),  # Positive
            (r'"""', "Has docstring", True),  # Positive
        ]
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute GPA evaluation"""
        goal = params.get("goal", "")
        plan = params.get("plan", "")
        action = params.get("action", "")
        action_type = params.get("action_type", "general")
        context = params.get("context", {})
        
        try:
            # 1. Evaluate goal alignment
            goal_score, goal_analysis = self._evaluate_goal_alignment(goal, action)
            
            # 2. Evaluate plan alignment
            plan_score, plan_analysis = self._evaluate_plan_alignment(plan, action)
            
            # 3. Evaluate action quality
            if action_type == "code":
                quality_score, quality_analysis = self._evaluate_code_quality(action)
            else:
                quality_score, quality_analysis = self._evaluate_response_quality(action)
            
            # 4. Calculate GPA score
            gpa = GPAScore.calculate(goal_score.score, plan_score.score, quality_score)
            
            # 5. Collect all dimension scores
            dimension_scores = [goal_analysis, plan_analysis]
            if action_type == "code":
                dimension_scores.extend(quality_analysis)
            
            # 6. Generate feedback
            strengths = self._identify_strengths(dimension_scores)
            weaknesses = self._identify_weaknesses(dimension_scores)
            tactical = self._generate_tactical_feedback(dimension_scores, gpa)
            strategic = self._generate_strategic_feedback(dimension_scores, gpa)
            improvements = self._suggest_improvements(dimension_scores)
            
            # 7. Build result
            overall_feedback = self._generate_overall_feedback(gpa, strengths, weaknesses)
            
            evaluation = EvaluationResult(
                gpa_score=gpa,
                dimension_scores=dimension_scores,
                overall_feedback=overall_feedback,
                tactical_feedback=tactical,
                strategic_feedback=strategic,
                strengths=strengths,
                weaknesses=weaknesses,
                improvement_actions=improvements
            )
            
            return AlgorithmResult(
                status="success",
                data={
                    "gpa_score": {
                        "goal_alignment": gpa.goal_alignment,
                        "plan_alignment": gpa.plan_alignment,
                        "action_quality": gpa.action_quality,
                        "overall": gpa.overall,
                        "level": gpa.level.value
                    },
                    "evaluation": evaluation.to_dict()
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=str(e))
    
    def _evaluate_goal_alignment(self, goal: str, action: str) -> Tuple[DimensionScore, DimensionScore]:
        """Evaluate how well action aligns with goal"""
        # Extract key terms from goal
        goal_terms = set(re.findall(r'\b\w{4,}\b', goal.lower()))
        action_terms = set(re.findall(r'\b\w{4,}\b', action.lower()))
        
        # Calculate overlap
        if not goal_terms:
            overlap = 0.5
        else:
            overlap = len(goal_terms & action_terms) / len(goal_terms)
        
        # Boost if action contains key goal indicators
        boost = 0
        if any(kw in action.lower() for kw in ["achieve", "complete", "done", "success", "result"]):
            boost = 0.1
        
        score = min(overlap + boost, 1.0)
        
        # Check for goal-related keywords
        issues = []
        suggestions = []
        
        if score < 0.4:
            issues.append("Action doesn't address main goal objectives")
            suggestions.append("Focus on primary goal requirements first")
        
        feedback = f"Goal alignment: {score:.0%}. "
        if score >= 0.8:
            feedback += "Excellent focus on goal."
        elif score >= 0.5:
            feedback += "Adequate goal coverage."
        else:
            feedback += "Weak goal alignment - reconsider approach."
        
        dim_score = DimensionScore(
            dimension=EvaluationDimension.GOAL_ALIGNMENT,
            score=score,
            feedback=feedback,
            critical_issues=issues,
            suggestions=suggestions
        )
        
        return dim_score, dim_score
    
    def _evaluate_plan_alignment(self, plan: str, action: str) -> Tuple[DimensionScore, DimensionScore]:
        """Evaluate how well action follows the plan"""
        # Extract steps from plan
        plan_steps = re.findall(r'(?:step\s*\d+|^\d+\.|^\-)', plan.lower(), re.MULTILINE)
        plan_terms = set(re.findall(r'\b\w{4,}\b', plan.lower()))
        action_terms = set(re.findall(r'\b\w{4,}\b', action.lower()))
        
        # Calculate overlap
        if not plan_terms:
            overlap = 0.5
        else:
            overlap = len(plan_terms & action_terms) / len(plan_terms)
        
        # Check if action appears to follow structured approach
        has_structure = bool(re.search(r'(?:first|then|next|finally|step)', action.lower()))
        
        score = min(overlap + (0.1 if has_structure else 0), 1.0)
        
        issues = []
        suggestions = []
        
        if score < 0.4:
            issues.append("Action deviates from planned approach")
            suggestions.append("Review plan steps before taking action")
        
        feedback = f"Plan alignment: {score:.0%}. "
        if score >= 0.8:
            feedback += "Follows plan closely."
        elif score >= 0.5:
            feedback += "Partially follows plan."
        else:
            feedback += "Significant deviation from plan."
        
        dim_score = DimensionScore(
            dimension=EvaluationDimension.PLAN_ALIGNMENT,
            score=score,
            feedback=feedback,
            critical_issues=issues,
            suggestions=suggestions
        )
        
        return dim_score, dim_score
    
    def _evaluate_code_quality(self, code: str) -> Tuple[float, List[DimensionScore]]:
        """Evaluate code quality across multiple dimensions"""
        scores = []
        
        # 1. Security check
        security_issues = []
        for pattern, issue, *positive in self.security_issues:
            if re.search(pattern, code, re.IGNORECASE):
                if not positive:  # Negative pattern
                    security_issues.append(issue)
        
        security_score = max(0, 1.0 - len(security_issues) * 0.25)
        scores.append(DimensionScore(
            dimension=EvaluationDimension.CODE_SECURITY,
            score=security_score,
            feedback=f"Security: {security_score:.0%}",
            critical_issues=security_issues,
            suggestions=["Address security issues immediately"] if security_issues else []
        ))
        
        # 2. Efficiency check
        efficiency_issues = []
        for pattern, issue, *positive in self.efficiency_issues:
            if re.search(pattern, code, re.MULTILINE):
                if not positive:
                    efficiency_issues.append(issue)
        
        efficiency_score = max(0, 1.0 - len(efficiency_issues) * 0.2)
        scores.append(DimensionScore(
            dimension=EvaluationDimension.CODE_EFFICIENCY,
            score=efficiency_score,
            feedback=f"Efficiency: {efficiency_score:.0%}",
            critical_issues=efficiency_issues,
            suggestions=["Consider algorithm optimization"] if efficiency_issues else []
        ))
        
        # 3. Readability check
        readability_positives = 0
        readability_negatives = 0
        
        # Check for docstrings and comments
        if '"""' in code or "'''" in code:
            readability_positives += 1
        if re.search(r'#\s*\w', code):
            readability_positives += 1
        
        # Check for single letter variables (negative)
        single_letters = len(re.findall(r'\b([a-z])\s*=', code))
        if single_letters > 5:
            readability_negatives += 1
        
        # Check line length
        long_lines = sum(1 for line in code.split('\n') if len(line) > 120)
        if long_lines > 3:
            readability_negatives += 1
        
        readability_score = min(1.0, max(0, 0.5 + readability_positives * 0.2 - readability_negatives * 0.15))
        scores.append(DimensionScore(
            dimension=EvaluationDimension.CODE_READABILITY,
            score=readability_score,
            feedback=f"Readability: {readability_score:.0%}",
            critical_issues=[],
            suggestions=["Add docstrings"] if '"""' not in code else []
        ))
        
        # 4. Correctness (basic check)
        correctness_issues = []
        
        # Check for obvious syntax issues
        if code.count('(') != code.count(')'):
            correctness_issues.append("Unbalanced parentheses")
        if code.count('[') != code.count(']'):
            correctness_issues.append("Unbalanced brackets")
        if code.count('{') != code.count('}'):
            correctness_issues.append("Unbalanced braces")
        
        correctness_score = max(0, 1.0 - len(correctness_issues) * 0.3)
        scores.append(DimensionScore(
            dimension=EvaluationDimension.CODE_CORRECTNESS,
            score=correctness_score,
            feedback=f"Correctness: {correctness_score:.0%}",
            critical_issues=correctness_issues,
            suggestions=["Fix syntax errors"] if correctness_issues else []
        ))
        
        # Overall quality
        overall = (
            security_score * 0.35 +
            efficiency_score * 0.25 +
            readability_score * 0.2 +
            correctness_score * 0.2
        )
        
        return overall, scores
    
    def _evaluate_response_quality(self, response: str) -> Tuple[float, List[DimensionScore]]:
        """Evaluate response quality"""
        scores = []
        
        # Length and completeness
        length = len(response)
        if length < 50:
            completeness = 0.3
        elif length < 200:
            completeness = 0.6
        elif length < 1000:
            completeness = 0.8
        else:
            completeness = 0.9
        
        scores.append(DimensionScore(
            dimension=EvaluationDimension.ACTION_QUALITY,
            score=completeness,
            feedback=f"Response completeness: {completeness:.0%}",
            critical_issues=[],
            suggestions=[]
        ))
        
        return completeness, scores
    
    def _identify_strengths(self, scores: List[DimensionScore]) -> List[str]:
        """Identify strengths from scores"""
        strengths = []
        for ds in scores:
            if ds.score >= 0.8:
                strengths.append(f"Strong {ds.dimension.value.replace('_', ' ')}")
        return strengths
    
    def _identify_weaknesses(self, scores: List[DimensionScore]) -> List[str]:
        """Identify weaknesses from scores"""
        weaknesses = []
        for ds in scores:
            if ds.score < 0.5:
                weaknesses.append(f"Weak {ds.dimension.value.replace('_', ' ')}")
            weaknesses.extend(ds.critical_issues)
        return weaknesses
    
    def _generate_tactical_feedback(self, scores: List[DimensionScore], gpa: GPAScore) -> str:
        """Generate short-term tactical feedback"""
        if gpa.level in [ScoreLevel.EXCELLENT, ScoreLevel.GOOD]:
            return "Continue current approach. Minor optimizations possible."
        
        # Find lowest scoring dimension
        worst = min(scores, key=lambda x: x.score)
        
        if worst.dimension == EvaluationDimension.GOAL_ALIGNMENT:
            return "IMMEDIATE: Refocus on goal requirements. Current action drifting."
        elif worst.dimension == EvaluationDimension.PLAN_ALIGNMENT:
            return "IMMEDIATE: Review and follow the plan. Deviations detected."
        elif worst.dimension == EvaluationDimension.CODE_SECURITY:
            return "CRITICAL: Fix security issues before proceeding."
        else:
            return f"FOCUS: Improve {worst.dimension.value.replace('_', ' ')}."
    
    def _generate_strategic_feedback(self, scores: List[DimensionScore], gpa: GPAScore) -> str:
        """Generate long-term strategic feedback"""
        if gpa.level == ScoreLevel.EXCELLENT:
            return "Pattern: Consistent high quality. Consider documenting approach for reuse."
        elif gpa.level == ScoreLevel.GOOD:
            return "Pattern: Good performance. Small improvements in weak areas will compound."
        elif gpa.level == ScoreLevel.ACCEPTABLE:
            return "Pattern: Room for improvement. Focus on one dimension per iteration."
        else:
            return "Pattern: Significant improvement needed. Consider different approach or algorithm."
    
    def _suggest_improvements(self, scores: List[DimensionScore]) -> List[str]:
        """Suggest improvement actions"""
        improvements = []
        for ds in scores:
            improvements.extend(ds.suggestions)
        return improvements[:5]  # Limit to top 5
    
    def _generate_overall_feedback(
        self,
        gpa: GPAScore,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """Generate overall feedback summary"""
        emoji = {
            ScoreLevel.EXCELLENT: "🌟",
            ScoreLevel.GOOD: "✅",
            ScoreLevel.ACCEPTABLE: "⚠️",
            ScoreLevel.POOR: "❌",
            ScoreLevel.FAIL: "🚨"
        }
        
        result = f"{emoji.get(gpa.level, '📊')} GPA Score: {gpa.overall:.2f} ({gpa.level.value})\n"
        result += f"   Goal: {gpa.goal_alignment:.0%} | Plan: {gpa.plan_alignment:.0%} | Quality: {gpa.action_quality:.0%}\n"
        
        if strengths:
            result += f"   Strengths: {', '.join(strengths[:3])}\n"
        if weaknesses:
            result += f"   Weaknesses: {', '.join(weaknesses[:3])}"
        
        return result


# ==========================================
# FEEDBACK SYNTHESIZER
# ==========================================

class FeedbackSynthesizer:
    """
    Synthesizes tactical and strategic feedback
    for the Feedback Loop in Metacognition Layer
    """
    
    def synthesize(
        self,
        tactical_feedbacks: List[str],
        strategic_feedbacks: List[str],
        gpa_scores: List[GPAScore]
    ) -> Dict[str, Any]:
        """
        Synthesize multiple feedbacks into consolidated recommendations
        """
        # Calculate average scores
        avg_gpa = sum(g.overall for g in gpa_scores) / len(gpa_scores) if gpa_scores else 0.5
        avg_goal = sum(g.goal_alignment for g in gpa_scores) / len(gpa_scores) if gpa_scores else 0.5
        avg_plan = sum(g.plan_alignment for g in gpa_scores) / len(gpa_scores) if gpa_scores else 0.5
        avg_action = sum(g.action_quality for g in gpa_scores) / len(gpa_scores) if gpa_scores else 0.5
        
        # Identify common themes
        tactical_themes = self._extract_themes(tactical_feedbacks)
        strategic_themes = self._extract_themes(strategic_feedbacks)
        
        # Generate recommendations
        tactical_recommendation = self._generate_tactical_recommendation(
            avg_gpa, tactical_themes
        )
        strategic_recommendation = self._generate_strategic_recommendation(
            avg_gpa, strategic_themes
        )
        
        return {
            "aggregated_scores": {
                "avg_gpa": avg_gpa,
                "avg_goal": avg_goal,
                "avg_plan": avg_plan,
                "avg_action": avg_action
            },
            "tactical": {
                "themes": tactical_themes,
                "recommendation": tactical_recommendation,
                "target": "Reasoning Engine"
            },
            "strategic": {
                "themes": strategic_themes,
                "recommendation": strategic_recommendation,
                "target": "Cognitive Layer"
            }
        }
    
    def _extract_themes(self, feedbacks: List[str]) -> List[str]:
        """Extract common themes from feedback list"""
        theme_counts = {}
        keywords = ["goal", "plan", "security", "efficiency", "quality", "alignment"]
        
        for feedback in feedbacks:
            feedback_lower = feedback.lower()
            for kw in keywords:
                if kw in feedback_lower:
                    theme_counts[kw] = theme_counts.get(kw, 0) + 1
        
        # Return top themes
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_themes[:3]]
    
    def _generate_tactical_recommendation(self, avg_gpa: float, themes: List[str]) -> str:
        if avg_gpa >= 0.8:
            return "Maintain current execution patterns. Minor optimizations only."
        elif avg_gpa >= 0.6:
            focus = themes[0] if themes else "general quality"
            return f"Focus next actions on improving {focus}."
        else:
            return "Consider algorithm switch. Current approach underperforming."
    
    def _generate_strategic_recommendation(self, avg_gpa: float, themes: List[str]) -> str:
        if avg_gpa >= 0.8:
            return "Current Meta-Algorithm effective. Log pattern for future reuse."
        elif avg_gpa >= 0.6:
            return "Meta-Algorithm adequate. Consider refinements to workflow graph."
        else:
            return "Meta-Algorithm selection may be suboptimal. Consider alternative."


# ==========================================
# REGISTRATION
# ==========================================

def register(algorithm_manager):
    """Register GPA Scorer Algorithm"""
    algo = GPAScorerAlgorithm()
    algorithm_manager.register("GPAScorer", algo)
    print("✅ GPAScorer Algorithm registered (GPA evaluation + feedback synthesis)")


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📊 GPA SCORER TEST")
    print("=" * 60)
    
    scorer = GPAScorerAlgorithm()
    
    # Test 1: Good code
    print("\n📝 Test 1: Good code evaluation")
    result = scorer.execute({
        "goal": "Create a function to calculate factorial",
        "plan": "1. Define function 2. Add input validation 3. Use recursion",
        "action": '''
def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',
        "action_type": "code"
    })
    
    if result.status == "success":
        gpa = result.data["gpa_score"]
        print(f"   GPA: {gpa['overall']:.2f} ({gpa['level']})")
        print(f"   Goal: {gpa['goal_alignment']:.0%} | Plan: {gpa['plan_alignment']:.0%}")
    
    # Test 2: Bad code with security issues
    print("\n📝 Test 2: Bad code with security issues")
    result = scorer.execute({
        "goal": "Calculate user input",
        "plan": "Parse and calculate",
        "action": '''
def calculate(expression):
    return eval(expression)
''',
        "action_type": "code"
    })
    
    if result.status == "success":
        gpa = result.data["gpa_score"]
        eval_data = result.data["evaluation"]
        print(f"   GPA: {gpa['overall']:.2f} ({gpa['level']})")
        print(f"   Tactical: {eval_data['tactical_feedback']}")
        print(f"   Weaknesses: {eval_data['weaknesses'][:2]}")
    
    # Test 3: Feedback synthesizer
    print("\n📝 Test 3: Feedback Synthesizer")
    synthesizer = FeedbackSynthesizer()
    
    synthesis = synthesizer.synthesize(
        tactical_feedbacks=[
            "FOCUS: Improve security",
            "IMMEDIATE: Fix security issues",
            "Review goal alignment"
        ],
        strategic_feedbacks=[
            "Pattern: Security issues recurring",
            "Consider security-first approach"
        ],
        gpa_scores=[
            GPAScore.calculate(0.7, 0.6, 0.4),
            GPAScore.calculate(0.8, 0.7, 0.5),
            GPAScore.calculate(0.6, 0.5, 0.3)
        ]
    )
    
    print(f"   Avg GPA: {synthesis['aggregated_scores']['avg_gpa']:.2f}")
    print(f"   Tactical themes: {synthesis['tactical']['themes']}")
    print(f"   Recommendation: {synthesis['tactical']['recommendation']}")
    
    print("\n" + "=" * 60)
    print("✅ GPA Scorer test completed!")
