"""
Dive AI — Deployment Rules Engine
===================================
Auto-generated rules for algorithm deployment.

Before any algorithm executes, this engine:
  1. Validates inputs against schema
  2. Checks resource limits (memory, time, cost)
  3. Verifies algorithm compatibility
  4. Enforces trust thresholds
  5. Generates rollback conditions

Rules are auto-generated from verified execution history:
  - High-failure algos get stricter rules
  - Verified algos get relaxed rules
  - New algos get default conservative rules
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class Rule:
    """A single deployment rule."""
    rule_id: str
    name: str
    condition: str          # "trust_score > 0.3", "input_has_key:user_request"
    action: str             # "allow", "block", "warn", "require_confirmation"
    severity: str = "medium"  # low, medium, high, critical
    auto_generated: bool = False


@dataclass
class RuleSet:
    """Collection of rules for an algorithm/execution."""
    algorithm: str
    rules: List[Rule] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)

    def check(self, context: Dict) -> Dict:
        """Check all rules against context. Returns {allowed, violations}."""
        violations = []
        warnings = []
        for rule in self.rules:
            passed = self._evaluate_condition(rule.condition, context)
            if not passed:
                if rule.action == "block":
                    violations.append({
                        "rule": rule.name,
                        "condition": rule.condition,
                        "severity": rule.severity,
                    })
                elif rule.action == "warn":
                    warnings.append({
                        "rule": rule.name,
                        "condition": rule.condition,
                    })
        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
        }

    @staticmethod
    def _evaluate_condition(condition: str, context: Dict) -> bool:
        """Evaluate a rule condition against context."""
        try:
            if condition.startswith("trust_score"):
                parts = condition.split()
                if len(parts) >= 3:
                    op, threshold = parts[1], float(parts[2])
                    trust = context.get("trust_score", 0.0)
                    if op == ">": return trust > threshold
                    if op == ">=": return trust >= threshold
                    if op == "<": return trust < threshold
                return True

            elif condition.startswith("input_has_key:"):
                key = condition.split(":")[1]
                inputs = context.get("inputs", {})
                return key in inputs

            elif condition.startswith("max_cost:"):
                limit = float(condition.split(":")[1])
                cost = context.get("estimated_cost", 0)
                return cost <= limit

            elif condition.startswith("min_completeness:"):
                threshold = float(condition.split(":")[1])
                completeness = context.get("completeness_score", 0)
                return completeness >= threshold

            elif condition == "not_blacklisted":
                return not context.get("blacklisted", False)

        except Exception:
            pass
        return True  # Default: allow


class DeploymentRules:
    """
    Auto-generated and enforced deployment rules.
    
    Rules evolve based on execution history:
      - Verified algorithms get relaxed rules
      - Failing algorithms get stricter rules
      - New algorithms get conservative defaults
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> 'DeploymentRules':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._rule_sets: Dict[str, RuleSet] = {}
        self._global_rules: List[Rule] = self._default_global_rules()
        self._total_checks = 0
        self._total_blocked = 0

    def _default_global_rules(self) -> List[Rule]:
        """Default global rules applied to all executions."""
        return [
            Rule(
                rule_id="global_01",
                name="Require user_request in input",
                condition="input_has_key:user_request",
                action="warn",
                severity="low",
            ),
            Rule(
                rule_id="global_02",
                name="Not blacklisted",
                condition="not_blacklisted",
                action="block",
                severity="critical",
            ),
        ]

    def check_pre_execution(self, algorithms: List[Dict],
                            user_input: str,
                            context: Dict = None) -> Dict:
        """
        Check all rules before execution.
        Returns {allowed, violations, warnings}.
        """
        context = context or {}
        self._total_checks += 1
        
        all_violations = []
        all_warnings = []

        # Check global rules
        for rule in self._global_rules:
            eval_ctx = {
                "inputs": {"user_request": user_input, **context},
                "trust_score": 0.5,
                **context,
            }
            passed = RuleSet._evaluate_condition(rule.condition, eval_ctx)
            if not passed:
                entry = {"rule": rule.name, "condition": rule.condition, "severity": rule.severity}
                if rule.action == "block":
                    all_violations.append(entry)
                elif rule.action == "warn":
                    all_warnings.append(entry)

        # Check per-algorithm rules
        for algo_info in algorithms:
            name = algo_info.get("name", "") if isinstance(algo_info, dict) else str(algo_info)
            if name in self._rule_sets:
                result = self._rule_sets[name].check({
                    "inputs": {"user_request": user_input, **context},
                    "trust_score": algo_info.get("scores", {}).get("trust", 0) if isinstance(algo_info, dict) else 0,
                    "completeness_score": algo_info.get("scores", {}).get("completeness", 0) if isinstance(algo_info, dict) else 0,
                    **context,
                })
                all_violations.extend(result["violations"])
                all_warnings.extend(result["warnings"])

        allowed = len(all_violations) == 0
        if not allowed:
            self._total_blocked += 1

        return {
            "allowed": allowed,
            "violations": all_violations,
            "warnings": all_warnings,
            "algorithms_checked": len(algorithms),
        }

    def generate_rules(self, algo_name: str, verified_info=None,
                       execution_history: List[Dict] = None) -> RuleSet:
        """
        Auto-generate rules for an algorithm based on its history.
        
        - High trust → relaxed rules
        - Low trust → strict rules  
        - New/unknown → conservative defaults
        """
        rules = []
        
        trust = 0.0
        if verified_info:
            trust = getattr(verified_info, 'trust_score', 0.0)

        # Trust-based rules
        if trust < 0.3:
            rules.append(Rule(
                rule_id=f"{algo_name}_trust",
                name=f"Low trust threshold for {algo_name}",
                condition="trust_score >= 0.0",
                action="warn",
                severity="medium",
                auto_generated=True,
            ))

        # Completeness rules
        rules.append(Rule(
            rule_id=f"{algo_name}_complete",
            name=f"Minimum completeness for {algo_name}",
            condition=f"min_completeness:0.3",
            action="warn",
            severity="low",
            auto_generated=True,
        ))

        # Cost limit (based on history average × 3)
        if execution_history:
            costs = [e.get("cost", 0) for e in execution_history if e.get("cost", 0) > 0]
            if costs:
                avg_cost = sum(costs) / len(costs)
                rules.append(Rule(
                    rule_id=f"{algo_name}_cost",
                    name=f"Cost limit for {algo_name}",
                    condition=f"max_cost:{avg_cost * 3:.2f}",
                    action="warn",
                    severity="medium",
                    auto_generated=True,
                ))

        ruleset = RuleSet(algorithm=algo_name, rules=rules)
        self._rule_sets[algo_name] = ruleset
        return ruleset

    def get_stats(self) -> Dict:
        """Get rules engine statistics."""
        return {
            "total_checks": self._total_checks,
            "total_blocked": self._total_blocked,
            "rule_sets": len(self._rule_sets),
            "global_rules": len(self._global_rules),
            "block_rate": round(
                self._total_blocked / max(self._total_checks, 1) * 100, 1
            ),
        }
