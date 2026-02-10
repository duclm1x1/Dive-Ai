"""
🎯 MULTI-AGENT COORDINATOR TEST
Test the 512 Dive Coder AI orchestration system
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from core.orchestrator.multi_agent_coordinator import MultiAgentCoordinator


def test_spawn_agents():
    """Test 1: Spawn 512 agents"""
    print("\n" + "=" * 70)
    print("TEST 1: Spawn 512 Dive Coder Agents")
    print("=" * 70)
    
    coordinator = MultiAgentCoordinator()
    result = coordinator.execute({"action": "spawn_agents"})
    
    print(f"\n✅ Status: {result.status}")
    print(f"   Total Agents: {result.data['total_agents']}")
    print(f"   Distribution:")
    for role, count in result.data['distribution'].items():
        print(f"      - {role.title()}: {count} agents")
    
    return result.status == "success"


def test_get_status():
    """Test 2: Get coordinator status"""
    print("\n" + "=" * 70)
    print("TEST 2: Get Coordinator Status")
    print("=" * 70)
    
    coordinator = MultiAgentCoordinator()
    result = coordinator.execute({"action": "get_status"})
    
    print(f"\n✅ Status: {result.status}")
    print(f"   Coordinator: {result.data['coordinator']}")
    print(f"   Agents Idle: {result.data['agents_idle']}")
    print(f"   Agents Busy: {result.data['agents_busy']}")
    print(f"   Dashboard:")
    for key, value in result.data['dashboard'].items():
        print(f"      - {key}: {value}")
    
    return result.status == "success"


def test_assign_task():
    """Test 3: Assign task (user drops task)"""
    print("\n" + "=" * 70)
    print("TEST 3: Assign Task (User Drops Task)")
    print("=" * 70)
    
    coordinator = MultiAgentCoordinator()
    result = coordinator.execute({
        "action": "assign_task",
        "task": "Create a REST API for user authentication with JWT",
        "priority": 5
    })
    
    print(f"\n✅ Status: {result.status}")
    print(f"   Task: {result.data['task']}")
    print(f"   Subtasks: {result.data['subtasks']}")
    print(f"   Assigned Agents: {result.data['assigned_agents']}")
    print(f"\n   Assignments:")
    for assignment in result.data['assignments']:
        print(f"      - Agent-{assignment['agent_id']:03d} [{assignment['role']}]: {assignment['subtask']}")
    
    return result.status == "success"


def test_generate_24h_plan():
    """Test 4: Generate 24-hour autonomous plan"""
    print("\n" + "=" * 70)
    print("TEST 4: Generate 24-Hour Autonomous Plan")
    print("=" * 70)
    
    coordinator = MultiAgentCoordinator()
    result = coordinator.execute({"action": "generate_24h_plan"})
    
    print(f"\n✅ Status: {result.status}")
    print(f"   Plan Date: {result.data['plan_date']}")
    print(f"\n   Timeline:")
    for time_slot, details in result.data['timeline'].items():
        print(f"\n   {time_slot}:")
        print(f"      Activity: {details['activity']}")
        print(f"      Agents: {details['agents_allocated']}")
        print(f"      Tasks: {', '.join(details['tasks'][:2])}...")
    
    print(f"\n   Expected Outcomes:")
    for outcome in result.data['expected_outcomes']:
        print(f"      ✓ {outcome}")
    
    return result.status == "success"


def test_autonomous_no_task():
    """Test 5: Autonomous mode (no task dropped)"""
    print("\n" + "=" * 70)
    print("TEST 5: Autonomous Mode (No Task Dropped)")
    print("=" * 70)
    
    coordinator = MultiAgentCoordinator()
    result = coordinator.execute({
        "action": "autonomous_execute",
        "autonomous_mode": True
    })
    
    print(f"\n✅ Status: {result.status}")
    print(f"   Mode: {result.data['mode']}")
    print(f"   Task Source: {result.data['task_source']}")
    print(f"   Message: {result.data['message']}")
    print(f"\n   📅 24h Plan Generated:")
    print(f"      Date: {result.data['plan']['plan_date']}")
    print(f"      Time Slots: {len(result.data['plan']['timeline'])}")
    
    return result.status == "success"


def test_autonomous_with_task():
    """Test 6: Autonomous mode (task dropped)"""
    print("\n" + "=" * 70)
    print("TEST 6: Autonomous Mode (Task Dropped)")
    print("=" * 70)
    
    coordinator = MultiAgentCoordinator()
    result = coordinator.execute({
        "action": "autonomous_execute",
        "task": "Implement caching layer for database queries",
        "priority": 4,
        "autonomous_mode": True
    })
    
    print(f"\n✅ Status: {result.status}")
    print(f"   Mode: {result.data['mode']}")
    print(f"   Task Source: {result.data['task_source']}")
    print(f"   Message: {result.data['message']}")
    print(f"\n   Execution:")
    print(f"      Subtasks: {result.data['execution']['subtasks']}")
    print(f"      Assigned Agents: {result.data['execution']['assigned_agents']}")
    
    return result.status == "success"


def run_all_tests():
    """Run all coordinator tests"""
    print("\n" + "=" * 70)
    print("🤖 MULTI-AGENT COORDINATOR TEST SUITE")
    print("=" * 70)
    print("\nTesting 512 Dive Coder AI Coordination System")
    print("Inspired by OpenClaw × Discord Architecture")
    print("=" * 70)
    
    tests = [
        ("Spawn 512 Agents", test_spawn_agents),
        ("Get Coordinator Status", test_get_status),
        ("Assign Task (User Drops)", test_assign_task),
        ("Generate 24h Plan", test_generate_24h_plan),
        ("Autonomous (No Task)", test_autonomous_no_task),
        ("Autonomous (With Task)", test_autonomous_with_task)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\n   Test Details:")
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"      {icon} {name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 Multi-Agent Coordinator Ready for Production!")
        print("   - 512 Dive Coder AIs spawned")
        print("   - Autonomous execution enabled")
        print("   - 24-hour planning active")
    else:
        print("⚠️  SOME TESTS FAILED")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
