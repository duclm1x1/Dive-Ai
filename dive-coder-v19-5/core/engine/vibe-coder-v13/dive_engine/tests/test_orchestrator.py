#!/usr/bin/env python3
"""
Dive Engine V2 - Test Orchestrator
===================================

This script demonstrates the complete Dive Engine V2 workflow:
1. Task routing with dual thinking model
2. Effort planning and budget allocation
3. Cognitive phase execution
4. Process trace generation
5. Quality monitoring with follow-up loop
6. E3 evidence packing

Run: python -m dive_engine.tests.test_orchestrator
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dive_engine import (
    DiveEngineOrchestrator,
    EvidenceLevel,
    RunSpec,
    generate_run_id,
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_basic_run():
    """Test basic orchestrator run."""
    print_section("TEST: Basic Orchestrator Run")
    
    orchestrator = DiveEngineOrchestrator()
    
    result = orchestrator.run(
        prompt="Fix the null pointer exception in user authentication module",
        mode="debug",
        context_files=["src/auth/login.py", "src/auth/session.py"],
        required_evidence_level=EvidenceLevel.E2,
    )
    
    print(f"\nRun ID: {result.run_id}")
    print(f"Status: {result.status}")
    
    if result.run_state.router_decision:
        print(f"\nRouting Decision:")
        print(f"  - Path: {result.run_state.router_decision.path.value}")
        print(f"  - Strategy: {result.run_state.router_decision.thinking_strategy.value}")
        print(f"  - Risk: {result.run_state.router_decision.risk_class.value}")
        print(f"  - Complexity: {result.run_state.router_decision.complexity_score:.2f}")
    
    if result.run_state.effort_plan:
        print(f"\nEffort Plan:")
        print(f"  - Level: {result.run_state.effort_plan.effort_level.value}")
        print(f"  - Budget Tokens: {result.run_state.effort_plan.budget_tokens}")
        print(f"  - Samples: {result.run_state.effort_plan.num_samples}")
        print(f"  - Phases: {len(result.run_state.effort_plan.phases)}")
    
    if result.monitor_report:
        print(f"\nMonitor Report:")
        print(f"  - Verdict: {result.monitor_report.verdict.value}")
        print(f"  - Completeness: {result.monitor_report.completeness_score:.2f}")
        print(f"  - Coherence: {result.monitor_report.logical_coherence_score:.2f}")
        print(f"  - Evidence: {result.monitor_report.evidence_coverage_score:.2f}")
        print(f"  - Risk: {result.monitor_report.risk_assessment_score:.2f}")
    
    print(f"\nArtifacts Generated: {len(result.artifacts)}")
    for name, path in result.artifacts.items():
        print(f"  - {name}: {path}")
    
    return result


def test_security_review():
    """Test security review mode with high evidence requirements."""
    print_section("TEST: Security Review Mode")
    
    orchestrator = DiveEngineOrchestrator()
    
    result = orchestrator.run(
        prompt="Review the OAuth implementation for security vulnerabilities",
        mode="security-review",
        context_files=[
            "src/auth/oauth.py",
            "src/auth/tokens.py",
            "src/crypto/encryption.py",
        ],
        required_evidence_level=EvidenceLevel.E3,
    )
    
    print(f"\nRun ID: {result.run_id}")
    print(f"Status: {result.status}")
    
    if result.run_state.router_decision:
        print(f"\nRouting (Security Mode):")
        print(f"  - Path: {result.run_state.router_decision.path.value}")
        print(f"  - Strategy: {result.run_state.router_decision.thinking_strategy.value}")
        print(f"  - Policy: {result.run_state.router_decision.policy_branch}")
    
    if result.evidence_pack_path:
        print(f"\nEvidence Pack: {result.evidence_pack_path}")
    
    return result


def test_simple_task():
    """Test simple task that should use fast path."""
    print_section("TEST: Simple Task (Fast Path)")
    
    orchestrator = DiveEngineOrchestrator()
    
    result = orchestrator.run(
        prompt="Add a comment to the README file",
        mode="generic",
        context_files=["README.md"],
        required_evidence_level=EvidenceLevel.E0,
    )
    
    print(f"\nRun ID: {result.run_id}")
    print(f"Status: {result.status}")
    
    if result.run_state.router_decision:
        print(f"\nRouting (Simple Task):")
        print(f"  - Path: {result.run_state.router_decision.path.value}")
        print(f"  - Strategy: {result.run_state.router_decision.thinking_strategy.value}")
        print(f"  - Complexity: {result.run_state.router_decision.complexity_score:.2f}")
    
    return result


def test_process_trace():
    """Test process trace generation."""
    print_section("TEST: Process Trace Generation")
    
    orchestrator = DiveEngineOrchestrator()
    
    result = orchestrator.run(
        prompt="Refactor the database connection pool for better performance",
        mode="performance",
        context_files=["src/db/pool.py", "src/db/connection.py"],
        required_evidence_level=EvidenceLevel.E2,
    )
    
    if result.process_trace:
        print(f"\nProcess Trace Summary:")
        print(f"  - Task: {result.process_trace.task_summary[:100]}...")
        print(f"  - Key Decisions: {len(result.process_trace.key_decisions)}")
        print(f"  - Assumptions: {len(result.process_trace.assumptions)}")
        print(f"  - Risks: {len(result.process_trace.risks)}")
        print(f"  - Evidence Plan: {len(result.process_trace.evidence_plan)} items")
        print(f"  - Outcome: {result.process_trace.outcome}")
        print(f"  - Confidence: {result.process_trace.confidence:.0%}")
    
    return result


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  DIVE ENGINE V2 - ORCHESTRATOR TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Basic Run", test_basic_run()))
    results.append(("Security Review", test_security_review()))
    results.append(("Simple Task", test_simple_task()))
    results.append(("Process Trace", test_process_trace()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    for name, result in results:
        status_icon = "✓" if result.status == "completed" else "✗"
        print(f"  {status_icon} {name}: {result.status}")
    
    print("\n" + "=" * 60)
    print("  All tests completed!")
    print("=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
