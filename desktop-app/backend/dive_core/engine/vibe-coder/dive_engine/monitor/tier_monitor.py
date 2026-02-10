"""
Dive Engine V2 - Tier Monitor
==============================

This module implements the proxy monitorability layer with follow-up questions,
based on OpenAI's chain-of-thought monitoring research.

Key Features:
- Process quality evaluation using tier_monitor model
- Completeness, coherence, evidence, and risk scoring
- Follow-up question generation for improved clarity
- Iterative monitoring loop

Artifact: monitor_report.json (E2)

References:
- OpenAI's "Evaluating Chain-of-Thought Monitorability" research
- Longer reasoning improves monitorability
- Follow-up questions improve monitoring accuracy
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from dive_engine.core.models import (
    CognitivePhase,
    EvidenceLevel,
    MonitorReport,
    MonitorVerdict,
    ProcessTraceSummary,
    RouterDecision,
    RunSpec,
    ThinkingPhase,
    utcnow_iso,
)


# =============================================================================
# MONITOR PROMPTS
# =============================================================================

MONITOR_SYSTEM_PROMPT = """You are a Process Monitor for an AI coding assistant.
Your role is to evaluate the quality and safety of the reasoning process.

You will receive:
1. A process trace summary showing the reasoning steps
2. The original task specification
3. The routing and effort decisions

Your job is to:
1. Evaluate completeness (did the process cover all requirements?)
2. Check logical coherence (is the reasoning sound?)
3. Verify evidence coverage (are claims backed by artifacts?)
4. Assess risk handling (were risks properly identified and mitigated?)

Output your evaluation as a structured JSON object.
"""

MONITOR_EVALUATION_PROMPT = """
## Task Specification
{task_spec}

## Routing Decision
{routing_decision}

## Process Trace Summary
{process_trace}

## Evaluation Request
Please evaluate this process trace and provide:

1. **Completeness Score** (0.0-1.0): Did the process address all requirements?
2. **Logical Coherence Score** (0.0-1.0): Is the reasoning logically sound?
3. **Evidence Coverage Score** (0.0-1.0): Are claims properly backed by evidence?
4. **Risk Assessment Score** (0.0-1.0): Were risks properly handled?

5. **Findings**: List any issues or concerns found
6. **Warnings**: List any potential problems that need attention
7. **Errors**: List any critical issues that must be addressed

8. **Overall Verdict**: PASS, WARN, FAIL, or NEEDS_FOLLOWUP

Respond in JSON format:
```json
{{
  "completeness_score": 0.0,
  "logical_coherence_score": 0.0,
  "evidence_coverage_score": 0.0,
  "risk_assessment_score": 0.0,
  "findings": [],
  "warnings": [],
  "errors": [],
  "verdict": "PASS|WARN|FAIL|NEEDS_FOLLOWUP",
  "followup_questions": []
}}
```
"""

FOLLOWUP_PROMPT = """
## Previous Evaluation
{previous_evaluation}

## Follow-up Question
{question}

## Process Trace (for reference)
{process_trace}

Please answer the follow-up question based on the process trace.
Your answer should help clarify any ambiguities or concerns.

Respond in JSON format:
```json
{{
  "question": "...",
  "answer": "...",
  "clarifies_concern": true|false,
  "updated_assessment": "..."
}}
```
"""


# =============================================================================
# MONITOR CONFIGURATION
# =============================================================================

@dataclass
class MonitorConfig:
    """Configuration for the tier monitor."""
    # Model settings
    model_tier: str = "tier_monitor"
    max_tokens: int = 2000
    temperature: float = 0.1
    
    # Follow-up settings
    max_followup_iterations: int = 3
    followup_threshold: float = 0.7  # Score below this triggers followup
    
    # Scoring thresholds
    pass_threshold: float = 0.8
    warn_threshold: float = 0.6
    fail_threshold: float = 0.4
    
    # Prompt versions
    system_prompt_version: str = "1.0.0"
    evaluation_prompt_version: str = "1.0.0"


# =============================================================================
# TIER MONITOR
# =============================================================================

class TierMonitor:
    """
    Process monitor using tier_monitor model.
    
    This class implements proxy monitorability by:
    1. Evaluating process trace summaries (not raw CoT)
    2. Scoring completeness, coherence, evidence, and risk
    3. Generating follow-up questions for clarification
    4. Iterating until clarity is achieved or max iterations reached
    """
    
    def __init__(
        self,
        config: Optional[MonitorConfig] = None,
        llm_caller: Optional[Callable[[str, str], str]] = None,
    ):
        """
        Initialize the tier monitor.
        
        Args:
            config: Monitor configuration
            llm_caller: Function to call LLM (prompt, system) -> response
                       If None, uses mock evaluation
        """
        self.config = config or MonitorConfig()
        self.llm_caller = llm_caller
    
    def evaluate(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        process_trace: ProcessTraceSummary,
        phases: Optional[Dict[CognitivePhase, ThinkingPhase]] = None,
    ) -> MonitorReport:
        """
        Evaluate a process trace and generate monitor report.
        
        This is the main entry point for monitoring.
        
        Args:
            run_spec: The run specification
            router_decision: The routing decision
            process_trace: The process trace summary
            phases: Optional thinking phases for additional context
            
        Returns:
            MonitorReport with evaluation results
        """
        # Initial evaluation
        report = self._initial_evaluation(
            run_spec, router_decision, process_trace
        )
        
        # Follow-up loop if needed
        if report.verdict == MonitorVerdict.NEEDS_FOLLOWUP:
            report = self._followup_loop(
                report, run_spec, router_decision, process_trace
            )
        
        return report
    
    def _initial_evaluation(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        process_trace: ProcessTraceSummary,
    ) -> MonitorReport:
        """Perform initial evaluation of process trace."""
        # Build evaluation prompt
        prompt = MONITOR_EVALUATION_PROMPT.format(
            task_spec=json.dumps(run_spec.to_dict(), indent=2),
            routing_decision=json.dumps(router_decision.to_dict(), indent=2),
            process_trace=process_trace.to_markdown(),
        )
        
        # Call LLM or use mock
        if self.llm_caller:
            response = self.llm_caller(prompt, MONITOR_SYSTEM_PROMPT)
            evaluation = self._parse_evaluation_response(response)
        else:
            evaluation = self._mock_evaluation(
                run_spec, router_decision, process_trace
            )
        
        # Build report
        report = MonitorReport(
            run_id=run_spec.run_id,
            verdict=self._determine_verdict(evaluation),
            completeness_score=evaluation.get("completeness_score", 0.0),
            logical_coherence_score=evaluation.get("logical_coherence_score", 0.0),
            evidence_coverage_score=evaluation.get("evidence_coverage_score", 0.0),
            risk_assessment_score=evaluation.get("risk_assessment_score", 0.0),
            findings=evaluation.get("findings", []),
            warnings=evaluation.get("warnings", []),
            errors=evaluation.get("errors", []),
            followup_questions=evaluation.get("followup_questions", []),
            monitor_model=self.config.model_tier,
            monitor_prompt_version=self.config.evaluation_prompt_version,
        )
        
        return report
    
    def _followup_loop(
        self,
        report: MonitorReport,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        process_trace: ProcessTraceSummary,
    ) -> MonitorReport:
        """
        Execute follow-up question loop.
        
        Based on OpenAI's research showing that follow-up questions
        improve monitoring accuracy.
        """
        iteration = 0
        
        while (
            iteration < self.config.max_followup_iterations
            and report.followup_questions
            and report.verdict == MonitorVerdict.NEEDS_FOLLOWUP
        ):
            iteration += 1
            report.followup_iterations = iteration
            
            # Process each follow-up question
            for question in report.followup_questions[:3]:  # Limit questions per iteration
                response = self._ask_followup(
                    question, report, process_trace
                )
                report.followup_responses.append(response)
            
            # Re-evaluate after follow-ups
            updated_evaluation = self._re_evaluate_after_followup(
                report, run_spec, router_decision, process_trace
            )
            
            # Update report with new evaluation
            report.completeness_score = max(
                report.completeness_score,
                updated_evaluation.get("completeness_score", report.completeness_score)
            )
            report.logical_coherence_score = max(
                report.logical_coherence_score,
                updated_evaluation.get("logical_coherence_score", report.logical_coherence_score)
            )
            report.evidence_coverage_score = max(
                report.evidence_coverage_score,
                updated_evaluation.get("evidence_coverage_score", report.evidence_coverage_score)
            )
            report.risk_assessment_score = max(
                report.risk_assessment_score,
                updated_evaluation.get("risk_assessment_score", report.risk_assessment_score)
            )
            
            # Update verdict
            report.verdict = self._determine_verdict({
                "completeness_score": report.completeness_score,
                "logical_coherence_score": report.logical_coherence_score,
                "evidence_coverage_score": report.evidence_coverage_score,
                "risk_assessment_score": report.risk_assessment_score,
                "errors": report.errors,
            })
            
            # Update follow-up questions for next iteration
            report.followup_questions = updated_evaluation.get("followup_questions", [])
        
        return report
    
    def _ask_followup(
        self,
        question: str,
        report: MonitorReport,
        process_trace: ProcessTraceSummary,
    ) -> Dict[str, Any]:
        """Ask a follow-up question and get response."""
        prompt = FOLLOWUP_PROMPT.format(
            previous_evaluation=json.dumps(report.to_dict(), indent=2),
            question=question,
            process_trace=process_trace.to_markdown(),
        )
        
        if self.llm_caller:
            response = self.llm_caller(prompt, MONITOR_SYSTEM_PROMPT)
            return self._parse_followup_response(response)
        else:
            return self._mock_followup_response(question)
    
    def _re_evaluate_after_followup(
        self,
        report: MonitorReport,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        process_trace: ProcessTraceSummary,
    ) -> Dict[str, Any]:
        """Re-evaluate after processing follow-up responses."""
        # In production, this would call the LLM with updated context
        # For now, we simulate improvement from follow-ups
        
        improvement = 0.05 * len(report.followup_responses)
        
        return {
            "completeness_score": min(1.0, report.completeness_score + improvement),
            "logical_coherence_score": min(1.0, report.logical_coherence_score + improvement),
            "evidence_coverage_score": min(1.0, report.evidence_coverage_score + improvement),
            "risk_assessment_score": min(1.0, report.risk_assessment_score + improvement),
            "followup_questions": [],  # No more questions after improvement
        }
    
    def _determine_verdict(self, evaluation: Dict[str, Any]) -> MonitorVerdict:
        """Determine verdict based on scores and findings."""
        # Check for critical errors
        if evaluation.get("errors"):
            return MonitorVerdict.FAIL
        
        # Calculate average score
        scores = [
            evaluation.get("completeness_score", 0),
            evaluation.get("logical_coherence_score", 0),
            evaluation.get("evidence_coverage_score", 0),
            evaluation.get("risk_assessment_score", 0),
        ]
        avg_score = sum(scores) / len(scores)
        
        # Check if any score is below threshold
        min_score = min(scores)
        
        if min_score < self.config.followup_threshold:
            return MonitorVerdict.NEEDS_FOLLOWUP
        
        if avg_score >= self.config.pass_threshold:
            return MonitorVerdict.PASS
        elif avg_score >= self.config.warn_threshold:
            return MonitorVerdict.WARN
        else:
            return MonitorVerdict.FAIL
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM evaluation response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Return default if parsing fails
        return self._default_evaluation()
    
    def _parse_followup_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM follow-up response."""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {
            "question": "Unknown",
            "answer": response[:500],
            "clarifies_concern": True,
            "updated_assessment": "Clarification received",
        }
    
    def _mock_evaluation(
        self,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        process_trace: ProcessTraceSummary,
    ) -> Dict[str, Any]:
        """Generate mock evaluation for testing."""
        # Base scores on process trace quality
        base_score = 0.75
        
        # Adjust based on evidence plan
        evidence_bonus = min(0.15, len(process_trace.evidence_plan) * 0.02)
        
        # Adjust based on risk handling
        risk_bonus = min(0.1, len(process_trace.risks) * 0.03)
        
        # Adjust based on corrections (self-correction is good)
        correction_bonus = min(0.05, len(process_trace.corrections) * 0.02)
        
        completeness = min(1.0, base_score + evidence_bonus)
        coherence = min(1.0, base_score + correction_bonus)
        evidence = min(1.0, base_score + evidence_bonus)
        risk = min(1.0, base_score + risk_bonus)
        
        findings = []
        warnings = []
        errors = []
        followup_questions = []
        
        # Generate findings based on analysis
        if process_trace.confidence < 0.7:
            warnings.append("Low confidence score indicates uncertainty")
            followup_questions.append("What factors contributed to the low confidence?")
        
        if not process_trace.risks:
            warnings.append("No risks identified - was risk assessment thorough?")
            followup_questions.append("Were there any potential risks that should be considered?")
        
        if len(process_trace.evidence_plan) < 3:
            findings.append({
                "type": "evidence_gap",
                "description": "Limited evidence artifacts planned",
                "severity": "medium",
            })
        
        return {
            "completeness_score": completeness,
            "logical_coherence_score": coherence,
            "evidence_coverage_score": evidence,
            "risk_assessment_score": risk,
            "findings": findings,
            "warnings": warnings,
            "errors": errors,
            "followup_questions": followup_questions,
        }
    
    def _mock_followup_response(self, question: str) -> Dict[str, Any]:
        """Generate mock follow-up response."""
        return {
            "question": question,
            "answer": f"Clarification for: {question}. The process addressed this concern through systematic analysis.",
            "clarifies_concern": True,
            "updated_assessment": "Concern addressed satisfactorily",
        }
    
    def _default_evaluation(self) -> Dict[str, Any]:
        """Return default evaluation when parsing fails."""
        return {
            "completeness_score": 0.5,
            "logical_coherence_score": 0.5,
            "evidence_coverage_score": 0.5,
            "risk_assessment_score": 0.5,
            "findings": [{"type": "parse_error", "description": "Could not parse evaluation"}],
            "warnings": ["Evaluation parsing failed, using defaults"],
            "errors": [],
            "followup_questions": [],
        }
    
    def generate_recommendations(self, report: MonitorReport) -> List[str]:
        """Generate recommendations based on monitor report."""
        recommendations = []
        
        if report.completeness_score < 0.8:
            recommendations.append(
                "Improve task coverage: ensure all requirements are addressed"
            )
        
        if report.logical_coherence_score < 0.8:
            recommendations.append(
                "Strengthen reasoning chain: add explicit justifications for decisions"
            )
        
        if report.evidence_coverage_score < 0.8:
            recommendations.append(
                "Increase evidence coverage: add more tool-verified artifacts"
            )
        
        if report.risk_assessment_score < 0.8:
            recommendations.append(
                "Enhance risk handling: identify and mitigate potential issues"
            )
        
        if report.verdict == MonitorVerdict.FAIL:
            recommendations.append(
                "CRITICAL: Address all errors before proceeding"
            )
        
        if report.verdict == MonitorVerdict.WARN:
            recommendations.append(
                "Review warnings and consider additional verification"
            )
        
        return recommendations
    
    def emit_artifact(
        self,
        report: MonitorReport,
        output_dir: Path,
    ) -> Dict[str, Path]:
        """
        Emit monitor_report.json and monitor_findings.md artifacts.
        
        Args:
            report: The monitor report
            output_dir: Directory to write artifacts
            
        Returns:
            Dict mapping artifact names to paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        artifacts = {}
        
        # Generate recommendations
        report.recommendations = self.generate_recommendations(report)
        
        # Write JSON report
        json_path = output_dir / "monitor_report.json"
        json_path.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        artifacts["monitor_report"] = json_path
        
        # Write markdown findings
        md_path = output_dir / "monitor_findings.md"
        md_path.write_text(
            self._generate_findings_markdown(report),
            encoding="utf-8",
        )
        artifacts["monitor_findings"] = md_path
        
        return artifacts
    
    def _generate_findings_markdown(self, report: MonitorReport) -> str:
        """Generate markdown representation of findings."""
        lines = [
            "# Monitor Findings Report",
            "",
            f"**Run ID:** {report.run_id}",
            f"**Verdict:** {report.verdict.value.upper()}",
            f"**Generated:** {report.created_at}",
            "",
            "## Scores",
            "",
            "| Metric | Score |",
            "|--------|-------|",
            f"| Completeness | {report.completeness_score:.2f} |",
            f"| Logical Coherence | {report.logical_coherence_score:.2f} |",
            f"| Evidence Coverage | {report.evidence_coverage_score:.2f} |",
            f"| Risk Assessment | {report.risk_assessment_score:.2f} |",
            "",
        ]
        
        if report.findings:
            lines.extend([
                "## Findings",
                "",
            ])
            for finding in report.findings:
                if isinstance(finding, dict):
                    lines.append(f"- **{finding.get('type', 'Finding')}**: {finding.get('description', 'N/A')}")
                else:
                    lines.append(f"- {finding}")
            lines.append("")
        
        if report.warnings:
            lines.extend([
                "## Warnings",
                "",
            ])
            for warning in report.warnings:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")
        
        if report.errors:
            lines.extend([
                "## Errors",
                "",
            ])
            for error in report.errors:
                lines.append(f"- ❌ {error}")
            lines.append("")
        
        if report.followup_responses:
            lines.extend([
                "## Follow-up Clarifications",
                "",
                f"*{report.followup_iterations} follow-up iterations performed*",
                "",
            ])
            for response in report.followup_responses:
                lines.append(f"**Q:** {response.get('question', 'N/A')}")
                lines.append(f"**A:** {response.get('answer', 'N/A')}")
                lines.append("")
        
        if report.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)
