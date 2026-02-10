"""
Hybrid Prompting Algorithm
Optimize prompts for LLM for best results

Algorithm = CODE + STEPS
"""

import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class HybridPromptingAlgorithm(BaseAlgorithm):
    """
    Hybrid Prompting - Optimize prompts for LLM
    
    Combines multiple prompting techniques for best results
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="HybridPrompting",
            name="Hybrid Prompting",
            level="operational",
            category="prompting",
            version="1.0",
            description="Optimize prompts using hybrid techniques: clear instructions, examples, chain-of-thought, format specification.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("raw_prompt", "string", True, "Raw user prompt"),
                    IOField("task_type", "string", False, "Type: qa/code/analysis/creative"),
                    IOField("include_examples", "boolean", False, "Add few-shot examples"),
                    IOField("include_cot", "boolean", False, "Add chain-of-thought"),
                    IOField("output_format", "string", False, "Desired format: json/markdown/plain")
                ],
                outputs=[
                    IOField("optimized_prompt", "string", True, "Optimized prompt"),
                    IOField("techniques_used", "list", True, "Applied techniques"),
                    IOField("estimated_tokens", "integer", True, "Prompt token count")
                ]
            ),
            
            steps=[
                "Step 1: Analyze raw prompt & task type",
                "Step 2: Apply clear instruction formatting",
                "Step 3: Add few-shot examples if requested",
                "Step 4: Add chain-of-thought if requested",
                "Step 5: Specify output format",
                "Step 6: Estimate token count",
                "Step 7: Return optimized prompt"
            ],
            
            tags=["prompting", "optimization", " hybrid", "llm"],
            performance_target={
                "improvement": "20-50% better LLM responses",
                "token_overhead": "<30% increase"
            }
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute hybrid prompting"""
        
        raw_prompt = params.get("raw_prompt", "")
        task_type = params.get("task_type", "qa")
        include_examples = params.get("include_examples", False)
        include_cot = params.get("include_cot", False)
        output_format = params.get("output_format", "plain")
        
        print(f"\n📝 Hybrid Prompting: '{raw_prompt[:50]}...'")
        
        try:
            techniques_used = []
            
            # Step 1: Analyze
            task_type = self._detect_task_type(raw_prompt, task_type)
            print(f"   🎯 Task type: {task_type}")
            
            # Step 2: Clear instructions
            optimized = self._apply_clear_instructions(raw_prompt, task_type)
            techniques_used.append("clear_instructions")
            
            # Step 3: Few-shot examples
            if include_examples:
                optimized = self._add_examples(optimized, task_type)
                techniques_used.append("few_shot_examples")
            
            # Step 4: Chain-of-thought
            if include_cot or task_type in ["code", "analysis"]:
                optimized = self._add_chain_of_thought(optimized)
                techniques_used.append("chain_of_thought")
            
            # Step 5: Output format
            optimized = self._specify_output_format(optimized, output_format)
            techniques_used.append(f"format_{output_format}")
            
            # Step 6: Estimate tokens
            est_tokens = len(optimized.split()) * 1.3  # Rough estimate
            
            print(f"   ✅ Applied {len(techniques_used)} techniques")
            print(f"   📊 Estimated tokens: {est_tokens:.0f}")
            
            # Step 7: Return
            return AlgorithmResult(
                status="success",
                data={
                    "optimized_prompt": optimized,
                    "techniques_used": techniques_used,
                    "estimated_tokens": int(est_tokens)
                },
                metadata={
                    "task_type": task_type,
                    "original_length": len(raw_prompt),
                    "optimized_length": len(optimized)
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Prompting failed: {str(e)}"
            )
    
    def _detect_task_type(self, prompt: str, provided: str) -> str:
        """Detect task type from prompt"""
        if provided and provided != "qa":
            return provided
        
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ["code", "function", "class", "implement"]):
            return "code"
        elif any(kw in prompt_lower for kw in ["analyze", "evaluate", "compare"]):
            return "analysis"
        elif any(kw in prompt_lower for kw in ["create", "write", "generate", "story"]):
            return "creative"
        
        return "qa"
    
    def _apply_clear_instructions(self, prompt: str, task_type: str) -> str:
        """Apply clear instruction formatting"""
        
        # Add role-based framing
        role_prompts = {
            "code": "You are an expert software engineer.",
            "analysis": "You are an expert analyst.",
            "creative": "You are a creative writer.",
            "qa": "You are a helpful assistant."
        }
        
        formatted = f"{role_prompts.get(task_type, '')}\n\n"
        formatted += f"Task: {prompt}\n\n"
        formatted += "Provide a clear, accurate, and complete response."
        
        return formatted
    
    def _add_examples(self, prompt: str, task_type: str) -> str:
        """Add few-shot examples"""
        
        # Example templates by task type
        examples = {
            "code": "\n\nExample:\nTask: Create a function to add two numbers\nResponse: ```python\ndef add(a, b):\n    return a + b\n```",
            "analysis": "\n\nExample:\nTask: Analyze the pros and cons of X\nResponse: **Pros:** 1. ..., 2. ... **Cons:** 1. ..., 2. ...",
            "qa": "\n\nExample:\nQuestion: What is X?\nAnswer: X is ...",
        }
        
        return prompt + examples.get(task_type, "")
    
    def _add_chain_of_thought(self, prompt: str) -> str:
        """Add chain-of-thought prompting"""
        
        cot_instruction = "\n\nThink step-by-step:\n1. First, ...\n2. Then, ...\n3. Finally, ..."
        return prompt + cot_instruction
    
    def _specify_output_format(self, prompt: str, output_format: str) -> str:
        """Specify desired output format"""
        
        format_instructions = {
            "json": "\n\nProvide your response in valid JSON format.",
            "markdown": "\n\nProvide your response in well-formatted Markdown.",
            "plain": "\n\nProvide your response in plain text."
        }
        
        return prompt + format_instructions.get(output_format, "")


def register(algorithm_manager):
    """Register Hybrid Prompting Algorithm"""
    try:
        algo = HybridPromptingAlgorithm()
        algorithm_manager.register("HybridPrompting", algo)
        print("✅ Hybrid Prompting Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register HybridPrompting: {e}")
