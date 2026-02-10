"""
FINAL COMPREHENSIVE TEST WITH DETAILED ERROR REPORTING
Shows exactly where issues occur
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.algorithms import get_algorithm_manager


def main():
    print("\n🦞 FINAL COMPREHENSIVE TEST - DETAILED ERROR MODE\n")
    
    manager = get_algorithm_manager()
    
    print(f"\n✅ Total Algorithms: {len(manager.algorithms)}\n")
    
    # Test the 2 failing algorithms  in detail
    print("="*80)
    print("🔍 DETAILED TEST: VisionAnalysis")
    print("="*80)
    
    try:
        result = manager.execute("VisionAnalysis", {
            "screenshot_b64": "test_base64_data",
            "prompt": "test prompt"
        })
        
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        if hasattr(result, 'status'):
            print(f"✅ Has .status attribute: {result.status}")
        else:
            print(f"❌ Missing .status attribute - it's returning: {result}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "="*80)
    print("🔍 DETAILED TEST: HybridPrompting")
    print("="*80)
    
    try:
        result = manager.execute("HybridPrompting", {
            "raw_prompt": "test prompt"
        })
        
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        if hasattr(result, 'status'):
            print(f"✅ Has .status attribute: {result.status}")
        else:
            print(f"❌ Missing .status attribute - it's returning: {result}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "="*80)
    
    # Test one working algorithm for comparison
    print("🔍 CONTROL TEST: SmartModelRouter (working)")
    print("="*80)
    
    result = manager.execute("SmartModelRouter", {"task": "test"})
    print(f"Result type: {type(result)}")
    print(f"Has .status: {hasattr(result, 'status')}")
    if hasattr(result, 'status'):
        print(f"Status: {result.status}")
    
    print("\n✅ DIAGNOSTIC COMPLETE\n")


if __name__ == "__main__":
    main()
