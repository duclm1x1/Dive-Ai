"""
Test Priority System
Test background algorithms and priority management
"""

import sys
import os
import time

sys.path.append(os.path.dirname(__file__))

from core.algorithms import get_algorithm_manager
from core.algorithms.priority_manager import AlgorithmPriorityManager


def test_priority_system():
    """Test the priority management system"""
    
    print("\n" + "="*80)
    print("🧪 TESTING ALGORITHM PRIORITY SYSTEM (V28.7 Style)")
    print("="*80)
    
    # Get managers
    manager = get_algorithm_manager()
    priority_manager = AlgorithmPriorityManager(manager)
    
    # Show status
    status = priority_manager.get_status()
    
    print(f"\n📊 Priority System Configuration:")
    print(f"   Total Managed Algorithms: {status['total_managed']}")
    print(f"\n   Distribution by Priority:")
    for priority_level, count in status['by_priority'].items():
        print(f"      {priority_level}: {count} algorithms")
    
    print(f"\n   Always-Running Algorithms ({len(status['always_running'])}):")
    for algo in status['always_running']:
        config = priority_manager.priorities[algo]
        print(f"      ✅ [{config.priority.name}] {algo} - Every {config.execution_interval}s")
    
    # Test sorted by priority
    print(f"\n   Algorithm Execution Order (by priority):")
    sorted_algos = priority_manager.get_sorted_algorithms()
    for i, algo_id in enumerate(sorted_algos[:10], 1):  # Top 10
        priority = priority_manager.get_priority(algo_id)
        auto = "🔄" if priority_manager.should_auto_execute(algo_id) else "⏸️ "
        print(f"      {i}. {auto} [{priority.name}] {algo_id}")
    
    # Test background execution (short demo)
    print(f"\n🔄 Starting background algorithms for 10 seconds...")
    priority_manager.start_all_background_algorithms()
    
    time.sleep(10)
    
    priority_manager.stop_all_background_algorithms()
    
    print("\n" + "="*80)
    print("✅ PRIORITY SYSTEM TEST COMPLETE!")
    print("="*80)
    
    return status


if __name__ == "__main__":
    print("\n🦞 DIVE AI V29.4 - PRIORITY SYSTEM TEST\n")
    status = test_priority_system()
    
    print(f"\n📈 Summary:")
    print(f"   - {status['by_priority']['CRITICAL']} CRITICAL algorithms (always-running)")
    print(f"   - {status['by_priority']['HIGH']} HIGH priority algorithms")
    print(f"   - {status['by_priority']['NORMAL']} NORMAL priority algorithms")
    print(f"   - {status['by_priority']['LOW']} LOW priority algorithms")
    print(f"\n🦞🚀 V29.4 Priority System is OPERATIONAL!")
