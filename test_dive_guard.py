"""
🛡️ TEST DIVE GUARD
Unified security system - currently DISABLED
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.algorithms.operational.dive_guard import DiveGuard, MUST_ASK_ACTIONS


def test_dive_guard():
    print("\n" + "="*60)
    print("🛡️ DIVE GUARD TEST")
    print("="*60)
    
    guard = DiveGuard()
    
    # Show status
    print(f"\n   Status: {guard.status()}")
    
    # Test when DISABLED
    print("\n" + "-"*40)
    print("   When DISABLED (current state):")
    print("-"*40)
    
    for action in ["login", "reveal_password", "delete_file", "send_email"]:
        allowed, msg = guard.check_action(action)
        print(f"   {action}: {'✅ ALLOWED' if allowed else '❌ BLOCKED'}")
    
    # Enable and test
    print("\n" + "-"*40)
    print("   If ENABLED:")
    print("-"*40)
    
    guard.enable()
    
    print(f"\n   {guard.status()}")
    
    for action in ["login", "reveal_password", "delete_file", "send_email"]:
        allowed, msg = guard.check_action(action)
        print(f"   {action}: {'✅ ALLOWED' if allowed else msg}")
    
    # Disable again
    guard.disable()
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"""
   🔴 DIVE GUARD is currently: DISABLED
   
   When DISABLED:
      • All actions auto-execute
      • No verification required
   
   When ENABLED:
      • Must ask for: login, reveal secrets, etc.
      • High-risk needs owner verification
      • Everything else auto-executes
   
   To enable: guard.enable()
   To disable: guard.disable()
""")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_dive_guard()
