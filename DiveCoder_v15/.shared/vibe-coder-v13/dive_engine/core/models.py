"""
Dive Engine V2 - Core Data Models
==================================

This module defines the core data structures for the Dive Engine,
incorporating concepts from both GPT-5.2 and Claude Opus 4.5 thinking models.

Key Concepts:
- Dual-Path Routing (Fast vs Think)
- Extended Thinking with Budget Control
- Interleaved Thinking for Tool Integration
- Evidence Levels (E0-E3)
- Cognitive Phases (6-phase loop)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def utcnow_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def generate_run_id() -> str:
    """Generate a unique run ID."""
    return f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"


# =============================================================================
# ENUMS
# =============================================================================

class TaskMode(Enum):
    """Task execution modes."""
    ANALYSIS = "analysis"
    BUILD = "build"
    DEBUG = "debug"
    SECURITY_REVIEW = "security_review"
    PERFORMANCE = "performance"
    GENERAL = "general"


class EvidenceLevel(Enum):
    """Evidence levels for artifact classification.
    
    E0: Reasoning only (no external validation)
    E1: User-provided logs/inputs
    E2: Tool-executed output (stdout, test logs)
    E3: Reproducible artifacts (SARIF, reports, baseline-compare)
    """
    E0 = "E0"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"


class TaskType(Enum):
    """Task type classification for routing decisions."""
    DEBUG = "debug"
    BUILD = "build"
    SECURITY = "security"
    PERFORMANCE = "performance"
    WEBSITE = "website"
    GENERIC = "generic"
    CODE_REVIEW = "code_review"
    REFACTOR = "refactor"


class RiskClass(Enum):
    """Risk classification for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoutingPath(Enum):
    """Routing path selection."""
    FAST = "fast"
    THINK = "think"


class EffortLevel(Enum):
    """Reasoning effort level.
    
    Maps to:
    - GPT-5.2: reasoning.effort parameter
    - Claude Opus 4.5: budget_tokens allocation
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ThinkingStrategy(Enum):
    """Thinking strategy selection.
    
    Based on GPT-5.2 and Claude Opus 4.5 mechanisms:
    - SINGLE_PASS: Direct response (fast path)
    - CHAIN_OF_THOUGHT: Sequential reasoning
    - EXTENDED_THINKING: Claude-style budget-controlled thinking
    - INTERLEAVED: Tool-integrated reasoning
    - MULTI_SAMPLE: Multiple candidates + voting
    - SEARCH_BEAM: Beam-style exploration
    """
    SINGLE_PASS = "single_pass"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    EXTENDED_THINKING = "extended_thinking"
    INTERLEAVED = "interleaved"
    MULTI_SAMPLE = "multi_sample"
    SEARCH_BEAM = "search_beam"


class CognitivePhase(Enum):
    """Cognitive phases in the thinking loop.
    
    Based on Claude Opus 4.5 Extended Thinking phases:
    1. INPUT_PROCESSING: Normalize prompt → structured task spec
    2. EXPLORATION: Generate candidate approaches
    3. ANALYSIS: Pick approach, write plan with risks
    4. VERIFICATION: Run gates/tests/scans
    5. CONCLUSION: Synthesize final decisions
    6. OUTPUT_GENERATION: Format final answer + artifacts
    """
    INPUT_PROCESSING = "input_processing"
    EXPLORATION = "exploration"
    ANALYSIS = "analysis"
    VERIFICATION = "verification"
    CONCLUSION = "conclusion"
    OUTPUT_GENERATION = "output_generation"


class MonitorVerdict(Enum):
    """Monitor evaluation verdict."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    NEEDS_FOLLOWUP = "needs_followup"


# =============================================================================
# CORE DATA CLASSES
# =============================================================================

@dataclass
class RunSpec:
    """Specification for a Dive Engine run.
    
    This is the primary input to the engine, containing all information
    needed to execute a task with appropriate routing and effort.
    """
    run_id: str = field(default_factory=generate_run_id)
    mode: str = "generic"
    task_type: TaskType = TaskType.GENERIC
    repo_root: str = "."
    
    # Input specification
    prompt: str = ""
    references: List[str] = field(default_factory=list)
    context_files: List[str] = field(default_factory=list)
    
    # Constraints
    required_evidence_level: EvidenceLevel = EvidenceLevel.E2
    latency_budget_ms: int = 300000  # 5 minutes default
    cost_budget_usd: float = 1.0
    max_tool_calls: int = 20
    max_llm_calls: int = 10
    
    # Privacy settings
    store_scratchpad: bool = False
    redact_logs: bool = True
    
    # Provider preferences
    provider_route: Optional[str] = None
    preferred_model: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "task_type": self.task_type.value,
            "repo_root": self.repo_root,
            "inputs": {
                "prompt": self.prompt,
                "references": self.references,
                "context_files": self.context_files,
            },
            "constraints": {
                "required_evidence_level": self.required_evidence_level.value,
                "latency_budget_ms": self.latency_budget_ms,
                "cost_budget_usd": self.cost_budget_usd,
                "max_tool_calls": self.max_tool_calls,
                "max_llm_calls": self.max_llm_calls,
                "privacy": {
                    "store_scratchpad": self.store_scratchpad,
                    "redact_logs": self.redact_logs,
                },
            },
            "provider_preferences": {
                "provider_route": self.provider_route,
                "preferred_model": self.preferred_model,
            },
            "created_at": self.created_at,
            "tags": self.tags,
        }


@dataclass
class RouterDecision:
    """Output of the dual-path router.
    
    Determines whether to use fast path or thinking path,
    based on task complexity, risk, and evidence requirements.
    
    Artifact: router_decision.json (E2)
    """
    run_id: str
    path: RoutingPath
    
    # Decision factors
    task_type: TaskType
    risk_class: RiskClass
    required_evidence: EvidenceLevel
    complexity_score: float  # 0.0 - 1.0
    
    # Routing rationale
    policy_branch: str  # Which policy rule was triggered
    rationale: str
    
    # Model tier selection
    selected_tier: str  # tier_fast, tier_think, tier_monitor
    fallback_tiers: List[str] = field(default_factory=list)
    
    # Thinking strategy
    thinking_strategy: ThinkingStrategy = ThinkingStrategy.SINGLE_PASS
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    router_version: str = "2.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "path": self.path.value,
            "decision_factors": {
                "task_type": self.task_type.value,
                "risk_class": self.risk_class.value,
                "required_evidence": self.required_evidence.value,
                "complexity_score": self.complexity_score,
            },
            "routing": {
                "policy_branch": self.policy_branch,
                "rationale": self.rationale,
                "selected_tier": self.selected_tier,
                "fallback_tiers": self.fallback_tiers,
                "thinking_strategy": self.thinking_strategy.value,
            },
            "meta": {
                "created_at": self.created_at,
                "router_version": self.router_version,
            },
        }
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RouterDecision":
        factors = d.get("decision_factors", {})
        routing = d.get("routing", {})
        meta = d.get("meta", {})
        
        return RouterDecision(
            run_id=d.get("run_id", ""),
            path=RoutingPath(d.get("path", "fast")),
            task_type=TaskType(factors.get("task_type", "generic")),
            risk_class=RiskClass(factors.get("risk_class", "low")),
            required_evidence=EvidenceLevel(factors.get("required_evidence", "E2")),
            complexity_score=factors.get("complexity_score", 0.0),
            policy_branch=routing.get("policy_branch", ""),
            rationale=routing.get("rationale", ""),
            selected_tier=routing.get("selected_tier", "tier_fast"),
            fallback_tiers=routing.get("fallback_tiers", []),
            thinking_strategy=ThinkingStrategy(routing.get("thinking_strategy", "single_pass")),
            created_at=meta.get("created_at", utcnow_iso()),
            router_version=meta.get("router_version", "2.0.0"),
        )


@dataclass
class EffortPlan:
    """Reasoning effort allocation plan.
    
    Controls how much computational effort to allocate for reasoning,
    based on GPT-5.2 reasoning.effort and Claude Opus 4.5 budget_tokens.
    
    Artifact: effort_plan.json (E2)
    """
    run_id: str
    effort_level: EffortLevel
    
    # Budget allocation (Claude-style)
    budget_tokens: int  # Max tokens for thinking
    budget_used: int = 0
    
    # Inference-time scaling (GPT-style)
    num_samples: int = 1  # Number of candidate generations
    use_self_consistency: bool = False
    use_search_beam: bool = False
    beam_width: int = 1
    
    # Tool verification loop
    max_tool_verify_iterations: int = 3
    tool_verify_enabled: bool = True
    
    # Interleaved thinking (Claude-style)
    interleaved_thinking_enabled: bool = False
    preserve_thinking_blocks: bool = True  # Opus 4.5 feature
    
    # Cognitive phases to execute
    phases: List[CognitivePhase] = field(default_factory=lambda: list(CognitivePhase))
    
    # Rationale
    rationale: str = ""
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "effort_level": self.effort_level.value,
            "budget": {
                "budget_tokens": self.budget_tokens,
                "budget_used": self.budget_used,
            },
            "inference_scaling": {
                "num_samples": self.num_samples,
                "use_self_consistency": self.use_self_consistency,
                "use_search_beam": self.use_search_beam,
                "beam_width": self.beam_width,
            },
            "tool_verification": {
                "max_iterations": self.max_tool_verify_iterations,
                "enabled": self.tool_verify_enabled,
            },
            "thinking": {
                "interleaved_enabled": self.interleaved_thinking_enabled,
                "preserve_blocks": self.preserve_thinking_blocks,
            },
            "phases": [p.value for p in self.phases],
            "rationale": self.rationale,
            "created_at": self.created_at,
        }
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "EffortPlan":
        budget = d.get("budget", {})
        scaling = d.get("inference_scaling", {})
        tool_verify = d.get("tool_verification", {})
        thinking = d.get("thinking", {})
        
        return EffortPlan(
            run_id=d.get("run_id", ""),
            effort_level=EffortLevel(d.get("effort_level", "medium")),
            budget_tokens=budget.get("budget_tokens", 10000),
            budget_used=budget.get("budget_used", 0),
            num_samples=scaling.get("num_samples", 1),
            use_self_consistency=scaling.get("use_self_consistency", False),
            use_search_beam=scaling.get("use_search_beam", False),
            beam_width=scaling.get("beam_width", 1),
            max_tool_verify_iterations=tool_verify.get("max_iterations", 3),
            tool_verify_enabled=tool_verify.get("enabled", True),
            interleaved_thinking_enabled=thinking.get("interleaved_enabled", False),
            preserve_thinking_blocks=thinking.get("preserve_blocks", True),
            phases=[CognitivePhase(p) for p in d.get("phases", [])],
            rationale=d.get("rationale", ""),
            created_at=d.get("created_at", utcnow_iso()),
        )


@dataclass
class BudgetPlan:
    """Budget allocation for a run.
    
    Tracks token, time, and cost budgets.
    
    Artifact: budget_plan.json (E2)
    """
    run_id: str
    
    # Token budgets
    input_token_budget: int = 100000
    output_token_budget: int = 50000
    thinking_token_budget: int = 10000
    
    # Time budget
    latency_budget_ms: int = 300000
    
    # Cost budget
    cost_budget_usd: float = 1.0
    estimated_cost_usd: float = 0.0
    
    # Call limits
    max_llm_calls: int = 10
    max_tool_calls: int = 20
    
    # Usage tracking
    llm_calls_used: int = 0
    tool_calls_used: int = 0
    tokens_used: int = 0
    thinking_tokens_used: int = 0
    elapsed_ms: int = 0
    actual_cost_usd: float = 0.0
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "budgets": {
                "input_token_budget": self.input_token_budget,
                "output_token_budget": self.output_token_budget,
                "thinking_token_budget": self.thinking_token_budget,
                "latency_budget_ms": self.latency_budget_ms,
                "cost_budget_usd": self.cost_budget_usd,
                "estimated_cost_usd": self.estimated_cost_usd,
                "max_llm_calls": self.max_llm_calls,
                "max_tool_calls": self.max_tool_calls,
            },
            "usage": {
                "llm_calls_used": self.llm_calls_used,
                "tool_calls_used": self.tool_calls_used,
                "tokens_used": self.tokens_used,
                "thinking_tokens_used": self.thinking_tokens_used,
                "elapsed_ms": self.elapsed_ms,
                "actual_cost_usd": self.actual_cost_usd,
            },
            "created_at": self.created_at,
        }


@dataclass
class ThinkingBlock:
    """A single thinking block (Claude Opus 4.5 style).
    
    Represents a unit of internal reasoning that can be
    preserved across conversation turns.
    """
    block_id: str
    phase: CognitivePhase
    content: str
    signature: str  # For verification
    
    # Token tracking
    tokens_used: int = 0
    
    # Redaction status
    is_redacted: bool = False
    redacted_data: Optional[str] = None  # Base64 encoded if redacted
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "phase": self.phase.value,
            "content": self.content if not self.is_redacted else "[REDACTED]",
            "signature": self.signature,
            "tokens_used": self.tokens_used,
            "is_redacted": self.is_redacted,
            "redacted_data": self.redacted_data,
            "created_at": self.created_at,
        }


@dataclass
class ThinkingPhase:
    """A complete cognitive phase with multiple thinking blocks.
    
    Tracks the execution of a single phase in the 6-phase cognitive loop.
    """
    phase: CognitivePhase
    run_id: str
    
    # Thinking blocks generated in this phase
    blocks: List[ThinkingBlock] = field(default_factory=list)
    
    # Phase status
    status: str = "pending"  # pending, running, completed, failed
    
    # Tool interactions (for interleaved thinking)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Self-correction tracking
    corrections_made: int = 0
    correction_details: List[str] = field(default_factory=list)
    
    # Artifacts produced
    artifacts: List[str] = field(default_factory=list)
    
    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "run_id": self.run_id,
            "blocks": [b.to_dict() for b in self.blocks],
            "status": self.status,
            "tool_interactions": {
                "tool_calls": self.tool_calls,
                "tool_results": self.tool_results,
            },
            "self_correction": {
                "corrections_made": self.corrections_made,
                "correction_details": self.correction_details,
            },
            "artifacts": self.artifacts,
            "timing": {
                "started_at": self.started_at,
                "completed_at": self.completed_at,
                "duration_ms": self.duration_ms,
            },
        }


@dataclass
class MonitorReport:
    """Monitor evaluation report.
    
    Implements proxy monitorability with follow-up questions,
    based on OpenAI's chain-of-thought monitoring research.
    
    Artifact: monitor_report.json (E2)
    """
    run_id: str
    verdict: MonitorVerdict
    
    # Evaluation scores (0.0 - 1.0)
    completeness_score: float = 0.0
    logical_coherence_score: float = 0.0
    evidence_coverage_score: float = 0.0
    risk_assessment_score: float = 0.0
    
    # Findings
    findings: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Follow-up questions (for improved monitorability)
    followup_questions: List[str] = field(default_factory=list)
    followup_responses: List[Dict[str, Any]] = field(default_factory=list)
    followup_iterations: int = 0
    max_followup_iterations: int = 3
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Monitor model info
    monitor_model: str = "tier_monitor"
    monitor_prompt_version: str = "1.0.0"
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "verdict": self.verdict.value,
            "scores": {
                "completeness": self.completeness_score,
                "logical_coherence": self.logical_coherence_score,
                "evidence_coverage": self.evidence_coverage_score,
                "risk_assessment": self.risk_assessment_score,
            },
            "findings": self.findings,
            "warnings": self.warnings,
            "errors": self.errors,
            "followup": {
                "questions": self.followup_questions,
                "responses": self.followup_responses,
                "iterations": self.followup_iterations,
                "max_iterations": self.max_followup_iterations,
            },
            "recommendations": self.recommendations,
            "monitor_info": {
                "model": self.monitor_model,
                "prompt_version": self.monitor_prompt_version,
            },
            "created_at": self.created_at,
        }


@dataclass
class ProcessTraceSummary:
    """Structured process trace summary.
    
    A privacy-preserving summary of the reasoning process,
    suitable for auditing without exposing raw chain-of-thought.
    
    Artifact: process_trace_summary.md (E0/E1)
    """
    run_id: str
    
    # High-level summary
    task_summary: str = ""
    approach_summary: str = ""
    
    # Phase summaries
    phase_summaries: Dict[str, str] = field(default_factory=dict)
    
    # Key decisions
    key_decisions: List[Dict[str, str]] = field(default_factory=list)
    
    # Assumptions made
    assumptions: List[str] = field(default_factory=list)
    
    # Risks identified
    risks: List[Dict[str, str]] = field(default_factory=list)
    
    # Evidence plan
    evidence_plan: List[Dict[str, str]] = field(default_factory=list)
    
    # Tool usage summary
    tools_used: List[Dict[str, Any]] = field(default_factory=list)
    
    # Self-corrections
    corrections: List[Dict[str, str]] = field(default_factory=list)
    
    # Final outcome
    outcome: str = ""
    confidence: float = 0.0
    
    # Metadata
    created_at: str = field(default_factory=utcnow_iso)
    
    def to_markdown(self) -> str:
        """Generate markdown representation."""
        lines = [
            f"# Process Trace Summary",
            f"",
            f"**Run ID:** {self.run_id}",
            f"**Created:** {self.created_at}",
            f"",
            f"## Task Summary",
            f"",
            self.task_summary,
            f"",
            f"## Approach",
            f"",
            self.approach_summary,
            f"",
            f"## Phase Summaries",
            f"",
        ]
        
        for phase, summary in self.phase_summaries.items():
            lines.append(f"### {phase}")
            lines.append(f"")
            lines.append(summary)
            lines.append(f"")
        
        lines.extend([
            f"## Key Decisions",
            f"",
        ])
        for i, decision in enumerate(self.key_decisions, 1):
            lines.append(f"{i}. **{decision.get('decision', 'N/A')}**")
            lines.append(f"   - Rationale: {decision.get('rationale', 'N/A')}")
            lines.append(f"")
        
        lines.extend([
            f"## Assumptions",
            f"",
        ])
        for assumption in self.assumptions:
            lines.append(f"- {assumption}")
        lines.append(f"")
        
        lines.extend([
            f"## Risks Identified",
            f"",
        ])
        for risk in self.risks:
            lines.append(f"- **{risk.get('risk', 'N/A')}** ({risk.get('severity', 'unknown')})")
            lines.append(f"  - Mitigation: {risk.get('mitigation', 'N/A')}")
        lines.append(f"")
        
        lines.extend([
            f"## Evidence Plan",
            f"",
        ])
        for evidence in self.evidence_plan:
            lines.append(f"- [{evidence.get('level', 'E0')}] {evidence.get('artifact', 'N/A')}")
            lines.append(f"  - Source: {evidence.get('source', 'N/A')}")
        lines.append(f"")
        
        lines.extend([
            f"## Tools Used",
            f"",
        ])
        for tool in self.tools_used:
            lines.append(f"- **{tool.get('name', 'N/A')}**: {tool.get('purpose', 'N/A')}")
            lines.append(f"  - Result: {tool.get('result_summary', 'N/A')}")
        lines.append(f"")
        
        if self.corrections:
            lines.extend([
                f"## Self-Corrections",
                f"",
            ])
            for correction in self.corrections:
                lines.append(f"- **Original:** {correction.get('original', 'N/A')}")
                lines.append(f"  - **Corrected:** {correction.get('corrected', 'N/A')}")
                lines.append(f"  - **Reason:** {correction.get('reason', 'N/A')}")
            lines.append(f"")
        
        lines.extend([
            f"## Outcome",
            f"",
            f"**Result:** {self.outcome}",
            f"",
            f"**Confidence:** {self.confidence:.1%}",
        ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_summary": self.task_summary,
            "approach_summary": self.approach_summary,
            "phase_summaries": self.phase_summaries,
            "key_decisions": self.key_decisions,
            "assumptions": self.assumptions,
            "risks": self.risks,
            "evidence_plan": self.evidence_plan,
            "tools_used": self.tools_used,
            "corrections": self.corrections,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "created_at": self.created_at,
        }
