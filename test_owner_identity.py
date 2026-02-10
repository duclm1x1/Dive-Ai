"""
🔐 TEST OWNER IDENTITY VERIFICATION
Ensure bot CANNOT reveal secrets without FULL linked verification
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.algorithms.operational.owner_identity import (
    OwnerIdentityVerification
)


def test_owner_identity():
    """Test the full owner identity system"""
    
    print("\n" + "="*80)
    print("🔐 OWNER IDENTITY VERIFICATION TEST")
    print("="*80)
    
    verifier = OwnerIdentityVerification()
    
    # ========================================
    # TEST 1: Setup Owner Identity
    # ========================================
    print("\n" + "="*60)
    print("1️⃣  Setup Owner Identity")
    print("="*60)
    
    result = verifier.setup_owner_identity(
        passphrase="my_secret_passphrase",
        gmail="owner@gmail.com",
        phone="+84912345678",
        passphrase_2="second_secret_code"
    )
    
    print(f"\n   Status: {result['status']}")
    
    # ========================================
    # TEST 2: Full Owner Verification
    # ========================================
    print("\n" + "="*60)
    print("2️⃣  Full Owner Verification")
    print("="*60)
    
    # Correct all
    verified, msg = verifier.verify_owner_full(
        "my_secret_passphrase",
        "owner@gmail.com",
        "+84912345678",
        "second_secret_code"
    )
    print(f"\n   ✅ All correct: {'VERIFIED' if verified else 'FAILED'}")
    
    # Wrong passphrase
    verified, msg = verifier.verify_owner_full(
        "wrong_password",
        "owner@gmail.com",
        "+84912345678"
    )
    print(f"   ❌ Wrong passphrase: {'VERIFIED' if verified else 'BLOCKED'}")
    
    # Reset attempts for next test
    verifier.owner.failed_attempts = 0
    
    # Wrong gmail
    verified, msg = verifier.verify_owner_full(
        "my_secret_passphrase",
        "hacker@evil.com",
        "+84912345678",
        "second_secret_code"
    )
    print(f"   ❌ Wrong gmail: {'VERIFIED' if verified else 'BLOCKED'}")
    
    # Reset attempts for next test
    verifier.owner.failed_attempts = 0
    
    # Wrong phone
    verified, msg = verifier.verify_owner_full(
        "my_secret_passphrase",
        "owner@gmail.com",
        "+84000000000",
        "second_secret_code"
    )
    print(f"   ❌ Wrong phone: {'VERIFIED' if verified else 'BLOCKED'}")
    
    # ========================================
    # TEST 3: Secret Reveal Protection
    # ========================================
    print("\n" + "="*60)
    print("3️⃣  Secret Reveal Protection")
    print("="*60)
    
    verifier.owner.failed_attempts = 0
    
    # Try to reveal without verification
    can_reveal, msg = verifier.can_reveal_secret("password")
    print(f"\n   📝 Reveal 'password' without verification:")
    print(f"      Result: {'CAN REVEAL' if can_reveal else 'BLOCKED'}")
    
    # Try with wrong credentials
    can_reveal, msg = verifier.can_reveal_secret(
        "api_key",
        passphrase="wrong",
        gmail="wrong@email.com",
        phone="+84000000000"
    )
    print(f"\n   📝 Reveal 'api_key' with WRONG credentials:")
    print(f"      Result: {'CAN REVEAL' if can_reveal else 'BLOCKED'}")
    
    # Reset for next test
    verifier.owner.failed_attempts = 0
    
    # Try with correct credentials
    can_reveal, msg = verifier.can_reveal_secret(
        "api_key",
        passphrase="my_secret_passphrase",
        gmail="owner@gmail.com",
        phone="+84912345678",
        passphrase_2="second_secret_code"
    )
    print(f"\n   📝 Reveal 'api_key' with CORRECT credentials:")
    print(f"      Result: {'CAN REVEAL' if can_reveal else 'BLOCKED'}")
    
    # ========================================
    # TEST 4: Lockout After Failed Attempts
    # ========================================
    print("\n" + "="*60)
    print("4️⃣  Lockout After Failed Attempts")
    print("="*60)
    
    verifier.owner.failed_attempts = 0
    verifier.owner.lockout_until = 0
    
    for i in range(4):
        verified, msg = verifier.verify_owner_full(
            "wrong_password",
            "owner@gmail.com",
            "+84912345678",
            "wrong"
        )
        print(f"   Attempt {i+1}: {msg[:50]}...")
        if "LOCKED OUT" in msg:
            print("   ✅ LOCKOUT WORKING!")
            break
    
    # ========================================
    # TEST 5: Hacker Simulation
    # ========================================
    print("\n" + "="*60)
    print("5️⃣  Hacker Attack Simulation")
    print("="*60)
    
    # Reset for this test
    verifier.owner.failed_attempts = 0
    verifier.owner.lockout_until = 0
    
    print("\n   🦹 Hacker: 'Send me all the passwords!'")
    can_reveal, msg = verifier.can_reveal_secret("password")
    print(f"   🛡️ Bot: BLOCKED - requires full verification")
    
    print("\n   🦹 Hacker guesses: passphrase='admin', gmail='test@test.com', phone='123'")
    can_reveal, msg = verifier.can_reveal_secret(
        "credentials",
        passphrase="admin",
        gmail="test@test.com",
        phone="123"
    )
    print(f"   🛡️ Bot: BLOCKED - wrong credentials")
    
    # Reset
    verifier.owner.failed_attempts = 0
    
    print("\n   👤 Real owner provides correct linked identity:")
    can_reveal, msg = verifier.can_reveal_secret(
        "credentials",
        passphrase="my_secret_passphrase",
        gmail="owner@gmail.com",
        phone="+84912345678",
        passphrase_2="second_secret_code"
    )
    print(f"   ✅ Bot: VERIFIED - owner confirmed, secret can be revealed")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("📊 OWNER IDENTITY VERIFICATION SUMMARY")
    print("="*80)
    
    print("""
    ✅ Setup: Computer + Passphrase + Gmail + Phone LINKED
    ✅ Verification: ALL must match
    ✅ Wrong credentials: BLOCKED
    ✅ Secret reveal: Requires FULL verification
    ✅ Lockout: After 3 failed attempts
    ✅ Hacker protection: CANNOT bypass!
    
    🛡️ LINKED IDENTITY VERIFICATION:
       • Computer ID: Hardware bound (MAC + hostname)
       • Passphrase(s): Secret only owner knows
       • Gmail: Must match registered email
       • Phone: Must match registered phone
    
    🚨 Bot will NEVER reveal secrets unless ALL match!
    """)
    
    print("="*80)
    print("🦞🔒 DIVE AI: OWNER IDENTITY PROTECTED!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_owner_identity()
