"""
Dive Engine V2 - Orchestrator
==============================

This module provides the main orchestrator that wires all components together
and provides a unified interface for executing Dive Engine runs.

The orchestrator integrates:
- Dual Thinking Router (GPT-5.2 + Claude Opus 4.5 routing logic)
- Effort Controller (reasoning compute allocation)
- Daemon Runner (execution engine)
- Process Trace Generator (structured summaries)
- Tier Monitor (quality evaluation with follow-up loop)
- Evidence Packer (E3 artifact bundling)

Usage:
    orchestrator = DiveEngineOrchestrator()
    result = orchestrator.run(prompt="Fix the bug in auth.py", mode="debug")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dive_engine.core.models import (
    BudgetPlan,
    CognitivePhase,
    EffortPlan,
    EvidenceLevel,
    MonitorReport,
    ProcessTraceSummary,
    RouterDecision,
    RunSpec,
    TaskType,
    ThinkingPhase,
    generate_run_id,
    utcnow_iso,
)
from dive_engine.thinking.dual_router import DualThinkingRouter
from dive_engine.thinking.effort_controller import EffortController
from dive_engine.daemon.runner import DaemonRunner, RunState
from dive_engine.artifacts.process_trace import ProcessTraceGenerator
from dive_engine.artifacts.evidence_packer import EvidencePackerV2
from dive_engine.monitor.tier_monitor import TierMonitor, MonitorConfig
from dive_engine.tools.rag_context import build_rag_context


# =============================================================================
# ORCHESTRATOR RESULT
# =============================================================================

class OrchestratorResult:
    """Result of a Dive Engine orchestrated run."""
    
    def __init__(
        self,
        run_id: str,
        status: str,
        run_state: RunState,
        process_trace: Optional[ProcessTraceSummary] = None,
        monitor_report: Optional[MonitorReport] = None,
        evidence_pack_path: Optional[Path] = None,
        artifacts: Optional[Dict[str, Path]] = None,
        error: Optional[str] = None,
    ):
        self.run_id = run_id
        self.status = status
        self.run_state = run_state
        self.process_trace = process_trace
        self.monitor_report = monitor_report
        self.evidence_pack_path = evidence_pack_path
        self.artifacts = artifacts or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "routing": self.run_state.router_decision.to_dict() if self.run_state.router_decision else None,
            "effort": self.run_state.effort_plan.to_dict() if self.run_state.effort_plan else None,
            "monitor_verdict": self.monitor_report.verdict.value if self.monitor_report else None,
            "evidence_pack": str(self.evidence_pack_path) if self.evidence_pack_path else None,
            "artifacts": {k: str(v) for k, v in self.artifacts.items()},
            "error": self.error,
        }
    
    def __repr__(self) -> str:
        return f"OrchestratorResult(run_id={self.run_id}, status={self.status})"


# =============================================================================
# DIVE ENGINE ORCHESTRATOR
# =============================================================================

class DiveEngineOrchestrator:
    """
    Main orchestrator for Dive Engine V2.
    
    This class provides a unified interface for executing complete
    Dive Engine runs with all components wired together.
    
    Features:
    - Dual thinking model routing (GPT-5.2 + Claude Opus 4.5)
    - Automatic effort and budget planning
    - Cognitive phase execution
    - Process trace generation
    - Quality monitoring with follow-up loop
    - E3 evidence packing
    """
    
    def __init__(
        self,
        repo_root: Optional[Path] = None,
        router: Optional[DualThinkingRouter] = None,
        effort_controller: Optional[EffortController] = None,
        monitor: Optional[TierMonitor] = None,
        llm_caller: Optional[Callable[[str, str], str]] = None,
    ):
        """
        Initialize the orchestrator.
        
        Args:
            repo_root: Repository root path
            router: Custom router (creates default if None)
            effort_controller: Custom effort controller (creates default if None)
            monitor: Custom monitor (creates default if None)
            llm_caller: Function to call LLM for monitoring
        """
        self.repo_root = repo_root or Path.cwd()
        
        # Initialize components
        self.router = router or DualThinkingRouter()
        self.effort_controller = effort_controller or EffortController()
        self.daemon = DaemonRunner(
            router=self.router,
            effort_controller=self.effort_controller,
            repo_root=self.repo_root,
        )
        self.trace_generator = ProcessTraceGenerator()
        self.monitor = monitor or TierMonitor(llm_caller=llm_caller)
        self.evidence_packer = EvidencePackerV2(repo_root=self.repo_root)
    
    def run(
        self,
        prompt: str,
        mode: str = "generic",
        context_files: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
        enable_rag_context: bool = False,
        rag_spec_path: str = ".vibe/inputs/v13/rag_spec.yml",
        rag_max_context_chars: int = 8000,
        required_evidence_level: EvidenceLevel = EvidenceLevel.E2,
        run_id: Optional[str] = None,
        phase_executors: Optional[Dict[CognitivePhase, Callable]] = None,
    ) -> OrchestratorResult:
        """
        Execute a complete Dive Engine run.
        
        This is the main entry point that orchestrates:
        1. Run initialization with routing and effort planning
        2. Cognitive phase execution
        3. Process trace generation
        4. Quality monitoring
        5. Evidence packing
        
        Args:
            prompt: The task prompt
            mode: Run mode (generic, debug, security-review, etc.)
            context_files: List of context file paths
            references: List of reference file paths
            required_evidence_level: Required evidence level
            run_id: Optional run ID (generates if None)
            phase_executors: Optional custom phase executors
            
        Returns:
            OrchestratorResult with all run data
        """
        # Create run specification
        run_spec = RunSpec(
            run_id=run_id or generate_run_id(),
            mode=mode,
            prompt=prompt,
            context_files=context_files or [],
            references=references or [],
            required_evidence_level=required_evidence_level,
        )
        
        try:
            # Step 1: Start run (routing + effort planning)
            run_state = self.daemon.start(run_spec)
            
            if run_state.status == "failed":
                return OrchestratorResult(
                    run_id=run_spec.run_id,
                    status="failed",
                    run_state=run_state,
                    error=run_state.error,
                )

            # Optional: attach offline-first RAG context as an additional context file.
            if enable_rag_context:
                ctx_path, rag_artifacts = build_rag_context(
                    repo_root=self.repo_root,
                    output_dir=run_state.output_dir,
                    prompt=prompt,
                    spec_path=rag_spec_path,
                    max_context_chars=int(rag_max_context_chars),
                )
                if ctx_path:
                    run_state.run_spec.context_files.append(str(ctx_path))
                    run_state.artifacts.update({k: Path(v) for k, v in rag_artifacts.items()})
            
            # Step 2: Execute all cognitive phases
            run_state = self.daemon.execute_all_phases(
                run_spec.run_id,
                executors=phase_executors,
            )
            
            # Step 3: Generate process trace
            process_trace = self.trace_generator.generate(
                run_spec=run_spec,
                router_decision=run_state.router_decision,
                effort_plan=run_state.effort_plan,
                phases=run_state.phases,
            )
            trace_path = self.trace_generator.emit_artifact(
                process_trace,
                run_state.output_dir,
            )
            run_state.artifacts["process_trace"] = trace_path
            
            # Step 4: Run quality monitoring
            monitor_report = self.monitor.evaluate(
                run_spec=run_spec,
                router_decision=run_state.router_decision,
                process_trace=process_trace,
                phases=run_state.phases,
            )
            monitor_artifacts = self.monitor.emit_artifact(
                monitor_report,
                run_state.output_dir,
            )
            run_state.artifacts.update(monitor_artifacts)
            
            # Step 5: Complete run
            run_state = self.daemon.complete(run_spec.run_id)
            
            # Step 6: Pack evidence (E3)
            evidence_artifacts = self.evidence_packer.pack(
                run_id=run_spec.run_id,
                run_spec=run_spec,
                router_decision=run_state.router_decision,
                effort_plan=run_state.effort_plan,
                budget_plan=run_state.budget_plan,
                phases=run_state.phases,
                process_trace=process_trace,
                monitor_report=monitor_report,
                artifacts=run_state.artifacts,
                output_dir=run_state.output_dir,
            )
            run_state.artifacts.update(evidence_artifacts)
            
            return OrchestratorResult(
                run_id=run_spec.run_id,
                status=run_state.status,
                run_state=run_state,
                process_trace=process_trace,
                monitor_report=monitor_report,
                evidence_pack_path=evidence_artifacts.get("evidencepack"),
                artifacts=run_state.artifacts,
            )
            
        except Exception as e:
            return OrchestratorResult(
                run_id=run_spec.run_id,
                status="failed",
                run_state=self.daemon.runs.get(run_spec.run_id, RunState(
                    run_id=run_spec.run_id,
                    run_spec=run_spec,
                    status="failed",
                )),
                error=str(e),
            )
    
    def run_from_spec(
        self,
        run_spec: RunSpec,
        phase_executors: Optional[Dict[CognitivePhase, Callable]] = None,
    ) -> OrchestratorResult:
        """
        Execute a run from a pre-built RunSpec.
        
        Args:
            run_spec: The run specification
            phase_executors: Optional custom phase executors
            
        Returns:
            OrchestratorResult with all run data
        """
        return self.run(
            prompt=run_spec.prompt,
            mode=run_spec.mode,
            context_files=run_spec.context_files,
            references=run_spec.references,
            required_evidence_level=run_spec.required_evidence_level,
            run_id=run_spec.run_id,
            phase_executors=phase_executors,
        )
    
    def get_run_state(self, run_id: str) -> Optional[RunState]:
        """Get the state of a run."""
        return self.daemon.runs.get(run_id)
    
    def list_runs(self) -> List[str]:
        """List all run IDs."""
        return list(self.daemon.runs.keys())


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point for Dive Engine orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dive Engine V2 Orchestrator")
    parser.add_argument("--prompt", "-p", required=True, help="Task prompt")
    parser.add_argument("--mode", "-m", default="generic", help="Run mode")
    parser.add_argument("--files", "-f", nargs="*", default=[], help="Context files")
    parser.add_argument("--evidence", "-e", default="E2", 
                        choices=["E0", "E1", "E2", "E3"],
                        help="Required evidence level")
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    
    args = parser.parse_args()
    
    # Map evidence level
    evidence_map = {
        "E0": EvidenceLevel.E0,
        "E1": EvidenceLevel.E1,
        "E2": EvidenceLevel.E2,
        "E3": EvidenceLevel.E3,
    }
    
    # Create orchestrator
    orchestrator = DiveEngineOrchestrator(
        repo_root=Path(args.output) if args.output else None,
    )
    
    # Run
    result = orchestrator.run(
        prompt=args.prompt,
        mode=args.mode,
        context_files=args.files,
        required_evidence_level=evidence_map[args.evidence],
    )
    
    # Output result
    print(json.dumps(result.to_dict(), indent=2))
    
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
