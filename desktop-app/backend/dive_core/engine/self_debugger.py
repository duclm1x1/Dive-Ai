"""
Dive AI — Self Debugger
========================
Auto-detect failures, diagnose root causes, suggest fixes, and auto-retry.

When an algorithm execution fails or produces low-quality results,
SelfDebugger analyzes what went wrong and attempts to fix it automatically.

Strategies:
  1. Parameter adjustment — try different inputs
  2. Algorithm substitution — swap failing algo for alternative
  3. Partial extraction — use subset of steps
  4. Skill fallback — replace with skills
  5. Retry with exponential backoff
"""

import time
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class Diagnosis:
    """Result of diagnosing a failure."""
    error_type: str = "unknown"     # timeout, missing_input, algo_error, low_quality
    root_cause: str = ""
    failing_component: str = ""     # algorithm name or skill name
    fixable: bool = False
    suggested_fixes: List[Dict] = field(default_factory=list)
    severity: str = "medium"       # low, medium, high, critical
    details: Dict = field(default_factory=dict)


@dataclass
class FixResult:
    """Result of an auto-fix attempt."""
    success: bool = False
    strategy_used: str = ""
    attempts: int = 0
    original_error: str = ""
    fix_description: str = ""
    new_result: Dict = field(default_factory=dict)


class SelfDebugger:
    """
    Auto-diagnose and fix execution failures.
    
    Strategies (tried in order):
      1. Retry with same params (transient errors)
      2. Adjust parameters (missing/wrong inputs)
      3. Substitute algorithm (algo-specific failure)
      4. Partial extraction (reduce scope)
      5. Skill fallback (use skills instead)
    """

    _instance = None
    MAX_RETRIES = 3

    @classmethod
    def get_instance(cls) -> 'SelfDebugger':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._diagnosis_history: List[Diagnosis] = []
        self._fix_history: List[FixResult] = []
        self._total_diagnoses = 0
        self._total_fixes_attempted = 0
        self._total_fixes_succeeded = 0

    def diagnose(self, failed_result: Dict) -> Dict:
        """
        Analyze a failed execution and determine root cause.
        
        Returns diagnosis with error type, root cause, and suggested fixes.
        """
        diag = Diagnosis()
        self._total_diagnoses += 1

        # Analyze the result
        success = failed_result.get("success", False)
        mode = failed_result.get("mode", "")
        results = failed_result.get("results", [])
        error = failed_result.get("error", "")
        algorithms = failed_result.get("algorithms_used", [])
        eval_score = failed_result.get("eval_score", {})

        # Determine error type
        if not success and error:
            if "timeout" in str(error).lower():
                diag.error_type = "timeout"
                diag.severity = "medium"
            elif "missing" in str(error).lower() or "required" in str(error).lower():
                diag.error_type = "missing_input"
                diag.severity = "low"
            elif "permission" in str(error).lower() or "access" in str(error).lower():
                diag.error_type = "permission_error"
                diag.severity = "high"
            else:
                diag.error_type = "algo_error"
                diag.severity = "medium"
            diag.root_cause = str(error)[:200]
        elif success and eval_score.get("total", 0) < 0.5:
            diag.error_type = "low_quality"
            diag.severity = "low"
            diag.root_cause = f"Execution succeeded but quality too low ({eval_score.get('total', 0):.2f})"
        elif not success:
            diag.error_type = "execution_failure"
            diag.severity = "medium"
            diag.root_cause = "Execution returned failure without specific error"

        # Find failing component
        if results:
            for r in results:
                if not r.get("success", True):
                    diag.failing_component = r.get("algorithm", r.get("skill", "unknown"))
                    break
        elif algorithms:
            diag.failing_component = algorithms[0] if algorithms else ""

        # Generate fix suggestions
        diag.fixable = True
        fixes = []

        if diag.error_type == "timeout":
            fixes.append({
                "strategy": "retry",
                "description": "Retry with increased timeout",
                "params": {"timeout_multiplier": 2},
            })
            fixes.append({
                "strategy": "partial_extraction",
                "description": "Reduce scope by using partial algorithm steps",
            })

        elif diag.error_type == "missing_input":
            fixes.append({
                "strategy": "parameter_adjust",
                "description": "Fill missing parameters with defaults",
                "params": {"use_defaults": True},
            })

        elif diag.error_type == "algo_error":
            fixes.append({
                "strategy": "substitute",
                "description": f"Replace {diag.failing_component} with alternative algorithm",
            })
            fixes.append({
                "strategy": "skill_fallback",
                "description": "Fall back to skills for the failing step",
            })

        elif diag.error_type == "low_quality":
            fixes.append({
                "strategy": "add_algorithms",
                "description": "Add more algorithms to improve coverage",
            })
            fixes.append({
                "strategy": "retry",
                "description": "Retry execution (might get better results)",
            })

        elif diag.error_type == "permission_error":
            diag.fixable = False
            fixes.append({
                "strategy": "manual",
                "description": "Permission error requires manual intervention",
            })

        diag.suggested_fixes = fixes
        diag.details = {
            "mode": mode,
            "algorithms": algorithms,
            "eval_score": eval_score,
        }

        self._diagnosis_history.append(diag)

        return {
            "error_type": diag.error_type,
            "root_cause": diag.root_cause,
            "failing_component": diag.failing_component,
            "fixable": diag.fixable,
            "severity": diag.severity,
            "suggested_fixes": diag.suggested_fixes,
        }

    def auto_fix(self, diagnosis: Dict, user_input: str,
                 context: Dict = None) -> Dict:
        """
        Attempt to auto-fix based on diagnosis.
        Tries each suggested fix strategy in order.
        """
        context = context or {}
        self._total_fixes_attempted += 1
        
        fixes = diagnosis.get("suggested_fixes", [])
        if not fixes:
            return {"success": False, "reason": "No fix strategies available"}

        for fix in fixes:
            strategy = fix.get("strategy", "")
            
            try:
                if strategy == "retry":
                    result = self._retry_execution(user_input, context)
                    if result.get("success"):
                        self._total_fixes_succeeded += 1
                        return {
                            "success": True,
                            "strategy": "retry",
                            "result": result,
                        }

                elif strategy == "parameter_adjust":
                    result = self._adjust_and_retry(user_input, context, fix.get("params", {}))
                    if result.get("success"):
                        self._total_fixes_succeeded += 1
                        return {
                            "success": True,
                            "strategy": "parameter_adjust",
                            "result": result,
                        }

                elif strategy == "substitute":
                    result = self._substitute_algorithm(
                        user_input, context,
                        diagnosis.get("failing_component", "")
                    )
                    if result.get("success"):
                        self._total_fixes_succeeded += 1
                        return {
                            "success": True,
                            "strategy": "substitute",
                            "result": result,
                        }

                elif strategy == "skill_fallback":
                    result = self._skill_fallback(user_input, context)
                    if result.get("success"):
                        self._total_fixes_succeeded += 1
                        return {
                            "success": True,
                            "strategy": "skill_fallback",
                            "result": result,
                        }

            except Exception as e:
                continue  # Try next strategy

        return {"success": False, "reason": "All fix strategies exhausted"}

    def _retry_execution(self, user_input: str, context: Dict) -> Dict:
        """Simple retry of the execution."""
        try:
            from dive_core.engine.lifecycle_bridge import get_lifecycle_bridge
            bridge = get_lifecycle_bridge()
            return bridge.smart_execute(user_input, context)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _adjust_and_retry(self, user_input: str, context: Dict,
                          params: Dict) -> Dict:
        """Adjust parameters and retry."""
        adjusted_context = {**context, **params, "_retry": True}
        return self._retry_execution(user_input, adjusted_context)

    def _substitute_algorithm(self, user_input: str, context: Dict,
                              failing_algo: str) -> Dict:
        """Exclude failing algorithm and retry with alternatives."""
        context_with_exclusion = {
            **context,
            "_exclude_algorithms": [failing_algo],
            "_retry": True,
        }
        return self._retry_execution(user_input, context_with_exclusion)

    def _skill_fallback(self, user_input: str, context: Dict) -> Dict:
        """Fall back to pure skill execution."""
        context_with_fallback = {
            **context,
            "_skills_only": True,
            "_retry": True,
        }
        return self._retry_execution(user_input, context_with_fallback)

    def get_stats(self) -> Dict:
        """Get debugger statistics."""
        return {
            "total_diagnoses": self._total_diagnoses,
            "total_fixes_attempted": self._total_fixes_attempted,
            "total_fixes_succeeded": self._total_fixes_succeeded,
            "fix_success_rate": (
                round(self._total_fixes_succeeded / max(self._total_fixes_attempted, 1) * 100, 1)
            ),
            "common_errors": self._get_common_errors(),
        }

    def _get_common_errors(self) -> List[Dict]:
        """Get most common error types."""
        counts = {}
        for d in self._diagnosis_history:
            t = d.error_type
            counts[t] = counts.get(t, 0) + 1
        return sorted(
            [{"type": t, "count": c} for t, c in counts.items()],
            key=lambda x: x["count"], reverse=True
        )
