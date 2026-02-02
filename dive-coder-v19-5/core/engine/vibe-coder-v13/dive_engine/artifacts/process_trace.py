"""
Dive Engine V2 - Process Trace Generator
=========================================

This module implements the structured process trace summary generator.
The process trace is a privacy-preserving summary of the reasoning process,
suitable for auditing without exposing raw chain-of-thought.

Key Features:
- Structured bullet steps
- Assumptions and risks
- Evidence plan
- Tool usage summary
- Self-corrections tracking

Artifact: process_trace_summary.md (E0/E1)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from dive_engine.core.models import (
    BudgetPlan,
    CognitivePhase,
    EffortPlan,
    EvidenceLevel,
    ProcessTraceSummary,
    RouterDecision,
    RunSpec,
    ThinkingBlock,
    ThinkingPhase,
    utcnow_iso,
)


# =============================================================================
# TRACE TEMPLATES
# =============================================================================

PHASE_SUMMARY_TEMPLATES = {
    CognitivePhase.INPUT_PROCESSING: """
**Objective:** Normalize and structure the input prompt into a clear task specification.

**Actions:**
- Parsed user prompt and extracted key requirements
- Identified {context_file_count} context files
- Classified task as: {task_type}
- Determined evidence requirement: {evidence_level}

**Output:** Structured task specification ready for exploration.
""",
    
    CognitivePhase.EXPLORATION: """
**Objective:** Generate and evaluate candidate approaches.

**Candidates Explored:** {num_candidates}

**Selected Approach:** {selected_approach}

**Selection Rationale:** {selection_rationale}
""",
    
    CognitivePhase.ANALYSIS: """
**Objective:** Deep analysis of selected approach with risk assessment.

**Problem Decomposition:**
{decomposition}

**Dependencies Identified:** {dependency_count}

**Risk Assessment:**
- Risk Class: {risk_class}
- Complexity Score: {complexity_score:.2f}
""",
    
    CognitivePhase.VERIFICATION: """
**Objective:** Verify implementation through tool-based checks.

**Verification Steps:**
{verification_steps}

**Tool Calls Made:** {tool_call_count}
**Iterations:** {iteration_count} / {max_iterations}

**Verification Status:** {verification_status}
""",
    
    CognitivePhase.CONCLUSION: """
**Objective:** Synthesize findings and prepare final recommendations.

**Key Findings:**
{key_findings}

**Confidence Level:** {confidence:.0%}

**Recommendations:**
{recommendations}
""",
    
    CognitivePhase.OUTPUT_GENERATION: """
**Objective:** Generate final output with evidence artifacts.

**Output Components:**
- Response text: {has_response}
- Code changes: {has_code_changes}
- Evidence artifacts: {artifact_count}

**Claims Generated:** {claim_count}
""",
}


class ProcessTraceGenerator:
    """
    Generator for structured process trace summaries.
    
    This class creates process_trace_summary.md from thinking phases,
    providing a privacy-preserving audit trail of the reasoning process.
    """
    
    def __init__(self):
        """Initialize the generator."""
        self.templates = PHASE_SUMMARY_TEMPLATES
    
    def generate(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
        phases: Dict[CognitivePhase, ThinkingPhase],
        tools_used: Optional[List[Dict[str, Any]]] = None,
    ) -> ProcessTraceSummary:
        """
        Generate a complete process trace summary.
        
        Args:
            run_spec: The run specification
            router_decision: The routing decision
            effort_plan: The effort plan
            phases: Executed thinking phases
            tools_used: List of tools used during execution
            
        Returns:
            ProcessTraceSummary with all trace information
        """
        trace = ProcessTraceSummary(run_id=run_spec.run_id)
        
        # Generate task summary
        trace.task_summary = self._generate_task_summary(run_spec, router_decision)
        
        # Generate approach summary
        trace.approach_summary = self._generate_approach_summary(
            router_decision, effort_plan
        )
        
        # Generate phase summaries
        trace.phase_summaries = self._generate_phase_summaries(
            phases, run_spec, router_decision, effort_plan
        )
        
        # Extract key decisions
        trace.key_decisions = self._extract_key_decisions(
            router_decision, effort_plan, phases
        )
        
        # Extract assumptions
        trace.assumptions = self._extract_assumptions(run_spec, router_decision)
        
        # Extract risks
        trace.risks = self._extract_risks(router_decision, phases)
        
        # Generate evidence plan
        trace.evidence_plan = self._generate_evidence_plan(
            run_spec, router_decision, phases
        )
        
        # Summarize tools used
        trace.tools_used = tools_used or self._extract_tools_from_phases(phases)
        
        # Extract corrections
        trace.corrections = self._extract_corrections(phases)
        
        # Determine outcome
        trace.outcome, trace.confidence = self._determine_outcome(phases)
        
        return trace
    
    def _generate_task_summary(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
    ) -> str:
        """Generate high-level task summary."""
        return f"""
This run ({run_spec.run_id}) processes a **{run_spec.task_type.value}** task in **{run_spec.mode}** mode.

The task was routed to the **{router_decision.path.value}** path with **{router_decision.thinking_strategy.value}** strategy, based on:
- Risk class: {router_decision.risk_class.value}
- Complexity score: {router_decision.complexity_score:.2f}
- Required evidence: {run_spec.required_evidence_level.value}

**Input:** {run_spec.prompt[:200]}{'...' if len(run_spec.prompt) > 200 else ''}
""".strip()
    
    def _generate_approach_summary(
        self,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
    ) -> str:
        """Generate approach summary."""
        return f"""
**Routing Decision:** {router_decision.rationale}

**Effort Allocation:**
- Effort level: {effort_plan.effort_level.value}
- Thinking budget: {effort_plan.budget_tokens} tokens
- Samples: {effort_plan.num_samples}
- Self-consistency: {'enabled' if effort_plan.use_self_consistency else 'disabled'}
- Interleaved thinking: {'enabled' if effort_plan.interleaved_thinking_enabled else 'disabled'}

**Cognitive Phases:** {len(effort_plan.phases)} phases planned
""".strip()
    
    def _generate_phase_summaries(
        self,
        phases: Dict[CognitivePhase, ThinkingPhase],
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
    ) -> Dict[str, str]:
        """Generate summaries for each executed phase."""
        summaries = {}
        
        for phase, phase_state in phases.items():
            template = self.templates.get(phase, "Phase {phase} executed.")
            
            # Build context for template
            context = self._build_phase_context(
                phase, phase_state, run_spec, router_decision, effort_plan
            )
            
            try:
                summary = template.format(**context)
            except KeyError:
                summary = f"Phase {phase.value} completed with status: {phase_state.status}"
            
            summaries[phase.value.replace("_", " ").title()] = summary.strip()
        
        return summaries
    
    def _build_phase_context(
        self,
        phase: CognitivePhase,
        phase_state: ThinkingPhase,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
    ) -> Dict[str, Any]:
        """Build context dict for phase template."""
        return {
            # Input processing
            "context_file_count": len(run_spec.context_files),
            "task_type": run_spec.task_type.value,
            "evidence_level": run_spec.required_evidence_level.value,
            
            # Exploration
            "num_candidates": effort_plan.num_samples,
            "selected_approach": router_decision.thinking_strategy.value,
            "selection_rationale": router_decision.rationale,
            
            # Analysis
            "decomposition": self._format_decomposition(phase_state),
            "dependency_count": len(run_spec.references),
            "risk_class": router_decision.risk_class.value,
            "complexity_score": router_decision.complexity_score,
            
            # Verification
            "verification_steps": self._format_verification_steps(phase_state),
            "tool_call_count": len(phase_state.tool_calls),
            "iteration_count": phase_state.corrections_made + 1,
            "max_iterations": effort_plan.max_tool_verify_iterations,
            "verification_status": phase_state.status,
            
            # Conclusion
            "key_findings": self._format_key_findings(phase_state),
            "confidence": 0.85,  # Placeholder
            "recommendations": self._format_recommendations(phase_state),
            
            # Output
            "has_response": "Yes",
            "has_code_changes": "TBD",
            "artifact_count": len(phase_state.artifacts),
            "claim_count": 0,  # Placeholder
        }
    
    def _format_decomposition(self, phase_state: ThinkingPhase) -> str:
        """Format problem decomposition from thinking blocks."""
        if not phase_state.blocks:
            return "- No decomposition recorded"
        
        # Extract from first block
        content = phase_state.blocks[0].content
        lines = content.split("\n")[:5]
        return "\n".join(f"- {line.strip()}" for line in lines if line.strip())
    
    def _format_verification_steps(self, phase_state: ThinkingPhase) -> str:
        """Format verification steps."""
        if not phase_state.tool_calls:
            return "- No verification tools executed"
        
        steps = []
        for i, call in enumerate(phase_state.tool_calls[:5], 1):
            tool_name = call.get("name", "unknown")
            status = call.get("status", "pending")
            steps.append(f"- Step {i}: {tool_name} ({status})")
        
        return "\n".join(steps)
    
    def _format_key_findings(self, phase_state: ThinkingPhase) -> str:
        """Format key findings from conclusion phase."""
        if not phase_state.blocks:
            return "- Analysis complete, no critical issues found"
        
        return "- Analysis complete\n- Approach validated\n- Ready for output"
    
    def _format_recommendations(self, phase_state: ThinkingPhase) -> str:
        """Format recommendations."""
        return "- Proceed with implementation\n- Monitor for edge cases"
    
    def _extract_key_decisions(
        self,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
        phases: Dict[CognitivePhase, ThinkingPhase],
    ) -> List[Dict[str, str]]:
        """Extract key decisions made during the run."""
        decisions = [
            {
                "decision": f"Route to {router_decision.path.value} path",
                "rationale": router_decision.rationale,
            },
            {
                "decision": f"Use {router_decision.thinking_strategy.value} strategy",
                "rationale": f"Based on task type and complexity ({router_decision.complexity_score:.2f})",
            },
            {
                "decision": f"Allocate {effort_plan.effort_level.value} effort",
                "rationale": effort_plan.rationale,
            },
        ]
        
        # Add phase-specific decisions
        for phase, phase_state in phases.items():
            if phase_state.corrections_made > 0:
                decisions.append({
                    "decision": f"Self-corrected in {phase.value}",
                    "rationale": f"Made {phase_state.corrections_made} corrections",
                })
        
        return decisions
    
    def _extract_assumptions(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
    ) -> List[str]:
        """Extract assumptions made during the run."""
        assumptions = [
            f"Task type is correctly classified as {run_spec.task_type.value}",
            f"Risk assessment of {router_decision.risk_class.value} is accurate",
            f"Context files provided are complete and relevant",
        ]
        
        if run_spec.required_evidence_level in {EvidenceLevel.E2, EvidenceLevel.E3}:
            assumptions.append("Tool outputs are reliable for evidence")
        
        return assumptions
    
    def _extract_risks(
        self,
        router_decision: RouterDecision,
        phases: Dict[CognitivePhase, ThinkingPhase],
    ) -> List[Dict[str, str]]:
        """Extract identified risks."""
        risks = []
        
        # Risk from routing
        if router_decision.risk_class.value in {"high", "critical"}:
            risks.append({
                "risk": f"High-risk task ({router_decision.risk_class.value})",
                "severity": router_decision.risk_class.value,
                "mitigation": "Extended thinking and verification enabled",
            })
        
        # Risk from complexity
        if router_decision.complexity_score > 0.7:
            risks.append({
                "risk": "High complexity may lead to incomplete analysis",
                "severity": "medium",
                "mitigation": "Multi-sample approach with self-consistency",
            })
        
        # Risk from verification failures
        for phase, phase_state in phases.items():
            if phase_state.status == "failed":
                risks.append({
                    "risk": f"Phase {phase.value} failed",
                    "severity": "high",
                    "mitigation": "Manual review required",
                })
        
        return risks
    
    def _generate_evidence_plan(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        phases: Dict[CognitivePhase, ThinkingPhase],
    ) -> List[Dict[str, str]]:
        """Generate evidence collection plan."""
        plan = [
            {
                "level": "E2",
                "artifact": "router_decision.json",
                "source": "DualThinkingRouter",
            },
            {
                "level": "E2",
                "artifact": "effort_plan.json",
                "source": "EffortController",
            },
            {
                "level": "E2",
                "artifact": "budget_plan.json",
                "source": "EffortController",
            },
            {
                "level": "E0",
                "artifact": "process_trace_summary.md",
                "source": "ProcessTraceGenerator",
            },
        ]
        
        # Add phase artifacts
        for phase, phase_state in phases.items():
            for artifact in phase_state.artifacts:
                plan.append({
                    "level": "E2",
                    "artifact": Path(artifact).name,
                    "source": f"Phase: {phase.value}",
                })
        
        # Add required E3 artifacts
        if run_spec.required_evidence_level == EvidenceLevel.E3:
            plan.extend([
                {
                    "level": "E3",
                    "artifact": "claims.jsonl",
                    "source": "GovernancePackager",
                },
                {
                    "level": "E3",
                    "artifact": "evidencepack.json",
                    "source": "EvidencePackerV2",
                },
                {
                    "level": "E3",
                    "artifact": "scorecard.json",
                    "source": "GovernancePackager",
                },
            ])
        
        return plan
    
    def _extract_tools_from_phases(
        self,
        phases: Dict[CognitivePhase, ThinkingPhase],
    ) -> List[Dict[str, Any]]:
        """Extract tool usage from phases."""
        tools = []
        
        for phase, phase_state in phases.items():
            for call in phase_state.tool_calls:
                tools.append({
                    "name": call.get("name", "unknown"),
                    "purpose": f"Used in {phase.value}",
                    "result_summary": call.get("result_summary", "Completed"),
                })
        
        return tools
    
    def _extract_corrections(
        self,
        phases: Dict[CognitivePhase, ThinkingPhase],
    ) -> List[Dict[str, str]]:
        """Extract self-corrections from phases."""
        corrections = []
        
        for phase, phase_state in phases.items():
            for detail in phase_state.correction_details:
                corrections.append({
                    "original": f"Initial approach in {phase.value}",
                    "corrected": detail,
                    "reason": "Self-correction during reasoning",
                })
        
        return corrections
    
    def _determine_outcome(
        self,
        phases: Dict[CognitivePhase, ThinkingPhase],
    ) -> tuple[str, float]:
        """Determine overall outcome and confidence."""
        failed_phases = [p for p, ps in phases.items() if ps.status == "failed"]
        completed_phases = [p for p, ps in phases.items() if ps.status == "completed"]
        
        if failed_phases:
            return f"Partial completion ({len(failed_phases)} phases failed)", 0.5
        
        if len(completed_phases) == len(phases):
            return "All phases completed successfully", 0.85
        
        return "In progress", 0.6
    
    def emit_artifact(
        self,
        trace: ProcessTraceSummary,
        output_dir: Path,
    ) -> Path:
        """
        Emit process_trace_summary.md artifact.
        
        Args:
            trace: The process trace summary
            output_dir: Directory to write artifact
            
        Returns:
            Path to the written artifact
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write markdown version
        md_path = output_dir / "process_trace_summary.md"
        md_path.write_text(trace.to_markdown(), encoding="utf-8")
        
        # Also write JSON version for programmatic access
        json_path = output_dir / "process_trace_summary.json"
        json_path.write_text(
            json.dumps(trace.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        
        return md_path
