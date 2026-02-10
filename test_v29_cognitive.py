# Test V29 Cognitive Layer
import sys
import time
sys.path.insert(0, '.')

print("=" * 50)
print("Testing V29 Cognitive Layer")
print("=" * 50)

# 1. Test Manager
print("\n1. Meta-Algorithm Manager...")
try:
    from core.cognitive.meta_algorithm_manager import get_meta_algorithm_manager
    from core.cognitive.strategies.standard_strategy import StandardStrategy
    
    manager = get_meta_algorithm_manager()
    
    # Register strategy
    strategy = StandardStrategy()
    manager.register("StandardStrategy", strategy)
    
    print(f"   ✅ Manager initialized. Registry size: {len(manager.registry)}")
    
except Exception as e:
    print(f"   ❌ Manager Failed: {e}")
    sys.exit(1)

# 2. Test Execution
print("\n2. Executing Standard Strategy...")
print("   Goal: Build a simple calculator app")

try:
    # Execute through manager
    result = manager.execute_strategy("Build a simple calculator app")
    
    if result.status == "success":
        data = result.data
        print(f"\n   ✅ Execution Successful!")
        print(f"   Workflow ID: {data['workflow_id']}")
        print(f"   Duration: {data['state']['duration']:.2f}s")
        print(f"   Steps Completed: {data['state']['current_step']}/{data['state']['total_steps']}")
        
        kpis = data.get("kpis", {})
        print(f"   KPI Score: {kpis.get('overall_score', 0):.2f}")
        
    else:
        print(f"   ❌ Execution Failed: {result.error}")

except Exception as e:
    print(f"   ❌ Execution Exception: {e}")

print("\n" + "=" * 50)
print("Cognitive Layer Tests Complete!")
print("=" * 50)
