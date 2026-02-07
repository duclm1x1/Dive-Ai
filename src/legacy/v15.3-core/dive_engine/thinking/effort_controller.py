"""
Dive Engine V2 - Effort Controller
===================================

This module implements reasoning effort control that combines:
- GPT-5.2 reasoning.effort parameter (low/medium/high)
- Claude Opus 4.5 budget_tokens allocation

The controller determines how much computational effort to allocate
for reasoning based on task requirements and budget constraints.

Key Concepts:
- Effort Levels: low, medium, high
- Budget Tokens: Max tokens for thinking (Claude-style)
- Inference-time Scaling: Multi-sample, self-consistency, search-beam
- Tool Verification Loop: Iterative tool-based verification
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from dive_engine.core.models import (
    BudgetPlan,
    CognitivePhase,
    EffortLevel,
    EffortPlan,
    EvidenceLevel,
    RiskClass,
    RouterDecision,
    RoutingPath,
    RunSpec,
    ThinkingStrategy,
    utcnow_iso,
)


# =============================================================================
# EFFORT CONFIGURATION
# =============================================================================

@dataclass
class EffortConfig:
    """Configuration for a specific effort level."""
    level: EffortLevel
    
    # Token budgets
    budget_tokens: int
    
    # Inference scaling
    num_samples: int
    use_self_consistency: bool
    use_search_beam: bool
    beam_width: int
    
    # Tool verification
    max_tool_verify_iterations: int
    tool_verify_enabled: bool
    
    # Thinking features
    interleaved_thinking_enabled: bool
    preserve_thinking_blocks: bool
    
    # Phases to execute
    phases: List[CognitivePhase]


# Default effort configurations
DEFAULT_EFFORT_CONFIGS: Dict[EffortLevel, EffortConfig] = {
    EffortLevel.LOW: EffortConfig(
        level=EffortLevel.LOW,
        budget_tokens=2000,
        num_samples=1,
        use_self_consistency=False,
        use_search_beam=False,
        beam_width=1,
        max_tool_verify_iterations=1,
        tool_verify_enabled=True,
        interleaved_thinking_enabled=False,
        preserve_thinking_blocks=False,
        phases=[
            CognitivePhase.INPUT_PROCESSING,
            CognitivePhase.ANALYSIS,
            CognitivePhase.OUTPUT_GENERATION,
        ],
    ),
    
    EffortLevel.MEDIUM: EffortConfig(
        level=EffortLevel.MEDIUM,
        budget_tokens=10000,
        num_samples=2,
        use_self_consistency=True,
        use_search_beam=False,
        beam_width=1,
        max_tool_verify_iterations=3,
        tool_verify_enabled=True,
        interleaved_thinking_enabled=True,
        preserve_thinking_blocks=True,
        phases=[
            CognitivePhase.INPUT_PROCESSING,
            CognitivePhase.EXPLORATION,
            CognitivePhase.ANALYSIS,
            CognitivePhase.VERIFICATION,
            CognitivePhase.CONCLUSION,
            CognitivePhase.OUTPUT_GENERATION,
        ],
    ),
    
    EffortLevel.HIGH: EffortConfig(
        level=EffortLevel.HIGH,
        budget_tokens=50000,
        num_samples=5,
        use_self_consistency=True,
        use_search_beam=True,
        beam_width=3,
        max_tool_verify_iterations=5,
        tool_verify_enabled=True,
        interleaved_thinking_enabled=True,
        preserve_thinking_blocks=True,
        phases=list(CognitivePhase),  # All phases
    ),
}


# Strategy-specific effort adjustments
STRATEGY_EFFORT_ADJUSTMENTS: Dict[ThinkingStrategy, Dict[str, Any]] = {
    ThinkingStrategy.SINGLE_PASS: {
        "num_samples": 1,
        "use_self_consistency": False,
        "use_search_beam": False,
        "interleaved_thinking_enabled": False,
    },
    
    ThinkingStrategy.CHAIN_OF_THOUGHT: {
        "use_self_consistency": True,
        "interleaved_thinking_enabled": False,
    },
    
    ThinkingStrategy.EXTENDED_THINKING: {
        "budget_tokens_multiplier": 2.0,
        "interleaved_thinking_enabled": True,
        "preserve_thinking_blocks": True,
    },
    
    ThinkingStrategy.INTERLEAVED: {
        "interleaved_thinking_enabled": True,
        "max_tool_verify_iterations_multiplier": 1.5,
    },
    
    ThinkingStrategy.MULTI_SAMPLE: {
        "num_samples_multiplier": 2.0,
        "use_self_consistency": True,
    },
    
    ThinkingStrategy.SEARCH_BEAM: {
        "use_search_beam": True,
        "beam_width_multiplier": 1.5,
    },
}


class EffortController:
    """
    Controller for reasoning effort allocation.
    
    This controller determines:
    1. Effort level (low/medium/high)
    2. Token budget for thinking
    3. Inference-time scaling parameters
    4. Tool verification loop settings
    
    The controller emits effort_plan.json and budget_plan.json as E2 artifacts.
    """
    
    def __init__(
        self,
        effort_configs: Optional[Dict[EffortLevel, EffortConfig]] = None,
        strategy_adjustments: Optional[Dict[ThinkingStrategy, Dict[str, Any]]] = None,
    ):
        """
        Initialize the effort controller.
        
        Args:
            effort_configs: Custom effort configurations (uses defaults if None)
            strategy_adjustments: Custom strategy adjustments (uses defaults if None)
        """
        self.effort_configs = effort_configs or DEFAULT_EFFORT_CONFIGS
        self.strategy_adjustments = strategy_adjustments or STRATEGY_EFFORT_ADJUSTMENTS
    
    def plan_effort(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
    ) -> EffortPlan:
        """
        Create an effort plan based on run spec and routing decision.
        
        Args:
            run_spec: The run specification
            router_decision: The routing decision
            
        Returns:
            EffortPlan with all effort parameters
        """
        # Determine base effort level
        effort_level = self._determine_effort_level(run_spec, router_decision)
        
        # Get base configuration
        base_config = self.effort_configs[effort_level]
        
        # Apply strategy-specific adjustments
        adjusted_config = self._apply_strategy_adjustments(
            base_config,
            router_decision.thinking_strategy,
        )
        
        # Apply budget constraints
        final_config = self._apply_budget_constraints(adjusted_config, run_spec)
        
        # Build effort plan
        effort_plan = EffortPlan(
            run_id=run_spec.run_id,
            effort_level=effort_level,
            budget_tokens=final_config["budget_tokens"],
            num_samples=final_config["num_samples"],
            use_self_consistency=final_config["use_self_consistency"],
            use_search_beam=final_config["use_search_beam"],
            beam_width=final_config["beam_width"],
            max_tool_verify_iterations=final_config["max_tool_verify_iterations"],
            tool_verify_enabled=final_config["tool_verify_enabled"],
            interleaved_thinking_enabled=final_config["interleaved_thinking_enabled"],
            preserve_thinking_blocks=final_config["preserve_thinking_blocks"],
            phases=final_config["phases"],
            rationale=self._generate_rationale(
                effort_level,
                router_decision,
                run_spec,
            ),
        )
        
        return effort_plan
    
    def plan_budget(
        self,
        run_spec: RunSpec,
        effort_plan: EffortPlan,
    ) -> BudgetPlan:
        """
        Create a budget plan based on run spec and effort plan.
        
        Args:
            run_spec: The run specification
            effort_plan: The effort plan
            
        Returns:
            BudgetPlan with all budget parameters
        """
        # Estimate token usage based on effort
        input_budget = self._estimate_input_tokens(run_spec)
        output_budget = self._estimate_output_tokens(effort_plan)
        
        # Estimate cost
        estimated_cost = self._estimate_cost(
            input_budget,
            output_budget,
            effort_plan.budget_tokens,
        )
        
        budget_plan = BudgetPlan(
            run_id=run_spec.run_id,
            input_token_budget=input_budget,
            output_token_budget=output_budget,
            thinking_token_budget=effort_plan.budget_tokens,
            latency_budget_ms=run_spec.latency_budget_ms,
            cost_budget_usd=run_spec.cost_budget_usd,
            estimated_cost_usd=estimated_cost,
            max_llm_calls=run_spec.max_llm_calls,
            max_tool_calls=run_spec.max_tool_calls,
        )
        
        return budget_plan
    
    def _determine_effort_level(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
    ) -> EffortLevel:
        """Determine effort level based on routing and requirements."""
        # Fast path always uses low effort
        if router_decision.path == RoutingPath.FAST:
            return EffortLevel.LOW
        
        # Security/performance/release modes require high effort
        high_effort_modes = {"security", "security-review", "performance", "release", "build"}
        mode_str = run_spec.mode.value if hasattr(run_spec.mode, 'value') else str(run_spec.mode)
        if mode_str.lower() in high_effort_modes:
            return EffortLevel.HIGH
        
        # E3 evidence requires high effort
        if run_spec.required_evidence_level == EvidenceLevel.E3:
            return EffortLevel.HIGH
        
        # High/critical risk requires high effort
        if router_decision.risk_class in {RiskClass.HIGH, RiskClass.CRITICAL}:
            return EffortLevel.HIGH
        
        # Extended thinking strategy suggests high effort
        if router_decision.thinking_strategy in {
            ThinkingStrategy.EXTENDED_THINKING,
            ThinkingStrategy.SEARCH_BEAM,
        }:
            return EffortLevel.HIGH
        
        # Medium complexity gets medium effort
        if router_decision.complexity_score >= 0.4:
            return EffortLevel.MEDIUM
        
        # Default to medium for think path
        return EffortLevel.MEDIUM
    
    def _apply_strategy_adjustments(
        self,
        base_config: EffortConfig,
        strategy: ThinkingStrategy,
    ) -> Dict[str, Any]:
        """Apply strategy-specific adjustments to base configuration."""
        config = {
            "budget_tokens": base_config.budget_tokens,
            "num_samples": base_config.num_samples,
            "use_self_consistency": base_config.use_self_consistency,
            "use_search_beam": base_config.use_search_beam,
            "beam_width": base_config.beam_width,
            "max_tool_verify_iterations": base_config.max_tool_verify_iterations,
            "tool_verify_enabled": base_config.tool_verify_enabled,
            "interleaved_thinking_enabled": base_config.interleaved_thinking_enabled,
            "preserve_thinking_blocks": base_config.preserve_thinking_blocks,
            "phases": base_config.phases,
        }
        
        adjustments = self.strategy_adjustments.get(strategy, {})
        
        for key, value in adjustments.items():
            if key.endswith("_multiplier"):
                base_key = key.replace("_multiplier", "")
                if base_key in config:
                    config[base_key] = int(config[base_key] * value)
            else:
                config[key] = value
        
        return config
    
    def _apply_budget_constraints(
        self,
        config: Dict[str, Any],
        run_spec: RunSpec,
    ) -> Dict[str, Any]:
        """Apply budget constraints to configuration."""
        # If cost budget is tight, reduce effort
        if run_spec.cost_budget_usd < 0.5:
            config["budget_tokens"] = min(config["budget_tokens"], 5000)
            config["num_samples"] = min(config["num_samples"], 2)
            config["beam_width"] = min(config["beam_width"], 2)
        
        # If latency budget is tight, reduce iterations
        if run_spec.latency_budget_ms < 60000:  # Less than 1 minute
            config["max_tool_verify_iterations"] = min(
                config["max_tool_verify_iterations"], 2
            )
            config["num_samples"] = min(config["num_samples"], 2)
        
        return config
    
    def _estimate_input_tokens(self, run_spec: RunSpec) -> int:
        """Estimate input token usage."""
        # Base estimate from prompt
        prompt_tokens = len(run_spec.prompt) // 4  # Rough estimate
        
        # Add context files estimate
        context_tokens = len(run_spec.context_files) * 2000  # Estimate per file
        
        return min(prompt_tokens + context_tokens, 100000)
    
    def _estimate_output_tokens(self, effort_plan: EffortPlan) -> int:
        """Estimate output token usage."""
        base_output = 2000
        
        # Scale by effort level
        effort_multipliers = {
            EffortLevel.LOW: 1.0,
            EffortLevel.MEDIUM: 2.0,
            EffortLevel.HIGH: 4.0,
        }
        
        multiplier = effort_multipliers.get(effort_plan.effort_level, 2.0)
        
        # Account for multiple samples
        sample_multiplier = effort_plan.num_samples
        
        return int(base_output * multiplier * sample_multiplier)
    
    def _estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        thinking_tokens: int,
    ) -> float:
        """Estimate cost in USD."""
        # Rough estimates based on typical pricing
        input_cost_per_1k = 0.003
        output_cost_per_1k = 0.015
        thinking_cost_per_1k = 0.015
        
        cost = (
            (input_tokens / 1000) * input_cost_per_1k +
            (output_tokens / 1000) * output_cost_per_1k +
            (thinking_tokens / 1000) * thinking_cost_per_1k
        )
        
        return round(cost, 4)
    
    def _generate_rationale(
        self,
        effort_level: EffortLevel,
        router_decision: RouterDecision,
        run_spec: RunSpec,
    ) -> str:
        """Generate human-readable rationale for effort selection."""
        parts = [
            f"Effort level: {effort_level.value}",
            f"Routing path: {router_decision.path.value}",
            f"Thinking strategy: {router_decision.thinking_strategy.value}",
            f"Risk class: {router_decision.risk_class.value}",
            f"Required evidence: {run_spec.required_evidence_level.value}",
        ]
        
        if effort_level == EffortLevel.HIGH:
            parts.append("High effort selected due to: " + self._high_effort_reason(
                router_decision, run_spec
            ))
        
        return " | ".join(parts)
    
    def _high_effort_reason(
        self,
        router_decision: RouterDecision,
        run_spec: RunSpec,
    ) -> str:
        """Explain why high effort was selected."""
        reasons = []
        
        mode_str = run_spec.mode.value if hasattr(run_spec.mode, 'value') else str(run_spec.mode)
        if mode_str.lower() in {"security", "security-review", "performance", "release"}:
            reasons.append(f"mode={run_spec.mode}")
        
        if run_spec.required_evidence_level == EvidenceLevel.E3:
            reasons.append("E3 evidence required")
        
        if router_decision.risk_class in {RiskClass.HIGH, RiskClass.CRITICAL}:
            reasons.append(f"risk={router_decision.risk_class.value}")
        
        if router_decision.thinking_strategy in {
            ThinkingStrategy.EXTENDED_THINKING,
            ThinkingStrategy.SEARCH_BEAM,
        }:
            reasons.append(f"strategy={router_decision.thinking_strategy.value}")
        
        return ", ".join(reasons) if reasons else "default policy"
    
    def emit_artifacts(
        self,
        effort_plan: EffortPlan,
        budget_plan: BudgetPlan,
        output_dir: Path,
    ) -> Dict[str, Path]:
        """
        Emit effort_plan.json and budget_plan.json artifacts.
        
        Args:
            effort_plan: The effort plan
            budget_plan: The budget plan
            output_dir: Directory to write artifacts
            
        Returns:
            Dict mapping artifact names to paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts = {}
        
        # Emit effort_plan.json
        effort_path = output_dir / "effort_plan.json"
        effort_path.write_text(
            json.dumps(effort_plan.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        artifacts["effort_plan"] = effort_path
        
        # Emit budget_plan.json
        budget_path = output_dir / "budget_plan.json"
        budget_path.write_text(
            json.dumps(budget_plan.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        artifacts["budget_plan"] = budget_path
        
        return artifacts
