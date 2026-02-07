"""
Dive Engine V2 - Daemon Runner
===============================

This module implements the daemon runner that orchestrates the entire
Dive Engine execution flow, including:

1. run.start: Initialize run with router_decision.json and effort_plan.json
2. run.execute: Execute cognitive phases with thinking blocks
3. run.verify: Run verification gates
4. run.monitor: Generate monitor_report.json
5. run.pack: Pack evidence artifacts

The daemon can be run as:
- CLI command: `dive engine run`
- JSON-RPC server: `dive engine serve`
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from dive_engine.core.models import (
    BudgetPlan,
    CognitivePhase,
    EffortPlan,
    EvidenceLevel,
    MonitorReport,
    MonitorVerdict,
    ProcessTraceSummary,
    RouterDecision,
    RoutingPath,
    RunSpec,
    ThinkingBlock,
    ThinkingPhase,
    ThinkingStrategy,
    generate_run_id,
    utcnow_iso,
)
from dive_engine.thinking.dual_router import DualThinkingRouter
from dive_engine.thinking.effort_controller import EffortController


# =============================================================================
# RUN STATE
# =============================================================================

@dataclass
class RunState:
    """State of a Dive Engine run."""
    run_id: str
    run_spec: RunSpec
    
    # Routing and effort
    router_decision: Optional[RouterDecision] = None
    effort_plan: Optional[EffortPlan] = None
    budget_plan: Optional[BudgetPlan] = None
    
    # Thinking phases
    phases: Dict[CognitivePhase, ThinkingPhase] = field(default_factory=dict)
    current_phase: Optional[CognitivePhase] = None
    
    # Process trace
    process_trace: Optional[ProcessTraceSummary] = None
    
    # Monitor report
    monitor_report: Optional[MonitorReport] = None
    
    # Artifacts
    artifacts: Dict[str, Path] = field(default_factory=dict)
    
    # Status
    status: str = "initialized"  # initialized, running, completed, failed
    error: Optional[str] = None
    
    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Output directory
    output_dir: Optional[Path] = None


# =============================================================================
# DAEMON RUNNER
# =============================================================================

class DaemonRunner:
    """
    Main daemon runner for Dive Engine.
    
    This class orchestrates the entire execution flow:
    1. Initialize run with routing and effort planning
    2. Execute cognitive phases
    3. Run verification gates
    4. Generate monitor report
    5. Pack evidence artifacts
    """
    
    def __init__(
        self,
        router: Optional[DualThinkingRouter] = None,
        effort_controller: Optional[EffortController] = None,
        repo_root: Optional[Path] = None,
    ):
        """
        Initialize the daemon runner.
        
        Args:
            router: Custom router (creates default if None)
            effort_controller: Custom effort controller (creates default if None)
            repo_root: Repository root path
        """
        self.router = router or DualThinkingRouter()
        self.effort_controller = effort_controller or EffortController()
        self.repo_root = repo_root or Path.cwd()
        
        # Active runs
        self.runs: Dict[str, RunState] = {}
    
    # =========================================================================
    # RUN LIFECYCLE
    # =========================================================================
    
    def start(self, run_spec: RunSpec) -> RunState:
        """
        Start a new run.
        
        This is the main entry point that:
        1. Creates run state
        2. Routes the task (emits router_decision.json)
        3. Plans effort (emits effort_plan.json)
        4. Plans budget (emits budget_plan.json)
        
        Args:
            run_spec: The run specification
            
        Returns:
            RunState with routing and effort decisions
        """
        # Create output directory
        output_dir = self._create_output_dir(run_spec.run_id)
        
        # Initialize run state
        state = RunState(
            run_id=run_spec.run_id,
            run_spec=run_spec,
            output_dir=output_dir,
            started_at=utcnow_iso(),
        )
        
        try:
            # Step 1: Route the task
            state.router_decision = self.router.route(run_spec)
            router_path = self.router.emit_artifact(
                state.router_decision,
                output_dir,
            )
            state.artifacts["router_decision"] = router_path
            
            # Step 2: Plan effort
            state.effort_plan = self.effort_controller.plan_effort(
                run_spec,
                state.router_decision,
            )
            
            # Step 3: Plan budget
            state.budget_plan = self.effort_controller.plan_budget(
                run_spec,
                state.effort_plan,
            )
            
            # Emit effort and budget artifacts
            effort_artifacts = self.effort_controller.emit_artifacts(
                state.effort_plan,
                state.budget_plan,
                output_dir,
            )
            state.artifacts.update(effort_artifacts)
            
            # Initialize thinking phases
            for phase in state.effort_plan.phases:
                state.phases[phase] = ThinkingPhase(
                    phase=phase,
                    run_id=run_spec.run_id,
                )
            
            state.status = "started"
            
        except Exception as e:
            state.status = "failed"
            state.error = str(e)
        
        # Store run state
        self.runs[run_spec.run_id] = state
        
        return state
    
    def execute_phase(
        self,
        run_id: str,
        phase: CognitivePhase,
        executor: Optional[Callable[[ThinkingPhase, RunState], ThinkingPhase]] = None,
    ) -> ThinkingPhase:
        """
        Execute a single cognitive phase.
        
        Args:
            run_id: The run ID
            phase: The phase to execute
            executor: Optional custom executor function
            
        Returns:
            Updated ThinkingPhase
        """
        state = self.runs.get(run_id)
        if not state:
            raise ValueError(f"Run not found: {run_id}")
        
        if phase not in state.phases:
            raise ValueError(f"Phase not in plan: {phase}")
        
        phase_state = state.phases[phase]
        phase_state.status = "running"
        phase_state.started_at = utcnow_iso()
        state.current_phase = phase
        
        try:
            if executor:
                phase_state = executor(phase_state, state)
            else:
                phase_state = self._default_phase_executor(phase_state, state)
            
            phase_state.status = "completed"
            
        except Exception as e:
            phase_state.status = "failed"
            state.error = str(e)
        
        phase_state.completed_at = utcnow_iso()
        
        # Calculate duration
        if phase_state.started_at and phase_state.completed_at:
            # Simple duration calculation
            phase_state.duration_ms = 1000  # Placeholder
        
        state.phases[phase] = phase_state
        
        return phase_state
    
    def execute_all_phases(
        self,
        run_id: str,
        executors: Optional[Dict[CognitivePhase, Callable]] = None,
    ) -> RunState:
        """
        Execute all planned cognitive phases in order.
        
        Args:
            run_id: The run ID
            executors: Optional dict of phase-specific executors
            
        Returns:
            Updated RunState
        """
        state = self.runs.get(run_id)
        if not state:
            raise ValueError(f"Run not found: {run_id}")
        
        if not state.effort_plan:
            raise ValueError("Effort plan not initialized")
        
        state.status = "running"
        executors = executors or {}
        
        for phase in state.effort_plan.phases:
            executor = executors.get(phase)
            self.execute_phase(run_id, phase, executor)
            
            # Check for failure
            if state.phases[phase].status == "failed":
                state.status = "failed"
                break
        
        if state.status != "failed":
            state.status = "phases_completed"
        
        return state
    
    def complete(self, run_id: str) -> RunState:
        """
        Complete a run and finalize artifacts.
        
        Args:
            run_id: The run ID
            
        Returns:
            Final RunState
        """
        state = self.runs.get(run_id)
        if not state:
            raise ValueError(f"Run not found: {run_id}")
        
        state.completed_at = utcnow_iso()
        
        if state.status != "failed":
            state.status = "completed"
        
        # Emit final run summary
        self._emit_run_summary(state)
        
        return state
    
    # =========================================================================
    # DEFAULT EXECUTORS
    # =========================================================================
    
    def _default_phase_executor(
        self,
        phase_state: ThinkingPhase,
        run_state: RunState,
    ) -> ThinkingPhase:
        """
        Default executor for cognitive phases.
        
        This creates placeholder thinking blocks for each phase.
        In production, this would be replaced with actual LLM calls.
        """
        phase = phase_state.phase
        
        # Create a thinking block for this phase
        block = ThinkingBlock(
            block_id=f"{run_state.run_id}-{phase.value}-001",
            phase=phase,
            content=self._generate_phase_content(phase, run_state),
            signature=f"sig_{hash(run_state.run_id + phase.value) % 10000}",
        )
        
        phase_state.blocks.append(block)
        
        # Record artifact for this phase
        artifact_name = f"phase_{phase.value}.json"
        artifact_path = run_state.output_dir / artifact_name
        artifact_path.write_text(
            json.dumps(phase_state.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        phase_state.artifacts.append(str(artifact_path))
        
        return phase_state
    
    def _generate_phase_content(
        self,
        phase: CognitivePhase,
        run_state: RunState,
    ) -> str:
        """Generate placeholder content for a phase."""
        contents = {
            CognitivePhase.INPUT_PROCESSING: f"""
Analyzing input for run {run_state.run_id}:
- Task type: {run_state.run_spec.task_type.value}
- Mode: {run_state.run_spec.mode}
- Evidence required: {run_state.run_spec.required_evidence_level.value}
- Context files: {len(run_state.run_spec.context_files)}

Normalized task specification created.
""",
            CognitivePhase.EXPLORATION: f"""
Exploring candidate approaches for {run_state.run_spec.task_type.value}:

Approach 1: Direct implementation
- Pros: Fast, straightforward
- Cons: May miss edge cases

Approach 2: Systematic analysis first
- Pros: Thorough, catches issues early
- Cons: Takes more time

Selected: Approach 2 (based on {run_state.router_decision.risk_class.value} risk)
""",
            CognitivePhase.ANALYSIS: f"""
Detailed analysis:

1. Problem decomposition:
   - Core requirement: {run_state.run_spec.prompt[:100]}...
   - Dependencies identified: {len(run_state.run_spec.references)}
   
2. Risk assessment:
   - Risk class: {run_state.router_decision.risk_class.value}
   - Complexity score: {run_state.router_decision.complexity_score:.2f}

3. Plan:
   - Execute with {run_state.effort_plan.effort_level.value} effort
   - Budget: {run_state.effort_plan.budget_tokens} thinking tokens
""",
            CognitivePhase.VERIFICATION: f"""
Verification phase:

1. Static checks: PENDING
2. Build verification: PENDING
3. Test execution: PENDING
4. Security scan: PENDING (if required)

Tool verification loop: {run_state.effort_plan.max_tool_verify_iterations} iterations max
""",
            CognitivePhase.CONCLUSION: f"""
Conclusion:

Based on analysis and verification:
- Primary approach validated
- No blocking issues found
- Ready for output generation

Confidence: 85%
""",
            CognitivePhase.OUTPUT_GENERATION: f"""
Generating final output:

1. Synthesizing findings
2. Formatting response
3. Attaching evidence artifacts
4. Creating claims ledger

Output ready for delivery.
""",
        }
        
        return contents.get(phase, f"Phase {phase.value} executed.")
    
    # =========================================================================
    # ARTIFACT MANAGEMENT
    # =========================================================================
    
    def _create_output_dir(self, run_id: str) -> Path:
        """Create output directory for run artifacts."""
        output_dir = self.repo_root / ".vibe" / "runs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _emit_run_summary(self, state: RunState) -> Path:
        """Emit final run summary artifact."""
        summary = {
            "run_id": state.run_id,
            "status": state.status,
            "started_at": state.started_at,
            "completed_at": state.completed_at,
            "routing": state.router_decision.to_dict() if state.router_decision else None,
            "effort": state.effort_plan.to_dict() if state.effort_plan else None,
            "budget": state.budget_plan.to_dict() if state.budget_plan else None,
            "phases": {
                p.value: state.phases[p].to_dict()
                for p in state.phases
            },
            "artifacts": {k: str(v) for k, v in state.artifacts.items()},
            "error": state.error,
        }
        
        summary_path = state.output_dir / "mode_run.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        state.artifacts["mode_run"] = summary_path
        
        return summary_path
    
    # =========================================================================
    # JSON-RPC INTERFACE
    # =========================================================================
    
    def handle_rpc(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle JSON-RPC method calls.
        
        Supported methods:
        - engine.ping: Health check
        - run.start: Start a new run
        - run.execute: Execute phases
        - run.status: Get run status
        - run.complete: Complete a run
        - artifacts.list: List artifacts
        - artifacts.read: Read artifact content
        """
        handlers = {
            "engine.ping": self._rpc_ping,
            "run.start": self._rpc_run_start,
            "run.execute": self._rpc_run_execute,
            "run.status": self._rpc_run_status,
            "run.complete": self._rpc_run_complete,
            "artifacts.list": self._rpc_artifacts_list,
            "artifacts.read": self._rpc_artifacts_read,
        }
        
        handler = handlers.get(method)
        if not handler:
            return {"error": f"Unknown method: {method}"}
        
        try:
            return handler(params)
        except Exception as e:
            return {"error": str(e)}
    
    def _rpc_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Health check."""
        return {
            "status": "ok",
            "version": "2.0.0",
            "active_runs": len(self.runs),
        }
    
    def _rpc_run_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new run."""
        run_spec = RunSpec(
            run_id=params.get("run_id", generate_run_id()),
            mode=params.get("mode", "generic"),
            prompt=params.get("prompt", ""),
            context_files=params.get("context_files", []),
            references=params.get("references", []),
        )
        
        state = self.start(run_spec)
        
        return {
            "run_id": state.run_id,
            "status": state.status,
            "router_decision": state.router_decision.to_dict() if state.router_decision else None,
            "effort_plan": state.effort_plan.to_dict() if state.effort_plan else None,
            "artifacts": {k: str(v) for k, v in state.artifacts.items()},
        }
    
    def _rpc_run_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute phases for a run."""
        run_id = params.get("run_id")
        if not run_id:
            return {"error": "run_id required"}
        
        state = self.execute_all_phases(run_id)
        
        return {
            "run_id": state.run_id,
            "status": state.status,
            "phases_completed": [
                p.value for p, ps in state.phases.items()
                if ps.status == "completed"
            ],
        }
    
    def _rpc_run_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get run status."""
        run_id = params.get("run_id")
        if not run_id:
            return {"error": "run_id required"}
        
        state = self.runs.get(run_id)
        if not state:
            return {"error": f"Run not found: {run_id}"}
        
        return {
            "run_id": state.run_id,
            "status": state.status,
            "current_phase": state.current_phase.value if state.current_phase else None,
            "error": state.error,
        }
    
    def _rpc_run_complete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a run."""
        run_id = params.get("run_id")
        if not run_id:
            return {"error": "run_id required"}
        
        state = self.complete(run_id)
        
        return {
            "run_id": state.run_id,
            "status": state.status,
            "artifacts": {k: str(v) for k, v in state.artifacts.items()},
        }
    
    def _rpc_artifacts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List artifacts for a run."""
        run_id = params.get("run_id")
        if not run_id:
            return {"error": "run_id required"}
        
        state = self.runs.get(run_id)
        if not state:
            return {"error": f"Run not found: {run_id}"}
        
        return {
            "run_id": state.run_id,
            "artifacts": {k: str(v) for k, v in state.artifacts.items()},
        }
    
    def _rpc_artifacts_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read artifact content."""
        run_id = params.get("run_id")
        artifact_name = params.get("artifact")
        
        if not run_id or not artifact_name:
            return {"error": "run_id and artifact required"}
        
        state = self.runs.get(run_id)
        if not state:
            return {"error": f"Run not found: {run_id}"}
        
        artifact_path = state.artifacts.get(artifact_name)
        if not artifact_path:
            return {"error": f"Artifact not found: {artifact_name}"}
        
        content = Path(artifact_path).read_text(encoding="utf-8")
        
        return {
            "run_id": state.run_id,
            "artifact": artifact_name,
            "path": str(artifact_path),
            "content": content[:10000],  # Limit content size
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def run_cli(args: List[str]) -> int:
    """
    CLI entry point for Dive Engine daemon.
    
    Usage:
        dive engine run --mode security-review --prompt "..."
        dive engine serve --socket /tmp/dive.sock
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Dive Engine Daemon")
    subparsers = parser.add_subparsers(dest="command")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Execute a single run")
    run_parser.add_argument("--mode", default="generic", help="Run mode")
    run_parser.add_argument("--prompt", required=True, help="Task prompt")
    run_parser.add_argument("--files", nargs="*", default=[], help="Context files")
    run_parser.add_argument("--output", default=".vibe/runs", help="Output directory")
    
    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start JSON-RPC server")
    serve_parser.add_argument("--socket", default="/tmp/dive.sock", help="Socket path")
    
    parsed = parser.parse_args(args)
    
    if parsed.command == "run":
        runner = DaemonRunner()
        
        run_spec = RunSpec(
            mode=parsed.mode,
            prompt=parsed.prompt,
            context_files=parsed.files,
        )
        
        # Start run
        state = runner.start(run_spec)
        print(f"Started run: {state.run_id}")
        print(f"Router decision: {state.router_decision.path.value}")
        print(f"Effort level: {state.effort_plan.effort_level.value}")
        
        # Execute phases
        state = runner.execute_all_phases(state.run_id)
        print(f"Phases completed: {state.status}")
        
        # Complete run
        state = runner.complete(state.run_id)
        print(f"Run completed: {state.status}")
        print(f"Artifacts: {list(state.artifacts.keys())}")
        
        return 0 if state.status == "completed" else 1
    
    elif parsed.command == "serve":
        print(f"Starting JSON-RPC server on {parsed.socket}")
        # Server implementation would go here
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_cli(sys.argv[1:]))
