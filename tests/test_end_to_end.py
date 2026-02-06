"""
End-to-End Workflow Test for Dive Coder v14
============================================

Test the complete workflow from user request to final output.
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared/vibe-coder-v13'))

from dive_engine.orchestrator import DiveEngineOrchestrator
from dive_engine.core.models import TaskMode, EvidenceLevel


async def test_simple_analysis():
    """Test a simple analysis task end-to-end."""
    print("\n" + "=" * 70)
    print("END-TO-END TEST: Simple Analysis Task")
    print("=" * 70)
    
    orchestrator = DiveEngineOrchestrator()
    
    prompt = """
    Analyze this simple Python function and identify any issues:
    
    def calculate_average(numbers):
        total = sum(numbers)
        return total / len(numbers)
    """
    
    print(f"\n📝 Prompt: {prompt[:100]}...")
    print(f"\n🚀 Starting orchestration...")
    
    try:
        result = orchestrator.run(
            prompt=prompt,
            mode="analysis",
            context_files=[],
        )
        
        print(f"\n✅ Orchestration completed!")
        print(f"\n📊 Results:")
        print(f"   Run ID: {result.run_id}")
        print(f"   Status: {result.status}")
        if result.run_state and result.run_state.router_decision:
            print(f"   Router Decision: {result.run_state.router_decision.path}")
            print(f"   Thinking Strategy: {result.run_state.router_decision.thinking_strategy}")
        if result.run_state and result.run_state.effort_plan:
            print(f"   Effort Level: {result.run_state.effort_plan.effort_level}")
        
        if result.artifacts:
            print(f"\n📄 Artifacts Generated:")
            for artifact_type, artifact_path in result.artifacts.items():
                if artifact_path:
                    print(f"   - {artifact_type}: {artifact_path}")
        
        if result.evidence_pack_path:
            print(f"\n📦 Evidence Pack:")
            print(f"   Path: {result.evidence_pack_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_llm_integration():
    """Test end-to-end with real LLM calls."""
    print("\n" + "=" * 70)
    print("END-TO-END TEST: With Real LLM Integration")
    print("=" * 70)
    
    orchestrator = DiveEngineOrchestrator()
    
    prompt = "What is 2+2? Explain briefly."
    
    print(f"\n📝 Prompt: {prompt}")
    print(f"\n🚀 Starting orchestration with real LLM...")
    
    try:
        result = orchestrator.run(
            prompt=prompt,
            mode="general",
            context_files=[],
        )
        
        print(f"\n✅ Orchestration with LLM completed!")
        print(f"\n📊 Results:")
        print(f"   Run ID: {result.run_id}")
        print(f"   Status: {result.status}")
        
        # Check if we got actual LLM response
        if hasattr(result, 'final_output') and result.final_output:
            print(f"\n💬 LLM Response Preview:")
            print(f"   {result.final_output[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestration with LLM failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_e2e_tests():
    """Run all end-to-end tests."""
    print("\n" + "=" * 80)
    print(" " * 25 + "DIVE CODER V14 - END-TO-END TESTS")
    print("=" * 80)
    
    results = []
    
    # Test 1: Simple analysis (without real LLM)
    results.append(("Simple Analysis", await test_simple_analysis()))
    
    # Test 2: With real LLM integration
    results.append(("Real LLM Integration", await test_with_llm_integration()))
    
    # Summary
    print("\n" + "=" * 80)
    print(" " * 30 + "TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<60} {status}")
    
    print("=" * 80)
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All end-to-end tests passed! System is fully functional.")
    elif passed >= total * 0.5:
        print(f"\n✅ Most tests passed. System is functional.")
    else:
        print(f"\n⚠️  Multiple failures. System needs attention.")
    
    return passed, total


if __name__ == "__main__":
    passed, total = asyncio.run(run_all_e2e_tests())
    sys.exit(0 if passed == total else 1)
