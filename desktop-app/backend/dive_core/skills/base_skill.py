"""
Dive AI Base Skill — Every skill extends BaseAlgorithm with verification.
"""
from abc import abstractmethod
from typing import Dict, Any, Optional
from ..algorithms.base import BaseAlgorithm, AlgorithmResult
from ..specs import VerificationResult
from .skill_spec import SkillSpec, SkillCategory


class BaseSkill(BaseAlgorithm):
    """
    Base class for all Dive AI skills.
    Extends BaseAlgorithm with skill-specific features:
    - Category-based routing
    - Input validation (pre_check)
    - Output verification (post_verify)
    - Combo interface (can_chain_with, transform_output_for)
    """

    def __init__(self):
        super().__init__()
        self._skill_spec: Optional[SkillSpec] = None
        self._execution_count: int = 0
        self._total_cost: float = 0.0
        self._last_result: Optional[AlgorithmResult] = None

    @property
    def skill_spec(self) -> SkillSpec:
        if self._skill_spec is None:
            self._skill_spec = self._build_spec()
        return self._skill_spec

    @property
    def category(self) -> SkillCategory:
        return self.skill_spec.category

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "name": self.skill_spec.name,
            "executions": self._execution_count,
            "total_cost": round(self._total_cost, 6),
            "last_success": self._last_result.status == "success" if self._last_result else None,
        }

    @abstractmethod
    def _build_spec(self) -> SkillSpec:
        """Return the SkillSpec for this skill."""
        pass

    @abstractmethod
    def _execute(self, inputs: Dict[str, Any], context: Optional[Dict] = None) -> AlgorithmResult:
        """Core execution logic. Override this."""
        pass

    def pre_check(self, inputs: Dict[str, Any]) -> bool:
        """Validate inputs before execution. Override for custom validation."""
        schema = self.skill_spec.input_schema
        if not schema:
            return True
        for key, spec in schema.items():
            required = spec.get("required", False) if isinstance(spec, dict) else False
            if required and key not in inputs:
                return False
        return True

    def execute(self, inputs: Dict[str, Any], context: Optional[Dict] = None) -> AlgorithmResult:
        """Execute with pre-check, tracking, and verification."""
        # Pre-check
        if not self.pre_check(inputs):
            return AlgorithmResult(
                status="failure",
                data=None,
                meta={"error": "Input validation failed", "skill": self.skill_spec.name},
            )

        # Execute
        try:
            result = self._execute(inputs, context)
            self._execution_count += 1
            self._total_cost += self.skill_spec.cost_per_call
            self._last_result = result

            # Post-verify
            if result.status == "success":
                verification = self.post_verify(result)
                result.verification = verification

            return result
        except Exception as e:
            self._execution_count += 1
            return AlgorithmResult(
                status="failure",
                data=None,
                meta={"error": str(e), "skill": self.skill_spec.name},
            )

    def post_verify(self, result: AlgorithmResult) -> VerificationResult:
        """Verify output after execution. Override for custom verification."""
        if self.skill_spec.verifier:
            try:
                return self.skill_spec.verifier(result.data)
            except Exception as e:
                return VerificationResult(False, 0.0, f"Verifier error: {e}", {})
        # Default: success if we got data
        has_data = result.data is not None
        return VerificationResult(
            success=has_data,
            score=1.0 if has_data else 0.0,
            message="Output present" if has_data else "No output",
            details={"type": type(result.data).__name__} if has_data else {},
        )

    # ── Combo Interface ────────────────────────────────────
    def can_chain_with(self, next_skill: 'BaseSkill') -> bool:
        """Check if this skill can chain into next_skill."""
        my_compat = self.skill_spec.combo_compatible
        if not my_compat:
            return True  # No restrictions
        return next_skill.skill_spec.name in my_compat

    def transform_output_for(self, next_skill: 'BaseSkill', output: Any) -> Dict:
        """Transform this skill's output to match next skill's input schema."""
        if isinstance(output, dict):
            return output
        return {"data": output}

    def can_handle(self, task: str) -> float:
        """Score how well this skill matches a task description (0-1)."""
        task_lower = task.lower()
        score = 0.0
        # Check trigger patterns
        import re
        for pattern in self.skill_spec.trigger_patterns:
            if re.search(pattern, task_lower):
                score = max(score, 0.9)
        # Check tags
        for tag in self.skill_spec.tags:
            if tag.lower() in task_lower:
                score = max(score, 0.6)
        # Check name
        if self.skill_spec.name.replace("-", " ") in task_lower:
            score = max(score, 0.8)
        return score
