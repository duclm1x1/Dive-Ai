"""
🧪 COMPREHENSIVE CONNECTION TEST SUITE
Tests V98 and AICoding connection algorithms

Tests:
1. V98 Connection & Model Discovery
2. V98 Chat Completions (3 models)
3. AICoding Connection & Model Discovery  
4. AICoding OpenAI Format
5. AICoding Anthropic Format
6. Health Checks
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from core.algorithms.algorithm_manager import AlgorithmManager


def test_v98_connection():
    """Test 1: V98 Connection"""
    print("\n" + "=" * 70)
    print("TEST 1: V98 CONNECTION & MODEL DISCOVERY")
    print("=" * 70)
    
    manager = AlgorithmManager(auto_scan=True)
    v98 = manager.get_algorithm("V98Connection")
    
    if not v98:
        print("❌ V98Connection algorithm not found!")
        return False
    
    # Test connection
    result = v98.execute({"action": "connect"})
    
    if result.status == "success":
        print(f"\n✅ Connection successful!")
        print(f"   Total models: {result.data['total_models']}")
        print(f"   Categories: {result.data['categories']}")
        return True
    else:
        print(f"\n❌ Connection failed: {result.error}")
        return False


def test_v98_chat():
    """Test 2: V98 Chat with 3 models"""
    print("\n" + "=" * 70)
    print("TEST 2: V98 CHAT COMPLETIONS (3 Models)")
    print("=" * 70)
    
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    v98 = manager.get_algorithm("V98Connection")
    
    if not v98:
        print("❌ V98Connection algorithm not found!")
        return False
    
    # Test 3 models: Claude Opus, GPT Codex, GLM
    test_models = [
        ("claude-opus-4-6", "Claude Opus 4.6"),
        ("gpt-5.1-codex", "GPT-5.1-Codex"),
        ("glm-4.6v", "GLM-4.6v")
    ]
    
    results = []
    
    for model_id, model_name in test_models:
        print(f"\n   Testing {model_name}...")
        
        result = v98.execute({
            "action": "chat",
            "model": model_id,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Dive AI' and nothing else."}
            ],
            "temperature": 0.3,
            "max_tokens": 50
        })
        
        if result.status == "success":
            print(f"      ✅ {model_name}: {result.data['response'][:50]}")
            print(f"         Tokens: {result.data['usage'].get('total_tokens', 0)}")
            results.append(True)
        else:
            print(f"      ❌ {model_name}: {result.error}")
            results.append(False)
    
    success = all(results)
    print(f"\n{'✅' if success else '❌'} {sum(results)}/{len(results)} models responded successfully")
    return success


def test_aicoding_connection():
    """Test 3: AICoding Connection"""
    print("\n" + "=" * 70)
    print("TEST 3: AICODING CONNECTION & MODEL DISCOVERY")
    print("=" * 70)
    
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    aicoding = manager.get_algorithm("AICodingConnection")
    
    if not aicoding:
        print("❌ AICodingConnection algorithm not found!")
        return False
    
    # Test connection
    result = aicoding.execute({"action": "connect"})
    
    if result.status == "success":
        print(f"\n✅ Connection successful!")
        print(f"   Total models: {result.data['total_models']}")
        print(f"   Endpoints: {list(result.data['endpoints'].keys())}")
        return True
    else:
        print(f"\n❌ Connection failed: {result.error}")
        return False


def test_aicoding_openai_format():
    """Test 4: AICoding OpenAI Format"""
    print("\n" + "=" * 70)
    print("TEST 4: AICODING OPENAI FORMAT")
    print("=" * 70)
    
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    aicoding = manager.get_algorithm("AICodingConnection")
    
    if not aicoding:
        print("❌ AICodingConnection algorithm not found!")
        return False
    
    result = aicoding.execute({
        "action": "chat",
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from AICoding' and nothing else."}
        ],
        "temperature": 0.3,
        "max_tokens": 50
    })
    
    if result.status == "success":
        print(f"\n✅ OpenAI format successful!")
        print(f"   Response: {result.data['response']}")
        print(f"   Tokens: {result.data['usage'].get('total_tokens', 0)}")
        return True
    else:
        print(f"\n❌ OpenAI format failed: {result.error}")
        return False


def test_aicoding_anthropic_format():
    """Test 5: AICoding Anthropic Format"""
    print("\n" + "=" * 70)
    print("TEST 5: AICODING ANTHROPIC FORMAT")
    print("=" * 70)
    
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    aicoding = manager.get_algorithm("AICodingConnection")
    
    if not aicoding:
        print("❌ AICodingConnection algorithm not found!")
        return False
    
    result = aicoding.execute({
        "action": "messages",
        "model": "claude-opus-4-6",
        "messages": [
            {"role": "user", "content": "Say 'Hello from AICoding Anthropic' and nothing else."}
        ],
        "temperature": 0.3,
        "max_tokens": 50
    })
    
    if result.status == "success":
        print(f"\n✅ Anthropic format successful!")
        print(f"   Response: {result.data['response']}")
        print(f"   Tokens: {result.data['usage'].get('total_tokens', 0)}")
        return True
    else:
        print(f"\n❌ Anthropic format failed: {result.error}")
        return False


def test_health_checks():
    """Test 6: Health Checks"""
    print("\n" + "=" * 70)
    print("TEST 6: HEALTH CHECKS")
    print("=" * 70)
    
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    
    results = []
    
    # V98 Health
    print("\n   V98 Health Check...")
    v98 = manager.get_algorithm("V98Connection")
    if v98:
        result = v98.execute({"action": "health"})
        if result.status == "success":
            print(f"      ✅ V98 is healthy ({result.data['response_time_ms']:.0f}ms)")
            results.append(True)
        else:
            print(f"      ❌ V98 health check failed")
            results.append(False)
    
    # AICoding Health
    print("\n   AICoding Health Check...")
    aicoding = manager.get_algorithm("AICodingConnection")
    if aicoding:
        result = aicoding.execute({"action": "health"})
        if result.status == "success":
            print(f"      ✅ AICoding is healthy ({result.data['response_time_ms']:.0f}ms)")
            results.append(True)
        else:
            print(f"      ❌ AICoding health check failed")
            results.append(False)
    
    success = all(results)
    print(f"\n{'✅' if success else '❌'} {sum(results)}/{len(results)} health checks passed")
    return success


def run_all_tests():
    """Run all connection tests"""
    print("\n" + "=" * 70)
    print("🧪 CONNECTION ALGORITHMS COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("\nTesting:")
    print("  1. V98 Connection (475+ models)")
    print("  2. V98 Chat (Claude, GPT, GLM)")
    print("  3. AICoding Connection")
    print("  4. AICoding OpenAI Format")
    print("  5. AICoding Anthropic Format")
    print("  6. Health Checks")
    print("\n" + "=" * 70)
    
    tests = [
        ("V98 Connection", test_v98_connection),
        ("V98 Chat (3 Models)", test_v98_chat),
        ("AICoding Connection", test_aicoding_connection),
        ("AICoding OpenAI Format", test_aicoding_openai_format),
        ("AICoding Anthropic Format", test_aicoding_anthropic_format),
        ("Health Checks", test_health_checks)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for name, result in results if result)
    total = len(results)
    
    print(f"\n   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n   Test Details:")
    for name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"      {status_icon} {name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    elif passed > 0:
        print("⚠️  PARTIAL SUCCESS")
    else:
        print("❌ ALL TESTS FAILED")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
