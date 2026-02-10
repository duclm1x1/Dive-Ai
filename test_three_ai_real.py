"""
🦞 TEST 3-AI ORCHESTRATOR WITH REAL V98 API

Tests the ThreeAIOrchestrator with actual API calls to:
- Claude Opus 4.6 (Primary Lead)
- GPT-5.2-Codex (Code Reviewer)
- GLM-4.6v (Multimodal Consultant)
"""

import os
import sys
import json
import time

sys.path.append(os.path.dirname(__file__))

from core.orchestrator.three_ai_orchestrator import ThreeAIOrchestrator


def test_simple_coding_task():
    """Test 1: Simple coding task"""
    print("\n" + "=" * 70)
    print("TEST 1: Simple Coding Task")
    print("=" * 70)
    
    orchestrator = ThreeAIOrchestrator()
    
    result = orchestrator.execute({
        "request": "Create a Python function to calculate the factorial of a number using recursion",
        "max_iterations": 2
    })
    
    print(f"\n📊 Status: {result.status}")
    print(f"   Consensus: {result.data.get('consensus', False)}")
    print(f"   Iterations: {result.data.get('iterations', 0)}")
    print(f"   Total Time: {result.data.get('total_time', 0):.2f}s")
    
    if result.status == "success":
        print(f"\n✅ Test 1 PASSED")
        print(f"\n   Final Output Preview:")
        output = result.data.get('result', '')
        print(f"   {output[:200]}..." if len(output) > 200 else f"   {output}")
    else:
        print(f"\n❌ Test 1 FAILED: {result.data}")
    
    return result


def test_code_review_task():
    """Test 2: Code review task"""
    print("\n" + "=" * 70)
    print("TEST 2: Code Review Task")
    print("=" * 70)
    
    orchestrator = ThreeAIOrchestrator()
    
    code_to_review = '''
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            result.append(data[i] * 2)
    return result
'''
    
    result = orchestrator.execute({
        "request": f"Review this Python code and suggest improvements:\n{code_to_review}",
        "max_iterations": 2
    })
    
    print(f"\n📊 Status: {result.status}")
    print(f"   Consensus: {result.data.get('consensus', False)}")
    
    print("\n   Review Results:")
    reviews = result.data.get('reviews', {})
    for ai_name, review in reviews.items():
        if review:
            print(f"      {ai_name}:")
            print(f"         Approved: {review.get('approved', False)}")
            print(f"         Confidence: {review.get('confidence', 0):.0%}")
    
    if result.status in ["success", "partial"]:
        print(f"\n✅ Test 2 PASSED")
    else:
        print(f"\n❌ Test 2 FAILED")
    
    return result


def test_architecture_design():
    """Test 3: Architecture design task"""
    print("\n" + "=" * 70)
    print("TEST 3: Architecture Design")
    print("=" * 70)
    
    orchestrator = ThreeAIOrchestrator()
    
    result = orchestrator.execute({
        "request": "Design a simple REST API for a todo list application with CRUD operations",
        "context": {
            "requirements": [
                "User authentication",
                "Create/Read/Update/Delete todos",
                "Categories and tags",
                "Due dates and priorities"
            ]
        },
        "max_iterations": 2
    })
    
    print(f"\n📊 Status: {result.status}")
    print(f"   Consensus: {result.data.get('consensus', False)}")
    print(f"   Iterations: {result.data.get('iterations', 0)}")
    
    if result.data.get('consensus'):
        print(f"\n✅ Test 3 PASSED - All 3 AIs agreed on the design!")
    else:
        print(f"\n⚠️  Test 3 PARTIAL - Consensus not reached, but got valuable feedback")
    
    return result


def test_debugging_scenario():
    """Test 4: Debugging scenario"""
    print("\n" + "=" * 70)
    print("TEST 4: Debugging Scenario")
    print("=" * 70)
    
    orchestrator = ThreeAIOrchestrator()
    
    buggy_code = '''
def find_max(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max = num
    return max_val
'''
    
    result = orchestrator.execute({
        "request": f"Find and fix the bug in this code:\n{buggy_code}",
        "max_iterations": 3
    })
    
    print(f"\n📊 Status: {result.status}")
    
    # Check if Codex caught the bug
    codex_review = result.data.get('reviews', {}).get('codex', {})
    if codex_review and not codex_review.get('approved', True):
        print(f"\n✅ Test 4 PASSED - Codex detected the bug!")
        print(f"   Issues found: {len(codex_review.get('issues', []))}")
    else:
        print(f"\n⚠️  Test 4 WARNING - Bug detection unclear")
    
    return result


def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("\n" + "=" * 70)
    print("🦞 3-AI ORCHESTRATOR COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("\nTesting with REAL V98 API:")
    print("  - Claude Opus 4.6 (Primary Lead)")
    print("  - GPT-5.2-Codex (Code Reviewer)")
    print("  - GLM-4.6v (Multimodal Consultant)")
    print("\n" + "=" * 70)
    
    results = []
    start_time = time.time()
    
    # Run all tests
    try:
        results.append(("Simple Coding Task", test_simple_coding_task()))
    except Exception as e:
        print(f"\n❌ Test 1 ERROR: {e}")
        results.append(("Simple Coding Task", None))
    
    time.sleep(1)  # Rate limit between tests
    
    try:
        results.append(("Code Review", test_code_review_task()))
    except Exception as e:
        print(f"\n❌ Test 2 ERROR: {e}")
        results.append(("Code Review", None))
    
    time.sleep(1)
    
    try:
        results.append(("Architecture Design", test_architecture_design()))
    except Exception as e:
        print(f"\n❌ Test 3 ERROR: {e}")
        results.append(("Architecture Design", None))
    
    time.sleep(1)
    
    try:
        results.append(("Debugging", test_debugging_scenario()))
    except Exception as e:
        print(f"\n❌ Test 4 ERROR: {e}")
        results.append(("Debugging", None))
    
    total_time = time.time() - start_time
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for name, res in results if res and res.status in ["success", "partial"])
    failed = len(results) - successful
    
    print(f"\n   Total Tests: {len(results)}")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏱️  Total Time: {total_time:.2f}s")
    
    print("\n   Test Details:")
    for name, res in results:
        if res:
            status_icon = "✅" if res.status == "success" else "⚠️" if res.status == "partial" else "❌"
            consensus = "✓" if res.data.get('consensus', False) else "✗"
            print(f"      {status_icon} {name}: {res.status} (Consensus: {consensus})")
        else:
            print(f"      ❌ {name}: ERROR")
    
    print("\n" + "=" * 70)
    
    if successful == len(results):
        print("🎉 ALL TESTS PASSED!")
    elif successful > 0:
        print("⚠️  PARTIAL SUCCESS - Some tests passed")
    else:
        print("❌ ALL TESTS FAILED - Check API configuration")
    
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = run_comprehensive_tests()
    
    # Exit with appropriate code
    successful = sum(1 for name, res in results if res and res.status in ["success", "partial"])
    sys.exit(0 if successful == len(results) else 1)
