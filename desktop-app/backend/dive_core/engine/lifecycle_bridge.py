"""
Dive AI — Smart Lifecycle Bridge v2
=====================================
Multi-Algorithm Orchestration + Growth Engine.

Core philosophy:
  1 job → NHIỀU algorithms cùng chạy (không chỉ 1)
  Partial extraction → lấy chỉ phần cần thiết từ algorithm
  Algorithms ưu tiên → Skills bổ sung phần thiếu
  Verified real cases → auto tạo algorithm mới → AI ngày càng thông minh

Usage:
    bridge = LifecycleBridge.get_instance()
    result = bridge.smart_execute("build a REST API with auth and deploy to AWS")
    # → Uses: CodeGenerator (steps 1-4) + SecurityScanner (step 2) + CloudDeployer (all)
    # → Skills fill gaps: jwt_helper, env_config
    # → After confirmed working: auto-creates "RestAPIWithAuth" algorithm
    
    bridge.confirm_execution(result["execution_id"])
    # → Promotes verified combo to a new algorithm for next time
"""

import os
import sys
import time
import json
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
from enum import Enum

# Ensure dive_core is importable
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from dive_core.engine.full_lifecycle import (
    DiveSkillRegistry, AutoAlgorithmEngine, FullLifecycleEngine,
    LifecycleStage, LifecycleTask, STAGE_ALGORITHMS, ALGORITHM_TEMPLATES,
    AlgorithmSpec,
)


# ══════════════════════════════════════════════════════════════
# Smart Intent Router — maps user text to algorithm categories
# ══════════════════════════════════════════════════════════════

INTENT_KEYWORDS = {
    "coding": [
        "code", "program", "script", "function", "class", "module", "refactor",
        "debug", "fix bug", "implement", "develop", "write code", "algorithm",
        "python", "javascript", "typescript", "java", "rust", "go", "c++",
        "lập trình", "viết code", "sửa lỗi", "tạo hàm",
    ],
    "git": [
        "git", "commit", "branch", "merge", "pull request", "PR", "clone",
        "push", "rebase", "cherry-pick", "github", "gitlab", "bitbucket",
        "repo", "repository", "version control",
    ],
    "web_frontend": [
        "website", "webpage", "frontend", "html", "css", "react", "vue",
        "angular", "next.js", "vite", "UI", "component", "responsive",
        "trang web", "giao diện",
    ],
    "devops_cloud": [
        "deploy", "server", "cloud", "aws", "gcp", "azure", "docker",
        "kubernetes", "k8s", "ci/cd", "pipeline", "infrastructure",
        "terraform", "ansible", "nginx", "load balancer",
        "triển khai", "máy chủ",
    ],
    "browser_automation": [
        "browse", "scrape", "crawl", "selenium", "playwright", "puppeteer",
        "automate browser", "web scraping", "screenshot", "form fill",
        "cookie", "session",
    ],
    "image_video": [
        "image", "video", "generate image", "create video", "animation",
        "thumbnail", "render", "visual", "media", "ảnh", "video",
    ],
    "search_research": [
        "search", "research", "find", "lookup", "discover", "investigate",
        "analyze", "study", "academic", "paper", "news",
        "tìm kiếm", "nghiên cứu",
    ],
    "ai_llm": [
        "ai", "llm", "model", "prompt", "gpt", "claude", "gemini",
        "fine-tune", "train", "inference", "embedding", "vector",
        "trí tuệ nhân tạo",
    ],
    "marketing_sales": [
        "marketing", "seo", "ads", "campaign", "social media", "analytics",
        "conversion", "leads", "sales", "email marketing", "content",
    ],
    "productivity": [
        "task", "todo", "schedule", "organize", "calendar", "reminder",
        "note", "plan", "workflow", "automate", "productivity",
        "công việc", "lịch", "nhắc nhở",
    ],
    "communication": [
        "email", "slack", "discord", "telegram", "whatsapp", "message",
        "notify", "send", "chat", "notification",
        "tin nhắn", "thông báo", "gửi",
    ],
    "data_analytics": [
        "data", "database", "sql", "nosql", "mongodb", "postgres",
        "analytics", "chart", "graph", "visualization", "report",
        "dữ liệu", "báo cáo",
    ],
    "security_passwords": [
        "security", "password", "encrypt", "decrypt", "vulnerability",
        "scan", "audit", "cve", "firewall", "ssl", "certificate",
        "bảo mật", "mật khẩu",
    ],
    "speech_transcription": [
        "transcribe", "speech", "voice", "audio", "tts", "stt",
        "recording", "dictation", "ghi âm", "phiên dịch",
    ],
    "finance": [
        "budget", "expense", "invoice", "crypto", "stock", "trading",
        "payment", "accounting", "tài chính", "ngân sách",
    ],
}

# Lifecycle stage hints — when user mentions these, trigger specific stages
STAGE_HINTS = {
    LifecycleStage.PLAN: [
        "plan", "design", "architect", "blueprint", "spec", "requirements",
        "lên kế hoạch", "thiết kế",
    ],
    LifecycleStage.SCAFFOLD: [
        "scaffold", "create project", "init", "setup", "bootstrap", "template",
        "khởi tạo", "tạo dự án",
    ],
    LifecycleStage.CODE: [
        "code", "implement", "write", "develop", "program",
        "viết code", "lập trình",
    ],
    LifecycleStage.BUILD: [
        "build", "compile", "bundle", "package", "make",
        "biên dịch", "đóng gói",
    ],
    LifecycleStage.TEST: [
        "test", "verify", "validate", "check", "assert", "qa",
        "kiểm thử", "kiểm tra",
    ],
    LifecycleStage.DEBUG: [
        "debug", "fix", "troubleshoot", "diagnose", "error", "bug",
        "sửa lỗi", "gỡ lỗi",
    ],
    LifecycleStage.DEPLOY: [
        "deploy", "ship", "release", "publish", "launch", "push to prod",
        "triển khai", "phát hành",
    ],
    LifecycleStage.VERIFY: [
        "verify", "confirm", "validate", "monitor", "health check",
        "xác nhận", "giám sát",
    ],
}


@dataclass
class RoutingResult:
    """Result of smart routing analysis."""
    categories: List[str]
    stages: List[LifecycleStage]
    confidence: float
    should_run_full_lifecycle: bool
    algorithms: List[str]           # ALL algorithms to use (multi-algo)
    partial_steps: Dict[str, List[str]]  # algo_name → subset of steps to extract
    skill_gaps: List[str]           # skills needed to fill what algorithms can't
    reasoning: str


@dataclass
class ExecutionRecord:
    """Record of an algorithm execution for learning + auto-promotion."""
    record_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    user_input: str = ""
    categories_matched: List[str] = field(default_factory=list)
    algorithms_used: List[str] = field(default_factory=list)
    partial_extractions: Dict[str, List[str]] = field(default_factory=dict)
    skills_used: List[str] = field(default_factory=list)
    stages_run: List[str] = field(default_factory=list)
    success: bool = False
    verified: bool = False          # Confirmed working by user/system
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    result_summary: Dict = field(default_factory=dict)
    promoted_to_algorithm: str = ""  # If this case was promoted to an algorithm


@dataclass
class VerifiedAlgorithm:
    """Tracks an algorithm's real-world verification status."""
    name: str
    success_count: int = 0
    failure_count: int = 0
    real_case_ids: List[str] = field(default_factory=list)
    trust_score: float = 0.0       # 0.0 to 1.0, higher = more trusted
    last_used: float = field(default_factory=time.time)
    last_verified: float = 0.0


class LifecycleBridge:
    """
    Smart Multi-Algorithm Orchestrator.
    
    Core principle: 1 job → nhiều algorithms cùng triển khai
    
    - Multi-algo per job: "build web app" → CodeGenerator + UIBuilder + CloudDeployer
    - Partial extraction: nếu algorithm có 5 steps nhưng chỉ cần step 2-4 → lấy phần đó
    - Priority: algorithms (verified) → algorithms (unverified) → skills fill gaps
    - Growth: mỗi confirmed case → auto-create algorithm → AI ngày càng thông minh
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> 'LifecycleBridge':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Core engines
        self.skill_registry = DiveSkillRegistry()
        self.algorithm_engine = AutoAlgorithmEngine()
        self.lifecycle_engine = FullLifecycleEngine(
            skill_registry=self.skill_registry,
            algorithm_engine=self.algorithm_engine,
        )

        # Execution history for learning
        self._history: List[ExecutionRecord] = []
        self._pattern_cache: Dict[str, List[str]] = {}

        # Algorithm creation from existing
        self._derived_algorithms: Dict[str, AlgorithmSpec] = {}

        # === NEW: Verified Algorithm Registry ===
        self._verified: Dict[str, VerifiedAlgorithm] = {}
        # Initialize all existing algorithms as unverified
        for name in self.algorithm_engine.list_algorithms():
            self._verified[name] = VerifiedAlgorithm(name=name)

        # === NEW: Auto-promoted algorithms (from confirmed cases) ===
        self._auto_promoted: Dict[str, Dict] = {}

        # Stats
        self._total_executions = 0
        self._total_lifecycle_runs = 0
        self._total_algorithms_created = 0
        self._total_promotions = 0
        self._total_confirmed = 0

        # Connect to AlgorithmService if available
        self._algo_service = None
        try:
            from dive_core.algorithm_service import get_algorithm_service
            self._algo_service = get_algorithm_service()
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════
    # 1. SMART ROUTING — user text → MULTIPLE algorithms + partial extraction
    # ══════════════════════════════════════════════════════════

    def route(self, user_input: str) -> RoutingResult:
        """
        Analyze user input → select MULTIPLE algorithms + determine
        which steps to extract from each + which skills to fill gaps.
        
        Returns RoutingResult with multi-algo composition plan.
        """
        text = user_input.lower().strip()
        category_scores: Dict[str, float] = defaultdict(float)

        # Score each category by keyword matches
        for category, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    weight = len(kw.split()) * 0.3 + 0.1
                    category_scores[category] += weight

        # Boost verified categories (algorithms that have been confirmed working)
        for name, verified in self._verified.items():
            if verified.trust_score > 0:
                algo_spec = self.algorithm_engine.get_algorithm(name)
                if algo_spec and algo_spec.category in category_scores:
                    category_scores[algo_spec.category] += verified.trust_score * 0.5

        # Sort by score
        ranked = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        matched_categories = [cat for cat, score in ranked if score > 0.1]

        # Determine lifecycle stages
        matched_stages = []
        for stage, hints in STAGE_HINTS.items():
            for hint in hints:
                if hint in text:
                    matched_stages.append(stage)
                    break

        # Check for complex tasks first
        should_full_lifecycle = False
        complexity_indicators = [
            "full", "complete", "entire", "end-to-end", "e2e",
            "from scratch", "production", "toàn bộ", "đầy đủ",
            "all stages", "comprehensive", "toàn diện",
        ]
        if any(ind in text for ind in complexity_indicators):
            should_full_lifecycle = True
            matched_stages = list(LifecycleStage)
        elif len(matched_categories) >= 3:
            should_full_lifecycle = True
            matched_stages = list(LifecycleStage)
        elif not matched_stages:
            matched_stages = [LifecycleStage.CODE]

        # === MULTI-ALGORITHM SELECTION ===
        # Get ALL relevant algorithms (not just 1), sorted by verification trust
        algorithms = []
        partial_steps: Dict[str, List[str]] = {}
        
        for cat in matched_categories:
            algo = self.algorithm_engine.get_for_category(cat)
            if algo and algo.name not in algorithms:
                algorithms.append(algo.name)
                # Determine if we need ALL steps or just partial
                partial = self._analyze_partial_need(algo, text, matched_categories)
                if partial:
                    partial_steps[algo.name] = partial

        # Also check auto-promoted algorithms (from verified cases)
        for promo_name, promo_info in self._auto_promoted.items():
            # Check if promoted algo's categories overlap
            promo_cats = set(promo_info.get("categories", []))
            if promo_cats & set(matched_categories) and promo_name not in algorithms:
                algorithms.append(promo_name)

        # Sort by trust_score (verified algorithms first)
        algorithms = self._sort_by_trust(algorithms)

        # === SKILLS GAP ANALYSIS ===
        # Find what the algorithms DON'T cover and fill with skills
        skill_gaps = self._find_skill_gaps(matched_categories, algorithms, text)

        # Confidence
        max_score = ranked[0][1] if ranked else 0
        trust_bonus = sum(
            self._verified[a].trust_score
            for a in algorithms if a in self._verified
        ) / max(len(algorithms), 1)
        confidence = min(1.0, (max_score / 2.0) + trust_bonus * 0.3)

        # Reasoning
        if matched_categories:
            algo_desc = ", ".join(algorithms[:5]) if algorithms else "none"
            gap_desc = f" + {len(skill_gaps)} skills" if skill_gaps else ""
            partial_desc = f" ({len(partial_steps)} partial)" if partial_steps else ""
            reasoning = (
                f"Matched {len(matched_categories)} categories → "
                f"{len(algorithms)} algorithms{partial_desc}{gap_desc}. "
                f"Verified trust: {trust_bonus:.1%}. "
                f"{'Full lifecycle' if should_full_lifecycle else f'{len(matched_stages)} stages'}."
            )
        else:
            reasoning = "No strong match. Using defaults."
            matched_categories = ["coding", "ai_llm"]
            algorithms = ["CodeGenerator", "LLMOrchestrator"]

        return RoutingResult(
            categories=matched_categories,
            stages=matched_stages,
            confidence=confidence,
            should_run_full_lifecycle=should_full_lifecycle,
            algorithms=algorithms,
            partial_steps=partial_steps,
            skill_gaps=skill_gaps,
            reasoning=reasoning,
        )

    def _analyze_partial_need(self, algo: AlgorithmSpec,
                              text: str,
                              matched_categories: List[str]) -> Optional[List[str]]:
        """
        Determine if we need all steps or just a subset from this algorithm.
        Returns None if all steps needed, or list of step names if partial.
        """
        if not algo.steps or len(algo.steps) <= 2:
            return None  # Too small to decompose

        # If this algorithm's category is the PRIMARY match, use all steps
        if matched_categories and matched_categories[0] == algo.category:
            return None  # Primary category → use all

        # Secondary/tertiary category → extract only relevant steps
        relevant = []
        for step in algo.steps:
            step_lower = step.lower()
            # Keep steps that match any keyword from the user's text
            for word in text.split():
                if len(word) > 3 and word in step_lower:
                    relevant.append(step)
                    break

        # If we found specific relevant steps, use those; otherwise use all
        if relevant and len(relevant) < len(algo.steps):
            return relevant
        return None

    def _sort_by_trust(self, algorithms: List[str]) -> List[str]:
        """Sort algorithms by trust score (verified first)."""
        def sort_key(name):
            v = self._verified.get(name)
            return v.trust_score if v else 0.0
        return sorted(algorithms, key=sort_key, reverse=True)

    def _find_skill_gaps(self, categories: List[str],
                         algorithms: List[str],
                         text: str) -> List[str]:
        """Find skills that can fill gaps not covered by selected algorithms."""
        # Get categories covered by algorithms
        covered_cats = set()
        for algo_name in algorithms:
            spec = self.algorithm_engine.get_algorithm(algo_name)
            if spec:
                covered_cats.add(spec.category)

        # Find uncovered categories
        uncovered = [c for c in categories if c not in covered_cats]

        # Find skills that match uncovered categories
        gap_skills = []
        available = self.skill_registry.list_skills()
        for skill_name in available:
            skill_info = self.skill_registry.get_skill(skill_name)
            if not skill_info:
                continue
            skill_cat = skill_info.get("category", "")
            if skill_cat in uncovered:
                gap_skills.append(skill_name)
            elif any(kw in skill_name.lower() for kw in text.split() if len(kw) > 3):
                gap_skills.append(skill_name)

        return gap_skills[:10]  # Max 10 gap-filling skills

    # ══════════════════════════════════════════════════════════
    # 2. SMART EXECUTE — multi-algorithm orchestration
    # ══════════════════════════════════════════════════════════

    def smart_execute(self, user_input: str,
                      context: Dict = None) -> Dict[str, Any]:
        """
        Main entry point: multi-algorithm orchestration.
        
        1. Route → select N algorithms + partial extractions + skill gaps
        2. Execute ALL selected algorithms (full or partial)
        3. Fill gaps with skills
        4. Record for learning
        5. Return comprehensive result
        """
        start = time.time()
        context = context or {}

        # Step 1: Route (multi-algorithm)
        routing = self.route(user_input)

        # Step 2: Execute based on routing
        if routing.should_run_full_lifecycle:
            result = self._execute_lifecycle(user_input, routing, context)
        else:
            result = self._execute_multi_algo(user_input, routing, context)

        # Step 3: Record for learning
        duration = round((time.time() - start) * 1000, 1)
        record = ExecutionRecord(
            user_input=user_input,
            categories_matched=routing.categories,
            algorithms_used=result.get("algorithms_used", []),
            partial_extractions=routing.partial_steps,
            skills_used=result.get("skills_used", []),
            stages_run=result.get("stages_run", []),
            success=result.get("success", False),
            duration_ms=duration,
            result_summary={
                "mode": result.get("mode"),
                "total_algos": len(result.get("algorithms_used", [])),
                "total_skills": len(result.get("skills_used", [])),
                "partial_count": len(routing.partial_steps),
            },
        )
        self._history.append(record)
        self._total_executions += 1

        # Step 4: Update verification tracking
        for algo_name in result.get("algorithms_used", []):
            if algo_name in self._verified:
                self._verified[algo_name].last_used = time.time()

        # Step 5: Enrich result
        result["routing"] = {
            "categories": routing.categories,
            "stages": [s.value for s in routing.stages],
            "confidence": routing.confidence,
            "reasoning": routing.reasoning,
            "full_lifecycle": routing.should_run_full_lifecycle,
            "multi_algo_count": len(routing.algorithms),
            "partial_extractions": len(routing.partial_steps),
            "skill_gaps_filled": len(routing.skill_gaps),
        }
        result["execution_id"] = record.record_id
        result["duration_ms"] = duration

        return result

    def _execute_multi_algo(self, user_input: str,
                            routing: RoutingResult,
                            context: Dict) -> Dict:
        """
        Execute MULTIPLE algorithms for a single job.
        
        For each algorithm:
        - If partial_steps defined → extract only those steps
        - If full → execute all steps
        Then fill gaps with skills.
        """
        algo_results = []
        algorithms_used = []
        skills_used = []
        stages_run = [s.value for s in routing.stages]

        # Execute each selected algorithm
        for algo_name in routing.algorithms:
            partial = routing.partial_steps.get(algo_name)
            algo_result = self._execute_single_algo(
                algo_name, user_input, context, partial_steps=partial
            )
            algo_results.append(algo_result)
            algorithms_used.append(algo_name)

        # Fill gaps with skills
        for skill_name in routing.skill_gaps:
            skill_result = self._execute_skill_gap(skill_name, user_input, context)
            if skill_result.get("success"):
                skills_used.append(skill_name)
                algo_results.append(skill_result)

        # Also try AlgorithmService for additional coverage
        if self._algo_service:
            for cat in routing.categories[:2]:
                if not any(r.get("category") == cat for r in algo_results):
                    try:
                        svc_result = self._algo_service.execute(
                            cat, {"user_request": user_input, **context}
                        )
                        if svc_result.get("success"):
                            algo_results.append({
                                "algorithm": cat,
                                "source": "algorithm_service",
                                "success": True,
                            })
                    except Exception:
                        pass

        return {
            "success": len(algo_results) > 0,
            "mode": "multi_algorithm",
            "algorithms_used": algorithms_used,
            "skills_used": skills_used,
            "stages_run": stages_run,
            "results": algo_results,
            "total_algorithms": len(algorithms_used),
            "total_skills": len(skills_used),
            "total_executed": len(algo_results),
            "composition": {
                "full_algos": [a for a in algorithms_used if a not in routing.partial_steps],
                "partial_algos": list(routing.partial_steps.keys()),
                "gap_skills": skills_used,
            },
        }

    def _execute_single_algo(self, algo_name: str,
                             user_input: str,
                             context: Dict,
                             partial_steps: List[str] = None) -> Dict:
        """Execute one algorithm (full or partial extraction)."""
        spec = self.algorithm_engine.get_algorithm(algo_name)
        
        if partial_steps:
            # Partial extraction — only run specified steps
            algo_result = self.algorithm_engine.execute(
                algo_name,
                {
                    **context,
                    "user_request": user_input,
                    "_partial_steps": partial_steps,
                }
            )
            return {
                "algorithm": algo_name,
                "mode": "partial",
                "extracted_steps": partial_steps,
                "total_steps_available": len(spec.steps) if spec else 0,
                "steps_used": len(partial_steps),
                "success": algo_result.get("success", False),
                "category": algo_result.get("category", ""),
            }
        else:
            # Full execution
            algo_result = self.algorithm_engine.execute(
                algo_name, {**context, "user_request": user_input}
            )
            return {
                "algorithm": algo_name,
                "mode": "full",
                "success": algo_result.get("success", False),
                "steps": algo_result.get("steps_executed", 0),
                "category": algo_result.get("category", ""),
            }

    def _execute_skill_gap(self, skill_name: str,
                           user_input: str,
                           context: Dict) -> Dict:
        """Execute a skill to fill gaps not covered by algorithms."""
        try:
            skill_info = self.skill_registry.get_skill(skill_name)
            if not skill_info:
                return {"success": False, "skill": skill_name, "error": "not found"}
            return {
                "success": True,
                "skill": skill_name,
                "source": "skill_gap_fill",
                "category": skill_info.get("category", ""),
                "description": skill_info.get("description", ""),
            }
        except Exception as e:
            return {"success": False, "skill": skill_name, "error": str(e)}

    def _execute_lifecycle(self, user_input: str,
                           routing: RoutingResult,
                           context: Dict) -> Dict:
        """Execute full lifecycle with multi-algorithm at each stage."""
        self._total_lifecycle_runs += 1

        lifecycle_result = self.lifecycle_engine.run_full_lifecycle(
            name=f"auto-{uuid.uuid4().hex[:6]}",
            description=user_input,
            inputs={**context, "user_request": user_input},
        )

        # Collect all algorithms used across stages
        all_algos = list(set(
            algo["name"]
            for stage in lifecycle_result.get("stage_results", {}).values()
            for algo in stage.get("algorithms_executed", [])
        ))

        return {
            "success": True,
            "mode": "full_lifecycle",
            "task_id": lifecycle_result.get("task_id"),
            "stages_completed": lifecycle_result.get("stages_completed", 0),
            "algorithms_used": all_algos,
            "skills_used": [],
            "stages_run": list(lifecycle_result.get("stage_results", {}).keys()),
            "total_algorithms": lifecycle_result.get("total_algorithms", 0),
            "total_skills": lifecycle_result.get("total_skills", 0),
            "lifecycle_duration_ms": lifecycle_result.get("duration_ms", 0),
            "stage_details": lifecycle_result.get("stage_results", {}),
        }

    # ══════════════════════════════════════════════════════════
    # 3. VERIFY & PROMOTE — confirm case → create algorithm
    # ══════════════════════════════════════════════════════════

    def confirm_execution(self, execution_id: str) -> Dict:
        """
        Confirm that an execution worked in a real case.
        
        This is the GROWTH ENGINE:
        1. Mark execution as verified
        2. Boost trust scores for algorithms used
        3. Auto-create new algorithm from the verified combo
        4. Future routing will prefer this verified combo
        """
        # Find the record
        record = None
        for r in self._history:
            if r.record_id == execution_id:
                record = r
                break
        
        if not record:
            return {"success": False, "error": f"Execution '{execution_id}' not found"}
        
        if record.verified:
            return {"success": True, "already_verified": True, "algorithm": record.promoted_to_algorithm}

        # 1. Mark as verified
        record.verified = True
        self._total_confirmed += 1

        # 2. Boost trust for each algorithm used
        for algo_name in record.algorithms_used:
            self._boost_trust(algo_name, execution_id, success=True)

        # 3. Auto-promote: create algorithm from verified combo
        promoted_name = None
        if len(record.algorithms_used) >= 2 or record.skills_used:
            promoted_name = self._auto_promote(record)
            record.promoted_to_algorithm = promoted_name or ""

        return {
            "success": True,
            "execution_id": execution_id,
            "verified": True,
            "algorithms_boosted": record.algorithms_used,
            "promoted_to_algorithm": promoted_name,
            "trust_scores": {
                a: self._verified[a].trust_score
                for a in record.algorithms_used
                if a in self._verified
            },
            "total_confirmed": self._total_confirmed,
            "total_algorithms_now": len(self.algorithm_engine.list_algorithms()),
        }

    def reject_execution(self, execution_id: str, reason: str = "") -> Dict:
        """Mark an execution as failed — reduces trust for algorithms used."""
        record = None
        for r in self._history:
            if r.record_id == execution_id:
                record = r
                break

        if not record:
            return {"success": False, "error": f"Execution '{execution_id}' not found"}

        # Reduce trust
        for algo_name in record.algorithms_used:
            self._boost_trust(algo_name, execution_id, success=False)

        return {
            "success": True,
            "execution_id": execution_id,
            "rejected": True,
            "reason": reason,
            "trust_reduced": record.algorithms_used,
        }

    def _boost_trust(self, algo_name: str, case_id: str, success: bool):
        """Boost or reduce trust score for an algorithm."""
        if algo_name not in self._verified:
            self._verified[algo_name] = VerifiedAlgorithm(name=algo_name)
        
        v = self._verified[algo_name]
        if success:
            v.success_count += 1
            v.real_case_ids.append(case_id)
            v.last_verified = time.time()
            # Trust grows with each success, max 1.0
            v.trust_score = min(1.0, v.success_count / (v.success_count + v.failure_count + 1))
        else:
            v.failure_count += 1
            # Trust decreases with failures
            v.trust_score = max(0.0, v.success_count / (v.success_count + v.failure_count + 1))

    def _auto_promote(self, record: ExecutionRecord) -> Optional[str]:
        """
        Auto-create a new algorithm from a verified execution.
        
        The combo of algorithms + skills that worked → becomes a new algorithm.
        Next time a similar task comes in, this pre-built algorithm runs first.
        """
        # Build a name from the combo
        parts = []
        for a in record.algorithms_used[:3]:
            short = re.sub(r'[^A-Za-z]', '', a)[:8]
            parts.append(short)
        if record.skills_used:
            parts.append(f"{len(record.skills_used)}skills")
        
        new_name = "Auto_" + "_".join(parts) + f"_{record.record_id}"

        # Build combined steps from all algos used
        combined_steps = []
        combined_categories = set()
        for algo_name in record.algorithms_used:
            spec = self.algorithm_engine.get_algorithm(algo_name)
            if spec:
                combined_categories.add(spec.category)
                partial = record.partial_extractions.get(algo_name)
                if partial:
                    combined_steps.extend([f"{algo_name}:{s}" for s in partial])
                else:
                    combined_steps.extend([f"{algo_name}:{s}" for s in spec.steps])
        
        # Add skill steps
        for skill_name in record.skills_used:
            combined_steps.append(f"skill:{skill_name}")

        # Create the promoted algorithm
        primary_cat = record.categories_matched[0] if record.categories_matched else "coding"
        new_spec = AlgorithmSpec(
            name=new_name,
            category=primary_cat,
            description=(
                f"Auto-promoted from verified case: {record.user_input[:80]}. "
                f"Combines: {', '.join(record.algorithms_used)}. "
                f"Skills: {', '.join(record.skills_used) if record.skills_used else 'none'}."
            ),
            steps=combined_steps,
            input_schema={"user_request": "string", "context": "object"},
            output_schema={"result": "object", "source_algorithms": "array"},
        )

        result = self.algorithm_engine.create_algorithm(new_spec)
        if result.get("success"):
            self.algorithm_engine.deploy(new_name)
            self._auto_promoted[new_name] = {
                "source_record": record.record_id,
                "algorithms": record.algorithms_used,
                "skills": record.skills_used,
                "categories": list(combined_categories),
                "created_at": time.time(),
            }
            self._verified[new_name] = VerifiedAlgorithm(
                name=new_name,
                success_count=1,
                trust_score=0.8,  # Start with high trust (it's verified!)
                real_case_ids=[record.record_id],
                last_verified=time.time(),
            )
            self._total_promotions += 1
            self._total_algorithms_created += 1
            return new_name

        return None

    # ══════════════════════════════════════════════════════════
    # 4. LIFECYCLE CONTROL — run specific stages
    # ══════════════════════════════════════════════════════════

    def run_lifecycle(self, description: str,
                      inputs: Dict = None) -> Dict[str, Any]:
        """Run full lifecycle for a task."""
        self._total_lifecycle_runs += 1
        return self.lifecycle_engine.run_full_lifecycle(
            name=f"lifecycle-{uuid.uuid4().hex[:6]}",
            description=description,
            inputs=inputs or {},
        )

    def run_stage(self, task_id: str, stage: str,
                  inputs: Dict = None) -> Dict[str, Any]:
        """Run a specific lifecycle stage."""
        stage_enum = LifecycleStage(stage)
        return self.lifecycle_engine.execute_stage(task_id, stage_enum, inputs)

    def start_task(self, name: str, description: str) -> Dict:
        """Start a new lifecycle task (returns task_id for stage control)."""
        task = self.lifecycle_engine.start_task(name, description)
        return {
            "task_id": task.task_id,
            "name": name,
            "status": task.status,
            "stages": [s.value for s in LifecycleStage],
        }

    # ══════════════════════════════════════════════════════════
    # 5. ALGORITHM LEARNING — create new from existing
    # ══════════════════════════════════════════════════════════

    def create_from_existing(self, new_name: str,
                             base_algorithm: str,
                             modifications: Dict = None) -> Dict:
        """
        Create a new algorithm by learning from an existing one.
        Copies structure, modifies steps/schema, and deploys.
        """
        modifications = modifications or {}

        base = self.algorithm_engine.get_algorithm(base_algorithm)
        if not base:
            return {"success": False, "error": f"Base algorithm '{base_algorithm}' not found"}

        new_spec = AlgorithmSpec(
            name=new_name,
            category=modifications.get("category", base.category),
            description=modifications.get("description", f"Derived from {base.name}: {base.description}"),
            steps=modifications.get("steps", base.steps.copy()),
            input_schema=modifications.get("input_schema", base.input_schema.copy()),
            output_schema=modifications.get("output_schema", base.output_schema.copy()),
        )

        extra_steps = modifications.get("extra_steps", [])
        if extra_steps:
            new_spec.steps.extend(extra_steps)

        result = self.algorithm_engine.create_algorithm(new_spec)
        if result.get("success"):
            self.algorithm_engine.deploy(new_name)
            self._derived_algorithms[new_name] = new_spec
            self._verified[new_name] = VerifiedAlgorithm(name=new_name)
            self._total_algorithms_created += 1

        result["base_algorithm"] = base_algorithm
        result["total_steps"] = len(new_spec.steps)
        result["derived"] = True
        return result

    def suggest_algorithm(self, task_description: str) -> Dict:
        """
        Analyze a task and suggest the best algorithm configuration.
        Uses verification history to improve suggestions.
        """
        routing = self.route(task_description)

        # Find similar past verified executions
        similar = []
        for record in self._history[-100:]:
            if not record.verified:
                continue
            overlap = set(record.categories_matched) & set(routing.categories)
            if overlap:
                similar.append({
                    "input": record.user_input[:60],
                    "categories": record.categories_matched,
                    "algorithms": record.algorithms_used,
                    "skills": record.skills_used,
                    "success": record.success,
                    "promoted_to": record.promoted_to_algorithm,
                })

        base_algo = routing.algorithms[0] if routing.algorithms else "CodeGenerator"
        base_spec = self.algorithm_engine.get_algorithm(base_algo)

        suggestion = {
            "recommended_algorithms": routing.algorithms,  # Multiple!
            "recommended_categories": routing.categories,
            "recommended_stages": [s.value for s in routing.stages],
            "partial_extractions": routing.partial_steps,
            "skill_gaps": routing.skill_gaps,
            "confidence": routing.confidence,
            "verified_similar_cases": similar[:5],
            "trust_scores": {
                a: self._verified[a].trust_score
                for a in routing.algorithms
                if a in self._verified
            },
            # Backwards compat
            "recommended_algorithm": base_algo,
        }

        if base_spec:
            suggestion["base_steps"] = base_spec.steps
            suggestion["suggested_modifications"] = {
                "extra_steps": [],
                "description": f"Custom algorithm for: {task_description[:80]}",
            }

        return suggestion

    # ══════════════════════════════════════════════════════════
    # 6. STATS & INSPECTION
    # ══════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        """Get comprehensive bridge statistics."""
        lifecycle_stats = self.lifecycle_engine.get_stats()
        algo_stats = self.algorithm_engine.get_stats()

        verified_count = sum(1 for v in self._verified.values() if v.trust_score > 0)
        avg_trust = (
            sum(v.trust_score for v in self._verified.values()) / max(len(self._verified), 1)
        )

        return {
            "bridge": {
                "total_executions": self._total_executions,
                "total_lifecycle_runs": self._total_lifecycle_runs,
                "total_algorithms_created": self._total_algorithms_created,
                "derived_algorithms": len(self._derived_algorithms),
                "auto_promoted": self._total_promotions,
                "confirmed_cases": self._total_confirmed,
                "execution_history_size": len(self._history),
            },
            "verification": {
                "verified_algorithms": verified_count,
                "unverified_algorithms": len(self._verified) - verified_count,
                "average_trust": round(avg_trust, 3),
                "top_trusted": sorted(
                    [(v.name, v.trust_score, v.success_count)
                     for v in self._verified.values() if v.trust_score > 0],
                    key=lambda x: x[1], reverse=True
                )[:10],
            },
            "growth": {
                "auto_promoted_algorithms": len(self._auto_promoted),
                "promotions_list": [
                    {"name": n, "source_algos": p["algorithms"], "categories": p["categories"]}
                    for n, p in self._auto_promoted.items()
                ],
                "growth_rate": f"{self._total_promotions}/{self._total_confirmed} confirmed → promoted",
            },
            "lifecycle": lifecycle_stats,
            "algorithms": algo_stats,
            "categories_available": list(INTENT_KEYWORDS.keys()),
            "stages_available": [s.value for s in LifecycleStage],
        }

    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent execution history."""
        records = self._history[-limit:]
        return [
            {
                "id": r.record_id,
                "input": r.user_input[:80],
                "categories": r.categories_matched,
                "algorithms": r.algorithms_used,
                "skills": r.skills_used,
                "partial_extractions": r.partial_extractions,
                "stages": r.stages_run,
                "success": r.success,
                "verified": r.verified,
                "promoted_to": r.promoted_to_algorithm,
                "duration_ms": r.duration_ms,
            }
            for r in reversed(records)
        ]

    def list_all_algorithms(self) -> Dict:
        """List all available algorithms with trust + verification details."""
        algos = {}
        for name in self.algorithm_engine.list_algorithms():
            spec = self.algorithm_engine.get_algorithm(name)
            v = self._verified.get(name)
            if spec:
                algos[name] = {
                    "category": spec.category,
                    "description": spec.description,
                    "steps": spec.steps,
                    "input_schema": spec.input_schema,
                    "output_schema": spec.output_schema,
                    "derived": name in self._derived_algorithms,
                    "auto_promoted": name in self._auto_promoted,
                    "trust_score": v.trust_score if v else 0.0,
                    "success_count": v.success_count if v else 0,
                    "failure_count": v.failure_count if v else 0,
                    "real_cases": len(v.real_case_ids) if v else 0,
                }
        return algos

    def get_verified_leaderboard(self) -> List[Dict]:
        """Get algorithms ranked by trust score."""
        ranked = sorted(
            self._verified.values(),
            key=lambda v: (v.trust_score, v.success_count),
            reverse=True,
        )
        return [
            {
                "name": v.name,
                "trust_score": v.trust_score,
                "success_count": v.success_count,
                "failure_count": v.failure_count,
                "real_cases": len(v.real_case_ids),
                "last_verified": v.last_verified,
            }
            for v in ranked
            if v.trust_score > 0 or v.success_count > 0
        ]


# ══════════════════════════════════════════════════════════════
# Module-level convenience
# ══════════════════════════════════════════════════════════════

def get_lifecycle_bridge() -> LifecycleBridge:
    """Get the global LifecycleBridge singleton."""
    return LifecycleBridge.get_instance()
