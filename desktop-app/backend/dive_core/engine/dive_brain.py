"""
Dive AI — DiveBrain: Central Intelligence Loop
=================================================
The BRAIN that controls everything:
  tự call → tự kiểm điểm → tự lấy thuật toán → tự tạo thuật toán → tự debug

Flow:
  User Input → think() → ExecutionPlan (multi-algo + skills)
  → execute() → Result
  → self_evaluate() → EvalScore (completeness, correctness, quality)
  → learn() → boost trust / create algorithm / index for RAG
  → If failed: self_debug() → retry

Integration:
  - IntentAnalyzer  → extract intent + entities
  - SkillIntelligence SkillRouter → find candidate skills
  - AlgorithmScorer → score each candidate (completeness + fitness + trust)
  - LifecycleBridge → multi-algo orchestration
  - SelfDebugger → auto-fix failures
  - DeploymentRules → enforce rules before execution
"""

import os
import sys
import time
import uuid
import json
import re
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ══════════════════════════════════════════════════════════════
# Algorithm Scorer — completeness + fitness + trust
# ══════════════════════════════════════════════════════════════

class AlgorithmScorer:
    """
    Score algorithms on 3 dimensions:
      1. completeness — how complete is the algorithm (steps, schema)?
      2. fitness — how well does it match THIS specific job?
      3. trust — how many real cases verified?
    
    Composite = completeness × 0.3 + fitness × 0.4 + trust × 0.3
    """

    @staticmethod
    def score_completeness(algo) -> float:
        """Score how complete an algorithm's definition is (0-1)."""
        score = 0.0
        total = 5.0

        # Has steps?
        if hasattr(algo, 'steps') and algo.steps:
            step_score = min(1.0, len(algo.steps) / 5.0)
            score += step_score
        
        # Has description?
        if hasattr(algo, 'description') and algo.description and len(algo.description) > 10:
            score += 1.0
        
        # Has input schema?
        if hasattr(algo, 'input_schema') and algo.input_schema:
            score += 1.0
        
        # Has output schema?
        if hasattr(algo, 'output_schema') and algo.output_schema:
            score += 1.0
        
        # Has category?
        if hasattr(algo, 'category') and algo.category:
            score += 1.0

        return round(score / total, 3)

    @staticmethod
    def score_fitness(algo, job_text: str, matched_categories: List[str] = None) -> float:
        """Score how well an algorithm matches a specific job (0-1)."""
        if not job_text:
            return 0.0
        
        text = job_text.lower()
        score = 0.0
        checks = 0

        # Category match
        if matched_categories and hasattr(algo, 'category'):
            checks += 1
            if algo.category in matched_categories:
                idx = matched_categories.index(algo.category)
                # Primary category gets 1.0, secondary 0.7, etc.
                score += max(0.1, 1.0 - idx * 0.3)

        # Step keyword overlap
        if hasattr(algo, 'steps') and algo.steps:
            checks += 1
            words = set(text.split())
            step_words = set()
            for step in algo.steps:
                step_words.update(step.lower().split())
            overlap = words & step_words
            if step_words:
                score += min(1.0, len(overlap) / max(3, len(step_words) * 0.3))

        # Description keyword overlap
        if hasattr(algo, 'description') and algo.description:
            checks += 1
            desc_words = set(algo.description.lower().split())
            overlap = set(text.split()) & desc_words
            if desc_words:
                score += min(1.0, len(overlap) / max(3, len(desc_words) * 0.3))

        # Name relevance
        if hasattr(algo, 'name') and algo.name:
            checks += 1
            name_parts = re.findall(r'[A-Z][a-z]+|[a-z]+', algo.name)
            name_lower = [p.lower() for p in name_parts]
            if any(n in text for n in name_lower if len(n) > 2):
                score += 1.0

        return round(score / max(checks, 1), 3)

    @staticmethod
    def score_trust(verified_info) -> float:
        """Score based on verification history (0-1)."""
        if not verified_info:
            return 0.0
        trust = getattr(verified_info, 'trust_score', 0.0)
        return round(trust, 3)

    @classmethod
    def composite_score(cls, algo, job_text: str,
                        matched_categories: List[str] = None,
                        verified_info=None) -> Dict[str, float]:
        """
        Calculate composite score:
          completeness × 0.3 + fitness × 0.4 + trust × 0.3
        """
        completeness = cls.score_completeness(algo)
        fitness = cls.score_fitness(algo, job_text, matched_categories)
        trust = cls.score_trust(verified_info)
        
        composite = completeness * 0.3 + fitness * 0.4 + trust * 0.3

        return {
            "completeness": completeness,
            "fitness": fitness,
            "trust": trust,
            "composite": round(composite, 3),
        }


# ══════════════════════════════════════════════════════════════
# Evaluation Score — self-evaluation result
# ══════════════════════════════════════════════════════════════

@dataclass
class EvalScore:
    """Result of self-evaluation after execution."""
    total_score: float = 0.0        # 0-1 composite
    completeness: float = 0.0       # Did it complete all intended steps?
    correctness: float = 0.0        # Did it produce correct results?
    quality: float = 0.0            # Quality of the output
    should_confirm: bool = False    # Auto-confirm if score > threshold
    should_reject: bool = False     # Auto-reject if score too low
    should_debug: bool = False      # Should trigger self-debug?
    reasoning: str = ""
    details: Dict = field(default_factory=dict)

    # Thresholds
    CONFIRM_THRESHOLD = 0.8
    REJECT_THRESHOLD = 0.4


@dataclass
class ExecutionPlan:
    """Plan generated by DiveBrain.think()."""
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    user_input: str = ""
    intent: Dict = field(default_factory=dict)
    algorithms: List[Dict] = field(default_factory=list)  # [{name, score, mode}]
    skills: List[str] = field(default_factory=list)
    stages: List[str] = field(default_factory=list)
    is_full_lifecycle: bool = False
    estimated_cost: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""


class DiveBrain:
    """
    Central Intelligence Loop for Dive AI.
    
    Connects:
      IntentAnalyzer → SkillRouter → AlgorithmScorer → LifecycleBridge
      → SelfEvaluator → SelfDebugger → GrowthEngine
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> 'DiveBrain':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Central connector for ALL modules
        self._connector = None
        
        # Lazy-loaded components (via connector)
        self._bridge = None
        self._intent_analyzer = None
        self._skill_intelligence = None
        self._self_debugger = None
        self._deployment_rules = None
        self._dive_engine = None
        self._memory_brain = None
        self._search_engine = None
        self._thinking_engine = None
        self._complexity_analyzer = None
        self._cruel_system = None
        self._claims_ledger = None
        self._scorer = AlgorithmScorer()

        # Brain state
        self._thought_history: List[Dict] = []
        self._eval_history: List[EvalScore] = []
        self._total_thoughts = 0
        self._total_auto_confirms = 0
        self._total_auto_rejects = 0
        self._total_debug_triggers = 0

    @property
    def connector(self):
        """Get DiveConnector — central wiring hub for ALL modules."""
        if self._connector is None:
            try:
                from dive_core.engine.dive_connector import get_connector
                self._connector = get_connector()
            except Exception:
                self._connector = None
        return self._connector

    @property
    def bridge(self):
        if self._bridge is None:
            from dive_core.engine.lifecycle_bridge import LifecycleBridge
            self._bridge = LifecycleBridge.get_instance()
        return self._bridge

    @property
    def intent_analyzer(self):
        if self._intent_analyzer is None:
            try:
                from dive_core.intent_analyzer import IntentAnalyzer
                self._intent_analyzer = IntentAnalyzer(language="auto")
            except Exception:
                self._intent_analyzer = None
        return self._intent_analyzer

    @property
    def skill_intelligence(self):
        if self._skill_intelligence is None:
            try:
                from dive_core.skills.skill_intelligence import SkillRegistry as IntelligenceRegistry, SkillRouter
                registry = IntelligenceRegistry()
                self._skill_intelligence = {
                    "registry": registry,
                    "router": SkillRouter(registry),
                }
            except Exception:
                self._skill_intelligence = None
        return self._skill_intelligence

    @property
    def self_debugger(self):
        if self._self_debugger is None:
            try:
                from dive_core.engine.self_debugger import SelfDebugger
                self._self_debugger = SelfDebugger.get_instance()
            except Exception:
                self._self_debugger = None
        return self._self_debugger

    @property
    def deployment_rules(self):
        if self._deployment_rules is None:
            if self.connector:
                self._deployment_rules = self.connector.get("deployment_rules")
            if self._deployment_rules is None:
                try:
                    from dive_core.engine.deployment_rules import DeploymentRules
                    self._deployment_rules = DeploymentRules.get_instance()
                except Exception:
                    self._deployment_rules = None
        return self._deployment_rules

    @property
    def dive_engine(self):
        """Get DiveEngine — 7-stage unified execution pipeline."""
        if self._dive_engine is None:
            if self.connector:
                self._dive_engine = self.connector.get_engine()
        return self._dive_engine

    @property
    def memory_brain(self):
        """Get DiveMemoryBrain — central unified memory."""
        if self._memory_brain is None:
            if self.connector:
                self._memory_brain = self.connector.get_memory()
        return self._memory_brain

    @property
    def search_engine(self):
        """Get DiveSearchEngine — algorithm RAG search."""
        if self._search_engine is None:
            if self.connector:
                self._search_engine = self.connector.get_search()
        return self._search_engine

    @property
    def thinking_engine(self):
        """Get DiveThinkingEngine — cognitive fast/slow path."""
        if self._thinking_engine is None:
            if self.connector:
                self._thinking_engine = self.connector.get_thinking_engine()
        return self._thinking_engine

    @property
    def complexity_analyzer(self):
        """Get DiveComplexityAnalyzer — task complexity scoring."""
        if self._complexity_analyzer is None:
            if self.connector:
                self._complexity_analyzer = self.connector.get("complexity_analyzer")
        return self._complexity_analyzer

    @property
    def cruel_system(self):
        """Get DiveCruelSystem — harsh self-evaluation."""
        if self._cruel_system is None:
            if self.connector:
                self._cruel_system = self.connector.get("cruel_system")
        return self._cruel_system

    @property
    def claims_ledger(self):
        """Get DiveClaimsLedger — factual claims tracker."""
        if self._claims_ledger is None:
            if self.connector:
                self._claims_ledger = self.connector.get("claims_ledger")
        return self._claims_ledger

    # ══════════════════════════════════════════════════════════
    # THINK — analyze input → execution plan
    # ══════════════════════════════════════════════════════════

    def think(self, user_input: str, context: Dict = None) -> ExecutionPlan:
        """
        Analyze user input and create a comprehensive execution plan.
        
        Flow:
          1. IntentAnalyzer → extract intent + entities
          2. SkillRouter → find candidate skills  
          3. LifecycleBridge.route() → select algorithms
          4. AlgorithmScorer → score each candidate
          5. Return ranked, optimized plan
        """
        context = context or {}
        plan = ExecutionPlan(user_input=user_input)

        # Step 1: Intent analysis
        if self.intent_analyzer:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                intent = loop.run_until_complete(
                    self.intent_analyzer.analyze(user_input, context)
                )
                loop.close()
                plan.intent = intent.to_dict() if hasattr(intent, 'to_dict') else {}
            except Exception:
                plan.intent = {"raw": user_input}
        else:
            plan.intent = {"raw": user_input}

        # Step 2: Route through lifecycle bridge (multi-algo selection)
        routing = self.bridge.route(user_input)
        plan.is_full_lifecycle = routing.should_run_full_lifecycle
        plan.stages = [s.value for s in routing.stages]

        # Step 3: Score each algorithm with AlgorithmScorer
        scored_algos = []
        for algo_name in routing.algorithms:
            algo_spec = self.bridge.algorithm_engine.get_algorithm(algo_name)
            if algo_spec:
                verified = self.bridge._verified.get(algo_name)
                scores = self._scorer.composite_score(
                    algo_spec, user_input, routing.categories, verified
                )
                partial = routing.partial_steps.get(algo_name)
                scored_algos.append({
                    "name": algo_name,
                    "category": algo_spec.category,
                    "scores": scores,
                    "composite": scores["composite"],
                    "mode": "partial" if partial else "full",
                    "partial_steps": partial,
                })

        # Sort by composite score (highest first)
        scored_algos.sort(key=lambda x: x["composite"], reverse=True)
        plan.algorithms = scored_algos
        plan.skills = routing.skill_gaps
        plan.confidence = routing.confidence

        # Step 4: Skill intelligence routing
        if self.skill_intelligence:
            try:
                task_desc = {"description": user_input, "type": "automation"}
                skill_matches = self.skill_intelligence["router"].route_task(task_desc)
                for skill_id, score in skill_matches[:5]:
                    if skill_id not in plan.skills:
                        plan.skills.append(skill_id)
            except Exception:
                pass

        # Step 5: Build reasoning
        algo_names = [a["name"] for a in scored_algos[:5]]
        avg_score = (
            sum(a["composite"] for a in scored_algos) / max(len(scored_algos), 1)
        )
        plan.reasoning = (
            f"Intent: {plan.intent.get('action', plan.intent.get('raw', '?')[:30])} | "
            f"Algorithms: {', '.join(algo_names)} (avg score: {avg_score:.2f}) | "
            f"Skills: {len(plan.skills)} gap-fillers | "
            f"{'Full lifecycle' if plan.is_full_lifecycle else f'{len(plan.stages)} stages'}"
        )

        self._total_thoughts += 1
        self._thought_history.append({
            "plan_id": plan.plan_id,
            "input": user_input[:80],
            "algos": len(scored_algos),
            "skills": len(plan.skills),
            "confidence": plan.confidence,
            "timestamp": time.time(),
        })

        return plan

    # ══════════════════════════════════════════════════════════
    # EXECUTE — run the plan
    # ══════════════════════════════════════════════════════════

    def execute(self, plan: ExecutionPlan = None,
                user_input: str = None,
                context: Dict = None) -> Dict:
        """
        Execute a plan (or auto-think + execute from user input).
        
        Flow:
          1. Check deployment rules
          2. Execute via LifecycleBridge
          3. Self-evaluate
          4. Auto-confirm/reject/debug
          5. Learn
        """
        context = context or {}

        # Auto-think if no plan provided
        if plan is None:
            if user_input is None:
                return {"success": False, "error": "No plan or user_input provided"}
            plan = self.think(user_input, context)

        # Step 1: Check deployment rules
        if self.deployment_rules:
            try:
                rule_check = self.deployment_rules.check_pre_execution(
                    plan.algorithms, plan.user_input, context
                )
                if not rule_check.get("allowed", True):
                    return {
                        "success": False,
                        "blocked_by_rules": True,
                        "rule_violations": rule_check.get("violations", []),
                        "plan_id": plan.plan_id,
                    }
            except Exception:
                pass  # Rules engine not critical

        # Step 2: Execute via bridge
        result = self.bridge.smart_execute(plan.user_input, context)
        result["plan_id"] = plan.plan_id
        result["algorithm_scores"] = {
            a["name"]: a["scores"] for a in plan.algorithms
        }

        # Step 3: Self-evaluate
        eval_score = self.self_evaluate(result, plan)
        result["eval_score"] = {
            "total": eval_score.total_score,
            "completeness": eval_score.completeness,
            "correctness": eval_score.correctness,
            "quality": eval_score.quality,
            "should_confirm": eval_score.should_confirm,
            "should_reject": eval_score.should_reject,
            "should_debug": eval_score.should_debug,
            "reasoning": eval_score.reasoning,
        }

        # Step 4: Auto-confirm/reject/debug
        execution_id = result.get("execution_id")
        if eval_score.should_confirm and execution_id:
            confirm_result = self.bridge.confirm_execution(execution_id)
            result["auto_confirmed"] = True
            result["promoted_to"] = confirm_result.get("promoted_to_algorithm")
            self._total_auto_confirms += 1
        elif eval_score.should_debug and execution_id:
            debug_result = self._try_self_debug(result, plan)
            result["debug_attempted"] = True
            result["debug_result"] = debug_result
            self._total_debug_triggers += 1
        elif eval_score.should_reject and execution_id:
            self.bridge.reject_execution(execution_id, eval_score.reasoning)
            result["auto_rejected"] = True
            self._total_auto_rejects += 1

        # Step 5: Learn (index for future RAG)
        self._learn(result, eval_score, plan)

        return result

    # ══════════════════════════════════════════════════════════
    # SELF-EVALUATE — score the result
    # ══════════════════════════════════════════════════════════

    def self_evaluate(self, result: Dict, plan: ExecutionPlan) -> EvalScore:
        """
        Evaluate execution result: completeness, correctness, quality.
        
        Auto-confirm if > 0.8, auto-reject if < 0.4, debug if between.
        """
        eval_s = EvalScore()

        # Completeness: did all planned algorithms execute?
        planned_algos = len(plan.algorithms)
        executed_algos = len(result.get("algorithms_used", []))
        if planned_algos > 0:
            eval_s.completeness = min(1.0, executed_algos / planned_algos)
        else:
            eval_s.completeness = 0.5  # No plan = unknown

        # Correctness: did execution succeed?
        if result.get("success"):
            eval_s.correctness = 0.8
            # Bonus for lifecycle completion
            if result.get("mode") == "full_lifecycle":
                stages = result.get("stages_completed", 0)
                eval_s.correctness = min(1.0, 0.5 + stages * 0.065)
            # Bonus for multi-algo
            elif result.get("mode") == "multi_algorithm":
                total_exec = result.get("total_executed", 0)
                eval_s.correctness = min(1.0, 0.6 + total_exec * 0.1)
        else:
            eval_s.correctness = 0.2

        # Quality: based on algorithm scores
        if plan.algorithms:
            avg_composite = (
                sum(a.get("composite", 0) for a in plan.algorithms)
                / len(plan.algorithms)
            )
            eval_s.quality = avg_composite
        else:
            eval_s.quality = 0.3

        # Composite
        eval_s.total_score = round(
            eval_s.completeness * 0.35 +
            eval_s.correctness * 0.40 +
            eval_s.quality * 0.25,
            3
        )

        # Decision
        eval_s.should_confirm = eval_s.total_score >= EvalScore.CONFIRM_THRESHOLD
        eval_s.should_reject = eval_s.total_score < EvalScore.REJECT_THRESHOLD
        eval_s.should_debug = (
            not eval_s.should_confirm and
            not eval_s.should_reject and
            eval_s.correctness < 0.6
        )

        # Reasoning
        parts = []
        if eval_s.should_confirm:
            parts.append(f"HIGH quality ({eval_s.total_score:.2f}) → auto-confirm")
        elif eval_s.should_reject:
            parts.append(f"LOW quality ({eval_s.total_score:.2f}) → auto-reject")
        elif eval_s.should_debug:
            parts.append(f"MEDIUM quality ({eval_s.total_score:.2f}) → trigger self-debug")
        else:
            parts.append(f"Score: {eval_s.total_score:.2f} → manual review needed")
        
        parts.append(
            f"completeness={eval_s.completeness:.2f}, "
            f"correctness={eval_s.correctness:.2f}, "
            f"quality={eval_s.quality:.2f}"
        )
        eval_s.reasoning = " | ".join(parts)

        self._eval_history.append(eval_s)
        return eval_s

    # ══════════════════════════════════════════════════════════
    # SELF-DEBUG — auto-fix failures
    # ══════════════════════════════════════════════════════════

    def _try_self_debug(self, failed_result: Dict, plan: ExecutionPlan) -> Dict:
        """Attempt self-debugging via SelfDebugger."""
        if self.self_debugger:
            try:
                diagnosis = self.self_debugger.diagnose(failed_result)
                if diagnosis.get("fixable"):
                    fix = self.self_debugger.auto_fix(diagnosis, plan.user_input)
                    return fix
                return {"attempted": True, "fixable": False, "diagnosis": diagnosis}
            except Exception as e:
                return {"attempted": True, "error": str(e)}
        return {"attempted": False, "reason": "SelfDebugger not available"}

    # ══════════════════════════════════════════════════════════
    # LEARN — index results for future RAG
    # ══════════════════════════════════════════════════════════

    def _learn(self, result: Dict, eval_score: EvalScore, plan: ExecutionPlan):
        """
        Index execution result for future retrieval.
        Each confirmed case makes future routing smarter.
        """
        # Store learning record
        learning = {
            "plan_id": plan.plan_id,
            "user_input": plan.user_input[:200],
            "algorithms": [a["name"] for a in plan.algorithms],
            "skills": plan.skills,
            "eval_total": eval_score.total_score,
            "eval_confirmed": eval_score.should_confirm,
            "eval_rejected": eval_score.should_reject,
            "timestamp": time.time(),
        }
        
        # Store in bridge pattern cache for fast lookup
        for cat in result.get("routing", {}).get("categories", []):
            key = f"learned:{cat}"
            if key not in self.bridge._pattern_cache:
                self.bridge._pattern_cache[key] = []
            self.bridge._pattern_cache[key].append(
                f"{plan.user_input[:50]}→{','.join(learning['algorithms'][:3])}"
            )

    # ══════════════════════════════════════════════════════════
    # STATS
    # ══════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        """Get DiveBrain statistics + full connector status."""
        avg_eval = 0.0
        if self._eval_history:
            avg_eval = sum(e.total_score for e in self._eval_history) / len(self._eval_history)

        stats = {
            "brain": {
                "total_thoughts": self._total_thoughts,
                "auto_confirms": self._total_auto_confirms,
                "auto_rejects": self._total_auto_rejects,
                "debug_triggers": self._total_debug_triggers,
                "average_eval_score": round(avg_eval, 3),
            },
            "components": {
                "intent_analyzer": self.intent_analyzer is not None,
                "skill_intelligence": self.skill_intelligence is not None,
                "self_debugger": self.self_debugger is not None,
                "deployment_rules": self.deployment_rules is not None,
                "lifecycle_bridge": self._bridge is not None,
                "dive_engine": self.dive_engine is not None,
                "memory_brain": self.memory_brain is not None,
                "search_engine": self.search_engine is not None,
                "thinking_engine": self.thinking_engine is not None,
                "complexity_analyzer": self.complexity_analyzer is not None,
                "cruel_system": self.cruel_system is not None,
                "claims_ledger": self.claims_ledger is not None,
            },
            "recent_thoughts": self._thought_history[-10:],
        }

        # Add connector status if available
        if self.connector:
            stats["connector"] = self.connector.get_stats()

        return stats


def get_dive_brain() -> DiveBrain:
    """Get the global DiveBrain singleton."""
    return DiveBrain.get_instance()
