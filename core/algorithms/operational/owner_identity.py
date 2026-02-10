"""
🔐 OWNER IDENTITY VERIFICATION SYSTEM
Bot CANNOT reveal any secrets unless FULL verification:
- Computer ID match
- Secret passphrase
- Gmail match
- Phone number match

ALL LINKED TOGETHER - Cannot bypass!
"""

import os
import sys
import hashlib
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


@dataclass
class OwnerIdentity:
    """
    Owner's linked identity - ALL must match for verification
    """
    # Computer binding
    computer_id: Optional[str] = None
    computer_name: Optional[str] = None
    
    # Secret passphrases (1-2)
    passphrase_hash: Optional[str] = None
    passphrase_2_hash: Optional[str] = None
    
    # Linked accounts
    gmail: Optional[str] = None
    phone: Optional[str] = None
    
    # Security state
    is_configured: bool = False
    failed_attempts: int = 0
    lockout_until: float = 0
    max_attempts: int = 3
    lockout_duration: int = 600  # 10 minutes


class OwnerIdentityVerification:
    """
    🔐 OWNER IDENTITY VERIFICATION
    
    Bot CANNOT reveal ANY secrets unless:
    1. Correct computer (hardware bound)
    2. Correct secret passphrase(s)
    3. Gmail matches registered
    4. Phone matches registered
    
    ALL LINKED - Hacker cannot bypass!
    """
    
    # 🚨 CRITICAL: Secrets the bot can NEVER reveal without verification
    PROTECTED_SECRETS = [
        "password", "api_key", "secret", "private_key",
        "access_token", "refresh_token", "credentials",
        "bank_account", "credit_card", "ssn", "pin"
    ]
    
    def __init__(self):
        self.owner = OwnerIdentity()
        self.security_log: List[Dict] = []
        self._config_file = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..',
            'config', 
            'owner_identity.json'
        )
    
    def get_computer_fingerprint(self) -> str:
        """Generate unique computer fingerprint"""
        import platform
        import socket
        import uuid
        
        mac = format(uuid.getnode(), '012X')
        hostname = socket.gethostname()
        platform_str = platform.platform()
        
        fingerprint = f"{mac}:{hostname}:{platform_str}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:32]
    
    def setup_owner_identity(
        self,
        passphrase: str,
        gmail: str,
        phone: str,
        passphrase_2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup owner's linked identity
        
        This BINDS:
        - Current computer
        - Secret passphrase(s)
        - Gmail
        - Phone
        
        ALL must match for ANY sensitive operation!
        """
        
        print("\n" + "="*60)
        print("🔐 SETTING UP OWNER IDENTITY")
        print("="*60)
        
        # Validate inputs
        if len(passphrase) < 6:
            return {"status": "error", "message": "❌ Passphrase must be at least 6 characters"}
        
        if "@gmail.com" not in gmail.lower() and "@" not in gmail:
            return {"status": "error", "message": "❌ Invalid email address"}
        
        if len(phone) < 10:
            return {"status": "error", "message": "❌ Invalid phone number"}
        
        # Get computer fingerprint
        computer_id = self.get_computer_fingerprint()
        
        import socket
        computer_name = socket.gethostname()
        
        # Hash sensitive data
        passphrase_hash = hashlib.sha256(passphrase.encode()).hexdigest()
        gmail_hash = hashlib.sha256(gmail.lower().encode()).hexdigest()
        phone_hash = hashlib.sha256(phone.encode()).hexdigest()
        
        # Store identity
        self.owner.computer_id = computer_id
        self.owner.computer_name = computer_name
        self.owner.passphrase_hash = passphrase_hash
        self.owner.gmail = gmail_hash  # Store hashed
        self.owner.phone = phone_hash  # Store hashed
        self.owner.is_configured = True
        
        if passphrase_2:
            if len(passphrase_2) < 6:
                return {"status": "error", "message": "❌ Passphrase 2 must be at least 6 characters"}
            self.owner.passphrase_2_hash = hashlib.sha256(passphrase_2.encode()).hexdigest()
        
        # Save config (hashed only)
        self._save_config()
        
        print(f"\n   🖥️  Computer: {computer_name}")
        print(f"   📧 Gmail: {gmail[:3]}***{gmail.split('@')[0][-2:]}@{gmail.split('@')[1]}")
        print(f"   📱 Phone: {phone[:3]}****{phone[-2:]}")
        print(f"   🔐 Passphrase 1: Configured")
        if passphrase_2:
            print(f"   🔐 Passphrase 2: Configured")
        
        print("\n   ✅ OWNER IDENTITY CONFIGURED!")
        print("   🛡️ Bot CANNOT reveal secrets without FULL verification!")
        
        self._log_event("IDENTITY_SETUP", "Owner identity configured")
        
        return {
            "status": "success",
            "computer": computer_name,
            "gmail_masked": f"{gmail[:3]}***@{gmail.split('@')[1]}",
            "phone_masked": f"{phone[:3]}****{phone[-2:]}",
            "passphrases_configured": 2 if passphrase_2 else 1
        }
    
    def verify_owner_full(
        self,
        passphrase: str,
        gmail: str,
        phone: str,
        passphrase_2: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        FULL OWNER VERIFICATION
        
        ALL must match:
        1. Computer ID
        2. Passphrase(s)
        3. Gmail
        4. Phone
        
        Returns:
            (is_verified, message)
        """
        
        if not self.owner.is_configured:
            return False, "❌ Owner identity not configured. Setup first."
        
        # Check lockout
        if self.owner.lockout_until > time.time():
            remaining = int(self.owner.lockout_until - time.time())
            return False, f"🔒 LOCKED OUT: Wait {remaining} seconds"
        
        failed_checks = []
        
        # 1. Verify Computer
        current_computer = self.get_computer_fingerprint()
        if current_computer != self.owner.computer_id:
            self._log_event("WRONG_COMPUTER", "Access attempt from different computer")
            return False, "🚨 BLOCKED: Wrong computer! Only registered computer can verify."
        
        # 2. Verify Passphrase 1
        passphrase_hash = hashlib.sha256(passphrase.encode()).hexdigest()
        if passphrase_hash != self.owner.passphrase_hash:
            failed_checks.append("passphrase_1")
        
        # 3. Verify Passphrase 2 (if configured)
        if self.owner.passphrase_2_hash:
            if not passphrase_2:
                return False, "❌ Second passphrase required!"
            
            passphrase_2_hash = hashlib.sha256(passphrase_2.encode()).hexdigest()
            if passphrase_2_hash != self.owner.passphrase_2_hash:
                failed_checks.append("passphrase_2")
        
        # 4. Verify Gmail
        gmail_hash = hashlib.sha256(gmail.lower().encode()).hexdigest()
        if gmail_hash != self.owner.gmail:
            failed_checks.append("gmail")
        
        # 5. Verify Phone
        phone_hash = hashlib.sha256(phone.encode()).hexdigest()
        if phone_hash != self.owner.phone:
            failed_checks.append("phone")
        
        # Check results
        if failed_checks:
            self.owner.failed_attempts += 1
            
            if self.owner.failed_attempts >= self.owner.max_attempts:
                self.owner.lockout_until = time.time() + self.owner.lockout_duration
                self._log_event("LOCKOUT", f"Too many failed attempts. Failed: {failed_checks}")
                return False, f"🚨 LOCKED OUT for {self.owner.lockout_duration}s - Too many wrong attempts!"
            
            remaining = self.owner.max_attempts - self.owner.failed_attempts
            self._log_event("VERIFICATION_FAILED", f"Failed checks: {failed_checks}")
            return False, f"❌ Verification failed. {remaining} attempts left."
        
        # SUCCESS!
        self.owner.failed_attempts = 0
        self._log_event("OWNER_VERIFIED", "Full verification successful")
        
        return True, f"""
🔓 OWNER VERIFIED!
   🖥️  Computer: {self.owner.computer_name}
   🔐 Passphrases: ✅ Correct
   📧 Gmail: ✅ Matched
   📱 Phone: ✅ Matched

You are confirmed as the REAL owner!
"""
    
    def can_reveal_secret(
        self,
        secret_type: str,
        passphrase: Optional[str] = None,
        gmail: Optional[str] = None,
        phone: Optional[str] = None,
        passphrase_2: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if bot can reveal a secret
        
        CRITICAL: Bot CANNOT reveal protected secrets without full verification!
        """
        
        # Check if this is a protected secret
        is_protected = any(p in secret_type.lower() for p in self.PROTECTED_SECRETS)
        
        if not is_protected:
            return True, "This is not a protected secret"
        
        # For protected secrets, REQUIRE FULL VERIFICATION
        if not all([passphrase, gmail, phone]):
            return False, f"""
🚨 CANNOT REVEAL: '{secret_type}'

This is a PROTECTED SECRET. To access, provide:
1️⃣  Your SECRET PASSPHRASE
2️⃣  Your registered GMAIL
3️⃣  Your registered PHONE

All must match your registered identity!
"""
        
        # Verify owner
        verified, message = self.verify_owner_full(passphrase, gmail, phone, passphrase_2)
        
        if verified:
            return True, "✅ Owner verified. Secret can be revealed."
        else:
            return False, message
    
    def _log_event(self, event_type: str, details: str):
        """Log security event"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        self.security_log.append(event)
        print(f"\n   🛡️ SECURITY: {event_type} - {details}")
        
        if len(self.security_log) > 100:
            self.security_log = self.security_log[-100:]
    
    def _save_config(self):
        """Save owner identity config (hashed data only)"""
        os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        
        config = {
            "computer_id": self.owner.computer_id,
            "computer_name": self.owner.computer_name,
            "passphrase_hash": self.owner.passphrase_hash,
            "passphrase_2_hash": self.owner.passphrase_2_hash,
            "gmail_hash": self.owner.gmail,
            "phone_hash": self.owner.phone,
            "is_configured": self.owner.is_configured
        }
        
        with open(self._config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> bool:
        """Load owner identity config"""
        if not os.path.exists(self._config_file):
            return False
        
        try:
            with open(self._config_file, 'r') as f:
                config = json.load(f)
            
            self.owner.computer_id = config.get("computer_id")
            self.owner.computer_name = config.get("computer_name")
            self.owner.passphrase_hash = config.get("passphrase_hash")
            self.owner.passphrase_2_hash = config.get("passphrase_2_hash")
            self.owner.gmail = config.get("gmail_hash")
            self.owner.phone = config.get("phone_hash")
            self.owner.is_configured = config.get("is_configured", False)
            
            return True
        except:
            return False


class OwnerIdentityAlgorithm(BaseAlgorithm):
    """
    Owner Identity Verification Algorithm
    
    Bot CANNOT reveal secrets without FULL owner verification
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="OwnerIdentity",
            name="Owner Identity Verification",
            level="operational",
            category="security",
            version="1.0",
            description="Linked identity verification: Computer + Passphrase + Gmail + Phone. Bot CANNOT reveal secrets without full verification.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "setup, verify, or can_reveal"),
                    IOField("passphrase", "string", False, "Secret passphrase"),
                    IOField("passphrase_2", "string", False, "Second passphrase"),
                    IOField("gmail", "string", False, "Gmail address"),
                    IOField("phone", "string", False, "Phone number"),
                    IOField("secret_type", "string", False, "Type of secret to reveal")
                ],
                outputs=[
                    IOField("verified", "boolean", True, "Whether owner is verified"),
                    IOField("message", "string", True, "Result message")
                ]
            ),
            
            steps=[
                "Step 1: Check action type",
                "Step 2: For setup - bind all credentials",
                "Step 3: For verify - check ALL linked credentials",
                "Step 4: For reveal - require FULL verification",
                "Step 5: Return result"
            ],
            
            tags=["security", "identity", "owner", "2fa", "critical"]
        )
        
        self.verifier = OwnerIdentityVerification()
        self.verifier.load_config()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute owner verification"""
        
        action = params.get("action", "verify")
        passphrase = params.get("passphrase")
        passphrase_2 = params.get("passphrase_2")
        gmail = params.get("gmail")
        phone = params.get("phone")
        secret_type = params.get("secret_type", "")
        
        try:
            if action == "setup":
                if not all([passphrase, gmail, phone]):
                    return AlgorithmResult(
                        status="error",
                        error="Setup requires: passphrase, gmail, phone"
                    )
                
                result = self.verifier.setup_owner_identity(
                    passphrase, gmail, phone, passphrase_2
                )
                
                return AlgorithmResult(
                    status=result["status"],
                    data=result
                )
            
            elif action == "verify":
                if not all([passphrase, gmail, phone]):
                    return AlgorithmResult(
                        status="error",
                        error="Verify requires: passphrase, gmail, phone"
                    )
                
                verified, message = self.verifier.verify_owner_full(
                    passphrase, gmail, phone, passphrase_2
                )
                
                return AlgorithmResult(
                    status="success" if verified else "failed",
                    data={
                        "verified": verified,
                        "message": message
                    }
                )
            
            elif action == "can_reveal":
                can_reveal, message = self.verifier.can_reveal_secret(
                    secret_type, passphrase, gmail, phone, passphrase_2
                )
                
                return AlgorithmResult(
                    status="success" if can_reveal else "blocked",
                    data={
                        "can_reveal": can_reveal,
                        "message": message
                    }
                )
            
            else:
                return AlgorithmResult(
                    status="error",
                    error=f"Unknown action: {action}. Use: setup, verify, can_reveal"
                )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Verification failed: {str(e)}"
            )


def register(algorithm_manager):
    """Register Owner Identity Algorithm"""
    try:
        algo = OwnerIdentityAlgorithm()
        algorithm_manager.register("OwnerIdentity", algo)
        print("✅ OwnerIdentity Algorithm registered (LINKED VERIFICATION)")
    except Exception as e:
        print(f"❌ Failed to register OwnerIdentity: {e}")


# ========================================
# QUICK REFERENCE
# ========================================

"""
🔐 OWNER IDENTITY VERIFICATION

Bot CANNOT reveal ANY secrets without FULL verification of:
1. 🖥️  Computer ID - Hardware bound
2. 🔐 Passphrase(s) - Secret only owner knows
3. 📧 Gmail - Registered email
4. 📱 Phone - Registered phone

SETUP:
    verifier = OwnerIdentityVerification()
    verifier.setup_owner_identity(
        passphrase="my_secret_123",
        gmail="owner@gmail.com",
        phone="+84912345678",
        passphrase_2="second_secret"  # Optional
    )

VERIFY:
    verified, message = verifier.verify_owner_full(
        passphrase="my_secret_123",
        gmail="owner@gmail.com",
        phone="+84912345678"
    )

CHECK SECRET ACCESS:
    can_reveal, message = verifier.can_reveal_secret(
        "password",
        passphrase="my_secret_123",
        gmail="owner@gmail.com",
        phone="+84912345678"
    )

If ANY credential is wrong → BLOCKED!
If wrong computer → BLOCKED!
3 wrong attempts → LOCKED OUT 10 minutes!
"""
