"""
Test Auto-Generation System
Test automatic algorithm generation and debugging
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.algorithms import get_algorithm_manager


def test_auto_generation():
    """Test the auto-generation system"""
    
    print("\n" + "="*80)
    print("🧪 TESTING AUTO-GENERATION SYSTEM")
    print("="*80)
    
    # Get manager
    manager = get_algorithm_manager()
    
    # Test auto-generator
    print("\n🤖 Testing AlgorithmAutoGenerator...\n")
    
    result = manager.execute("AlgorithmAutoGenerator", {
        "source": "skills",
        "scan_directory": "core/",
        "auto_debug": True
    })
    
    if result and result.status == "success":
        print(f"\n✅ Auto-Generation SUCCESS!")
        print(f"   Generated: {result.data.get('success_count')}/{result.data.get('total_patterns')} algorithms")
        print(f"   Algorithms: {result.data.get('generated_algorithms')}")
        
        # Show debug results
        debug_results = result.data.get('debug_results', [])
        if debug_results:
            print(f"\n   📊 Debug Results:")
            for debug in debug_results:
                status = "✅" if debug.get("status") == "success" else "❌"
                print(f"      {status} {debug}")
    else:
        print(f"\n❌ Auto-Generation FAILED")
        print(f"   Error: {result.error if result else 'Unknown'}")
    
    print("\n" + "="*80)
    print("✅ AUTO-GENERATION TEST COMPLETE!")
    print("="*80)
    
    return result


if __name__ == "__main__":
    print("\n🦞 DIVE AI V29.4 - AUTO-GENERATION SYSTEM TEST\n")
    result = test_auto_generation()
    
    if result and result.status == "success":
        print(f"\n🦞🚀 Self-Evolving System is OPERATIONAL!")
        print(f"   Can now auto-generate algorithms from skills/features!")
    else:
        print(f"\n⚠️  Auto-generation needs attention")
