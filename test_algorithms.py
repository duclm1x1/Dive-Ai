"""
Test Algorithm System
Test auto-registration and execution
"""

import sys
import os

# Add to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.algorithms import get_algorithm_manager


def test_registration():
    """Test algorithm auto-registration"""
    print("\n" + "="*60)
    print("🧪 TESTING ALGORITHM SYSTEM")
    print("="*60)
    
    # Get manager (will auto-register)
    manager = get_algorithm_manager()
    
    print(f"\n✅ Algorithms registered: {len(manager.algorithms)}")
    print(f"✅ Categories: {len(manager.get_categories())}")
    
    # List by category
    print("\n📊 Algorithms by Category:")
    for category in sorted(manager.get_categories()):
        algos = manager.category_index.get(category, [])
        print(f"\n  {category.upper()} ({len(algos)} algorithms):")
        for algo_id in algos:
            algo = manager.get_algorithm(algo_id)
            if algo and hasattr(algo, 'spec'):
                print(f"    - {algo_id}: {algo.spec.description[:60]}...")
    
    return manager


def test_llm_query(manager):
    """Test LLM Query algorithm"""
    print("\n" + "="*60)
    print("🧪 TEST 1: LLM Query Algorithm")
    print("="*60)
    
    try:
        result = manager.execute("LLMQuery", {
            "prompt": "What is Python?",
            "provider": "v98",
            "model": "claude-opus-4-6-thinking"
        })
        
        print(f"Status: {result.status}")
        print(f"Response: {result.data.get('response', 'N/A')[:100]}...")
        print(f"Tokens: {result.data.get('tokens', 0)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_smart_router(manager):
    """Test Smart Model Router"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Smart Model Router")
    print("="*60)
    
    test_tasks = [
        ("What is FastAPI?", 3),  # Simple → nano
        ("Build a todo app with React", 6),  # Medium → mini
        ("Design a distributed system architecture", 9)  # Complex → flash
    ]
    
    for task, expected_complexity in test_tasks:
        result = manager.execute("SmartModelRouter", {"task": task})
        
        print(f"\nTask: '{task}'")
        print(f"  Tier: {result.data.get('tier')}")
        print(f"  Model: {result.data.get('model')}")
        print(f"  Savings: {result.metadata.get('savings_vs_premium_pct', 0):.0f}%")


def test_computer_operator(manager):
    """Test Computer Operator"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Computer Operator")
    print("="*60)
    
    try:
        # Test screenshot
        result = manager.execute("ComputerOperator", {
            "action": "screenshot",
            "params": {}
        })
        
        print(f"Status: {result.status}")
        if result.status == "success":
            print(f"Screenshot size: {result.data.get('size')}")
            print(f"Screenshot captured: {len(result.data.get('screenshot', ''))} bytes")
        else:
            print(f"Error: {result.error}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_agent_selector(manager):
    """Test Agent Selector"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Agent Selector")
    print("="*60)
    
    result = manager.execute("AgentSelector", {
        "task": "Build a Python FastAPI backend with PostgreSQL database",
        "max_agents": 5
    })
    
    print(f"Status: {result.status}")
    print(f"Selected {len(result.data.get('selected_agents', []))} agents:")
    
    for agent in result.data.get('selected_agents', []):
        print(f"  - {agent['agent_name']} ({agent['category']}): {agent['match_score']:.2f}")


def test_semantic_routing(manager):
    """Test Semantic Routing"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Semantic Routing (SR)")
    print("="*60)
    
    test_queries = [
        "How do I fix this bug in my Python code?",
        "Analyze this dataset for correlations",
        "What is machine learning?"
    ]
    
    for query in test_queries:
        result = manager.execute("SemanticRouting", {"query": query})
        
        print(f"\nQuery: '{query}'")
        print(f"  Expert: {result.data.get('selected_expert')}")
        print(f"  Confidence: {result.data.get('confidence'):.2f}")


def test_stats(manager):
    """Test execution statistics"""
    print("\n" + "="*60)
    print("📊 EXECUTION STATISTICS")
    print("="*60)
    
    stats = manager.get_stats()
    
    print(f"\nTotal algorithm executions:")
    for algo_id, algo_stats in stats.items():
        calls = algo_stats.get("calls", 0)
        if calls > 0:
            success_rate = algo_stats.get("success_rate", 0)
            avg_time = algo_stats.get("avg_time_ms", 0)
            print(f"  {algo_id}: {calls} calls, {success_rate:.0f}% success, {avg_time:.2f}ms avg")


if __name__ == "__main__":
    print("\n🦞 DIVE AI V29.4 - ALGORITHM SYSTEM TEST\n")
    
    # Test 1: Registration
    manager = test_registration()
    
    # Test 2: Smart Router
    test_smart_router(manager)
    
    # Test 3: Agent Selector
    test_agent_selector(manager)
    
    # Test 4: Semantic Routing
    test_semantic_routing(manager)
    
    # Test 5: Computer Operator (optional - needs libraries)
    # test_computer_operator(manager)
    
    # Test 6: Stats
    test_stats(manager)
    
    print("\n" + "="*60)
    print("✅ ALGORITHM SYSTEM TEST COMPLETE!")
    print("="*60)
    print(f"\nTotal Algorithms: {len(manager.algorithms)}")
    print(f"Total Categories: {len(manager.get_categories())}")
    print("\n🦞🚀 V29.4 Algorithm Framework is READY!")
