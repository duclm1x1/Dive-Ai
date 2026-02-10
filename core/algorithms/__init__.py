"""
Register all algorithms on startup
Auto-discovery and manual registration for skills
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.algorithms.algorithm_manager import AlgorithmManager


def register_all_algorithms():
    """Auto-register all algorithms + manual skills registration"""
    print("\n" + "=" * 60)
    print("🧠 DIVE AI V29.4 - ALGORITHM REGISTRATION")
    print("=" * 60)
    
    manager = AlgorithmManager()
    
    # Auto-register operational and composite
    manager.auto_register_all()
    
    # Manually register skills (15 algorithms)
    print("\n🎯 Registering V27.2 Advanced Skills...")
    try:
        from core.algorithms.skills import register_all_skills
        register_all_skills(manager)
    except Exception as e:
        print(f"   ⚠️  Skills registration error: {e}")
    
    print("\n📊 Registration Summary:")
    print(f"   Total Algorithms: {len(manager.algorithms)}")
    print(f"   Categories: {len(manager.get_categories())}")
    
    for category in sorted(manager.get_categories()):
        algos = manager.category_index.get(category, [])
        print(f"   - {category}: {len(algos)} algorithms")
    
    print("=" * 60)
    print("✅ Algorithm System Ready!\n")
    
    return manager


algorithm_manager = None


def get_algorithm_manager():
    """Get global algorithm manager (singleton)"""
    global algorithm_manager
    
    if algorithm_manager is None:
        algorithm_manager = register_all_algorithms()
    
    return algorithm_manager


if __name__ == "__main__":
    manager = register_all_algorithms()
    print(f"\n✅ Registered {len(manager.algorithms)} algorithms")
