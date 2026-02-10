"""
CLI Ask Command Algorithm
Implements `dive ask` with smart model routing

Algorithm = CODE + STEPS
"""

import os
import sys
import requests
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class CLIAskAlgorithm(BaseAlgorithm):
    """
    CLI Ask Command - Smart Model Routing
    
    Implements `dive ask` command with intelligent model tier selection
    for cost optimization (10-50x savings)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="CLIAsk",
            name="CLI Ask Command",
            level="operational",
            category="cli",
            version="1.0",
            description="Handle 'dive ask' command with smart model routing. Analyzes question complexity and routes to optimal model tier (nano/mini/flash) for cost savings.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("question", "string", True, "User's question"),
                    IOField("context", "object", False, "Session context"),
                    IOField("complexity_hint", "integer", False, "Override complexity 1-10")
                ],
                outputs=[
                    IOField("answer", "string", True, "LLM response"),
                    IOField("model_used", "string", True, "Model tier used"),
                    IOField("cost_estimate", "float", True, "Estimated cost in USD"),
                    IOField("tokens", "integer", True, "Token count")
                ]
            ),
            
            steps=[
                "Step 1: Analyze question complexity (1-10 scale)",
                "Step 2: Route to model tier:",
                "  - Complexity 1-3 → nano (gpt-4.1-nano) ~$0.0001",
                "  - Complexity 4-6 → mini (gpt-4.1-mini) ~$0.001",
                "  - Complexity 7-10 → flash (gemini-2.5-flash) ~$0.005",
                "Step 3: Execute LLM query with selected model",
                "Step 4: Calculate actual cost based on tokens",
                "Step 5: Return answer + metadata (model, cost, tokens)"
            ],
            
            tags=["cli", "smart-routing", "cost-optimization"],
            performance_target={
                "cost_savings": "10-50x vs always using premium model",
                "latency": "nano: 50ms, mini: 200ms, flash: 500ms"
            }
        )
        
        # Model tier configuration
        self.model_tiers = {
            "nano": {
                "model": "gpt-4.1-nano",
                "cost_per_1k": 0.0001,
                "complexity_range": (1, 3),
                "use_cases": ["simple_qa", "formatting", "classification"]
            },
            "mini": {
                "model": "gpt-4.1-mini",
                "cost_per_1k": 0.001,
                "complexity_range": (4, 6),
                "use_cases": ["coding", "analysis", "generation"]
            },
            "flash": {
                "model": "gemini-2.5-flash",
                "cost_per_1k": 0.005,
                "complexity_range": (7, 10),
                "use_cases": ["complex_reasoning", "architecture", "multi_step"]
            }
        }
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute dive ask command"""
        
        question = params.get("question", "")
        complexity_hint = params.get("complexity_hint")
        context = params.get("context", {})
        
        print(f"\n💬 Dive Ask: '{question[:60]}...'")
        
        try:
            # Step 1: Analyze complexity
            complexity = complexity_hint or self._analyze_complexity(question)
            print(f"   🔍 Complexity: {complexity}/10")
            
            # Step 2: Route to model tier
            tier_name = self._select_tier(complexity)
            tier = self.model_tiers[tier_name]
            print(f"   🎯 Selected: {tier_name} ({tier['model']})")
            
            # Step 3: Execute query
            answer, tokens = self._query_llm(question, tier, context)
            
            # Step 4: Calculate cost
            cost = (tokens / 1000) * tier["cost_per_1k"]
            
            # Step 5: Return result
            return AlgorithmResult(
                status="success",
                data={
                    "answer": answer,
                    "model_used": tier["model"],
                    "cost_estimate": cost,
                    "tokens": tokens
                },
                metadata={
                    "complexity": complexity,
                    "tier": tier_name,
                    "savings_vs_premium": f"{(0.005 - tier['cost_per_1k']) / 0.005 * 100:.0f}%"
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Ask failed: {str(e)}"
            )
    
    def _analyze_complexity(self, question: str) -> int:
        """
        Analyze question complexity (1-10)
        
        Simple heuristic for now - in production would use LLM
        """
        question_lower = question.lower()
        
        # Simple questions (complexity 1-3)
        simple_keywords = ["what", "when", "where", "who", "define", "explain"]
        if len(question.split()) <= 10 and any(kw in question_lower for kw in simple_keywords):
            return 2
        
        # Complex questions (complexity 7-10)
        complex_keywords = ["design", "architect", "implement", "optimize", "analyze deeply"]
        if any(kw in questionlower for kw in complex_keywords):
            return 8
        
        # Medium (complexity 4-6)
        return 5
    
    def _select_tier(self, complexity: int) -> str:
        """Select model tier based on complexity"""
        for tier_name, tier_info in self.model_tiers.items():
            min_c, max_c = tier_info["complexity_range"]
            if min_c <= complexity <= max_c:
                return tier_name
        return "flash"  # Default to flash for very high complexity
    
    def _query_llm(self, question: str, tier: Dict, context: Dict) -> tuple[str, int]:
        """
        Query LLM with selected model
        
        In production: make actual API call
        For now: simulate response
        """
        
        # TODO: Replace with actual LLM API call
        # This is a placeholder simulation
        
        simulated_answer = f"[{tier['model']}] Answer to: {question}"
        simulated_tokens = len(question.split()) * 10  # Rough estimate
        
        return simulated_answer, simulated_tokens


def register(algorithm_manager):
    """Register CLI Ask Algorithm"""
    try:
        algo = CLIAskAlgorithm()
        algorithm_manager.register("CLIAsk", algo)
        print("✅ CLI Ask Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register CLIAsk: {e}")
