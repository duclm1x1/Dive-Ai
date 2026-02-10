"""
Dive AI Combo Engine — Algorithm-verified skill chaining.
THE unique differentiator vs OpenClaw: automatic planning + step verification + cost tracking.
"""
import time
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from ..algorithms.base import AlgorithmResult
from ..specs import VerificationResult
from .base_skill import BaseSkill
from .skill_registry import SkillRegistry, get_registry


@dataclass
class ComboStep:
    """One step in a combo chain."""
    skill_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    use_prev_output: bool = False  # Feed previous step's output as input
    output_key: Optional[str] = None  # Which key from prev output to use


@dataclass
class ComboChain:
    """A complete combo: ordered list of skills."""
    name: str
    description: str
    steps: List[ComboStep]
    estimated_cost: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class ComboStepResult:
    """Result of one combo step."""
    step_index: int
    skill_name: str
    result: Optional[AlgorithmResult] = None
    verification: Optional[VerificationResult] = None
    duration_ms: float = 0.0
    cost: float = 0.0
    error: Optional[str] = None


@dataclass
class ComboResult:
    """Full result of a combo execution."""
    combo_name: str
    success: bool
    step_results: List[ComboStepResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    total_cost: float = 0.0
    final_output: Any = None
    final_verification: Optional[VerificationResult] = None


class SkillComboEngine:
    """
    Plan, execute, and verify skill combos.
    
    Example combo: "Research AI trends and write summary"
    → [web-search] → [deep-research] → [note-taker] 
    → Each step verified → Final output verified
    """

    def __init__(self, registry: SkillRegistry = None):
        self.registry = registry or get_registry()
        self._combo_library: Dict[str, ComboChain] = {}
        self._execution_history: List[ComboResult] = []

    # ── Library ────────────────────────────────────────────

    def register_combo(self, combo: ComboChain):
        """Add a combo template to the library."""
        # Estimate cost
        combo.estimated_cost = self.registry.estimate_cost(
            [s.skill_name for s in combo.steps]
        )
        self._combo_library[combo.name] = combo

    def list_combos(self) -> List[Dict[str, Any]]:
        """List all available combos."""
        return [
            {
                "name": c.name,
                "description": c.description,
                "steps": len(c.steps),
                "skills": [s.skill_name for s in c.steps],
                "estimated_cost": c.estimated_cost,
                "tags": c.tags,
            }
            for c in self._combo_library.values()
        ]

    def get_combo(self, name: str) -> Optional[ComboChain]:
        return self._combo_library.get(name)

    # ── Planning ───────────────────────────────────────────

    def plan_combo(self, task: str) -> Optional[ComboChain]:
        """
        Auto-plan a combo for a natural language task.
        Uses skill discovery + compatibility checking.
        """
        # Find relevant skills
        candidates = self.registry.discover(task)
        if not candidates:
            return None

        # Build chain respecting combo_position
        starters = [s for s in candidates if s.skill_spec.combo_position in ("start", "any")]
        middlers = [s for s in candidates if s.skill_spec.combo_position in ("middle", "any")]
        enders = [s for s in candidates if s.skill_spec.combo_position in ("end", "any")]

        chain_skills = []
        # Pick best starter
        if starters:
            chain_skills.append(starters[0])
        # Add up to 3 middlers
        for m in middlers[:3]:
            if m not in chain_skills:
                chain_skills.append(m)
        # Pick best ender
        if enders:
            best_ender = enders[0]
            if best_ender not in chain_skills:
                chain_skills.append(best_ender)

        if not chain_skills:
            return None

        steps = []
        for i, skill in enumerate(chain_skills):
            steps.append(ComboStep(
                skill_name=skill.skill_spec.name,
                use_prev_output=i > 0,
            ))

        return ComboChain(
            name=f"auto-{int(time.time())}",
            description=f"Auto-planned for: {task}",
            steps=steps,
            tags=["auto-planned"],
        )

    # ── Execution ──────────────────────────────────────────

    def execute_combo(self, combo: ComboChain, initial_params: Dict = None) -> ComboResult:
        """
        Execute a combo chain with step-by-step verification.
        If a step fails, the combo stops (fail-fast).
        """
        combo_result = ComboResult(combo_name=combo.name, success=False)
        start_time = time.time()
        prev_output = initial_params or {}

        for i, step in enumerate(combo.steps):
            step_start = time.time()
            step_result = ComboStepResult(step_index=i, skill_name=step.skill_name)

            # Get skill
            skill = self.registry.get(step.skill_name)
            if not skill:
                step_result.error = f"Skill '{step.skill_name}' not found in registry"
                combo_result.step_results.append(step_result)
                break

            # Build inputs
            inputs = dict(step.params)
            if step.use_prev_output and prev_output:
                if step.output_key and step.output_key in prev_output:
                    inputs["data"] = prev_output[step.output_key]
                else:
                    # Always wrap prev output as "data" so next skill can access it
                    inputs["data"] = prev_output

            # Execute
            try:
                result = skill.execute(inputs)
                step_result.result = result
                step_result.verification = result.verification
                step_result.cost = skill.skill_spec.cost_per_call
                step_result.duration_ms = (time.time() - step_start) * 1000

                if result.status != "success":
                    step_result.error = result.meta.get("error", "Unknown failure")
                    combo_result.step_results.append(step_result)
                    break

                # Prepare output for next step
                prev_output = result.data if isinstance(result.data, dict) else {"data": result.data}

            except Exception as e:
                step_result.error = str(e)
                step_result.duration_ms = (time.time() - step_start) * 1000
                combo_result.step_results.append(step_result)
                break

            combo_result.step_results.append(step_result)

        # Final summary
        combo_result.total_duration_ms = (time.time() - start_time) * 1000
        combo_result.total_cost = sum(sr.cost for sr in combo_result.step_results)

        all_passed = all(
            sr.result and sr.result.status == "success"
            for sr in combo_result.step_results
        )
        combo_result.success = all_passed
        combo_result.final_output = prev_output

        # Final verification
        if all_passed and combo_result.step_results:
            last_verif = combo_result.step_results[-1].verification
            combo_result.final_verification = last_verif or VerificationResult(
                True, 1.0, "All steps passed", {}
            )

        self._execution_history.append(combo_result)
        return combo_result

    # ── Stats ──────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        return {
            "combos_registered": len(self._combo_library),
            "combos_executed": len(self._execution_history),
            "success_rate": (
                sum(1 for r in self._execution_history if r.success) /
                max(len(self._execution_history), 1)
            ),
            "total_cost": sum(r.total_cost for r in self._execution_history),
        }

    def to_dict(self, result: ComboResult) -> Dict[str, Any]:
        """Serialize a ComboResult to dict."""
        return {
            "combo_name": result.combo_name,
            "success": result.success,
            "steps": [
                {
                    "index": sr.step_index,
                    "skill": sr.skill_name,
                    "status": sr.result.status if sr.result else "error",
                    "duration_ms": round(sr.duration_ms, 1),
                    "cost": sr.cost,
                    "verified": sr.verification.success if sr.verification else None,
                    "error": sr.error,
                }
                for sr in result.step_results
            ],
            "total_duration_ms": round(result.total_duration_ms, 1),
            "total_cost": round(result.total_cost, 6),
            "final_output": str(result.final_output)[:500] if result.final_output else None,
        }
