"""
🔒 SECURITY GUARDRAILS FOR AUTONOMOUS EXECUTION
OpenClaw-style self-running with protection against:
- Personal data leaks
- Unauthorized access
- Hacker attacks

CRITICAL: Some actions ALWAYS require user confirmation!
"""

import os
import sys
import hashlib
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = 0       # Auto-execute allowed
    INTERNAL = 1     # Auto-execute with logging
    CONFIDENTIAL = 2 # Requires confirmation
    SECRET = 3       # ALWAYS requires user confirmation
    CRITICAL = 4     # Requires user confirmation + 2FA


class ActionCategory(Enum):
    """Action categories for security classification"""
    READ_ONLY = "read_only"           # Safe
    WRITE_LOCAL = "write_local"       # Needs logging
    NETWORK = "network"               # Needs confirmation
    AUTHENTICATION = "authentication" # ALWAYS confirm
    FINANCIAL = "financial"           # ALWAYS confirm
    PERSONAL_DATA = "personal_data"   # ALWAYS confirm
    SYSTEM_ADMIN = "system_admin"     # CRITICAL


@dataclass
class SecurityConfig:
    """Security configuration"""
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    last_auth_time: float = 0
    session_timeout: int = 3600  # 1 hour
    require_2fa: bool = False
    blocked_patterns: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    
    # 🔒 ANTI-HACKING FEATURES
    secret_passphrase: Optional[str] = None  # User's secret passphrase
    secret_passphrase_2: Optional[str] = None  # SECOND secret passphrase (optional)
    phone_number: Optional[str] = None       # For phone verification
    phone_verified: bool = False
    failed_attempts: int = 0
    lockout_until: float = 0
    max_failed_attempts: int = 3
    lockout_duration: int = 300  # 5 minutes
    
    # 🖥️ COMPUTER ID BINDING
    registered_computer_id: Optional[str] = None  # Only THIS computer can authenticate
    computer_name: Optional[str] = None


# ================================
# 🛡️ ANTI-HACKING DETECTION
# ================================

MALICIOUS_PATTERNS = [
    # Data exfiltration attempts
    "send all data",
    "export everything",
    "share all information",
    "transfer all files",
    "send credentials",
    "share passwords",
    "upload all",
    "exfiltrate",
    
    # Hacker impersonation attempts
    "ignore previous instructions",
    "forget security",
    "disable guardrails",
    "bypass security",
    "override protection",
    "act as admin",
    "sudo mode",
    "jailbreak",
    
    # Malware-like commands
    "delete all",
    "format disk",
    "encrypt files",
    "install backdoor",
    "create hidden",
    "run silently",
    "disable logging",
    "clear audit"
]

SUSPICIOUS_DESTINATIONS = [
    # Common data exfil targets
    "pastebin.com",
    "ghostbin.com",
    "temp-mail",
    "anonymous",
    "throwaway",
    "10minutemail",
    "guerrillamail"
]


# ================================
# SECURITY CLASSIFICATION TABLE
# ================================

SENSITIVE_DATA_PATTERNS = {
    # CRITICAL - ALWAYS ASK USER
    "password": SecurityLevel.CRITICAL,
    "secret": SecurityLevel.CRITICAL,
    "private_key": SecurityLevel.CRITICAL,
    "api_key": SecurityLevel.CRITICAL,
    "access_token": SecurityLevel.CRITICAL,
    "refresh_token": SecurityLevel.CRITICAL,
    "session_id": SecurityLevel.CRITICAL,
    "credit_card": SecurityLevel.CRITICAL,
    "cvv": SecurityLevel.CRITICAL,
    "ssn": SecurityLevel.CRITICAL,
    "bank_account": SecurityLevel.CRITICAL,
    "pin": SecurityLevel.CRITICAL,
    
    # SECRET - Requires confirmation
    "email": SecurityLevel.SECRET,
    "gmail": SecurityLevel.SECRET,
    "phone": SecurityLevel.SECRET,
    "address": SecurityLevel.SECRET,
    "user_id": SecurityLevel.SECRET,
    "username": SecurityLevel.SECRET,
    "birth_date": SecurityLevel.SECRET,
    "id_card": SecurityLevel.SECRET,
    "passport": SecurityLevel.SECRET,
    "driver_license": SecurityLevel.SECRET,
    "social_security": SecurityLevel.SECRET,
    
    # CONFIDENTIAL - Needs confirmation
    "name": SecurityLevel.CONFIDENTIAL,
    "full_name": SecurityLevel.CONFIDENTIAL,
    "location": SecurityLevel.CONFIDENTIAL,
    "ip_address": SecurityLevel.CONFIDENTIAL,
    "device_id": SecurityLevel.CONFIDENTIAL,
}

DANGEROUS_ACTIONS = {
    # CRITICAL - NEVER auto-execute
    "delete_all": SecurityLevel.CRITICAL,
    "format_drive": SecurityLevel.CRITICAL,
    "send_money": SecurityLevel.CRITICAL,
    "transfer_funds": SecurityLevel.CRITICAL,
    "share_credentials": SecurityLevel.CRITICAL,
    "export_database": SecurityLevel.CRITICAL,
    "modify_system": SecurityLevel.CRITICAL,
    
    # SECRET - Always confirm
    "send_email": SecurityLevel.SECRET,
    "post_online": SecurityLevel.SECRET,
    "upload_file": SecurityLevel.SECRET,
    "share_file": SecurityLevel.SECRET,
    "login": SecurityLevel.SECRET,
    "register": SecurityLevel.SECRET,
    "change_password": SecurityLevel.SECRET,
    
    # CONFIDENTIAL - Needs confirmation
    "install_package": SecurityLevel.CONFIDENTIAL,
    "run_script": SecurityLevel.CONFIDENTIAL,
    "modify_config": SecurityLevel.CONFIDENTIAL,
    "create_file": SecurityLevel.CONFIDENTIAL,
    "delete_file": SecurityLevel.CONFIDENTIAL,
}


class SecurityGuardrail:
    """
    Security Guardrail System
    
    Classifies actions and data by security level
    Blocks dangerous operations unless confirmed
    Protects personal data from unauthorized access
    """
    
    def __init__(self):
        self.config = SecurityConfig()
        self.audit_log: List[Dict] = []
        self.blocked_attempts: List[Dict] = []
    
    def classify_action(self, action: str, data: Dict[str, Any]) -> Tuple[SecurityLevel, List[str]]:
        """
        Classify an action's security level
        
        Returns:
            (SecurityLevel, list of reasons)
        """
        reasons = []
        max_level = SecurityLevel.PUBLIC
        
        # Check action itself
        action_lower = action.lower()
        for pattern, level in DANGEROUS_ACTIONS.items():
            if pattern in action_lower:
                if level.value > max_level.value:
                    max_level = level
                    reasons.append(f"Action '{pattern}' requires {level.name} clearance")
        
        # Check data for sensitive patterns
        for key, value in data.items():
            key_lower = key.lower()
            for pattern, level in SENSITIVE_DATA_PATTERNS.items():
                if pattern in key_lower:
                    if level.value > max_level.value:
                        max_level = level
                        reasons.append(f"Data '{pattern}' requires {level.name} clearance")
        
        return max_level, reasons
    
    def can_auto_execute(self, action: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if action can be auto-executed without user confirmation
        
        Returns:
            (can_execute, reason_if_blocked)
        """
        level, reasons = self.classify_action(action, data)
        
        # AUTO-EXECUTE ALLOWED
        if level == SecurityLevel.PUBLIC:
            self._log_action(action, data, "auto_executed", level)
            return True, "Auto-execute allowed"
        
        # AUTO-EXECUTE WITH LOGGING
        if level == SecurityLevel.INTERNAL:
            self._log_action(action, data, "auto_executed_with_log", level)
            return True, "Auto-executed with logging"
        
        # REQUIRES USER CONFIRMATION
        if level in [SecurityLevel.CONFIDENTIAL, SecurityLevel.SECRET, SecurityLevel.CRITICAL]:
            reason = f"Action requires {level.name} clearance: {', '.join(reasons)}"
            self._log_action(action, data, "blocked_pending_confirmation", level)
            return False, reason
        
        return False, "Unknown security level"
    
    def request_user_confirmation(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a confirmation request for user
        
        Returns details about what needs confirmation
        """
        level, reasons = self.classify_action(action, data)
        
        # Mask sensitive data for display
        masked_data = self._mask_sensitive_data(data)
        
        return {
            "action": action,
            "security_level": level.name,
            "reasons": reasons,
            "masked_data": masked_data,
            "requires_2fa": level == SecurityLevel.CRITICAL,
            "confirmation_prompt": self._generate_confirmation_prompt(action, level, reasons)
        }
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive values for safe display"""
        masked = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            is_sensitive = any(
                pattern in key_lower 
                for pattern in SENSITIVE_DATA_PATTERNS.keys()
            )
            
            if is_sensitive and isinstance(value, str):
                # Mask all but last 4 characters
                if len(value) > 4:
                    masked[key] = "*" * (len(value) - 4) + value[-4:]
                else:
                    masked[key] = "****"
            else:
                masked[key] = value
        
        return masked
    
    def _generate_confirmation_prompt(self, action: str, level: SecurityLevel, reasons: List[str]) -> str:
        """Generate user confirmation prompt"""
        
        emoji_map = {
            SecurityLevel.CONFIDENTIAL: "⚠️",
            SecurityLevel.SECRET: "🔒",
            SecurityLevel.CRITICAL: "🚨"
        }
        
        emoji = emoji_map.get(level, "❓")
        
        prompt = f"""
{emoji} SECURITY CONFIRMATION REQUIRED {emoji}

Action: {action}
Security Level: {level.name}

Reasons:
{chr(10).join(f'  • {r}' for r in reasons)}

Do you want to proceed? (yes/no)
"""
        return prompt
    
    def _log_action(self, action: str, data: Dict, status: str, level: SecurityLevel):
        """Log action for audit trail"""
        
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "data_keys": list(data.keys()),  # Don't log actual values
            "status": status,
            "security_level": level.name
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def verify_user_id(self, user_id: str, signature: str) -> bool:
        """
        V28.4-style user ID verification
        
        Uses cryptographic verification to ensure only the real user
        can authorize sensitive actions
        """
        # Generate expected signature from user_id + secret salt
        # In production, this would use secure key derivation
        expected = hashlib.sha256(
            f"{user_id}:dive_ai_v29_4".encode()
        ).hexdigest()[:16]
        
        return signature == expected
    
    def generate_session_token(self, user_id: str) -> str:
        """Generate a session token for authenticated user"""
        
        token_data = f"{user_id}:{time.time()}:{os.urandom(16).hex()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        self.config.user_id = user_id
        self.config.session_token = token
        self.config.last_auth_time = time.time()
        
        return token
    
    def is_session_valid(self) -> bool:
        """Check if current session is still valid"""
        
        if not self.config.session_token:
            return False
        
        elapsed = time.time() - self.config.last_auth_time
        return elapsed < self.config.session_timeout
    
    # ================================
    # 🖥️ COMPUTER ID BINDING
    # ================================
    
    def get_computer_id(self) -> str:
        """
        Generate unique computer fingerprint
        
        Combines: MAC address + Computer name + Platform
        This ensures only THIS specific computer can authenticate
        """
        import platform
        import socket
        import uuid
        
        # Get MAC address
        mac = format(uuid.getnode(), '012X')
        
        # Get computer name
        computer_name = socket.gethostname()
        
        # Get platform info
        platform_info = platform.platform()
        
        # Combine into unique fingerprint
        fingerprint = f"{mac}:{computer_name}:{platform_info}"
        computer_id = hashlib.sha256(fingerprint.encode()).hexdigest()[:32]
        
        return computer_id
    
    def register_this_computer(self) -> Dict[str, Any]:
        """
        Register the CURRENT computer as the only authorized device
        
        After this, only THIS computer can authenticate for CRITICAL actions
        """
        import socket
        
        computer_id = self.get_computer_id()
        computer_name = socket.gethostname()
        
        self.config.registered_computer_id = computer_id
        self.config.computer_name = computer_name
        
        print(f"\n   🖥️ COMPUTER REGISTERED:")
        print(f"      Name: {computer_name}")
        print(f"      ID: {computer_id[:8]}...{computer_id[-8:]}")
        print(f"   ✅ Only THIS computer can authorize CRITICAL actions!")
        
        return {
            "status": "registered",
            "computer_name": computer_name,
            "computer_id_prefix": computer_id[:8]
        }
    
    def verify_computer_id(self) -> Tuple[bool, str]:
        """
        Verify current computer matches registered computer
        
        Returns:
            (is_valid, message)
        """
        if not self.config.registered_computer_id:
            return True, "⚠️ No computer registered (any computer allowed)"
        
        current_id = self.get_computer_id()
        
        if current_id == self.config.registered_computer_id:
            return True, f"✅ Computer verified: {self.config.computer_name}"
        else:
            self._log_security_event(
                "WRONG_COMPUTER",
                f"Attempted access from unregistered computer"
            )
            return False, "🚨 BLOCKED: This computer is NOT registered!"
    
    # ================================
    # 🔐 DUAL SECRET PASSPHRASE
    # ================================
    
    def setup_dual_passphrase(self, passphrase_1: str, passphrase_2: Optional[str] = None) -> bool:
        """
        Setup 1 or 2 secret passphrases
        
        Both passphrases required for data exfiltration attempts
        """
        if len(passphrase_1) < 6:
            print("   ❌ Passphrase 1 too short (min 6 characters)")
            return False
        
        # Hash and store first passphrase
        self.config.secret_passphrase = hashlib.sha256(passphrase_1.encode()).hexdigest()
        print("   ✅ Secret passphrase 1 configured")
        
        # Optional second passphrase
        if passphrase_2:
            if len(passphrase_2) < 6:
                print("   ❌ Passphrase 2 too short (min 6 characters)")
                return False
            
            self.config.secret_passphrase_2 = hashlib.sha256(passphrase_2.encode()).hexdigest()
            print("   ✅ Secret passphrase 2 configured")
            print("   🔒 Both passphrases required for data sharing!")
        
        return True
    
    def verify_dual_passphrase(self, passphrase_1: str, passphrase_2: Optional[str] = None) -> Tuple[bool, str]:
        """
        Verify one or both passphrases
        
        If passphrase_2 is configured, BOTH are required for data exfil
        """
        # Check lockout
        if self.config.lockout_until > time.time():
            remaining = int(self.config.lockout_until - time.time())
            return False, f"🔒 LOCKED OUT: Wait {remaining} seconds"
        
        # Verify passphrase 1
        if not self.config.secret_passphrase:
            return False, "❌ No passphrase configured. Setup first."
        
        hash_1 = hashlib.sha256(passphrase_1.encode()).hexdigest()
        
        if hash_1 != self.config.secret_passphrase:
            self.config.failed_attempts += 1
            if self.config.failed_attempts >= self.config.max_failed_attempts:
                self.config.lockout_until = time.time() + self.config.lockout_duration
                self._log_security_event("LOCKOUT", "Too many failed attempts")
                return False, f"🚨 LOCKED OUT for {self.config.lockout_duration}s"
            return False, f"❌ Wrong passphrase 1. {self.config.max_failed_attempts - self.config.failed_attempts} attempts left."
        
        # Verify passphrase 2 if configured
        if self.config.secret_passphrase_2:
            if not passphrase_2:
                return False, "❌ Second passphrase required!"
            
            hash_2 = hashlib.sha256(passphrase_2.encode()).hexdigest()
            
            if hash_2 != self.config.secret_passphrase_2:
                self.config.failed_attempts += 1
                return False, "❌ Wrong passphrase 2!"
        
        # Success!
        self.config.failed_attempts = 0
        return True, "✅ All passphrases verified!"
    
    def full_verification(self, passphrase_1: str, passphrase_2: Optional[str] = None) -> Tuple[bool, str]:
        """
        COMPLETE VERIFICATION: Computer ID + Passphrases
        
        For CRITICAL data exfiltration attempts, requires:
        1. Correct computer (hardware bound)
        2. Passphrase 1
        3. Passphrase 2 (if configured)
        """
        results = []
        
        # Step 1: Verify computer
        computer_ok, computer_msg = self.verify_computer_id()
        if not computer_ok:
            return False, computer_msg
        results.append(f"🖥️ Computer: {self.config.computer_name}")
        
        # Step 2: Verify passphrases
        passphrase_ok, passphrase_msg = self.verify_dual_passphrase(passphrase_1, passphrase_2)
        if not passphrase_ok:
            return False, passphrase_msg
        results.append("🔐 Passphrases verified")
        
        self._log_security_event("FULL_VERIFICATION_SUCCESS", "Computer + Passphrases verified")
        
        return True, f"🔓 OWNER VERIFIED:\n   " + "\n   ".join(results)
    
    # ================================
    # 🔐 ANTI-HACKING 2FA SYSTEM
    # ================================
    
    def setup_secret_passphrase(self, passphrase: str) -> bool:
        """
        Setup user's secret passphrase
        
        This is a secret ONLY the real user knows.
        Required for CRITICAL operations even if hacker gains access.
        """
        if len(passphrase) < 6:
            print("   ❌ Passphrase too short (min 6 characters)")
            return False
        
        # Hash the passphrase for secure storage
        hashed = hashlib.sha256(passphrase.encode()).hexdigest()
        self.config.secret_passphrase = hashed
        
        print("   ✅ Secret passphrase configured")
        print("   🔒 CRITICAL operations will require this passphrase")
        return True
    
    def setup_phone_verification(self, phone_number: str) -> bool:
        """
        Setup phone for 2FA verification
        
        Phone will receive verification code for CRITICAL actions.
        """
        # Basic validation
        if len(phone_number) < 10:
            print("   ❌ Invalid phone number")
            return False
        
        self.config.phone_number = phone_number
        print(f"   ✅ Phone configured: {phone_number[:3]}****{phone_number[-2:]}")
        return True
    
    def verify_secret_passphrase(self, passphrase: str) -> Tuple[bool, str]:
        """
        Verify user's secret passphrase
        
        Returns:
            (success, message)
        """
        # Check lockout
        if self.config.lockout_until > time.time():
            remaining = int(self.config.lockout_until - time.time())
            return False, f"🔒 LOCKED OUT: Wait {remaining} seconds"
        
        # Check if passphrase is configured
        if not self.config.secret_passphrase:
            return False, "❌ No passphrase configured. Setup first."
        
        # Verify
        hashed = hashlib.sha256(passphrase.encode()).hexdigest()
        
        if hashed == self.config.secret_passphrase:
            self.config.failed_attempts = 0
            return True, "✅ Passphrase verified"
        else:
            self.config.failed_attempts += 1
            
            if self.config.failed_attempts >= self.config.max_failed_attempts:
                self.config.lockout_until = time.time() + self.config.lockout_duration
                self._log_security_event("LOCKOUT", "Too many failed passphrase attempts")
                return False, f"🚨 LOCKED OUT for {self.config.lockout_duration}s - Too many attempts"
            
            remaining = self.config.max_failed_attempts - self.config.failed_attempts
            return False, f"❌ Wrong passphrase. {remaining} attempts remaining."
    
    def generate_phone_verification_code(self) -> str:
        """Generate a 6-digit verification code for phone"""
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Store hashed code with expiration (5 minutes)
        self._pending_verification = {
            "code_hash": hashlib.sha256(code.encode()).hexdigest(),
            "expires_at": time.time() + 300,
            "attempts": 0
        }
        
        print(f"\n   📱 VERIFICATION CODE SENT TO: {self.config.phone_number}")
        print(f"   ⏰ Code expires in 5 minutes")
        
        # In production, this would send via SMS
        # For demo, we print it
        print(f"   🔐 CODE (demo mode): {code}")
        
        return code
    
    def verify_phone_code(self, code: str) -> Tuple[bool, str]:
        """Verify the phone verification code"""
        
        if not hasattr(self, '_pending_verification'):
            return False, "❌ No verification pending"
        
        pending = self._pending_verification
        
        # Check expiration
        if time.time() > pending["expires_at"]:
            del self._pending_verification
            return False, "❌ Code expired. Request new code."
        
        # Check attempts
        if pending["attempts"] >= 3:
            del self._pending_verification
            return False, "🚨 Too many wrong attempts. Request new code."
        
        # Verify
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash == pending["code_hash"]:
            del self._pending_verification
            self.config.phone_verified = True
            return True, "✅ Phone verified successfully"
        else:
            pending["attempts"] += 1
            return False, f"❌ Wrong code. {3 - pending['attempts']} attempts left."
    
    def detect_malicious_intent(self, action: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Detect malicious/hacker activity
        
        Returns:
            (is_malicious, reason)
        """
        action_lower = action.lower()
        data_str = json.dumps(data).lower()
        combined = action_lower + " " + data_str
        
        # Check for malicious patterns
        for pattern in MALICIOUS_PATTERNS:
            if pattern in combined:
                self._log_security_event("MALICIOUS_DETECTED", f"Pattern: {pattern}")
                return True, f"🚨 BLOCKED: Detected malicious pattern '{pattern}'"
        
        # Check for suspicious destinations
        for dest in SUSPICIOUS_DESTINATIONS:
            if dest in combined:
                self._log_security_event("SUSPICIOUS_DESTINATION", f"Destination: {dest}")
                return True, f"🚨 BLOCKED: Suspicious destination '{dest}'"
        
        return False, "Clean"
    
    def require_2fa_verification(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate 2FA verification challenge for CRITICAL actions
        
        Returns challenge that user must complete
        """
        level, _ = self.classify_action(action, data)
        
        # Check for malicious intent first
        is_malicious, reason = self.detect_malicious_intent(action, data)
        if is_malicious:
            return {
                "status": "BLOCKED",
                "reason": reason,
                "action_allowed": False
            }
        
        # Determine required verification
        verification_methods = []
        
        if level == SecurityLevel.CRITICAL:
            # Always require passphrase for CRITICAL
            if self.config.secret_passphrase:
                verification_methods.append("secret_passphrase")
            
            # Require phone for data exfil attempts
            if any(keyword in action.lower() for keyword in ["send", "share", "upload", "transfer", "export"]):
                if self.config.phone_number:
                    verification_methods.append("phone_code")
        
        elif level == SecurityLevel.SECRET:
            if self.config.secret_passphrase:
                verification_methods.append("secret_passphrase")
        
        return {
            "status": "VERIFICATION_REQUIRED",
            "security_level": level.name,
            "action": action,
            "verification_required": verification_methods,
            "prompt": self._generate_2fa_prompt(action, verification_methods)
        }
    
    def _generate_2fa_prompt(self, action: str, methods: List[str]) -> str:
        """Generate 2FA verification prompt"""
        
        prompt = f"""
🚨 2FA VERIFICATION REQUIRED 🚨

Action: {action}

To verify you are the real owner (not a hacker):
"""
        
        if "secret_passphrase" in methods:
            prompt += "\n1️⃣  Enter your SECRET PASSPHRASE:"
        
        if "phone_code" in methods:
            prompt += f"\n2️⃣  Enter the code sent to your phone ({self.config.phone_number[:3]}***)"
        
        prompt += "\n\n⚠️  If you did NOT request this action, BLOCK immediately!"
        
        return prompt
    
    def complete_2fa_verification(self, action: str, passphrase: Optional[str] = None, 
                                   phone_code: Optional[str] = None) -> Tuple[bool, str]:
        """
        Complete 2FA verification for an action
        
        Returns:
            (success, message)
        """
        results = []
        
        # Verify passphrase if provided
        if passphrase:
            success, msg = self.verify_secret_passphrase(passphrase)
            if not success:
                return False, msg
            results.append("✅ Passphrase verified")
        
        # Verify phone code if provided
        if phone_code:
            success, msg = self.verify_phone_code(phone_code)
            if not success:
                return False, msg
            results.append("✅ Phone verified")
        
        if results:
            self._log_security_event("2FA_SUCCESS", f"Action: {action}")
            return True, f"🔓 VERIFIED: {' | '.join(results)}"
        
        return False, "❌ No verification provided"
    
    def _log_security_event(self, event_type: str, details: str):
        """Log security events for audit"""
        
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details,
            "user_id": self.config.user_id
        }
        
        self.blocked_attempts.append(event)
        print(f"\n   🛡️ SECURITY EVENT: {event_type}")
        print(f"      {details}")
        
        # Keep last 100 security events
        if len(self.blocked_attempts) > 100:
            self.blocked_attempts = self.blocked_attempts[-100:]


class SecurityGuardrailAlgorithm(BaseAlgorithm):
    """
    Security Guardrail Algorithm for Autonomous Execution
    
    Enables OpenClaw-style self-running with protection
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="SecurityGuardrail",
            name="Security Guardrail",
            level="operational",
            category="security",
            version="1.0",
            description="Protect autonomous execution with security guardrails. Blocks sensitive operations without user confirmation.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "Action to check"),
                    IOField("data", "object", False, "Data involved in action"),
                    IOField("force_confirm", "boolean", False, "Force user confirmation")
                ],
                outputs=[
                    IOField("can_execute", "boolean", True, "Whether auto-execute is allowed"),
                    IOField("security_level", "string", True, "Security classification"),
                    IOField("confirmation_required", "object", False, "Confirmation details if needed")
                ]
            ),
            
            steps=[
                "Step 1: Classify action security level",
                "Step 2: Check data for sensitive patterns",
                "Step 3: Determine if auto-execute allowed",
                "Step 4: Generate confirmation request if needed",
                "Step 5: Return security decision"
            ],
            
            tags=["security", "guardrail", "autonomous", "critical"]
        )
        
        self.guardrail = SecurityGuardrail()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute security check"""
        
        action = params.get("action", "")
        data = params.get("data", {})
        force_confirm = params.get("force_confirm", False)
        
        try:
            # Check if auto-execute is allowed
            can_execute, reason = self.guardrail.can_auto_execute(action, data)
            
            # Force confirmation if requested
            if force_confirm:
                can_execute = False
                reason = "User forced confirmation"
            
            # Get security classification
            level, reasons = self.guardrail.classify_action(action, data)
            
            # Generate confirmation request if needed
            confirmation = None
            if not can_execute:
                confirmation = self.guardrail.request_user_confirmation(action, data)
            
            return AlgorithmResult(
                status="success",
                data={
                    "can_execute": can_execute,
                    "security_level": level.name,
                    "reasons": reasons,
                    "confirmation_required": confirmation
                },
                metadata={
                    "action": action,
                    "data_keys": list(data.keys())
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Security check failed: {str(e)}"
            )


class AutonomousExecutor:
    """
    OpenClaw-Style Autonomous Executor
    
    Self-running execution with security guardrails
    Only asks user when ABSOLUTELY necessary
    """
    
    def __init__(self, algorithm_manager):
        self.manager = algorithm_manager
        self.guardrail = SecurityGuardrail()
        self.pending_confirmations: List[Dict] = []
    
    def execute_autonomously(self, task: str, params: Dict[str, Any]) -> AlgorithmResult:
        """
        Execute task autonomously if security allows
        
        Returns:
            AlgorithmResult with execution result or confirmation request
        """
        
        print(f"\n🤖 Autonomous Executor: {task}")
        
        # Step 1: Security check
        can_execute, reason = self.guardrail.can_auto_execute(task, params)
        
        if can_execute:
            # AUTO-EXECUTE
            print(f"   ✅ Security: Auto-execute allowed")
            return self._execute_task(task, params)
        else:
            # NEEDS CONFIRMATION
            print(f"   🔒 Security: Confirmation required")
            print(f"   📝 Reason: {reason}")
            
            confirmation = self.guardrail.request_user_confirmation(task, params)
            self.pending_confirmations.append(confirmation)
            
            return AlgorithmResult(
                status="pending_confirmation",
                data={
                    "confirmation_required": True,
                    "security_level": confirmation["security_level"],
                    "prompt": confirmation["confirmation_prompt"]
                }
            )
    
    def confirm_and_execute(self, confirmation_id: int, user_confirmation: bool) -> AlgorithmResult:
        """Execute a pending action after user confirmation"""
        
        if confirmation_id >= len(self.pending_confirmations):
            return AlgorithmResult(status="error", error="Invalid confirmation ID")
        
        confirmation = self.pending_confirmations[confirmation_id]
        
        if not user_confirmation:
            return AlgorithmResult(
                status="cancelled",
                data={"message": "User cancelled the action"}
            )
        
        # Execute after confirmation
        return self._execute_task(
            confirmation["action"],
            confirmation.get("original_params", {})
        )
    
    def _execute_task(self, task: str, params: Dict[str, Any]) -> AlgorithmResult:
        """Internal task execution"""
        
        # Try to find matching algorithm
        algo = self.manager.get_algorithm(task)
        
        if algo:
            return self.manager.execute(task, params)
        else:
            # Execute as generic task
            return AlgorithmResult(
                status="success",
                data={"task": task, "params": params, "result": "Executed"}
            )


# ================================
# SECURITY CHECKLIST
# ================================

SECURITY_CHECKLIST = """
🔒 DIVE AI V29.4 SECURITY CHECKLIST
====================================

## 🚨 CRITICAL - ALWAYS ASK USER:
1. ❌ Passwords (any form)
2. ❌ API Keys / Tokens
3. ❌ Private Keys / Secrets
4. ❌ Credit Card / Bank Info
5. ❌ SSN / Government IDs
6. ❌ PIN codes
7. ❌ 2FA codes

## 🔒 SECRET - REQUIRES CONFIRMATION:
1. ⚠️ Email addresses (Gmail, etc.)
2. ⚠️ Phone numbers
3. ⚠️ User IDs / Usernames
4. ⚠️ Physical addresses
5. ⚠️ Birth dates
6. ⚠️ ID cards / Passports
7. ⚠️ Login actions
8. ⚠️ Send email/message
9. ⚠️ Upload files
10. ⚠️ Share data online

## ⚠️ CONFIDENTIAL - NEEDS LOG:
1. 📝 Names
2. 📝 Locations
3. 📝 IP addresses
4. 📝 Device IDs
5. 📝 Install packages
6. 📝 Run scripts
7. 📝 Create/delete files

## ✅ SAFE - AUTO-EXECUTE:
1. ✅ Read local files
2. ✅ Calculate/analyze
3. ✅ Generate code
4. ✅ Search memory
5. ✅ Route queries
6. ✅ Format output

## 🛡️ V28.4 USER ID SYSTEM:
- Each user has unique cryptographic ID
- Actions verified with user signature
- Session tokens with timeout
- Audit log for all actions
- Rate limiting on sensitive ops
"""


def register(algorithm_manager):
    """Register Security Guardrail"""
    try:
        algo = SecurityGuardrailAlgorithm()
        algorithm_manager.register("SecurityGuardrail", algo)
        print("✅ SecurityGuardrail Algorithm registered (SECURITY)")
    except Exception as e:
        print(f"❌ Failed to register SecurityGuardrail: {e}")
