"""
✨ PROMPT OPTIMIZER
Optimize prompts for better model responses

Based on V28's vibe_engine/prompt_optimizer.py
"""

import os
import sys
import re
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class PromptTemplate:
    """A prompt template"""
    id: str
    pattern: str
    optimizations: List[str]


class PromptOptimizerAlgorithm(BaseAlgorithm):
    """
    ✨ Prompt Optimizer
    
    Optimizes prompts for better results:
    - Clarity enhancement
    - Context enrichment
    - Instruction clarification
    - Format optimization
    
    From V28: vibe_engine/prompt_optimizer.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="PromptOptimizer",
            name="Prompt Optimizer",
            level="operational",
            category="optimization",
            version="1.0",
            description="Optimize prompts for better responses",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("prompt", "string", True, "Prompt to optimize"),
                    IOField("task_type", "string", False, "Type of task"),
                    IOField("model", "string", False, "Target model")
                ],
                outputs=[
                    IOField("optimized", "string", True, "Optimized prompt")
                ]
            ),
            steps=["Analyze prompt", "Identify improvements", "Apply optimizations", "Format output"],
            tags=["prompt", "optimization", "enhancement"]
        )
        
        self.templates: Dict[str, PromptTemplate] = {
            "code": PromptTemplate("code", "code|program|function|implement", 
                ["Add: 'Include error handling'", "Add: 'Add type hints'"]),
            "explain": PromptTemplate("explain", "explain|describe|what is",
                ["Add: 'Provide examples'", "Add: 'Use simple language'"]),
            "debug": PromptTemplate("debug", "debug|fix|error|bug",
                ["Add: 'Show the corrected code'", "Add: 'Explain the root cause'"])
        }
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        prompt = params.get("prompt", "")
        task_type = params.get("task_type", "")
        model = params.get("model", "")
        
        if not prompt:
            return AlgorithmResult(status="error", error="No prompt provided")
        
        print(f"\n✨ Prompt Optimizer")
        
        # Analyze and optimize
        optimizations = []
        optimized_prompt = prompt
        
        # 1. Detect task type if not provided
        if not task_type:
            task_type = self._detect_task_type(prompt)
        
        # 2. Apply task-specific optimizations
        if task_type in self.templates:
            template = self.templates[task_type]
            optimizations.extend(template.optimizations)
        
        # 3. Apply general optimizations
        optimized_prompt, general_opts = self._apply_general_optimizations(optimized_prompt)
        optimizations.extend(general_opts)
        
        # 4. Add clarity enhancements
        optimized_prompt, clarity_opts = self._enhance_clarity(optimized_prompt)
        optimizations.extend(clarity_opts)
        
        # 5. Apply model-specific tweaks
        if model:
            optimized_prompt = self._apply_model_tweaks(optimized_prompt, model)
        
        print(f"   Applied {len(optimizations)} optimizations")
        
        return AlgorithmResult(
            status="success",
            data={
                "original": prompt,
                "optimized": optimized_prompt,
                "task_type": task_type,
                "optimizations": optimizations,
                "improvement_score": self._calculate_improvement(prompt, optimized_prompt)
            }
        )
    
    def _detect_task_type(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for task_type, template in self.templates.items():
            if re.search(template.pattern, prompt_lower):
                return task_type
        return "general"
    
    def _apply_general_optimizations(self, prompt: str) -> tuple:
        optimizations = []
        
        # Add structure if needed
        if len(prompt) > 100 and "\n" not in prompt:
            prompt = prompt.replace(". ", ".\n\n")
            optimizations.append("Added paragraph breaks")
        
        # Remove vague language
        vague_words = ["maybe", "perhaps", "kind of", "sort of"]
        for word in vague_words:
            if word in prompt.lower():
                optimizations.append(f"Consider removing vague: '{word}'")
        
        return prompt, optimizations
    
    def _enhance_clarity(self, prompt: str) -> tuple:
        optimizations = []
        
        # Add explicit instruction markers
        if not any(marker in prompt.lower() for marker in ["please", "task:", "goal:"]):
            prompt = f"Task: {prompt}"
            optimizations.append("Added task marker")
        
        # Suggest output format if missing
        if not any(fmt in prompt.lower() for fmt in ["format:", "output:", "return:"]):
            optimizations.append("Consider specifying output format")
        
        return prompt, optimizations
    
    def _apply_model_tweaks(self, prompt: str, model: str) -> str:
        model_lower = model.lower()
        
        if "claude" in model_lower:
            # Claude prefers structured prompts
            if not prompt.startswith("Task:"):
                prompt = f"Task:\n{prompt}"
        elif "gpt" in model_lower:
            # GPT works well with examples
            if "example" not in prompt.lower():
                prompt += "\n\n(Provide examples if helpful.)"
        
        return prompt
    
    def _calculate_improvement(self, original: str, optimized: str) -> float:
        # Simple heuristic based on length increase and structure
        length_diff = len(optimized) - len(original)
        structure_bonus = 0.1 if "\n" in optimized else 0
        marker_bonus = 0.1 if "Task:" in optimized else 0
        
        return min(1.0, 0.5 + (length_diff / 100) + structure_bonus + marker_bonus)


def register(algorithm_manager):
    algo = PromptOptimizerAlgorithm()
    algorithm_manager.register("PromptOptimizer", algo)
    print("✅ PromptOptimizer registered")


if __name__ == "__main__":
    algo = PromptOptimizerAlgorithm()
    result = algo.execute({
        "prompt": "Write a function to sort a list",
        "model": "claude"
    })
    print(f"Optimized: {result.data['optimized'][:100]}...")
    print(f"Improvement: {result.data['improvement_score']:.0%}")
