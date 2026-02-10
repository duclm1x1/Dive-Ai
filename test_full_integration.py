"""
🧪 FULL INTEGRATION TEST SUITE
Comprehensive testing of all Dive AI components
"""

import os
import sys
import time
import traceback

sys.path.append(os.path.dirname(__file__))


def print_header(title):
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")


def print_result(test_name, passed, details=""):
    icon = "✅" if passed else "❌"
    print(f"   {icon} {test_name}" + (f" - {details}" if details else ""))
    return passed


def run_test_suite():
    """Run complete test suite for all components"""
    
    print(f"\n{'='*70}")
    print(f"🧪 DIVE AI - FULL INTEGRATION TEST SUITE")
    print(f"{'='*70}")
    print(f"\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # ═══════════════════════════════════════════════════════════════════════
    # TEST GROUP 1: Multi-Agent Coordinator
    # ═══════════════════════════════════════════════════════════════════════
    print_header("TEST GROUP 1: Multi-Agent Coordinator (512 AIs)")
    
    try:
        from core.orchestrator.multi_agent_coordinator import MultiAgentCoordinator
        
        coordinator = MultiAgentCoordinator()
        
        # Test 1.1: Agent spawning
        result = coordinator.execute({"action": "spawn_agents"})
        passed = result.status == "success" and result.data.get("total_agents") == 512
        all_results.append(("Spawn 512 Agents", passed))
        print_result("Spawn 512 Agents", passed, f"{result.data.get('total_agents', 0)} agents")
        
        # Test 1.2: Status
        result = coordinator.execute({"action": "get_status"})
        passed = result.status == "success" and result.data.get("coordinator") == "online"
        all_results.append(("Coordinator Status", passed))
        print_result("Coordinator Status", passed, result.data.get("coordinator", "unknown"))
        
        # Test 1.3: Task assignment
        result = coordinator.execute({
            "action": "assign_task",
            "task": "Test task for full integration",
            "priority": 5
        })
        passed = result.status == "success" and result.data.get("assigned_agents", 0) > 0
        all_results.append(("Task Assignment", passed))
        print_result("Task Assignment", passed, f"{result.data.get('assigned_agents', 0)} agents assigned")
        
        # Test 1.4: 24h plan
        result = coordinator.execute({"action": "generate_24h_plan"})
        passed = result.status == "success" and len(result.data.get("timeline", {})) > 0
        all_results.append(("24h Plan Generation", passed))
        print_result("24h Plan Generation", passed, f"{len(result.data.get('timeline', {}))} time slots")
        
        # Test 1.5: Autonomous (no task)
        result = coordinator.execute({"action": "autonomous_execute", "autonomous_mode": True})
        passed = result.status == "success" and result.data.get("task_source") == "24h_plan"
        all_results.append(("Autonomous (No Task)", passed))
        print_result("Autonomous (No Task)", passed, result.data.get("task_source", "unknown"))
        
        # Test 1.6: Autonomous (with task)
        result = coordinator.execute({"action": "autonomous_execute", "task": "Test autonomous execution"})
        passed = result.status == "success" and result.data.get("task_source") == "user_dropped"
        all_results.append(("Autonomous (With Task)", passed))
        print_result("Autonomous (With Task)", passed, result.data.get("task_source", "unknown"))
        
    except Exception as e:
        print(f"   ❌ Multi-Agent Coordinator tests failed: {e}")
        traceback.print_exc()
        all_results.append(("Multi-Agent Coordinator", False))
    
    # ═══════════════════════════════════════════════════════════════════════
    # TEST GROUP 2: V98 Connection
    # ═══════════════════════════════════════════════════════════════════════
    print_header("TEST GROUP 2: V98 Connection (475+ Models)")
    
    try:
        from core.algorithms.algorithm_manager import AlgorithmManager
        
        manager = AlgorithmManager(auto_scan=False)
        manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
        v98 = manager.get_algorithm("V98Connection")
        
        if v98:
            # Test 2.1: Connection
            result = v98.execute({"action": "connect"})
            passed = result.status == "success" and result.data.get("total_models", 0) > 0
            all_results.append(("V98 Connection", passed))
            print_result("V98 Connection", passed, f"{result.data.get('total_models', 0)} models")
            
            # Test 2.2: Health check
            result = v98.execute({"action": "health"})
            passed = result.status == "success"
            all_results.append(("V98 Health Check", passed))
            print_result("V98 Health Check", passed)
            
            # Test 2.3: Model listing
            result = v98.execute({"action": "list_models"})
            passed = result.status == "success"
            all_results.append(("V98 Model List", passed))
            print_result("V98 Model List", passed)
        else:
            print("   ⚠️  V98Connection algorithm not found")
            all_results.append(("V98 Connection", False))
            
    except Exception as e:
        print(f"   ❌ V98 tests failed: {e}")
        all_results.append(("V98 Connection", False))
    
    # ═══════════════════════════════════════════════════════════════════════
    # TEST GROUP 3: AICoding Connection
    # ═══════════════════════════════════════════════════════════════════════
    print_header("TEST GROUP 3: AICoding Connection")
    
    try:
        aicoding = manager.get_algorithm("AICodingConnection")
        
        if aicoding:
            # Test 3.1: Connection
            result = aicoding.execute({"action": "connect"})
            passed = result.status == "success"
            all_results.append(("AICoding Connection", passed))
            print_result("AICoding Connection", passed)
            
            # Test 3.2: Health check
            result = aicoding.execute({"action": "health"})
            passed = result.status == "success"
            all_results.append(("AICoding Health Check", passed))
            print_result("AICoding Health Check", passed)
        else:
            print("   ⚠️  AICodingConnection algorithm not found")
            all_results.append(("AICoding Connection", False))
            
    except Exception as e:
        print(f"   ❌ AICoding tests failed: {e}")
        all_results.append(("AICoding Connection", False))
    
    # ═══════════════════════════════════════════════════════════════════════
    # TEST GROUP 4: 3-AI Orchestrator
    # ═══════════════════════════════════════════════════════════════════════
    print_header("TEST GROUP 4: 3-AI Orchestrator")
    
    try:
        from core.orchestrator.three_ai_orchestrator import ThreeAIOrchestrator
        
        orchestrator = ThreeAIOrchestrator()
        
        # Test 4.1: Initialization
        passed = len(orchestrator.ais) == 3
        all_results.append(("3-AI Init (3 Models)", passed))
        print_result("3-AI Init (3 Models)", passed, f"{len(orchestrator.ais)} AIs configured")
        
        # Test 4.2: Simple execution
        result = orchestrator.execute({
            "request": "Simple test: say hello",
            "max_iterations": 1
        })
        passed = result.status in ["success", "partial"]
        all_results.append(("3-AI Execution", passed))
        print_result("3-AI Execution", passed, result.status)
        
    except Exception as e:
        print(f"   ❌ 3-AI Orchestrator tests failed: {e}")
        all_results.append(("3-AI Orchestrator", False))
    
    # ═══════════════════════════════════════════════════════════════════════
    # TEST GROUP 5: Algorithm Manager
    # ═══════════════════════════════════════════════════════════════════════
    print_header("TEST GROUP 5: Algorithm Manager")
    
    try:
        from core.algorithms.algorithm_manager import AlgorithmManager
        
        # Test 5.1: Initialization
        manager = AlgorithmManager(auto_scan=True)
        passed = True
        all_results.append(("AlgorithmManager Init", passed))
        print_result("AlgorithmManager Init", passed)
        
        # Test 5.2: List algorithms
        algorithms = manager.list_algorithms()
        passed = len(algorithms) > 0
        all_results.append(("Algorithm Discovery", passed))
        print_result("Algorithm Discovery", passed, f"{len(algorithms)} algorithms")
        
        # Test 5.3: Get specific algorithm
        algo = manager.get_algorithm("V98Connection")
        passed = algo is not None
        all_results.append(("Get Algorithm", passed))
        print_result("Get Algorithm", passed)
        
    except Exception as e:
        print(f"   ❌ Algorithm Manager tests failed: {e}")
        all_results.append(("Algorithm Manager", False))
    
    # ═══════════════════════════════════════════════════════════════════════
    # TEST GROUP 6: Dashboard Files
    # ═══════════════════════════════════════════════════════════════════════
    print_header("TEST GROUP 6: Dashboard Files")
    
    dashboard_path = "D:\\Antigravity\\Dive AI\\dashboard\\index.html"
    server_path = "D:\\Antigravity\\Dive AI\\dashboard_server.py"
    
    passed = os.path.exists(dashboard_path)
    all_results.append(("Dashboard HTML", passed))
    print_result("Dashboard HTML", passed, dashboard_path if passed else "Not found")
    
    passed = os.path.exists(server_path)
    all_results.append(("Dashboard Server", passed))
    print_result("Dashboard Server", passed, server_path if passed else "Not found")
    
    # ═══════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    print_header("📊 FINAL TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in all_results if passed)
    total_count = len(all_results)
    success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n   Total Tests: {total_count}")
    print(f"   ✅ Passed: {passed_count}")
    print(f"   ❌ Failed: {total_count - passed_count}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n   Test Breakdown:")
    for test_name, passed in all_results:
        icon = "✅" if passed else "❌"
        print(f"      {icon} {test_name}")
    
    print(f"\n{'='*70}")
    if success_rate >= 90:
        print(f"🎉 EXCELLENT! All major components working ({success_rate:.1f}% pass rate)")
        print(f"\n   Dashboard Available at: http://localhost:8080")
        print(f"   Run: python dashboard_server.py")
    elif success_rate >= 70:
        print(f"⚠️  GOOD - Most tests passed ({success_rate:.1f}%)")
    else:
        print(f"❌ NEEDS ATTENTION - {100-success_rate:.1f}% of tests failed")
    print(f"{'='*70}")
    
    return success_rate >= 80


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
