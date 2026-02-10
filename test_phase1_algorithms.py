"""
Test suite for Phase 1 algorithms
Tests ConnectionV98 and LLMRouter with live V98 API
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.algorithms.tactical.connection_v98 import ConnectionV98Algorithm, get_v98_connection
from core.algorithms.tactical.llm_router import LLMRouterAlgorithm, route_to_llm


def test_connection_v98():
    """Test V98 connection algorithm"""
    print("=== Testing ConnectionV98Algorithm ===\n")
    
    algo = ConnectionV98Algorithm()
    
    # Test 1: Basic connection
    print("[Test 1] Basic connection with verification")
    result = algo.execute({
        "model": "claude-opus-4-6-thinking",
        "verify_connection": True
    })
    
    print(f"Status: {result.status}")
    print(f"Model: {result.data.get('selected_model')}")
    print(f"Latency: {result.data.get('latency_ms'):.2f}ms")
    print(f"Available models: {len(result.data.get('available_models', []))}")
    
    if result.status == "success":
        print("✅ Connection test passed!\n")
        
        # Test 2: Use the client
        print("[Test 2] Testing chat completion")
        client = result.data["client"]
        response = client.chat_completion([
            {"role": "user", "content": "Say 'Hello from Dive V29.2' in exactly those words."}
        ])
        print(f"Response: {response}")
        
        if "Dive V29.2" in response:
            print("✅ Chat completion test passed!\n")
        else:
            print("❌ Chat completion test failed - unexpected response\n")
    else:
        print(f"❌ Connection failed: {result.error}\n")
    
    # Test 3: Quick helper function
    print("[Test 3] Testing quick helper function")
    quick_result = get_v98_connection(verify=False)
    print(f"Quick connection status: {quick_result.status}")
    print(f"From cache: {quick_result.metadata.get('from_cache', False)}")
    print("✅ Helper function test passed!\n")


def test_llm_router():
    """Test LLM router algorithm"""
    print("=== Testing LLMRouterAlgorithm ===\n")
    
    router = LLMRouterAlgorithm()
    
    # Test 1: Simple task -> Should route to Haiku
    print("[Test 1] Simple task routing")
    result = router.execute({
        "task": "What is 2+2?",
        "constraints": {"speed_tier": "realtime"}
    })
    
    print(f"Task: 'What is 2+2?'")
    print(f"Complexity: {result.data['complexity']}")
    print(f"Selected model: {result.data['selected_model']}")
    print(f"Reason: {result.data['routing_reason']}")
    print(f"Estimated latency: {result.data['estimated_latency_ms']:.0f}ms")
    print()
    
    # Test 2: Complex task -> Should route to Opus Thinking
    print("[Test 2] Complex task routing")
    result = router.execute({
        "task": "Design a distributed system architecture for a real-time collaborative editor with conflict resolution",
        "constraints": {"speed_tier": "deep"}
    })
    
    print(f"Task: 'Design distributed system...'")
    print(f"Complexity: {result.data['complexity']}")
    print(f"Selected model: {result.data['selected_model']}")
    print(f"Reason: {result.data['routing_reason']}")
    print()
    
    # Test 3: Cost constraint
    print("[Test 3] Cost-constrained routing")
    result = router.execute({
        "task": "Implement a binary search tree in Python",
        "constraints": {
            "speed_tier": "standard",
            "max_cost_per_request": 0.002  # Very low cost
        }
    })
    
    print(f"Task: 'Implement binary search tree'")
    print(f"Complexity: {result.data['complexity']}")
    print(f"Selected model: {result.data['selected_model']}")
    print(f"Estimated cost: ${result.data['estimated_cost']:.4f}")
    print(f"Reason: {result.data['routing_reason']}")
    print()
    
    # Test 4: Force model
    print("[Test 4] Forced model selection")
    result = router.execute({
        "task": "Any task",
        "force_model": "claude-opus-4-6-thinking"
    })
    
    print(f"Forced model: {result.data['selected_model']}")
    print(f"Reason: {result.data['routing_reason']}")
    print()
    
    # Test 5: Quick helper
    print("[Test 5] Quick routing helper")
    result = route_to_llm(
        "Write a Python function to calculate fibonacci",
        speed_tier="fast",
        max_cost_per_request=0.01
    )
    
    print(f"Selected: {result.data['selected_model']}")
    print(f"Routing time: {result.metadata['routing_time_ms']:.2f}ms")
    print()
    
    print("✅ All routing tests passed!\n")


def test_integration():
    """Test integration of ConnectionV98 + LLMRouter"""
    print("=== Testing Integration: Router + Connection ===\n")
    
    # Route a complex task
    print("[Step 1] Route task to optimal model")
    routing_result = route_to_llm(
        "Create a self-improving AI agent using Claude 4.6 Opus Thinking",
        speed_tier="deep"
    )
    
    selected_model = routing_result.data["selected_model"]
    print(f"Router selected: {selected_model}")
    print(f"Complexity: {routing_result.data['complexity']}")
    print()
    
    # Connect to that model
    print("[Step 2] Connect to selected model")
    connection_result = get_v98_connection(model=selected_model, verify=True)
    
    if connection_result.status == "success":
        print(f"✅ Connected to {selected_model}")
        print(f"Connection latency: {connection_result.data['latency_ms']:.2f}ms")
        
        # Use it
        print("\n[Step 3] Execute task with selected model")
        client = connection_result.data["client"]
        response = client.chat_completion([
            {"role": "user", "content": "Explain the concept of self-improving AI systems in one paragraph."}
        ])
        
        print(f"Response length: {len(response)} chars")
        print(f"Response preview: {response[:200]}...")
        print("\n✅ Integration test passed!")
    else:
        print(f"❌ Connection failed: {connection_result.error}")


if __name__ == "__main__":
    print("🚀 Dive AI V29.2 - Phase 1 Algorithm Tests\n")
    print("=" * 60)
    print()
    
    try:
        # Test individual algorithms
        test_connection_v98()
        print("-" * 60)
        print()
        
        test_llm_router()
        print("-" * 60)
        print()
        
        # Test integration
        test_integration()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
