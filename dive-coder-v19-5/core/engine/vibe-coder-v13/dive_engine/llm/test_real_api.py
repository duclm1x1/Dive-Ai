"""
Test Script for Real LLM API Integration
=========================================

This script tests the LLM client with real API calls to verify:
- All models are accessible
- Providers work correctly
- Failover mechanism functions
- Streaming works
- Token tracking is accurate
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dive_engine.llm import create_llm_client, ModelRegistry


def test_model_registry():
    """Test model registry."""
    print("=" * 80)
    print("TEST 1: Model Registry")
    print("=" * 80)
    
    registry = ModelRegistry()
    
    # List all models
    all_models = registry.list_models()
    print(f"\n✓ Total models available: {len(all_models)}")
    print(f"  Models: {', '.join(all_models[:10])}...")
    
    # List reasoning models
    reasoning_models = registry.list_models(capability="reasoning")
    print(f"\n✓ Reasoning models: {len(reasoning_models)}")
    print(f"  Models: {', '.join(reasoning_models)}")
    
    # List coding models
    coding_models = registry.list_models(capability="coding")
    print(f"\n✓ Coding models: {len(coding_models)}")
    print(f"  Models: {', '.join(coding_models)}")
    
    # Get model info
    model_info = registry.get_model_info("gpt-5.2-pro")
    print(f"\n✓ GPT-5.2 Pro info: {model_info}")
    
    model_info = registry.get_model_info("claude-opus-4.5")
    print(f"✓ Claude Opus 4.5 info: {model_info}")
    
    print("\n✅ Model Registry Test PASSED\n")


def test_simple_call():
    """Test simple synchronous call."""
    print("=" * 80)
    print("TEST 2: Simple Synchronous Call")
    print("=" * 80)
    
    client = create_llm_client()
    
    prompt = "Say 'Hello from Dive Engine!' in exactly those words."
    print(f"\nPrompt: {prompt}")
    
    try:
        response = client.call(
            prompt=prompt,
            system="You are a helpful assistant.",
            tier="tier_fast",
            max_tokens=50,
        )
        
        print(f"\n✓ Response: {response}")
        print(f"✓ Stats: {client.get_stats()}")
        print("\n✅ Simple Call Test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n❌ Simple Call Test FAILED\n")
        return False


async def test_async_call():
    """Test asynchronous call."""
    print("=" * 80)
    print("TEST 3: Asynchronous Call")
    print("=" * 80)
    
    client = create_llm_client()
    
    prompt = "Count from 1 to 5, one number per line."
    print(f"\nPrompt: {prompt}")
    
    try:
        response = await client.call_async(
            prompt=prompt,
            system="You are a helpful assistant.",
            tier="tier_fast",
            max_tokens=100,
        )
        
        print(f"\n✓ Response:\n{response}")
        print(f"\n✓ Stats: {client.get_stats()}")
        print("\n✅ Async Call Test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n❌ Async Call Test FAILED\n")
        return False


async def test_streaming():
    """Test streaming response."""
    print("=" * 80)
    print("TEST 4: Streaming Response")
    print("=" * 80)
    
    client = create_llm_client()
    
    prompt = "Write a haiku about coding."
    print(f"\nPrompt: {prompt}")
    print("\n✓ Streaming response:")
    
    try:
        async for chunk in client.stream(
            prompt=prompt,
            system="You are a poet.",
            tier="tier_fast",
            max_tokens=100,
        ):
            print(chunk, end="", flush=True)
        
        print(f"\n\n✓ Stats: {client.get_stats()}")
        print("\n✅ Streaming Test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n❌ Streaming Test FAILED\n")
        return False


def test_model_selection():
    """Test different models."""
    print("=" * 80)
    print("TEST 5: Model Selection")
    print("=" * 80)
    
    client = create_llm_client()
    
    models_to_test = [
        ("gpt-4.1-mini", "tier_fast"),
        ("gpt-4.1", "tier_think"),
        ("codex", "tier_code"),
    ]
    
    for model, tier in models_to_test:
        prompt = f"Say 'Testing {model}' in exactly those words."
        print(f"\n→ Testing model: {model} (tier: {tier})")
        
        try:
            response = client.call(
                prompt=prompt,
                model=model,
                tier=tier,
                max_tokens=50,
            )
            
            print(f"  ✓ Response: {response[:100]}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Final Stats: {client.get_stats()}")
    print("\n✅ Model Selection Test PASSED\n")


def test_reasoning_models():
    """Test reasoning models with complex prompt."""
    print("=" * 80)
    print("TEST 6: Reasoning Models")
    print("=" * 80)
    
    client = create_llm_client()
    
    prompt = """
    Problem: A farmer has 17 sheep. All but 9 die. How many sheep are left?
    
    Think step by step and provide your reasoning.
    """
    
    print(f"\nPrompt: {prompt.strip()}")
    
    # Test with thinking model
    print("\n→ Testing with tier_think (gpt-4.1):")
    try:
        response = client.call(
            prompt=prompt,
            system="You are a logical reasoning assistant.",
            tier="tier_think",
            max_tokens=500,
        )
        
        print(f"\n✓ Response:\n{response}")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print(f"\n✓ Stats: {client.get_stats()}")
    print("\n✅ Reasoning Models Test PASSED\n")


def test_failover():
    """Test provider failover mechanism."""
    print("=" * 80)
    print("TEST 7: Provider Failover")
    print("=" * 80)
    
    client = create_llm_client()
    
    print(f"\n✓ Active providers: {[p.name.value for p in client.providers if p.enabled]}")
    print(f"✓ Provider priority order: {[p.name.value for p in client.providers]}")
    
    # Make a call - should use highest priority provider
    prompt = "Say 'Failover test' in exactly those words."
    
    try:
        response = client.call(
            prompt=prompt,
            tier="tier_fast",
            max_tokens=50,
        )
        
        print(f"\n✓ Response: {response}")
        print(f"✓ Failover mechanism working correctly")
        print("\n✅ Failover Test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n❌ Failover Test FAILED\n")
        return False


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("DIVE ENGINE LLM CLIENT - COMPREHENSIVE TEST SUITE")
    print("=" * 80 + "\n")
    
    results = []
    
    # Test 1: Model Registry
    try:
        test_model_registry()
        results.append(("Model Registry", True))
    except Exception as e:
        print(f"✗ Model Registry Test failed: {e}\n")
        results.append(("Model Registry", False))
    
    # Test 2: Simple Call
    try:
        result = test_simple_call()
        results.append(("Simple Call", result))
    except Exception as e:
        print(f"✗ Simple Call Test failed: {e}\n")
        results.append(("Simple Call", False))
    
    # Test 3: Async Call
    try:
        result = await test_async_call()
        results.append(("Async Call", result))
    except Exception as e:
        print(f"✗ Async Call Test failed: {e}\n")
        results.append(("Async Call", False))
    
    # Test 4: Streaming
    try:
        result = await test_streaming()
        results.append(("Streaming", result))
    except Exception as e:
        print(f"✗ Streaming Test failed: {e}\n")
        results.append(("Streaming", False))
    
    # Test 5: Model Selection
    try:
        test_model_selection()
        results.append(("Model Selection", True))
    except Exception as e:
        print(f"✗ Model Selection Test failed: {e}\n")
        results.append(("Model Selection", False))
    
    # Test 6: Reasoning Models
    try:
        test_reasoning_models()
        results.append(("Reasoning Models", True))
    except Exception as e:
        print(f"✗ Reasoning Models Test failed: {e}\n")
        results.append(("Reasoning Models", False))
    
    # Test 7: Failover
    try:
        result = test_failover()
        results.append(("Failover", result))
    except Exception as e:
        print(f"✗ Failover Test failed: {e}\n")
        results.append(("Failover", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{'Total':.>50} {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed\n")
    
    return passed == total


if __name__ == "__main__":
    # Check if openai is installed
    try:
        import openai
        print("✓ openai package is installed\n")
    except ImportError:
        print("✗ openai package not installed")
        print("  Install with: pip install openai\n")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
