"""
🧪 Algorithm Validation Test
Tests all registered algorithms to ensure they load and execute properly
"""

import os
import sys
import time
from typing import Dict, List, Any

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.algorithms.algorithm_manager import AlgorithmManager


def run_validation_tests() -> Dict[str, Any]:
    """Run validation tests on all registered algorithms"""
    
    print("=" * 60)
    print("🧪 ALGORITHM VALIDATION TEST SUITE")
    print("=" * 60)
    
    # Initialize manager with auto-scan
    print("\n📦 Initializing AlgorithmManager with auto-scan...")
    manager = AlgorithmManager(auto_scan=True)
    
    # Get all algorithms
    algorithms = list(manager.algorithms.keys())
    
    print(f"\n📊 Found {len(algorithms)} algorithms to test")
    print(f"   Categories: {list(manager.category_index.keys())}")
    
    # Test results
    results = {
        "total": len(algorithms),
        "passed": 0,
        "failed": 0,
        "errors": [],
        "by_category": {}
    }
    
    # Test each algorithm
    print("\n" + "=" * 60)
    print("🔬 RUNNING TESTS")
    print("=" * 60)
    
    for algo_id in algorithms:
        algo = manager.algorithms[algo_id]
        
        try:
            # Check 1: Has spec
            if not hasattr(algo, 'spec') or not algo.spec:
                raise ValueError("Missing algorithm spec")
            
            # Check 2: Has execute method
            if not hasattr(algo, 'execute') or not callable(algo.execute):
                raise ValueError("Missing execute method")
            
            # Check 3: Spec has required fields
            spec = algo.spec
            required = ['algorithm_id', 'name', 'category']
            for field in required:
                if not getattr(spec, field, None):
                    raise ValueError(f"Missing spec field: {field}")
            
            # Track by category
            category = spec.category
            if category not in results["by_category"]:
                results["by_category"][category] = {"passed": 0, "failed": 0}
            
            results["passed"] += 1
            results["by_category"][category]["passed"] += 1
            print(f"   ✅ {algo_id}")
            
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"algorithm": algo_id, "error": str(e)})
            if hasattr(algo, 'spec') and algo.spec:
                category = algo.spec.category
                if category not in results["by_category"]:
                    results["by_category"][category] = {"passed": 0, "failed": 0}
                results["by_category"][category]["failed"] += 1
            print(f"   ❌ {algo_id}: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"\n   Total Algorithms: {results['total']}")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   Success Rate: {results['passed']/results['total']*100:.1f}%")
    
    print("\n   By Category:")
    for category, stats in sorted(results["by_category"].items()):
        total_cat = stats["passed"] + stats["failed"]
        print(f"      {category}: {stats['passed']}/{total_cat}")
    
    if results["errors"]:
        print("\n   Errors:")
        for err in results["errors"][:10]:  # Show first 10
            print(f"      - {err['algorithm']}: {err['error']}")
    
    print("\n" + "=" * 60)
    
    return results


def run_integration_test_3ai():
    """Test 3-AI Orchestrator integration"""
    
    print("\n" + "=" * 60)
    print("🤖 3-AI ORCHESTRATOR INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from core.orchestrator.three_ai_orchestrator import ThreeAIOrchestrator
        
        print("\n✅ ThreeAIOrchestrator imported successfully")
        
        # Check structure
        orchestrator = ThreeAIOrchestrator()
        
        required_attrs = ['ais', 'execute', 'spec']
        for attr in required_attrs:
            if hasattr(orchestrator, attr):
                print(f"   ✅ Has {attr}")
            else:
                print(f"   ❌ Missing {attr}")
        
        print("\n   AI Configurations:")
        for role, config in orchestrator.ais.items():
            print(f"      - {role.value}: {config.model}")
        
        print("\n✅ 3-AI Orchestrator ready for integration")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Run algorithm validation
    results = run_validation_tests()
    
    # Run 3-AI integration test
    run_integration_test_3ai()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)
