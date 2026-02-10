"""Self Improve Skill — Analyze failures and improve skills."""
import json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SelfImproveSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="self-improve", description="Analyze skill failures and suggest improvements",
            category=SkillCategory.AI, version="1.0.0",
            input_schema={"focus": {"type": "string"}},
            output_schema={"analysis": "dict", "recommendations": "list"},
            tags=["improve", "learn", "fix", "optimize", "self"],
            trigger_patterns=[r"improve\s+", r"self.?improve", r"learn\s+from", r"optimize\s+skills"],
            combo_compatible=["prompt-optimizer", "memory-query"], combo_position="end",
            cost_per_call=0.001)

    def _execute(self, inputs, context=None):
        focus = inputs.get("focus", "all")
        
        # Analyze registry stats if available
        try:
            from ..skill_registry import get_registry
            reg = get_registry()
            stats = reg.get_stats()
        except:
            stats = {"total_skills": 0, "total_executions": 0}
        
        recommendations = []
        
        # Check for under-used skills
        skill_stats = stats.get("skills", {})
        for name, s in skill_stats.items():
            if s.get("executions", 0) == 0:
                recommendations.append(f"Skill '{name}' has never been used. Consider promoting it.")
            if s.get("last_success") is False:
                recommendations.append(f"Skill '{name}' last execution FAILED. Investigate errors.")
        
        # Cost analysis
        total_cost = stats.get("total_cost", 0)
        if total_cost > 1.0:
            recommendations.append(f"Total cost is ${total_cost:.4f}. Review high-cost skills.")
        
        # General recommendations
        if stats.get("total_skills", 0) < 10:
            recommendations.append("Consider installing more skills to expand capabilities.")
        
        if not recommendations:
            recommendations.append("All systems nominal. No improvements needed at this time.")
        
        return AlgorithmResult("success", {
            "analysis": stats, "recommendations": recommendations,
            "focus": focus, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }, {"skill": "self-improve"})
