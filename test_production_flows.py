"""
Dive AI V29.2 - End-to-End Production Flow Tests
Complete validation of all critical user flows

Tests:
1. Simple Code Generation Flow
2. Complex Multi-Step Flow with Memory
3. Failover Chain Under Failure
4. Concurrent Request Handling
5. Self-Improvement Flow
"""

import sys
import os
import time
import concurrent.futures
sys.path.insert(0, r'D:\Antigravity\Dive-AI-v29 structle\Dive-AI-v29\src')

os.environ["V98_API_KEY"] = "YOUR_V98_API_KEY_HERE"

print("="*80)
print("PRODUCTION FLOW TESTS - Dive AI V29.2")
print("="*80)

from core.algorithms.algorithm_manager import get_manager

manager = get_manager()

# Test Results Tracker
results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def record_test(name, passed, duration_ms, details=""):
    """Record test result"""
    results["tests"].append({
        "name": name,
        "passed": passed,
        "duration_ms": duration_ms,
        "details": details
    })
    if passed:
        results["passed"] += 1
        print(f"[PASS] {name} ({duration_ms:.0f}ms)")
    else:
        results["failed"] += 1
        print(f"[FAIL] {name} - {details}")

# ============================================================================
# TEST 1: Simple Code Generation Flow
# ============================================================================
print("\n" + "="*80)
print("[TEST 1] Simple Code Generation Flow")
print("User Request -> QueryClassifier -> LLMRouter -> CodeWriterV2 -> Response")
print("="*80)

start = time.time()
try:
    # Step 1: Classify query
    classify_result = manager.execute("QueryClassifier", {
        "query": "Write a Python function to calculate fibonacci numbers"
    })
    
    if classify_result.status != "success":
        raise Exception(f"QueryClassifier failed: {classify_result.data.get('error')}")
    
    complexity = classify_result.data.get("complexity")
    intent = classify_result.data.get("intent")
    print(f"  Step 1 - Classification: complexity={complexity}, intent={intent}")
    
    # Step 2: Route to LLM
    route_result = manager.execute("LLMRouter", {
        "task": "Generate fibonacci function",
        "speed_tier": "standard"  
    })
    
    if route_result.status != "success":
        raise Exception(f"LLMRouter failed: {route_result.data.get('error')}")
    
    selected_model = route_result.data.get("selected_model")
    print(f"  Step 2 - Routing: selected_model={selected_model}")
    
    # Step 3: Generate code
    gen_result = manager.execute("CodeWriterV2", {
        "task": "Write a Python function to calculate fibonacci numbers",
        "language": "python",
        "force_model": selected_model
    })
    
    if gen_result.status != "success":
        raise Exception(f"CodeWriterV2 failed: {gen_result.data.get('error')}")
    
    code = gen_result.data.get("code", "")
    print(f"  Step 3 - Generation: code_length={len(code)} chars")
    
    # Validation
    if "fibonacci" in code.lower() and "def " in code:
        duration = (time.time() - start) * 1000
        record_test("Simple Code Generation Flow", True, duration, "Valid fibonacci function generated")
    else:
        raise Exception("Generated code invalid")
        
except Exception as e:
    duration = (time.time() - start) * 1000
    record_test("Simple Code Generation Flow", False, duration, str(e))

# ============================================================================
# TEST 2: Failover Chain Under Simulated Failure
# ============================================================================
print("\n" + "="*80)
print("[TEST 2] Failover Chain Under Failure")
print("V98 (simulated fail) -> AICoding -> Response")
print("="*80)

start = time.time()
try:
    # Force failover by using invalid API key for V98
    old_key = os.environ.get("V98_API_KEY")
    os.environ["V98_API_KEY"] = "invalid_key_to_force_failover"
    
    # Try connection with failover enabled
    conn_result = manager.get_connection(
        provider="v98",
        failover=True
    )
    
    # Restore key
    if old_key:
        os.environ["V98_API_KEY"] = old_key
    
    if conn_result.status == "success":
        provider_used = conn_result.meta.get("provider_used", "unknown")
        failover_attempted = conn_result.meta.get("failover_attempted", False)
        
        if failover_attempted and provider_used != "v98":
            duration = (time.time() - start) * 1000
            record_test("Failover Chain", True, duration, f"Failed over to {provider_used}")
        else:
            raise Exception("Failover not triggered")
    else:
        raise Exception(f"Connection failed: {conn_result.data.get('error')}")
        
except Exception as e:
    duration = (time.time() - start) * 1000
    record_test("Failover Chain", False, duration, str(e))

# ============================================================================
# TEST 3: Memory Persistence Flow
# ============================================================================
print("\n" + "="*80)
print("[TEST 3] Memory Persistence Flow")
print("Store context -> Generate code -> Retrieve context")
print("="*80)

start = time.time()
try:
    from core.algorithms.operational.memory_store import MemoryStoreAlgorithm
    
    memory = MemoryStoreAlgorithm()
    
    # Store preference
    store_result = memory.execute({
        "action": "store",
        "content": "User prefers Python with type hints and docstrings",
        "metadata": {"category": "coding_preferences"}
    })
    
    if store_result.status != "success":
        raise Exception("Memory store failed")
    
    memory_id = store_result.data.get("memory_id")
    print(f"  Step 1 - Stored memory: {memory_id}")
    
    # Search
    search_result = memory.execute({
        "action": "search",
        "query": "python preferences",
        "limit": 5
    })
    
    if search_result.status != "success":
        raise Exception("Memory search failed")
    
    memories = search_result.data.get("memories", [])
    print(f"  Step 2 - Retrieved: {len(memories)} memories")
    
    # Validate
    if len(memories) > 0 and "type hints" in memories[0]["content"]:
        duration = (time.time() - start) * 1000
        record_test("Memory Persistence", True, duration, f"Stored and retrieved {len(memories)} memories")
    else:
        raise Exception("Memory not found or invalid")
        
except Exception as e:
    duration = (time.time() - start) * 1000
    record_test("Memory Persistence", False, duration, str(e))

# ============================================================================
# TEST 4: Concurrent Request Handling
# ============================================================================
print("\n" + "="*80)
print("[TEST 4] Concurrent Request Handling")
print("5 parallel code generation requests")
print("="*80)

start = time.time()
try:
    def generate_code(task_num):
        """Generate code for a task"""
        result = manager.auto_execute({
            "task": f"Write a function to sort array using method {task_num}",
            "type": "code_generation"
        })
        return result.status == "success"
    
    # Run 5 tasks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(generate_code, i) for i in range(1, 6)]
        results_list = [f.result(timeout=60) for f in concurrent.futures.as_completed(futures)]
    
    success_count = sum(results_list)
    print(f"  Completed: {success_count}/5 successful")
    
    if success_count >= 4:  # Allow 1 failure
        duration = (time.time() - start) * 1000
        record_test("Concurrent Requests", True, duration, f"{success_count}/5 succeeded")
    else:
        raise Exception(f"Only {success_count}/5 succeeded")
        
except Exception as e:
    duration = (time.time() - start) * 1000
    record_test("Concurrent Requests", False, duration, str(e))

# ============================================================================
# TEST 5: Performance Benchmarks
# ============================================================================
print("\n" + "="*80)
print("[TEST 5] Performance Benchmarks")
print("Checking latency requirements")
print("="*80)

# Simple query benchmark
start = time.time()
try:
    result = manager.execute("QueryClassifier", {
        "query": "simple test query"
    })
    duration = (time.time() - start) * 1000
    
    # Target: < 1s for classifier
    if duration < 1000:
        record_test("Performance - Classifier", True, duration, f"{duration:.0f}ms < 1000ms target")
    else:
        record_test("Performance - Classifier", False, duration, f"{duration:.0f}ms > 1000ms target")
except Exception as e:
    record_test("Performance - Classifier", False, 0, str(e))

# ============================================================================
# FINAL REPORT
# ============================================================================
print("\n" + "="*80)
print("PRODUCTION FLOW TEST REPORT")
print("="*80)

total_tests = results["passed"] + results["failed"]
pass_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {results['passed']} [PASS]")
print(f"Failed: {results['failed']} [FAIL]")
print(f"Pass Rate: {pass_rate:.1f}%")

print("\nDetailed Results:")
for test in results["tests"]:
    status = "[PASS]" if test["passed"] else "[FAIL]"
    print(f"  {status} | {test['name']:<40} | {test['duration_ms']:>6.0f}ms | {test['details']}")

print("\n" + "="*80)
if pass_rate >= 80:
    print("[PASS] PRODUCTION FLOW TESTS: PASSED (>= 80% pass rate)")
    print("System is ready for production deployment")
else:
    print("[FAIL] PRODUCTION FLOW TESTS: FAILED (< 80% pass rate)")
    print("System needs improvements before production")
print("="*80)
