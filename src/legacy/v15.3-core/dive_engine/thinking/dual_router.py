"""
Dive Engine V2 - Dual Thinking Router
======================================

This module implements the dual-path routing logic that combines:
- GPT-5.2 reasoning model routing (fast vs reasoning path)
- Claude Opus 4.5 Extended Thinking activation

The router analyzes task complexity, risk, and evidence requirements
to determine the optimal thinking strategy.

Key Concepts:
- Fast Path: Direct response for simple/low-risk tasks
- Think Path: Extended reasoning for complex/high-risk tasks
- Thinking Strategy Selection: Chain-of-thought, extended thinking, interleaved, etc.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from dive_engine.core.models import (
    CognitivePhase,
    EffortLevel,
    EvidenceLevel,
    RiskClass,
    RouterDecision,
    RoutingPath,
    RunSpec,
    TaskType,
    ThinkingStrategy,
    utcnow_iso,
)


# =============================================================================
# ROUTING POLICIES
# =============================================================================

# High-risk file patterns (trigger think path)
HIGH_RISK_PATTERNS = [
    r"auth",
    r"login",
    r"password",
    r"crypto",
    r"encrypt",
    r"decrypt",
    r"secret",
    r"token",
    r"billing",
    r"payment",
    r"credit",
    r"admin",
    r"permission",
    r"role",
    r"privilege",
    r"security",
    r"vulnerability",
    r"injection",
    r"xss",
    r"csrf",
    r"sql",
]

# Task types that always require think path
THINK_REQUIRED_TASKS = {
    TaskType.SECURITY,
    TaskType.PERFORMANCE,
    TaskType.DEBUG,
}

# Evidence levels that require think path
THINK_REQUIRED_EVIDENCE = {
    EvidenceLevel.E2,
    EvidenceLevel.E3,
}


@dataclass
class RoutingPolicy:
    """A single routing policy rule."""
    name: str
    conditions: Dict[str, Any]
    route: RoutingPath
    thinking_strategy: ThinkingStrategy
    rationale: str
    priority: int = 0


# Default routing policies (ordered by priority)
DEFAULT_POLICIES: List[RoutingPolicy] = [
    # Critical security tasks always get extended thinking
    RoutingPolicy(
        name="security_critical",
        conditions={
            "task_type": [TaskType.SECURITY],
            "risk_class": [RiskClass.HIGH, RiskClass.CRITICAL],
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.EXTENDED_THINKING,
        rationale="Security-critical tasks require deep analysis with extended thinking",
        priority=100,
    ),
    
    # Debug with failing tests needs think path
    RoutingPolicy(
        name="debug_with_evidence",
        conditions={
            "task_type": [TaskType.DEBUG],
            "has_failing_tests": True,
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.INTERLEAVED,
        rationale="Debugging with test failures requires interleaved tool verification",
        priority=90,
    ),
    
    # Performance analysis needs think path
    RoutingPolicy(
        name="performance_analysis",
        conditions={
            "task_type": [TaskType.PERFORMANCE],
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.MULTI_SAMPLE,
        rationale="Performance analysis benefits from multiple candidate approaches",
        priority=85,
    ),
    
    # High evidence requirements need think path
    RoutingPolicy(
        name="high_evidence_required",
        conditions={
            "required_evidence": [EvidenceLevel.E2, EvidenceLevel.E3],
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.CHAIN_OF_THOUGHT,
        rationale="High evidence requirements need structured reasoning chain",
        priority=80,
    ),
    
    # High-risk files touched
    RoutingPolicy(
        name="high_risk_files",
        conditions={
            "touches_high_risk_files": True,
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.EXTENDED_THINKING,
        rationale="Changes to auth/crypto/billing files require careful analysis",
        priority=75,
    ),
    
    # Code review with medium+ risk
    RoutingPolicy(
        name="code_review_risky",
        conditions={
            "task_type": [TaskType.CODE_REVIEW],
            "risk_class": [RiskClass.MEDIUM, RiskClass.HIGH, RiskClass.CRITICAL],
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.CHAIN_OF_THOUGHT,
        rationale="Code review with elevated risk needs systematic analysis",
        priority=70,
    ),
    
    # Complex refactoring
    RoutingPolicy(
        name="complex_refactor",
        conditions={
            "task_type": [TaskType.REFACTOR],
            "complexity_score_min": 0.6,
        },
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.SEARCH_BEAM,
        rationale="Complex refactoring benefits from exploring multiple approaches",
        priority=65,
    ),
    
    # Simple website/generic tasks with low risk
    RoutingPolicy(
        name="simple_fast_path",
        conditions={
            "task_type": [TaskType.WEBSITE, TaskType.GENERIC],
            "risk_class": [RiskClass.LOW],
            "required_evidence": [EvidenceLevel.E0, EvidenceLevel.E1],
        },
        route=RoutingPath.FAST,
        thinking_strategy=ThinkingStrategy.SINGLE_PASS,
        rationale="Simple low-risk tasks can use fast path for speed/cost efficiency",
        priority=10,
    ),
    
    # Default: medium complexity gets chain-of-thought
    RoutingPolicy(
        name="default_think",
        conditions={},
        route=RoutingPath.THINK,
        thinking_strategy=ThinkingStrategy.CHAIN_OF_THOUGHT,
        rationale="Default policy: use chain-of-thought for balanced accuracy",
        priority=0,
    ),
]


class DualThinkingRouter:
    """
    Dual-path router that combines GPT-5.2 and Claude Opus 4.5 routing logic.
    
    This router analyzes the run specification and determines:
    1. Whether to use fast path or think path
    2. Which thinking strategy to employ
    3. What model tier to use
    
    The router emits router_decision.json as an E2 artifact.
    """
    
    def __init__(
        self,
        policies: Optional[List[RoutingPolicy]] = None,
        routing_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the router.
        
        Args:
            policies: Custom routing policies (uses defaults if None)
            routing_config: Configuration from routing.yml
        """
        self.policies = policies or DEFAULT_POLICIES
        self.routing_config = routing_config or {}
        
        # Sort policies by priority (highest first)
        self.policies = sorted(self.policies, key=lambda p: p.priority, reverse=True)
    
    def route(self, run_spec: RunSpec) -> RouterDecision:
        """
        Route a run specification to the appropriate thinking path.
        
        This is the main entry point for routing decisions.
        
        Args:
            run_spec: The run specification to route
            
        Returns:
            RouterDecision with path, strategy, and rationale
        """
        # Compute routing signals
        signals = self._compute_signals(run_spec)
        
        # Find matching policy
        matched_policy = self._match_policy(signals)
        
        # Determine model tier
        selected_tier, fallback_tiers = self._select_model_tier(
            matched_policy.route,
            matched_policy.thinking_strategy,
            run_spec,
        )
        
        # Build router decision
        decision = RouterDecision(
            run_id=run_spec.run_id,
            path=matched_policy.route,
            task_type=run_spec.task_type,
            risk_class=signals["risk_class"],
            required_evidence=run_spec.required_evidence_level,
            complexity_score=signals["complexity_score"],
            policy_branch=matched_policy.name,
            rationale=matched_policy.rationale,
            selected_tier=selected_tier,
            fallback_tiers=fallback_tiers,
            thinking_strategy=matched_policy.thinking_strategy,
        )
        
        return decision
    
    def _compute_signals(self, run_spec: RunSpec) -> Dict[str, Any]:
        """
        Compute routing signals from run specification.
        
        Signals include:
        - task_type
        - risk_class
        - required_evidence
        - complexity_score
        - has_failing_tests
        - touches_high_risk_files
        """
        signals: Dict[str, Any] = {
            "task_type": run_spec.task_type,
            "required_evidence": run_spec.required_evidence_level,
        }
        
        # Compute risk class
        signals["risk_class"] = self._assess_risk(run_spec)
        
        # Compute complexity score
        signals["complexity_score"] = self._compute_complexity(run_spec)
        
        # Check for failing tests (from context/references)
        signals["has_failing_tests"] = self._has_failing_tests(run_spec)
        
        # Check for high-risk files
        signals["touches_high_risk_files"] = self._touches_high_risk_files(run_spec)
        
        return signals
    
    def _assess_risk(self, run_spec: RunSpec) -> RiskClass:
        """Assess risk class based on task type, mode, and files."""
        # Start with base risk from task type
        risk_scores = {
            TaskType.SECURITY: 3,
            TaskType.PERFORMANCE: 2,
            TaskType.DEBUG: 2,
            TaskType.CODE_REVIEW: 2,
            TaskType.REFACTOR: 2,
            TaskType.BUILD: 1,
            TaskType.WEBSITE: 1,
            TaskType.GENERIC: 1,
        }
        
        score = risk_scores.get(run_spec.task_type, 1)
        
        # Increase risk if touching sensitive files
        if self._touches_high_risk_files(run_spec):
            score += 2
        
        # Increase risk based on evidence requirements
        if run_spec.required_evidence_level in {EvidenceLevel.E2, EvidenceLevel.E3}:
            score += 1
        
        # Map score to risk class
        if score >= 5:
            return RiskClass.CRITICAL
        elif score >= 4:
            return RiskClass.HIGH
        elif score >= 2:
            return RiskClass.MEDIUM
        else:
            return RiskClass.LOW
    
    def _compute_complexity(self, run_spec: RunSpec) -> float:
        """
        Compute complexity score (0.0 - 1.0).
        
        Factors:
        - Number of context files
        - Prompt length
        - Task type complexity
        - Evidence requirements
        """
        score = 0.0
        
        # Context file count (more files = more complex)
        file_count = len(run_spec.context_files)
        score += min(file_count / 20, 0.3)  # Max 0.3 from files
        
        # Prompt length (longer = more complex)
        prompt_len = len(run_spec.prompt)
        score += min(prompt_len / 5000, 0.2)  # Max 0.2 from prompt
        
        # Task type complexity
        task_complexity = {
            TaskType.SECURITY: 0.3,
            TaskType.PERFORMANCE: 0.25,
            TaskType.DEBUG: 0.2,
            TaskType.CODE_REVIEW: 0.2,
            TaskType.REFACTOR: 0.2,
            TaskType.BUILD: 0.15,
            TaskType.WEBSITE: 0.1,
            TaskType.GENERIC: 0.1,
        }
        score += task_complexity.get(run_spec.task_type, 0.1)
        
        # Evidence requirements
        evidence_complexity = {
            EvidenceLevel.E3: 0.2,
            EvidenceLevel.E2: 0.15,
            EvidenceLevel.E1: 0.1,
            EvidenceLevel.E0: 0.05,
        }
        score += evidence_complexity.get(run_spec.required_evidence_level, 0.05)
        
        return min(score, 1.0)
    
    def _has_failing_tests(self, run_spec: RunSpec) -> bool:
        """Check if the run has failing test evidence."""
        # Check prompt for test failure indicators
        failure_indicators = [
            "fail",
            "error",
            "exception",
            "traceback",
            "assertion",
            "test.*failed",
            "tests.*failed",
        ]
        
        prompt_lower = run_spec.prompt.lower()
        for indicator in failure_indicators:
            if re.search(indicator, prompt_lower):
                return True
        
        # Check references for test output files
        for ref in run_spec.references:
            if any(x in ref.lower() for x in ["test", "spec", "error", "fail"]):
                return True
        
        return False
    
    def _touches_high_risk_files(self, run_spec: RunSpec) -> bool:
        """Check if the run touches high-risk files."""
        all_files = run_spec.context_files + run_spec.references
        
        for file_path in all_files:
            file_lower = file_path.lower()
            for pattern in HIGH_RISK_PATTERNS:
                if re.search(pattern, file_lower):
                    return True
        
        # Also check prompt for mentions of sensitive areas
        prompt_lower = run_spec.prompt.lower()
        for pattern in HIGH_RISK_PATTERNS:
            if re.search(pattern, prompt_lower):
                return True
        
        return False
    
    def _match_policy(self, signals: Dict[str, Any]) -> RoutingPolicy:
        """Find the first matching policy based on signals."""
        for policy in self.policies:
            if self._policy_matches(policy, signals):
                return policy
        
        # Should never reach here due to default policy
        return self.policies[-1]
    
    def _policy_matches(self, policy: RoutingPolicy, signals: Dict[str, Any]) -> bool:
        """Check if a policy matches the given signals."""
        conditions = policy.conditions
        
        # Empty conditions = always match (default policy)
        if not conditions:
            return True
        
        for key, expected in conditions.items():
            if key == "task_type":
                if signals.get("task_type") not in expected:
                    return False
            
            elif key == "risk_class":
                if signals.get("risk_class") not in expected:
                    return False
            
            elif key == "required_evidence":
                if signals.get("required_evidence") not in expected:
                    return False
            
            elif key == "has_failing_tests":
                if signals.get("has_failing_tests") != expected:
                    return False
            
            elif key == "touches_high_risk_files":
                if signals.get("touches_high_risk_files") != expected:
                    return False
            
            elif key == "complexity_score_min":
                if signals.get("complexity_score", 0) < expected:
                    return False
            
            elif key == "complexity_score_max":
                if signals.get("complexity_score", 0) > expected:
                    return False
        
        return True
    
    def _select_model_tier(
        self,
        path: RoutingPath,
        strategy: ThinkingStrategy,
        run_spec: RunSpec,
    ) -> Tuple[str, List[str]]:
        """
        Select model tier based on routing decision.
        
        Returns:
            Tuple of (selected_tier, fallback_tiers)
        """
        if path == RoutingPath.FAST:
            return "tier_fast", ["tier_think"]
        
        # Think path - select based on strategy
        if strategy in {ThinkingStrategy.EXTENDED_THINKING, ThinkingStrategy.SEARCH_BEAM}:
            # Most capable tier for complex strategies
            return "tier_think", ["tier_fast"]
        
        elif strategy == ThinkingStrategy.MULTI_SAMPLE:
            # Can use either tier depending on budget
            if run_spec.cost_budget_usd >= 2.0:
                return "tier_think", ["tier_fast"]
            else:
                return "tier_fast", []
        
        else:
            # Default think tier
            return "tier_think", ["tier_fast"]
    
    def emit_artifact(
        self,
        decision: RouterDecision,
        output_dir: Path,
    ) -> Path:
        """
        Emit router_decision.json artifact.
        
        Args:
            decision: The routing decision
            output_dir: Directory to write artifact
            
        Returns:
            Path to the written artifact
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = output_dir / "router_decision.json"
        
        artifact_path.write_text(
            json.dumps(decision.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        
        return artifact_path


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_router_from_config(config_path: Optional[Path] = None) -> DualThinkingRouter:
    """
    Create a router from configuration file.
    
    Args:
        config_path: Path to routing.yml (uses defaults if None)
        
    Returns:
        Configured DualThinkingRouter
    """
    routing_config = {}
    
    if config_path and config_path.exists():
        import yaml
        routing_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    
    return DualThinkingRouter(routing_config=routing_config)
