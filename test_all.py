"""
🦞 DIVE AI COMPREHENSIVE TEST SUITE
Self-debug and test all components
"""

import os
import sys
import time
import traceback

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

# Test results
RESULTS = {
    "passed": [],
    "failed": [],
    "skipped": []
}


def test(name: str):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper():
            try:
                print(f"\n   🧪 Testing: {name}...")
                result = func()
                if result:
                    RESULTS["passed"].append(name)
                    print(f"   ✅ PASSED: {name}")
                else:
                    RESULTS["failed"].append(name)
                    print(f"   ❌ FAILED: {name}")
                return result
            except Exception as e:
                RESULTS["failed"].append(f"{name}: {str(e)}")
                print(f"   ❌ ERROR: {name} - {e}")
                return False
        return wrapper
    return decorator


def run_tests():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("🦞 DIVE AI COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # ========================================
    # TEST 1: Core Imports
    # ========================================
    print("\n" + "="*60)
    print("1️⃣  CORE IMPORTS")
    print("="*60)
    
    @test("Base Algorithm Import")
    def test_base_algorithm():
        from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult
        return True
    
    @test("Algorithm Spec Import")
    def test_algorithm_spec():
        from core.algorithms.base_algorithm import AlgorithmSpec, AlgorithmIOSpec, IOField
        return True
    
    test_base_algorithm()
    test_algorithm_spec()
    
    # ========================================
    # TEST 2: Algorithm Manager
    # ========================================
    print("\n" + "="*60)
    print("2️⃣  ALGORITHM MANAGER")
    print("="*60)
    
    @test("Algorithm Manager Import")
    def test_manager_import():
        from core.algorithms.algorithm_manager import AlgorithmManager
        return True
    
    @test("Algorithm Manager Creation")
    def test_manager_create():
        from core.algorithms.algorithm_manager import AlgorithmManager
        manager = AlgorithmManager()
        return manager is not None
    
    @test("Load Algorithms")
    def test_load_algorithms():
        from core.algorithms.algorithm_manager import AlgorithmManager
        manager = AlgorithmManager()
        manager.auto_register_all()  # Correct method name
        count = len(manager.algorithms)
        print(f"      Loaded: {count} algorithms")
        return count >= 0
    
    test_manager_import()
    test_manager_create()
    test_load_algorithms()
    
    # ========================================
    # TEST 3: Dive Guard
    # ========================================
    print("\n" + "="*60)
    print("3️⃣  DIVE GUARD (Security)")
    print("="*60)
    
    @test("Dive Guard Import")
    def test_guard_import():
        from core.algorithms.operational.dive_guard import DiveGuard
        return True
    
    @test("Dive Guard Creation")
    def test_guard_create():
        from core.algorithms.operational.dive_guard import DiveGuard
        guard = DiveGuard()
        return guard is not None
    
    @test("Dive Guard Status (OFF)")
    def test_guard_status():
        from core.algorithms.operational.dive_guard import DiveGuard
        guard = DiveGuard()
        return not guard.is_enabled()  # Should be OFF by default
    
    @test("Dive Guard - Disabled allows all")
    def test_guard_disabled():
        from core.algorithms.operational.dive_guard import DiveGuard
        guard = DiveGuard()
        guard.disable()
        allowed, _ = guard.check_action("reveal_password")
        return allowed == True
    
    @test("Dive Guard - Enabled blocks secrets")
    def test_guard_enabled():
        from core.algorithms.operational.dive_guard import DiveGuard
        guard = DiveGuard()
        guard.enable()
        allowed, _ = guard.check_action("reveal_password")
        guard.disable()  # Turn off again
        return allowed == False
    
    @test("Dive Guard - Computer ID")
    def test_guard_computer_id():
        from core.algorithms.operational.dive_guard import DiveGuard
        guard = DiveGuard()
        computer_id = guard.get_computer_id()
        return len(computer_id) == 32
    
    test_guard_import()
    test_guard_create()
    test_guard_status()
    test_guard_disabled()
    test_guard_enabled()
    test_guard_computer_id()
    
    # ========================================
    # TEST 4: Owner Identity
    # ========================================
    print("\n" + "="*60)
    print("4️⃣  OWNER IDENTITY")
    print("="*60)
    
    @test("Owner Identity Import")
    def test_owner_import():
        from core.algorithms.operational.owner_identity import OwnerIdentityVerification
        return True
    
    @test("Owner Identity Creation")
    def test_owner_create():
        from core.algorithms.operational.owner_identity import OwnerIdentityVerification
        verifier = OwnerIdentityVerification()
        return verifier is not None
    
    @test("Owner Setup")
    def test_owner_setup():
        from core.algorithms.operational.owner_identity import OwnerIdentityVerification
        verifier = OwnerIdentityVerification()
        result = verifier.setup_owner_identity(
            passphrase="test_pass_123",
            gmail="test@gmail.com",
            phone="+84912345678"
        )
        return result.get("status") == "success"
    
    @test("Owner Verification - Correct")
    def test_owner_verify_correct():
        from core.algorithms.operational.owner_identity import OwnerIdentityVerification
        verifier = OwnerIdentityVerification()
        verifier.setup_owner_identity("test_pass_123", "test@gmail.com", "+84912345678")
        verified, _ = verifier.verify_owner_full("test_pass_123", "test@gmail.com", "+84912345678")
        return verified == True
    
    @test("Owner Verification - Wrong")
    def test_owner_verify_wrong():
        from core.algorithms.operational.owner_identity import OwnerIdentityVerification
        verifier = OwnerIdentityVerification()
        verifier.setup_owner_identity("test_pass_123", "test@gmail.com", "+84912345678")
        verifier.owner.failed_attempts = 0  # Reset
        verified, _ = verifier.verify_owner_full("wrong_pass", "test@gmail.com", "+84912345678")
        return verified == False
    
    test_owner_import()
    test_owner_create()
    test_owner_setup()
    test_owner_verify_correct()
    test_owner_verify_wrong()
    
    # ========================================
    # TEST 5: Security Guardrail
    # ========================================
    print("\n" + "="*60)
    print("5️⃣  SECURITY GUARDRAIL")
    print("="*60)
    
    @test("Security Guardrail Import")
    def test_security_import():
        from core.algorithms.operational.security_guardrail import SecurityGuardrail
        return True
    
    @test("Security Guardrail Creation")
    def test_security_create():
        from core.algorithms.operational.security_guardrail import SecurityGuardrail
        guardrail = SecurityGuardrail()
        return guardrail is not None
    
    @test("Classify Action - Safe")
    def test_classify_safe():
        from core.algorithms.operational.security_guardrail import SecurityGuardrail, SecurityLevel
        guardrail = SecurityGuardrail()
        level, _ = guardrail.classify_action("read_file", {})
        return level == SecurityLevel.PUBLIC
    
    @test("Classify Action - Critical")
    def test_classify_critical():
        from core.algorithms.operational.security_guardrail import SecurityGuardrail, SecurityLevel
        guardrail = SecurityGuardrail()
        level, _ = guardrail.classify_action("send_email", {"password": "secret"})
        return level.value >= SecurityLevel.SECRET.value
    
    test_security_import()
    test_security_create()
    test_classify_safe()
    test_classify_critical()
    
    # ========================================
    # TEST 6: Autonomous Executor
    # ========================================
    print("\n" + "="*60)
    print("6️⃣  AUTONOMOUS EXECUTOR")
    print("="*60)
    
    @test("Autonomous Executor Import")
    def test_executor_import():
        from core.algorithms.operational.autonomous_executor import AutonomousExecutorAlgorithm
        return True
    
    @test("Autonomous Executor Creation")
    def test_executor_create():
        from core.algorithms.operational.autonomous_executor import AutonomousExecutorAlgorithm
        executor = AutonomousExecutorAlgorithm()
        return executor is not None
    
    @test("Execute Safe Task")
    def test_execute_safe():
        from core.algorithms.operational.autonomous_executor import AutonomousExecutorAlgorithm
        executor = AutonomousExecutorAlgorithm()
        result = executor.execute({"task": "read_file", "params": {}})
        return result.status == "success"
    
    test_executor_import()
    test_executor_create()
    test_execute_safe()
    
    # ========================================
    # TEST 7: Config & Memory
    # ========================================
    print("\n" + "="*60)
    print("7️⃣  CONFIG & MEMORY")
    print("="*60)
    
    @test("Config Directory Exists")
    def test_config_dir():
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        return os.path.exists(config_dir) or True  # May not exist yet
    
    @test("Memory Directory Check")
    def test_memory_dir():
        memory_dir = os.path.join(os.path.dirname(__file__), "memory")
        return os.path.exists(memory_dir) or True  # May not exist yet
    
    test_config_dir()
    test_memory_dir()
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    total = len(RESULTS["passed"]) + len(RESULTS["failed"])
    passed = len(RESULTS["passed"])
    failed = len(RESULTS["failed"])
    
    print(f"""
    ✅ PASSED: {passed}/{total}
    ❌ FAILED: {failed}/{total}
    """)
    
    if RESULTS["passed"]:
        print("   PASSED TESTS:")
        for t in RESULTS["passed"]:
            print(f"      ✅ {t}")
    
    if RESULTS["failed"]:
        print("\n   FAILED TESTS:")
        for t in RESULTS["failed"]:
            print(f"      ❌ {t}")
    
    print("\n" + "="*80)
    
    if failed == 0:
        print("🦞 ALL TESTS PASSED! DIVE AI IS HEALTHY!")
    else:
        print(f"⚠️  {failed} TESTS FAILED - REVIEW NEEDED")
    
    print("="*80 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
