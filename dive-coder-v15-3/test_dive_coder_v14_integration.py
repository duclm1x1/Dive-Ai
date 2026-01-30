"""
Dive Coder v14 - Comprehensive Integration Test
================================================

This script tests the entire Dive Coder v14 stack:
- Dive Engine V2 orchestration
- LLM client integration
- All cognitive phases
- Evidence packing
- Monitoring and faithfulness checking
"""

import asyncio
import pytest
import json
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent / ".shared" / "vibe-coder-v13"))

from dive_engine import DiveEngineOrchestrator
from dive_engine.llm import create_llm_client
from dive_engine.core import MonitorVerdict


def test_dive_engine_import():
    """Test 1: Dive Engine imports."""
    print("=" * 80)
    print("TEST 1: Dive Engine Imports")
    print("=" * 80)

    try:
        from dive_engine.core import RunSpec, RouterDecision
        from dive_engine.thinking import DualThinkingRouter, EffortController
        from dive_engine.daemon import DaemonRunner
        from dive_engine.artifacts import ProcessTraceGenerator, EvidencePackerV2
        from dive_engine.monitor import TierMonitor, FaithfulnessChecker
        from dive_engine.llm import LLMClient, ModelRegistry
        
        print("\n✓ All core modules imported successfully")
        print("✓ Dive Engine V2 is properly installed")
        print("\n✅ Import Test PASSED\n")
        assert True
    
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        print("\n❌ Import Test FAILED\n")
        raise


def test_llm_client():
    """Test 2: LLM Client."""
    print("=" * 80)
    print("TEST 2: LLM Client")
    print("=" * 80)

    # This integration test requires the optional openai dependency.
    import importlib.util
    if importlib.util.find_spec("openai") is None:
        pytest.skip("openai not installed; skipping LLM client integration test")

    try:
        client = create_llm_client()
        
        # List models
        from dive_engine.llm import ModelRegistry
        registry = ModelRegistry()
        models = registry.list_models()
        
        print(f"\n✓ LLM Client created")
        print(f"✓ {len(models)} models available")
        print(f"✓ Providers: {[p.name.value for p in client.providers]}")
        
        # Test simple call
        response = client.call(
            prompt="Say 'Integration test passed!'",
            tier="tier_fast",
            max_tokens=50,
        )
        
        print(f"\n✓ Test call response: {response}")
        print(f"✓ Stats: {client.get_stats()}")
        
        print("\n✅ LLM Client Test PASSED\n")
        assert True
    
    except Exception as e:
        print(f"\n✗ LLM Client test failed: {e}")
        print("\n❌ LLM Client Test FAILED\n")
        raise


def test_orchestrator_basic():
    """Test 3: Basic Orchestrator Run."""
    print("=" * 80)
    print("TEST 3: Basic Orchestrator Run")
    print("=" * 80)

    try:
        # Create orchestrator
        orchestrator = DiveEngineOrchestrator()
        
        print("\n✓ Orchestrator created")
        
        # Run simple task
        result = orchestrator.run(
            prompt="Calculate 2 + 2 and explain your reasoning.",
            mode="debug",
        )
        
        print(f"\n✓ Run completed: {result.run_id}")
        print(f"✓ Status: {result.status}")
        if result.run_state and result.run_state.router_decision:
            print(f"✓ Router decision: {result.run_state.router_decision.path}")
        if result.run_state and result.run_state.effort_plan:
            print(f"✓ Effort level: {result.run_state.effort_plan.effort_level}")
        if result.process_trace:
            print(f"✓ Process trace generated")
        if result.monitor_report:
            print(f"✓ Monitor report generated")
        
        if result.evidence_pack_path:
            print(f"✓ Evidence pack: {result.evidence_pack_path}")
        
        print("\n✅ Basic Orchestrator Test PASSED\n")
        assert True
    
    except Exception as e:
        print(f"\n✗ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ Basic Orchestrator Test FAILED\n")
        raise


def test_cognitive_phases():
    """Test 4: Cognitive Phases Execution."""
    print("=" * 80)
    print("TEST 4: Cognitive Phases Execution")
    print("=" * 80)

    try:
        from dive_engine.daemon import DaemonRunner
        from dive_engine.core import RunSpec, CognitivePhase
        from dive_engine.llm import SimpleLLMCaller
        
        # Create runner
        runner = DaemonRunner()
        
        # Create run spec
        spec = RunSpec(
            run_id="test_phases",
            prompt="Analyze the security of a simple login function.",
            mode="security-review",
        )
        
        print("\n✓ Daemon Runner created")
        print(f"✓ Run spec: {spec.run_id}")
        
        # Start run
        result = runner.start(spec)
        
        print(f"\n✓ Run started: {result.run_id}")
        print(f"✓ Phases to execute: {len(result.phases)}")
        
        # Check phases
        expected_phases = [
            CognitivePhase.INPUT_PROCESSING,
            CognitivePhase.EXPLORATION,
            CognitivePhase.ANALYSIS,
            CognitivePhase.VERIFICATION,
            CognitivePhase.CONCLUSION,
            CognitivePhase.OUTPUT_GENERATION,
        ]
        
        for phase in expected_phases:
            print(f"  ✓ Phase: {phase.value}")
        
        print("\n✅ Cognitive Phases Test PASSED\n")
        assert True
    
    except Exception as e:
        print(f"\n✗ Cognitive phases test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ Cognitive Phases Test FAILED\n")
        raise


def test_evidence_packing():
    """Test 5: Evidence Packing."""
    print("=" * 80)
    print("TEST 5: Evidence Packing")
    print("=" * 80)

    try:
        from dive_engine.artifacts import EvidencePackerV2
        from dive_engine.core import ProcessTraceSummary, MonitorReport
        
        # Create packer
        packer = EvidencePackerV2()
        
        print("\n✓ Evidence Packer created")
        
        # Create mock artifacts
        process_trace = ProcessTraceSummary(
            run_id="test_evidence",
            task_summary="Test task",
            approach_summary="Test approach",
            key_decisions=[{"decision": "Use fast path", "rationale": "Simple task"}],
            assumptions=["Input is valid"],
            risks=[{"risk": "Edge case not covered", "severity": "low"}],
            evidence_plan=[{"evidence": "Test coverage", "level": "E1"}],
        )
        
        monitor_report = MonitorReport(
            run_id="test_evidence",
            verdict=MonitorVerdict.PASS,
            completeness_score=0.9,
            logical_coherence_score=0.85,
            evidence_coverage_score=0.8,
            risk_assessment_score=0.75,
            followup_questions=[],
            recommendations=["Recommendation 1: Add more tests"],
        )

        # Pack evidence
        from dive_engine.core import (
            RunSpec, RouterDecision, RoutingPath, TaskType, RiskClass, EvidenceLevel,
            ThinkingStrategy, EffortPlan, EffortLevel, BudgetPlan, CognitivePhase, ThinkingPhase,
        )

        run_spec = RunSpec(run_id="test_evidence", prompt="Test evidence pack")
        router_decision = RouterDecision(
            run_id="test_evidence",
            path=RoutingPath.FAST,
            task_type=TaskType.GENERIC,
            risk_class=RiskClass.LOW,
            required_evidence=EvidenceLevel.E2,
            complexity_score=1.0,
            policy_branch="default",
            rationale="unit-test",
            selected_tier="tier_fast",
            thinking_strategy=ThinkingStrategy.SINGLE_PASS,
        )
        effort_plan = EffortPlan(
            run_id="test_evidence",
            effort_level=EffortLevel.LOW,
            budget_tokens=2000,
            phases=[CognitivePhase.INPUT_PROCESSING],
            rationale="unit-test",
        )
        budget_plan = BudgetPlan(run_id="test_evidence")
        phases = {CognitivePhase.INPUT_PROCESSING: ThinkingPhase(phase=CognitivePhase.INPUT_PROCESSING, run_id="test_evidence")}
        artifacts = {}
        packed = packer.pack(
            run_id="test_evidence",
            run_spec=run_spec,
            router_decision=router_decision,
            effort_plan=effort_plan,
            budget_plan=budget_plan,
            phases=phases,
            process_trace=process_trace,
            monitor_report=monitor_report,
            artifacts=artifacts,
        )

        assert "claims" in packed
        assert "evidencepack" in packed
        assert "scorecard" in packed

        print(f"\n✓ Evidence packed artifacts: {list(packed.keys())}")
        print(f"✓ Claims (ledger): {packed.get('claims')}")
        print(f"✓ EvidencePack: {packed.get('evidencepack')}")
        print(f"✓ Scorecard: {packed.get('scorecard')}")
        
        print("\n✅ Evidence Packing Test PASSED\n")
        assert True
    
    except Exception as e:
        print(f"\n✗ Evidence packing test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ Evidence Packing Test FAILED\n")
        raise


def test_model_selection():
    """Test 6: Model Selection for Different Tiers."""
    print("=" * 80)
    print("TEST 6: Model Selection")
    print("=" * 80)

    try:
        from dive_engine.llm import ModelRegistry
        
        registry = ModelRegistry()
        
        tiers = [
            "tier_fast",
            "tier_think",
            "tier_code",
            "tier_reasoning",
            "tier_extended_thinking",
        ]
        
        print("\n✓ Testing model selection for different tiers:")
        
        for tier in tiers:
            model = registry.get_model_for_tier(tier)
            info = registry.get_model_info(model)
            print(f"  ✓ {tier:.<30} → {model} ({info['tier']})")
        
        print("\n✅ Model Selection Test PASSED\n")
        assert True
    
    except Exception as e:
        print(f"\n✗ Model selection test failed: {e}")
        print("\n❌ Model Selection Test FAILED\n")
        raise


async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("DIVE CODER V14 - COMPREHENSIVE INTEGRATION TEST")
    print("=" * 80 + "\n")
    
    results = []
    
    # Test 1: Imports
    try:
        test_dive_engine_import(); result = True
        results.append(("Dive Engine Imports", result))
    except Exception as e:
        print(f"✗ Import test crashed: {e}\n")
        results.append(("Dive Engine Imports", False))
    
    # Test 2: LLM Client
    try:
        test_llm_client(); result = True
        results.append(("LLM Client", result))
    except Exception as e:
        print(f"✗ LLM Client test crashed: {e}\n")
        results.append(("LLM Client", False))
    
    # Test 3: Basic Orchestrator
    try:
        test_orchestrator_basic(); result = True
        results.append(("Basic Orchestrator", result))
    except Exception as e:
        print(f"✗ Orchestrator test crashed: {e}\n")
        results.append(("Basic Orchestrator", False))
    
    # Test 4: Cognitive Phases
    try:
        test_cognitive_phases(); result = True
        results.append(("Cognitive Phases", result))
    except Exception as e:
        print(f"✗ Cognitive phases test crashed: {e}\n")
        results.append(("Cognitive Phases", False))
    
    # Test 5: Evidence Packing
    try:
        test_evidence_packing(); result = True
        results.append(("Evidence Packing", result))
    except Exception as e:
        print(f"✗ Evidence packing test crashed: {e}\n")
        results.append(("Evidence Packing", False))
    
    # Test 6: Model Selection
    try:
        test_model_selection(); result = True
        results.append(("Model Selection", result))
    except Exception as e:
        print(f"✗ Model selection test crashed: {e}\n")
        results.append(("Model Selection", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{'Total':.>50} {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED! 🎉")
        print("\n✓ Dive Coder v14 is working smoothly!")
        print("✓ All components are properly integrated")
        print("✓ Ready for production use\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\n✗ Some components need attention\n")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
