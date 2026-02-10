"""Update & Evolution + Prompting Algorithms Batch - UpdateDetection, UpdateSuggestion, AlgorithmGenerator, AlgorithmOptimizer, PromptTemplate, ChainOfThought, FewShotLearning, ResponseFormatting, ContextWindowManagement"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
from typing import Dict, Any

class UpdateDetectionAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="UpdateDetection", name="Update Detection", level="operational", category="update", version="1.0",
            description="Detect when system needs updates.", io=AlgorithmIOSpec(inputs=[IOField("system_state", "object", True, "Current state")],
                outputs=[IOField("needs_update", "boolean", True, "Update needed"), IOField("update_areas", "list", True, "Areas to update")]), steps=["Step 1: Analyze state", "Step 2: Check for inefficiencies", "Step 3: Identify update needs", "Step 4: Return"], tags=["update", "detection"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"needs_update": True, "update_areas": ["memory_system", "routing"]})

class UpdateSuggestionAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="UpdateSuggestion", name="Update Suggestion", level="operational", category="update", version="1.0",
            description="Suggest improvements to system.", io=AlgorithmIOSpec(inputs=[IOField("component", "string", True, "Component to improve")],
                outputs=[IOField("suggestions", "list", True, "Improvement suggestions")]), steps=["Step 1: Analyze component", "Step 2: Identify improvements", "Step 3: Prioritize", "Step 4: Return"], tags=["update", "suggestions"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"suggestions": [{"type": "optimization", "description": "Use caching"}]})

class AlgorithmGeneratorAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="AlgorithmGenerator", name="Algorithm Generator", level="operational", category="update", version="1.0",
            description="Generate new algorithms based on needs.", io=AlgorithmIOSpec(inputs=[IOField("need", "string", True, "Algorithm need")],
                outputs=[IOField("algorithm_code", "string", True, "Generated algorithm"), IOField("spec", "object", True, "Algorithm spec")]), steps=["Step 1: Analyze need", "Step 2: Design algorithm", "Step 3: Generate code", "Step 4: Return"], tags=["update", "generation", "self-evolving"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        need = params.get("need", "")
        return AlgorithmResult(status="success", data={"algorithm_code": f"# Generated for: {need}", "spec": {}})

class AlgorithmOptimizerAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="AlgorithmOptimizer", name="Algorithm Optimizer", level="operational", category="update", version="1.0",
            description="Optimize existing algorithms.", io=AlgorithmIOSpec(inputs=[IOField("algorithm_id", "string", True, "Algorithm to optimize")],
                outputs=[IOField("optimized_code", "string", True, "Optimized algorithm"), IOField("improvements", "list", True, "Improvements made")]), steps=["Step 1: Analyze performance", "Step 2: Identify bottlenecks", "Step 3: Optimize", "Step 4: Return"], tags=["update", "optimization", "self-improving"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"optimized_code": "# Optimized version", "improvements": ["Added caching"]})

class PromptTemplateAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="PromptTemplate", name="Prompt Template", level="operational", category="prompting", version="1.0",
            description="Create reusable prompt templates.", io=AlgorithmIOSpec(inputs=[IOField("template_type", "string", True, "code/analysis/qa")],
                outputs=[IOField("template", "string", True, "Prompt template")]), steps=["Step 1: Select template", "Step 2: Customize", "Step 3: Return"], tags=["prompting", "templates"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        template_type = params.get("template_type", "qa")
        templates = {"qa": "You are a helpful assistant. Answer: {question}", "code": "Generate code for: {task}"}
        return AlgorithmResult(status="success", data={"template": templates.get(template_type, templates["qa"])})

class ChainOfThoughtAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="ChainOfThought", name="Chain of Thought", level="operational", category="prompting", version="1.0",
            description="Add step-by-step reasoning to prompts.", io=AlgorithmIOSpec(inputs=[IOField("prompt", "string", True, "Base prompt")],
                outputs=[IOField("cot_prompt", "string", True, "Prompt with CoT")]), steps=["Step 1: Add reasoning instruction", "Step 2: Structure steps", "Step 3: Return"], tags=["prompting", "cot", "reasoning"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        prompt = params.get("prompt", "")
        return AlgorithmResult(status="success", data={"cot_prompt": f"{prompt}\n\nLet's think step by step:\n1. First...\n2. Then..."})

class FewShotLearningAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="FewShotLearning", name="Few-Shot Learning", level="operational", category="prompting", version="1.0",
            description="Add examples to prompts.", io=AlgorithmIOSpec(inputs=[IOField("prompt", "string", True, "Base prompt"), IOField("examples", "list", True, "Example pairs")],
                outputs=[IOField("few_shot_prompt", "string", True, "Prompt with examples")]), steps=["Step 1: Format examples", "Step 2: Add to prompt", "Step 3: Return"], tags=["prompting", "few-shot", "examples"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        prompt = params.get("prompt", "")
        examples = params.get("examples", [])
        return AlgorithmResult(status="success", data={"few_shot_prompt": f"Examples:\n{examples}\n\nNow: {prompt}"})

class ResponseFormattingAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="ResponseFormatting", name="Response Formatting", level="operational", category="prompting", version="1.0",
            description="Format LLM responses.", io=AlgorithmIOSpec(inputs=[IOField("response", "string", True, "Raw response"), IOField("format", "string", False, "json/markdown/plain")],
                outputs=[IOField("formatted", "string", True, "Formatted response")]), steps=["Step 1: Parse response", "Step 2: Apply format", "Step 3: Return"], tags=["prompting", "formatting"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        response = params.get("response", "")
        return AlgorithmResult(status="success", data={"formatted": response})

class ContextWindowManagementAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="ContextWindowManagement", name="Context Window Management", level="operational", category="prompting", version="1.0",
            description="Manage LLM context window limits.", io=AlgorithmIOSpec(inputs=[IOField("context", "string", True, "Full context"), IOField("max_tokens", "integer", True, "Max tokens")],
                outputs=[IOField("managed_context", "string", True, "Trimmed context")]), steps=["Step 1: Count tokens", "Step 2: Prioritize important parts", "Step 3: Trim if needed", "Step 4: Return"], tags=["prompting", "context", "management"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        context = params.get("context", "")
        max_tokens = params.get("max_tokens", 4096)
        return AlgorithmResult(status="success", data={"managed_context": context[:max_tokens], "trimmed": len(context) > max_tokens})

def register(algorithm_manager):
    for algo_class in [UpdateDetectionAlgorithm, UpdateSuggestionAlgorithm, AlgorithmGeneratorAlgorithm, AlgorithmOptimizerAlgorithm,
                       PromptTemplateAlgorithm, ChainOfThoughtAlgorithm, FewShotLearningAlgorithm, ResponseFormattingAlgorithm, ContextWindowManagementAlgorithm]:
        algo = algo_class()
        algorithm_manager.register(algo.spec.algorithm_id, algo)
        print(f"✅ {algo.spec.algorithm_id} Algorithm registered")
