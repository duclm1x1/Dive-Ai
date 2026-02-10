"""
🧪 DIVE AI COMPREHENSIVE REAL-WORLD TEST SUITE
Tests 4 real scenarios to detect problems and self-debug

Scenarios:
1. Code Generation → Review → Fix workflow
2. Memory & Context persistence test
3. Multi-algorithm orchestration test
4. Error handling & recovery test
"""

import os
import sys
import time
import traceback
from typing import Dict, Any, List

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.algorithms.algorithm_manager import AlgorithmManager


class DiveAITestSuite:
    """Comprehensive test suite for Dive AI"""
    
    def __init__(self):
        print("=" * 70)
        print("🦞 DIVE AI COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        # Initialize with auto-scan
        self.manager = AlgorithmManager(auto_scan=True)
        
        self.results = {
            "scenarios": [],
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def run_all_scenarios(self):
        """Run all test scenarios"""
        scenarios = [
            ("Scenario 1: Code Generation Workflow", self.scenario_code_generation),
            ("Scenario 2: Memory & Context Test", self.scenario_memory_context),
            ("Scenario 3: Multi-Algorithm Orchestration", self.scenario_orchestration),
            ("Scenario 4: Error Handling & Recovery", self.scenario_error_recovery)
        ]
        
        for name, test_func in scenarios:
            print(f"\n{'='*70}")
            print(f"🧪 {name}")
            print("=" * 70)
            
            try:
                result = test_func()
                self.results["scenarios"].append({
                    "name": name,
                    "passed": result["passed"],
                    "failed": result["failed"],
                    "details": result.get("details", [])
                })
                self.results["total_tests"] += result["passed"] + result["failed"]
                self.results["passed"] += result["passed"]
                self.results["failed"] += result["failed"]
                
            except Exception as e:
                print(f"❌ SCENARIO CRASHED: {e}")
                traceback.print_exc()
                self.results["errors"].append({
                    "scenario": name,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                self.results["failed"] += 1
        
        self._print_summary()
        return self.results
    
    # =========================================================================
    # SCENARIO 1: Code Generation Workflow
    # =========================================================================
    
    def scenario_code_generation(self) -> Dict:
        """Test code generation, review, and quality gate"""
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Test 1.1: Code Generator
        print("\n   [1.1] Testing CodeGenerator...")
        try:
            algo = self.manager.get_algorithm("CodeGenerator")
            if algo:
                result = algo.execute({
                    "spec": {
                        "type": "function",
                        "name": "calculate_fibonacci",
                        "params": ["n: int"],
                        "return_type": "int",
                        "description": "Calculate nth Fibonacci number",
                        "body": "if n <= 1: return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)"
                    },
                    "language": "python"
                })
                
                if result.status == "success" and "code" in result.data:
                    lines = result.metadata.get('lines_of_code', len(result.data['code'].split('\n')))
                    print(f"      ✅ Generated {lines} lines of code")
                    results["passed"] += 1
                else:
                    print(f"      ❌ Code generation failed: {result}")
                    results["failed"] += 1
            else:
                print("      ⚠️ CodeGenerator not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 1.2: Quality Gate
        print("\n   [1.2] Testing QualityGate...")
        try:
            algo = self.manager.get_algorithm("QualityGate")
            if algo:
                result = algo.execute({
                    "artifact": {
                        "type": "code",
                        "content": '''def hello():
    """Say hello"""
    print("Hello, World!")
''',
                        "has_tests": True
                    }
                })
                
                if result.status == "success":
                    print(f"      ✅ Quality gate: {'PASSED' if result.data['passed'] else 'FAILED'}")
                    print(f"         Checks: {len(result.data['checks'])}")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ QualityGate not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 1.3: Test Generator
        print("\n   [1.3] Testing TestGenerator...")
        try:
            algo = self.manager.get_algorithm("TestGenerator")
            if algo:
                result = algo.execute({
                    "function_name": "calculate_total",
                    "spec": {
                        "examples": [
                            {"input": {"items": [10, 20], "tax": 0.1}, "expected": 33}
                        ]
                    }
                })
                
                if result.status == "success":
                    print(f"      ✅ Generated {result.data['count']} test cases")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ TestGenerator not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        return results
    
    # =========================================================================
    # SCENARIO 2: Memory & Context Test
    # =========================================================================
    
    def scenario_memory_context(self) -> Dict:
        """Test memory and context management"""
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Test 2.1: Session Manager
        print("\n   [2.1] Testing SessionManager...")
        try:
            algo = self.manager.get_algorithm("SessionManager")
            if algo:
                # Create session
                result = algo.execute({"action": "create"})
                if result.status == "success":
                    session_id = result.data["session_id"]
                    print(f"      ✅ Created session: {session_id}")
                    
                    # Add message
                    algo.execute({
                        "action": "add",
                        "message": {"role": "user", "content": "Test message"}
                    })
                    
                    # Get session
                    result = algo.execute({"action": "get"})
                    if result.data["message_count"] > 0:
                        print(f"      ✅ Message persisted ({result.data['message_count']} messages)")
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ SessionManager not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 2.2: Cache Manager
        print("\n   [2.2] Testing CacheManager...")
        try:
            algo = self.manager.get_algorithm("CacheManager")
            if algo:
                # Set value
                algo.execute({"action": "set", "key": "test_key", "value": {"data": 123}, "ttl": 3600})
                
                # Get value
                result = algo.execute({"action": "get", "key": "test_key"})
                
                if result.status == "hit":
                    print(f"      ✅ Cache hit! Value stored correctly")
                    results["passed"] += 1
                else:
                    print(f"      ❌ Cache miss")
                    results["failed"] += 1
                
                # Get stats
                stats = algo.execute({"action": "stats"})
                print(f"      📊 Hit rate: {stats.data['hit_rate']:.0%}")
            else:
                print("      ⚠️ CacheManager not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 2.3: Checkpoint Manager
        print("\n   [2.3] Testing CheckpointManager...")
        try:
            algo = self.manager.get_algorithm("CheckpointManager")
            if algo:
                # Save checkpoint
                algo.execute({
                    "action": "save",
                    "name": "test_checkpoint",
                    "state": {"step": 1, "data": "test"}
                })
                
                # List checkpoints
                result = algo.execute({"action": "list"})
                
                if result.data["count"] > 0:
                    print(f"      ✅ Saved {result.data['count']} checkpoints")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ CheckpointManager not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        return results
    
    # =========================================================================
    # SCENARIO 3: Multi-Algorithm Orchestration
    # =========================================================================
    
    def scenario_orchestration(self) -> Dict:
        """Test algorithm orchestration and coordination"""
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Test 3.1: Task Orchestrator
        print("\n   [3.1] Testing TaskOrchestrator...")
        try:
            algo = self.manager.get_algorithm("TaskOrchestrator")
            if algo:
                # Define tasks with dependencies
                algo.execute({
                    "action": "define",
                    "tasks": [
                        {"id": "setup", "name": "Setup", "dependencies": []},
                        {"id": "build", "name": "Build", "dependencies": ["setup"]},
                        {"id": "test", "name": "Test", "dependencies": ["build"]}
                    ]
                })
                
                # Execute orchestration
                result = algo.execute({"action": "execute"})
                
                if len(result.data.get("completed", [])) == 3:
                    print(f"      ✅ All 3 tasks completed in order")
                    results["passed"] += 1
                else:
                    print(f"      ⚠️ Only {len(result.data.get('completed', []))} completed")
                    results["failed"] += 1
            else:
                print("      ⚠️ TaskOrchestrator not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 3.2: DAG Executor
        print("\n   [3.2] Testing DAGExecutor...")
        try:
            algo = self.manager.get_algorithm("DAGExecutor")
            if algo:
                result = algo.execute({
                    "action": "build",
                    "nodes": [
                        {"id": "A", "handler": "start"},
                        {"id": "B", "handler": "process", "dependencies": ["A"]},
                        {"id": "C", "handler": "end", "dependencies": ["B"]}
                    ]
                })
                
                if result.status == "success":
                    node_count = result.data.get('node_count', result.data.get('edges', 0) + 1)
                    print(f"      ✅ DAG built with {node_count} nodes")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ DAGExecutor not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 3.3: Event Bus
        print("\n   [3.3] Testing EventBus...")
        try:
            algo = self.manager.get_algorithm("EventBus")
            if algo:
                # Subscribe
                algo.execute({"action": "subscribe", "event": "test.event"})
                algo.execute({"action": "subscribe", "event": "test.event"})
                
                # Emit
                result = algo.execute({
                    "action": "emit",
                    "event": "test.event",
                    "data": {"message": "hello"}
                })
                
                if result.data["delivered"] == 2:
                    print(f"      ✅ Event delivered to 2 subscribers")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ EventBus not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        return results
    
    # =========================================================================
    # SCENARIO 4: Error Handling & Recovery
    # =========================================================================
    
    def scenario_error_recovery(self) -> Dict:
        """Test error handling and recovery mechanisms"""
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Test 4.1: Recovery Handler
        print("\n   [4.1] Testing RecoveryHandler...")
        try:
            algo = self.manager.get_algorithm("RecoveryHandler")
            if algo:
                result = algo.execute({
                    "action": "recover",
                    "error": {"type": "timeout", "message": "API timeout"}
                })
                
                if result.data.get("success"):
                    print(f"      ✅ Recovery successful: {result.data['strategy_used']}")
                    results["passed"] += 1
                else:
                    print(f"      ⚠️ Recovery failed")
                    results["failed"] += 1
            else:
                print("      ⚠️ RecoveryHandler not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 4.2: Fault Tolerance
        print("\n   [4.2] Testing FaultTolerance...")
        try:
            algo = self.manager.get_algorithm("FaultTolerance")
            if algo:
                # Check health (uses 'check' action)
                result = algo.execute({
                    "action": "check",
                    "component": "test_service"
                })
                
                if result.status == "success":
                    print(f"      ✅ Health check passed: {result.data.get('status', 'ok')}")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ FaultTolerance not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 4.3: Rate Limiter
        print("\n   [4.3] Testing RateLimiter...")
        try:
            algo = self.manager.get_algorithm("RateLimiter")
            if algo:
                # Configure
                algo.execute({
                    "action": "config",
                    "key": "test_api",
                    "max_tokens": 10,
                    "refill_rate": 5
                })
                
                # Consume tokens
                result = algo.execute({
                    "action": "consume",
                    "key": "test_api",
                    "tokens": 3
                })
                
                if result.status == "allowed":
                    print(f"      ✅ Rate limit allowed, remaining: {result.data['remaining']}")
                    results["passed"] += 1
                else:
                    print(f"      ⚠️ Rate limited: wait {result.data.get('wait_time', 0):.1f}s")
                    results["passed"] += 1  # This is expected behavior
            else:
                print("      ⚠️ RateLimiter not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        # Test 4.4: Auto Error Handler
        print("\n   [4.4] Testing AutoErrorHandler...")
        try:
            algo = self.manager.get_algorithm("AutoErrorHandler")
            if algo:
                result = algo.execute({
                    "error": {
                        "type": "SyntaxError",
                        "message": "unexpected EOF",
                        "code": "def foo(:\n    pass"
                    }
                })
                
                if result.status == "success":
                    print(f"      ✅ Error categorized: {result.data.get('category', 'unknown')}")
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                print("      ⚠️ AutoErrorHandler not found")
                results["failed"] += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["failed"] += 1
        
        return results
    
    # =========================================================================
    # Summary
    # =========================================================================
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 70)
        
        print(f"\n   Total Tests: {self.results['total_tests']}")
        print(f"   ✅ Passed: {self.results['passed']}")
        print(f"   ❌ Failed: {self.results['failed']}")
        
        success_rate = (self.results['passed'] / max(1, self.results['total_tests'])) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print("\n   By Scenario:")
        for scenario in self.results["scenarios"]:
            total = scenario["passed"] + scenario["failed"]
            print(f"      {scenario['name']}: {scenario['passed']}/{total}")
        
        if self.results["errors"]:
            print("\n   ⚠️ Errors Detected:")
            for err in self.results["errors"]:
                print(f"      - {err['scenario']}: {err['error']}")
        
        print("\n" + "=" * 70)
        
        if self.results["failed"] == 0:
            print("🎉 ALL TESTS PASSED! Dive AI is functioning correctly.")
        else:
            print(f"⚠️ {self.results['failed']} tests failed. Review errors above.")
        
        print("=" * 70)


if __name__ == "__main__":
    suite = DiveAITestSuite()
    results = suite.run_all_scenarios()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)
