"""Prompt Optimizer Skill — Improve prompts for better LLM results."""
import re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class PromptSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="prompt-optimizer", description="Optimize prompts for better LLM results",
            category=SkillCategory.AI, version="1.0.0",
            input_schema={"prompt": {"type": "string", "required": True}, "task_type": {"type": "string"}},
            output_schema={"optimized_prompt": "string", "improvements": "list"},
            tags=["prompt", "optimize", "improve", "llm"],
            trigger_patterns=[r"optimize\s+prompt", r"improve\s+prompt", r"better\s+prompt"],
            combo_compatible=["deep-research", "code-review", "self-improve"], combo_position="middle")

    def _execute(self, inputs, context=None):
        prompt = inputs.get("prompt") or inputs.get("data", {}).get("summary", "")
        task_type = inputs.get("task_type", "general")
        
        improvements = []
        optimized = prompt
        
        # Add structure
        if not any(k in prompt.lower() for k in ["step", "1.", "first", "then"]):
            optimized = "Please follow these steps:\n1. " + optimized
            improvements.append("Added step-by-step structure")
        
        # Add specificity
        if len(prompt.split()) < 10:
            optimized += "\n\nPlease be specific and detailed in your response."
            improvements.append("Added specificity request")
        
        # Add output format
        if "format" not in prompt.lower() and "json" not in prompt.lower():
            if task_type == "code":
                optimized += "\n\nProvide your answer as working code with comments."
            elif task_type == "analysis":
                optimized += "\n\nStructure your analysis with headers and bullet points."
            else:
                optimized += "\n\nProvide a clear, structured response."
            improvements.append("Added output format guidance")
        
        # Add context
        if "context" not in prompt.lower():
            optimized = f"Context: {task_type} task\n\n" + optimized
            improvements.append("Added context header")
        
        return AlgorithmResult("success", {
            "original": prompt, "optimized_prompt": optimized,
            "improvements": improvements, "improvement_count": len(improvements),
        }, {"skill": "prompt-optimizer"})
