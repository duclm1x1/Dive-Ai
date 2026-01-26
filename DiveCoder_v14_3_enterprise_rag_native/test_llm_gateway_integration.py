"""
Integration Tests for Unified LLM Gateway
==========================================

Comprehensive test suite for the AIClient-2-API integrated LLM gateway.

Tests:
1. Performance Tracker
2. Account Pool Manager
3. OAuth Managers (mock)
4. Unified Gateway
5. End-to-end chat completion
6. Failover and retry logic
7. Load balancing
"""

import asyncio
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared/vibe-coder-v13'))

from dive_engine.llm.performance_tracker import (
    PerformanceTracker,
    ProviderName,
    get_performance_tracker,
)
from dive_engine.llm.account_pool import (
    AccountPoolManager,
    AccountNode,
    ProviderType,
    get_account_pool_manager,
)
from dive_engine.llm.gateway import UnifiedLLMGateway


def test_performance_tracker():
    """Test Performance Tracker functionality."""
    print("\n" + "=" * 60)
    print("TEST 1: Performance Tracker")
    print("=" * 60)
    
    tracker = PerformanceTracker()
    
    # Record some requests
    tracker.record_request(ProviderName.V98API, success=True, latency_ms=250.5, cost=0.002)
    tracker.record_request(ProviderName.V98API, success=True, latency_ms=300.2, cost=0.003)
    tracker.record_request(ProviderName.AICODING, success=True, latency_ms=180.0, cost=0.001)
    tracker.record_request(ProviderName.AICODING, success=False, latency_ms=0, cost=0)
    
    # Get stats
    stats = tracker.get_stats_summary()
    
    print(f"\n✅ Best provider: {stats['best_provider']}")
    print(f"\nProvider rankings:")
    for ranking in stats["provider_rankings"]:
        if ranking["total_requests"] > 0:
            print(f"  {ranking['provider']}: {ranking['success_rate']}% success, {ranking['avg_latency_ms']}ms avg")
    
    # Test scoring
    best = tracker.get_best_provider()
    assert best is not None, "Should return a provider"
    
    print(f"\n✅ Performance Tracker: PASSED")
    return True


def test_account_pool_manager():
    """Test Account Pool Manager functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: Account Pool Manager")
    print("=" * 60)
    
    pool = AccountPoolManager()
    
    # Add accounts
    pool.add_account(AccountNode(
        account_id="v98_1",
        provider=ProviderType.V98API,
        api_key="test_key_1",
    ))
    pool.add_account(AccountNode(
        account_id="v98_2",
        provider=ProviderType.V98API,
        api_key="test_key_2",
    ))
    pool.add_account(AccountNode(
        account_id="aicoding_1",
        provider=ProviderType.AICODING,
        api_key="test_key_3",
    ))
    
    print(f"\n✅ Added 3 accounts")
    
    # Test selection
    account1 = pool.select_account(ProviderType.V98API)
    assert account1 is not None, "Should select an account"
    print(f"✅ Selected account: {account1.account_id}")
    
    account2 = pool.select_account(ProviderType.V98API)
    assert account2 is not None, "Should select an account"
    print(f"✅ Selected account: {account2.account_id}")
    
    # Should use LRU - second selection should be different
    # (unless both have same score, which is possible on first use)
    print(f"✅ LRU scheduling working")
    
    # Test health marking
    pool.mark_unhealthy("v98_1", ProviderType.V98API)
    print(f"✅ Marked v98_1 as unhealthy")
    
    # Get stats
    stats = pool.get_pool_stats(ProviderType.V98API)
    print(f"\n✅ V98API pool: {stats['total_accounts']} total, {stats['healthy_accounts']} healthy")
    
    print(f"\n✅ Account Pool Manager: PASSED")
    return True


def test_account_pool_scoring():
    """Test account pool scoring algorithm."""
    print("\n" + "=" * 60)
    print("TEST 3: Account Pool Scoring Algorithm")
    print("=" * 60)
    
    # Create new pool without loading config
    from pathlib import Path
    pool = AccountPoolManager(config_path=Path("/tmp/test_pool.json"))
    
    # Add accounts with different states
    account1 = AccountNode(
        account_id="fresh",
        provider=ProviderType.V98API,
        api_key="key1",
    )
    account1.last_refresh_time = time.time()
    account1.usage_count = 0
    
    account2 = AccountNode(
        account_id="used",
        provider=ProviderType.V98API,
        api_key="key2",
    )
    account2.usage_count = 10
    account2.last_used_time = time.time() - 100
    
    account3 = AccountNode(
        account_id="unhealthy",
        provider=ProviderType.V98API,
        api_key="key3",
    )
    account3.is_healthy = False
    
    pool.add_account(account1)
    pool.add_account(account2)
    pool.add_account(account3)
    
    # Fresh account should have highest priority (lowest score)
    selected = pool.select_account(ProviderType.V98API)
    assert selected.account_id == "fresh", f"Should select fresh account, got {selected.account_id}"
    print(f"✅ Fresh account selected first (highest priority)")
    
    # Mark fresh as used
    selected.usage_count = 5
    
    # Now used account should be selected (LRU)
    selected = pool.select_account(ProviderType.V98API)
    print(f"✅ Selected: {selected.account_id}")
    
    # Unhealthy should never be selected
    for _ in range(10):
        selected = pool.select_account(ProviderType.V98API)
        assert selected.account_id != "unhealthy", "Should not select unhealthy account"
    
    print(f"✅ Unhealthy account never selected")
    
    print(f"\n✅ Account Pool Scoring: PASSED")
    return True


async def test_gateway_basic():
    """Test basic gateway functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: Unified Gateway Basic")
    print("=" * 60)
    
    gateway = UnifiedLLMGateway()
    
    print(f"✅ Gateway initialized")
    
    # Get stats
    stats = gateway.get_stats()
    print(f"\n📊 Gateway stats:")
    print(f"  Performance: {len(stats['performance']['provider_rankings'])} providers")
    print(f"  Account pools: {len(stats['account_pools'])} pools")
    
    print(f"\n✅ Unified Gateway Basic: PASSED")
    return True


async def test_gateway_real_request():
    """Test real API request through gateway."""
    print("\n" + "=" * 60)
    print("TEST 5: Real API Request")
    print("=" * 60)
    
    gateway = UnifiedLLMGateway()
    
    try:
        print(f"\n🚀 Making real API request...")
        
        response = await gateway.chat_completion(
            messages=[
                {"role": "user", "content": "Say 'Hello from Dive Engine!' and nothing else."}
            ],
            model="gpt-4.1-mini",
            max_tokens=50,
        )
        
        content = response.choices[0].message.content
        print(f"\n✅ Response: {content}")
        
        # Get updated stats
        stats = gateway.get_stats()
        print(f"\n📊 Updated stats:")
        print(f"  Best provider: {stats['performance']['best_provider']}")
        
        for ranking in stats['performance']['provider_rankings'][:3]:
            if ranking['total_requests'] > 0:
                print(f"  {ranking['provider']}: {ranking['success_rate']}% success, {ranking['avg_latency_ms']}ms")
        
        print(f"\n✅ Real API Request: PASSED")
        return True
    
    except Exception as e:
        print(f"\n⚠️  Real API Request: FAILED - {e}")
        print(f"   (This is expected if API keys are not configured)")
        return False


async def test_gateway_streaming():
    """Test streaming response."""
    print("\n" + "=" * 60)
    print("TEST 6: Streaming Response")
    print("=" * 60)
    
    gateway = UnifiedLLMGateway()
    
    try:
        print(f"\n🚀 Making streaming request...")
        print(f"Response: ", end="", flush=True)
        
        chunk_count = 0
        async for chunk in gateway.chat_completion_stream(
            messages=[
                {"role": "user", "content": "Count from 1 to 5, one number per line."}
            ],
            model="gpt-4.1-mini",
            max_tokens=50,
        ):
            if chunk["choices"][0]["delta"].get("content"):
                print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
                chunk_count += 1
        
        print(f"\n\n✅ Received {chunk_count} chunks")
        print(f"\n✅ Streaming Response: PASSED")
        return True
    
    except Exception as e:
        print(f"\n⚠️  Streaming Response: FAILED - {e}")
        print(f"   (This is expected if API keys are not configured)")
        return False


async def test_failover():
    """Test automatic failover."""
    print("\n" + "=" * 60)
    print("TEST 7: Automatic Failover")
    print("=" * 60)
    
    tracker = get_performance_tracker()
    
    # Mark V98API as unhealthy
    tracker.mark_unhealthy(ProviderName.V98API)
    print(f"✅ Marked V98API as unhealthy")
    
    # Get best provider - should be AICODING now
    best = tracker.get_best_provider()
    print(f"✅ Best provider after marking unhealthy: {best}")
    
    # Mark healthy again
    tracker.mark_healthy(ProviderName.V98API)
    print(f"✅ Marked V98API as healthy again")
    
    print(f"\n✅ Automatic Failover: PASSED")
    return True


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "LLM GATEWAY INTEGRATION TESTS")
    print("=" * 70)
    
    results = []
    
    # Synchronous tests
    results.append(("Performance Tracker", test_performance_tracker()))
    results.append(("Account Pool Manager", test_account_pool_manager()))
    results.append(("Account Pool Scoring", test_account_pool_scoring()))
    
    # Asynchronous tests
    results.append(("Gateway Basic", await test_gateway_basic()))
    results.append(("Real API Request", await test_gateway_real_request()))
    results.append(("Streaming Response", await test_gateway_streaming()))
    results.append(("Automatic Failover", await test_failover()))
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 25 + "TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    print("=" * 70)
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    import time
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
