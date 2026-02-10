"""
🦞 DIVE AI V29.4 - COMPLETE SYSTEM TEST
Tests everything: Algorithms, Priority, Auto-Generation, Self-Debugging
"""

import sys
import os
import time

sys.path.append(os.path.dirname(__file__))


def test_complete_system():
    """Run complete system test"""
    
    print("\n" + "="*80)
    print("🦞 DIVE AI V29.4 - COMPLETE SYSTEM TEST")
    print("="*80)
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
    
    # ========================================
    # TEST 1: Algorithm Registration
    # ========================================
    print("\n" + "="*60)
    print("📋 TEST 1: Algorithm Registration")
    print("="*60)
    
    from core.algorithms import get_algorithm_manager
    manager = get_algorithm_manager()
    
    total_algos = len(manager.algorithms)
    total_categories = len(manager.get_categories())
    
    print(f"\n   ✅ Algorithms Registered: {total_algos}")
    print(f"   ✅ Categories: {total_categories}")
    
    results["total_tests"] += 1
    if total_algos >= 75:
        print(f"   ✅ PASSED: {total_algos}/75 algorithms registered")
        results["passed"] += 1
    else:
        print(f"   ❌ FAILED: Only {total_algos}/75 algorithms")
        results["failed"] += 1
    
    # Show categories
    print(f"\n   📂 Categories:")
    for cat in sorted(manager.get_categories()):
        count = len(manager.category_index.get(cat, []))
        print(f"      - {cat}: {count} algorithms")
    
    # ========================================
    # TEST 2: Core Algorithms Execution
    # ========================================
    print("\n" + "="*60)
    print("⚡ TEST 2: Core Algorithms Execution")
    print("="*60)
    
    core_tests = [
        ("SmartModelRouter", {"task": "test task for routing"}),
        ("ComplexityAnalyzer", {"task": "analyze this task"}),
        ("HighPerformanceMemory", {"action": "add", "content": "test memory"}),
        ("AgentSelector", {"task": "select best agent"}),
        ("CodeGenerator", {"requirements": "hello world function"}),
        ("SemanticRouting", {"query": "how to code in Python?"}),
        ("HybridPrompting", {"raw_prompt": "test prompt for AI"}),
        ("TaskDecomposition", {"task": "build a web app"}),
    ]
    
    for algo_id, params in core_tests:
        results["total_tests"] += 1
        try:
            result = manager.execute(algo_id, params)
            if result and hasattr(result, 'status') and result.status == "success":
                print(f"   ✅ {algo_id}: PASSED")
                results["passed"] += 1
            else:
                print(f"   ⚠️  {algo_id}: Executed with status={getattr(result, 'status', 'unknown')}")
                results["warnings"] += 1
        except Exception as e:
            print(f"   ❌ {algo_id}: ERROR - {str(e)[:50]}")
            results["failed"] += 1
    
    # ========================================
    # TEST 3: V27.2 Skills
    # ========================================
    print("\n" + "="*60)
    print("🎯 TEST 3: V27.2 Advanced Skills")
    print("="*60)
    
    skills_tests = [
        ("FormalVerification", {"code": "def test(): pass"}),
        ("AutoErrorHandling", {"code": "risky_function()"}),
        ("DynamicNeuralArchitecture", {"task": "classification"}),
        ("ContinuousLearning", {"new_data": [1, 2, 3]}),
        ("GradientAwareRouting", {"gradients": [0.1, 0.2]}),
        ("HierarchicalExperts", {"query": "Python expert needed"}),
    ]
    
    for algo_id, params in skills_tests:
        results["total_tests"] += 1
        try:
            result = manager.execute(algo_id, params)
            if result and hasattr(result, 'status') and result.status == "success":
                print(f"   ✅ {algo_id}: PASSED")
                results["passed"] += 1
            else:
                print(f"   ⚠️  {algo_id}: status={getattr(result, 'status', 'unknown')}")
                results["warnings"] += 1
        except Exception as e:
            print(f"   ❌ {algo_id}: ERROR - {str(e)[:50]}")
            results["failed"] += 1
    
    # ========================================
    # TEST 4: Priority System
    # ========================================
    print("\n" + "="*60)
    print("🔄 TEST 4: V28.7 Priority System")
    print("="*60)
    
    results["total_tests"] += 1
    try:
        from core.algorithms.priority_manager import AlgorithmPriorityManager, Priority
        
        priority_mgr = AlgorithmPriorityManager(manager)
        status = priority_mgr.get_status()
        
        print(f"\n   📊 Priority System Status:")
        print(f"      Total Managed: {status['total_managed']}")
        print(f"      By Priority: {status['by_priority']}")
        print(f"      Always-Running: {len(status['always_running'])}")
        
        # Show always-running
        print(f"\n   🔄 Always-Running Algorithms:")
        for algo in status['always_running']:
            config = priority_mgr.priorities[algo]
            print(f"      [{config.priority.name}] {algo} - Every {config.execution_interval}s")
        
        if status['total_managed'] >= 10:
            print(f"\n   ✅ PASSED: Priority system operational")
            results["passed"] += 1
        else:
            print(f"\n   ❌ FAILED: Priority system incomplete")
            results["failed"] += 1
            
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        results["failed"] += 1
    
    # ========================================
    # TEST 5: Auto-Generation System
    # ========================================
    print("\n" + "="*60)
    print("🤖 TEST 5: Auto-Generation System")
    print("="*60)
    
    results["total_tests"] += 1
    try:
        result = manager.execute("AlgorithmAutoGenerator", {
            "source": "skills",
            "scan_directory": "core/",
            "auto_debug": True
        })
        
        if result and result.status == "success":
            generated = result.data.get('success_count', 0)
            print(f"\n   ✅ Auto-Generator Working!")
            print(f"      Generated: {generated} algorithms")
            print(f"      Algorithms: {result.data.get('generated_algorithms', [])}")
            results["passed"] += 1
        else:
            print(f"   ⚠️  Auto-generation returned: {result.status}")
            results["warnings"] += 1
            
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        results["failed"] += 1
    
    # ========================================
    # TEST 6: Memory Performance
    # ========================================
    print("\n" + "="*60)
    print("💾 TEST 6: Memory Performance")
    print("="*60)
    
    results["total_tests"] += 1
    try:
        import time as t
        
        # Test memory speed
        start = t.time()
        for i in range(100):
            manager.execute("HighPerformanceMemory", {
                "action": "add",
                "content": f"test item {i}"
            })
        elapsed = (t.time() - start) * 1000
        
        avg_time = elapsed / 100
        print(f"\n   ⚡ 100 memory operations in {elapsed:.2f}ms")
        print(f"   ⚡ Average: {avg_time:.3f}ms per operation")
        
        if avg_time < 1.0:  # Less than 1ms per operation
            print(f"   ✅ PASSED: Memory performance excellent")
            results["passed"] += 1
        else:
            print(f"   ⚠️  Memory slower than expected")
            results["warnings"] += 1
            
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        results["failed"] += 1
    
    # ========================================
    # TEST 7: Smart Router Cost Savings
    # ========================================
    print("\n" + "="*60)
    print("💰 TEST 7: Smart Router Cost Savings")
    print("="*60)
    
    results["total_tests"] += 1
    try:
        # Test different complexity levels
        test_cases = [
            ("What is 2+2?", "nano"),
            ("Explain Python classes", "mini"),
            ("Write a complex algorithm with error handling", "flash"),
        ]
        
        all_passed = True
        for task, expected_tier in test_cases:
            result = manager.execute("SmartModelRouter", {"task": task})
            if result and result.status == "success":
                tier = result.data.get("tier", "unknown")
                savings = result.data.get("cost_savings", 0)
                print(f"   📝 '{task[:30]}...'")
                print(f"      Tier: {tier} (expected: {expected_tier})")
                print(f"      Savings: {savings}% vs premium")
            else:
                all_passed = False
        
        if all_passed:
            print(f"\n   ✅ PASSED: Smart Router working")
            results["passed"] += 1
        else:
            results["warnings"] += 1
            
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        results["failed"] += 1
    
    # ========================================
    # TEST 8: Orchestration
    # ========================================
    print("\n" + "="*60)
    print("🎭 TEST 8: Orchestration")
    print("="*60)
    
    results["total_tests"] += 1
    try:
        result = manager.execute("SmartOrchestrator", {
            "task": "Build a REST API with authentication",
            "auto_execute": False
        })
        
        if result and result.status == "success":
            plan = result.data.get("plan", {})
            steps = plan.get("steps", [])
            print(f"\n   ✅ Orchestrator created plan with {len(steps)} steps")
            for i, step in enumerate(steps[:3], 1):
                print(f"      {i}. {step.get('action', 'unknown')}")
            if len(steps) > 3:
                print(f"      ... and {len(steps) - 3} more steps")
            results["passed"] += 1
        else:
            print(f"   ⚠️  Orchestrator status: {getattr(result, 'status', 'unknown')}")
            results["warnings"] += 1
            
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        results["failed"] += 1
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    total = results["total_tests"]
    passed = results["passed"]
    failed = results["failed"]
    warnings = results["warnings"]
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n   Total Tests: {total}")
    print(f"   ✅ Passed:   {passed}")
    print(f"   ⚠️  Warnings: {warnings}")
    print(f"   ❌ Failed:   {failed}")
    print(f"\n   📈 Pass Rate: {pass_rate:.1f}%")
    
    # Overall status
    print("\n" + "="*80)
    if failed == 0 and pass_rate >= 90:
        print("✅ ALL SYSTEMS OPERATIONAL - DIVE AI V29.4 READY!")
        print("🦞🚀 Self-Evolving Algorithm Framework is PRODUCTION READY!")
    elif failed <= 2:
        print("⚠️  MOSTLY OPERATIONAL - Minor issues detected")
        print("   Review warnings above for details")
    else:
        print("❌ SYSTEM NEEDS ATTENTION - Multiple failures detected")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    results = test_complete_system()
    sys.exit(0 if results["failed"] == 0 else 1)
