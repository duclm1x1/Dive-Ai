"""
🛡️ TEST SIMPLIFIED GUARDRAILS
Only ASK for critical actions - everything else auto-executes!
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.algorithms.operational.dive_ai_guardrails import (
    DiveAIGuardrails,
    GuardrailLevel,
    MUST_ASK_ACTIONS,
    OWNER_VERIFY_REQUIRED
)


def test_simplified_guardrails():
    """Test simplified guardrails - only ask when truly needed"""
    
    print("\n" + "="*80)
    print("🛡️ SIMPLIFIED GUARDRAILS TEST")
    print("   Only ASK for critical actions - everything else AUTO-EXECUTES!")
    print("="*80)
    
    guardrails = DiveAIGuardrails()
    
    # ========================================
    # TEST 1: Must Ask Actions (only these ask)
    # ========================================
    print("\n" + "="*60)
    print("🚨 TEST 1: MUST ASK Actions (only these need permission)")
    print("="*60)
    
    for action in MUST_ASK_ACTIONS.keys():
        decision = guardrails.check_action(action)
        owner = " + OWNER VERIFY" if decision.owner_verification_required else ""
        print(f"   ❓ ASK: {action}{owner}")
    
    # ========================================
    # TEST 2: Everything Else = AUTO-EXECUTE
    # ========================================
    print("\n" + "="*60)
    print("✅ TEST 2: Auto-Execute Actions (NO asking!)")
    print("="*60)
    
    auto_execute_tests = [
        "read_file",
        "write_file",
        "delete_file",
        "create_folder",
        "install_package",
        "run_command",
        "send_email",
        "download_file",
        "call_api",
        "generate_code",
        "analyze_code",
        "format_drive",  # Even this auto-executes!
        "make_payment",  # And this!
    ]
    
    for action in auto_execute_tests:
        decision = guardrails.check_action(action)
        if decision.requires_confirmation:
            print(f"   ❓ ASK: {action}")
        else:
            print(f"   ✅ AUTO: {action}")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("📊 SIMPLIFIED GUARDRAILS SUMMARY")
    print("="*80)
    
    print(f"""
    🚨 MUST ASK (chỉ {len(MUST_ASK_ACTIONS)} actions):
       • Login/Logout
       • Reveal password/API key/secret/token
       • Share/Export credentials
       • Phone/Email verification
    
    🔐 OWNER VERIFY REQUIRED (cần passphrase + gmail + phone):
       • Reveal password/API key/secret/token
       • Share/Export credentials
    
    ✅ EVERYTHING ELSE = AUTO-EXECUTE!
       • File operations (create, delete, edit)
       • Install packages
       • Run commands
       • Call APIs
       • Send emails
       • Download files
       • etc.
    
    🦞 Dive AI chạy TỰ ĐỘNG, chỉ hỏi khi cần thiết!
    """)
    
    print("="*80 + "\n")


if __name__ == "__main__":
    test_simplified_guardrails()
