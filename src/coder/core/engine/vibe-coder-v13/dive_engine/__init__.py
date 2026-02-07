"""
Dive Engine V2 - Cognitive Runtime for AI Coding Assistants
============================================================

Dive Engine V2 integrates dual thinking model mechanisms from:
- GPT-5.2 Reasoning Model (fast/think path routing, reasoning.effort)
- Claude Opus 4.5 Extended Thinking (budget_tokens, interleaved thinking)

Key Components:
- DualThinkingRouter: Routes tasks to fast or think path
- EffortController: Allocates reasoning compute budget
- DaemonRunner: Executes cognitive phases
- ProcessTraceGenerator: Creates structured process summaries
- TierMonitor: Evaluates process quality with follow-up loop
- EvidencePackerV2: Bundles E3 evidence artifacts
- DiveEngineOrchestrator: Wires all components together

Usage:
    from dive_engine import DiveEngineOrchestrator
    
    orchestrator = DiveEngineOrchestrator()
    result = orchestrator.run(
        prompt="Fix the authentication bug",
        mode="security-review",
    )
    print(result.monitor_report.verdict)

Version: 2.0.0 (Dive Coder v14)
"""

__version__ = "2.0.0"
__author__ = "Dive Coder Team"

# Core models
from dive_engine.core.models import (
    EvidenceLevel,
    TaskType,
    RiskClass,
    RoutingPath,
    EffortLevel,
    ThinkingStrategy,
    CognitivePhase,
    MonitorVerdict,
    RunSpec,
    RouterDecision,
    EffortPlan,
    BudgetPlan,
    ThinkingBlock,
    ThinkingPhase,
    MonitorReport,
    ProcessTraceSummary,
    generate_run_id,
    utcnow_iso,
)

# Thinking components
from dive_engine.thinking.dual_router import (
    DualThinkingRouter,
    RoutingPolicy,
    create_router_from_config,
)
from dive_engine.thinking.effort_controller import (
    EffortController,
    EffortConfig,
)

# Daemon
from dive_engine.daemon.runner import (
    DaemonRunner,
    RunState,
    run_cli,
)

# Artifacts
from dive_engine.artifacts.process_trace import ProcessTraceGenerator
from dive_engine.artifacts.evidence_packer import (
    EvidencePackerV2,
    Claim,
    Scorecard,
    EvidencePackV2,
    pack_evidence,
)

# Monitor
from dive_engine.monitor.tier_monitor import (
    TierMonitor,
    MonitorConfig,
)

# Orchestrator
from dive_engine.orchestrator import (
    DiveEngineOrchestrator,
    OrchestratorResult,
)

__all__ = [
    # Version
    "__version__",
    
    # Core models
    "EvidenceLevel",
    "TaskType",
    "RiskClass",
    "RoutingPath",
    "EffortLevel",
    "ThinkingStrategy",
    "CognitivePhase",
    "MonitorVerdict",
    "RunSpec",
    "RouterDecision",
    "EffortPlan",
    "BudgetPlan",
    "ThinkingBlock",
    "ThinkingPhase",
    "MonitorReport",
    "ProcessTraceSummary",
    "generate_run_id",
    "utcnow_iso",
    
    # Thinking
    "DualThinkingRouter",
    "RoutingPolicy",
    "create_router_from_config",
    "EffortController",
    "EffortConfig",
    
    # Daemon
    "DaemonRunner",
    "RunState",
    "run_cli",
    
    # Artifacts
    "ProcessTraceGenerator",
    "EvidencePackerV2",
    "Claim",
    "Scorecard",
    "EvidencePackV2",
    "pack_evidence",
    
    # Monitor
    "TierMonitor",
    "MonitorConfig",
    
    # Orchestrator
    "DiveEngineOrchestrator",
    "OrchestratorResult",
]
