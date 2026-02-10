"""
Smart Model Router Algorithm
Route to optimal model tier (nano/mini/flash) for cost savings

Algorithm = CODE + STEPS
"""

import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class SmartModelRouterAlgorithm(BaseAlgorithm):
    """
    Smart Model Router - Cost Optimization
    
    Routes queries to appropriate model tier for 10-50x cost savings
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="SmartModelRouter",
            name="Smart Model Router",
            level="operational",
            category="routing",
            version="1.0",
            description="Route to optimal model tier (nano/mini/flash) based on complexity for 10-50x cost savings.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("task", "string", True, "Task description"),
                    IOField("complexity", "integer", False, "Override complexity 1-10"),
                    IOField("force_tier", "string", False, "Force specific tier (nano/mini/flash)")
                ],
                outputs=[
                    IOField("tier", "string", True, "Selected tier (nano/mini/flash)"),
                    IOField("model", "string", True, "Model name"),
                    IOField("provider", "string", True, "API provider"),
                    IOField("cost_per_1m_tokens", "float", True, "Cost per 1M tokens"),
                    IOField("reasoning", "string", True, "Why this tier was selected")
                ]
            ),
            
            steps=[
                "Step 1: Analyze task complexity (use provided or calculate)",
                "Step 2: Map complexity to tier:",
                "  - 1-3: nano (simple tasks, ~$0.0001/1M)",
                "  - 4-6: mini (medium tasks, ~$0.001/1M)",
                "  - 7-10: flash (complex tasks, ~$0.005/1M)",
                "Step 3: Get model name for tier",
                "Step 4: Calculate cost savings vs premium",
                "Step 5: Return tier selection + reasoning"
            ],
            
            tags=["routing", "cost-optimization", "smart-routing"],
            performance_target={
                "cost_savings": "10-50x vs always using premium model",
                "accuracy": "95% appropriate tier selection"
            }
        )
        
        # Tier configuration
        self.tiers = {
            "nano": {
                "model": "gpt-4.1-nano",
                "provider": "openai",
                "cost_per_1m": 0.0001,
                "complexity_range": (1, 3),
                "use_cases": ["simple_qa", "formatting", "classification", "extraction"]
            },
            "mini": {
                "model": "gpt-4.1-mini",
                "provider": "openai",
                "cost_per_1m": 0.001,
                "complexity_range": (4, 6),
                "use_cases": ["coding", "analysis", "generation", "translation"]
            },
            "flash": {
                "model": "gemini-2.5-flash",
                "provider": "v98",
                "cost_per_1m": 0.005,
                "complexity_range": (7, 10),
                "use_cases": ["complex_reasoning", "architecture", "multi_step", "creative"]
            }
        }
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute smart routing"""
        
        task = params.get("task", "")
        force_tier = params.get("force_tier")
        
        print(f"\n🎯 Smart Router: '{task[:60]}...'")
        
        try:
            # Step 1: Get complexity
            complexity = params.get("complexity")
            if not complexity:
                complexity = self._analyze_complexity(task)
            
            print(f"   📊 Complexity: {complexity}/10")
            
            # Step 2-3: Select tier & get model
            if force_tier and force_tier in self.tiers:
                tier_name = force_tier
                print(f"   🔒 Forced tier: {tier_name}")
            else:
                tier_name = self._select_tier_by_complexity(complexity)
                print(f"   🎯 Selected tier: {tier_name}")
            
            tier = self.tiers[tier_name]
            
            # Step 4: Calculate savings
            premium_cost = self.tiers["flash"]["cost_per_1m"]
            savings_pct = ((premium_cost - tier["cost_per_1m"]) / premium_cost) * 100
            
            # Step 5: Create reasoning
            reasoning = self._create_reasoning(complexity, tier_name, tier, savings_pct)
            
            print(f"   💰 Savings: {savings_pct:.0f}% vs premium")
            
            return AlgorithmResult(
                status="success",
                data={
                    "tier": tier_name,
                    "model": tier["model"],
                    "provider": tier["provider"],
                    "cost_per_1m_tokens": tier["cost_per_1m"],
                    "reasoning": reasoning
                },
                metadata={
                    "complexity": complexity,
                    "savings_vs_premium_pct": savings_pct,
                    "use_cases": tier["use_cases"]
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Routing failed: {str(e)}")
    
    def _analyze_complexity(self, task: str) -> int:
        """
        Analyze task complexity (1-10)
        
        Uses heuristics - in production would use lightweight LLM
        """
        task_lower = task.lower()
        
        # Very simple (1-2)
        if len(task.split()) <= 5:
            return 2
        
        # Simple questions (2-3)
        simple_keywords = ["what", "when", "where", "who", "define", "explain", "list"]
        if any(kw in task_lower for kw in simple_keywords) and len(task.split()) <= 15:
            return 3
        
        # Complex indicators (8-10)
        complex_keywords = ["design", "architect", "implement", "optimize", "analyze deeply", 
                           "create system", "build application", "complex"]
        if any(kw in task_lower for kw in complex_keywords):
            return 8
        
        # Code-related (5-7)
        code_keywords = ["code", "function", "class", "api", "algorithm"]
        if any(kw in task_lower for kw in code_keywords):
            return 6
        
        # Medium (4-5)
        return 5
    
    def _select_tier_by_complexity(self, complexity: int) -> str:
        """Select tier based on complexity"""
        for tier_name, tier_info in self.tiers.items():
            min_c, max_c = tier_info["complexity_range"]
            if min_c <= complexity <= max_c:
                return tier_name
        return "flash"  # Default to flash for edge cases
    
    def _create_reasoning(self, complexity: int, tier_name: str, tier: Dict, savings_pct: float) -> str:
        """Generate human-readable reasoning"""
        
        reasons = [
            f"Task complexity: {complexity}/10 → {tier_name} tier",
            f"Model: {tier['model']}",
            f"Cost: ${tier['cost_per_1m']:.4f}/1M tokens",
            f"Savings: {savings_pct:.0f}% vs premium model"
        ]
        
        return " | ".join(reasons)


def register(algorithm_manager):
    """Register Smart Model Router Algorithm"""
    try:
        algo = SmartModelRouterAlgorithm()
        algorithm_manager.register("SmartModelRouter", algo)
        print("✅ Smart Model Router Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register SmartModelRouter: {e}")
