"""
🛡️ DIVE GUARD - Unified Security System
Combines all security features into one module

STATUS: OFF by default (set ENABLED = True to activate)
"""

import os
import sys
import hashlib
import time
import json
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


# ========================================
# 🔴 MASTER SWITCH - Set to True to enable
# ========================================

ENABLED = False  # ⬅️ TURN THIS ON TO ACTIVATE DIVE GUARD


# ========================================
# CONFIGURATION
# ========================================

@dataclass
class DiveGuardConfig:
    """Configuration for Dive Guard"""
    
    # Master switch
    enabled: bool = ENABLED
    
    # Owner identity
    computer_id: Optional[str] = None
    computer_name: Optional[str] = None
    passphrase_hash: Optional[str] = None
    passphrase_2_hash: Optional[str] = None
    gmail_hash: Optional[str] = None
    phone_hash: Optional[str] = None
    owner_configured: bool = False
    
    # Security state
    failed_attempts: int = 0
    lockout_until: float = 0
    max_attempts: int = 3
    lockout_duration: int = 600  # 10 minutes


# ========================================
# ACTIONS THAT REQUIRE PERMISSION
# ========================================

MUST_ASK_ACTIONS = {
    # Login/Authentication
    "login": "Logging into account",
    "logout": "Logging out of account",
    
    # Reveal secrets
    "reveal_password": "Revealing password",
    "reveal_api_key": "Revealing API key",
    "reveal_secret": "Revealing secret",
    "reveal_token": "Revealing token",
    "share_credentials": "Sharing credentials",
    "export_credentials": "Exporting credentials",
    
    # Phone/Email verification
    "verify_phone": "Phone verification",
    "verify_email": "Email verification",
    
    # File system - DANGEROUS
    "format_drive": "Formatting drive - DESTRUCTIVE!",
    "delete_all": "Deleting all files",
    "delete_folder": "Deleting folder",
    "delete_system": "Deleting system files",
    "wipe_disk": "Wiping disk",
    "clear_data": "Clearing all data",
    
    # Payments
    "make_payment": "Making payment",
    "send_money": "Sending money",
    "transfer_funds": "Transferring funds",
    
    # Personal security & ID
    "share_personal": "Sharing personal information",
    "export_id": "Exporting ID/identity",
    "reveal_id": "Revealing identity info",
    "share_location": "Sharing location",
    "access_contacts": "Accessing contacts",
    "export_contacts": "Exporting contacts",
    "access_messages": "Accessing messages",
    "share_photos": "Sharing photos externally",
}

# Actions requiring full owner verification
OWNER_VERIFY_REQUIRED = [
    "reveal_password", "reveal_api_key", "reveal_secret",
    "reveal_token", "share_credentials", "export_credentials"
]


class DiveGuard:
    """
    🛡️ DIVE GUARD - Unified Security System
    
    Features:
    - Owner identity verification (Computer + Passphrase + Gmail + Phone)
    - Action guardrails (ask for login, reveal secrets)
    - Can be turned ON/OFF
    
    Usage:
        guard = DiveGuard()
        
        # Check if enabled
        if not guard.is_enabled():
            print("Dive Guard is OFF")
        
        # Check action
        allowed, msg = guard.check_action("reveal_password")
    """
    
    def __init__(self):
        self.config = DiveGuardConfig()
        self.security_log: List[Dict] = []
        self._config_file = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'config',
            'dive_guard.json'
        )
        self._load_config()
    
    # ========================================
    # MASTER SWITCH
    # ========================================
    
    def is_enabled(self) -> bool:
        """Check if Dive Guard is enabled"""
        return self.config.enabled
    
    def enable(self):
        """Enable Dive Guard"""
        self.config.enabled = True
        self._save_config()
        print("🛡️ DIVE GUARD: ENABLED")
    
    def disable(self):
        """Disable Dive Guard"""
        self.config.enabled = False
        self._save_config()
        print("🔴 DIVE GUARD: DISABLED")
    
    # ========================================
    # ACTION CHECK
    # ========================================
    
    def check_action(self, action: str, context: Dict = None) -> Tuple[bool, str]:
        """
        Check if action is allowed
        
        Returns:
            (allowed, message)
            
        If DISABLED: Always returns (True, "Dive Guard disabled")
        If ENABLED: Checks against guardrails
        """
        
        # If disabled, allow everything
        if not self.config.enabled:
            return True, "Dive Guard disabled - auto-execute"
        
        action_lower = action.lower().replace(" ", "_").replace("-", "_")
        
        # Check if requires asking
        for pattern, description in MUST_ASK_ACTIONS.items():
            if pattern in action_lower:
                # Check if needs owner verification
                if pattern in OWNER_VERIFY_REQUIRED:
                    return False, f"🔐 {description} - requires OWNER VERIFICATION"
                else:
                    return False, f"❓ {description} - requires your permission"
        
        # Everything else is allowed
        return True, "✅ Auto-execute"
    
    def verify_and_execute(
        self, 
        action: str, 
        passphrase: str = None,
        gmail: str = None,
        phone: str = None,
        passphrase_2: str = None
    ) -> Tuple[bool, str]:
        """
        Verify owner and check if action allowed
        
        For high-risk actions, requires full owner verification
        """
        
        if not self.config.enabled:
            return True, "Dive Guard disabled"
        
        # Check if action needs permission
        allowed, msg = self.check_action(action)
        
        if allowed:
            return True, msg
        
        # Needs verification - check credentials
        if not all([passphrase, gmail, phone]):
            return False, msg  # Return the "requires permission" message
        
        # Verify owner
        verified, verify_msg = self.verify_owner(passphrase, gmail, phone, passphrase_2)
        
        if verified:
            self._log_event("ACTION_APPROVED", f"{action} verified by owner")
            return True, f"✅ Owner verified - {action} approved"
        else:
            return False, verify_msg
    
    # ========================================
    # OWNER IDENTITY
    # ========================================
    
    def get_computer_id(self) -> str:
        """Generate computer fingerprint"""
        import platform
        import socket
        import uuid
        
        mac = format(uuid.getnode(), '012X')
        hostname = socket.gethostname()
        platform_str = platform.platform()
        
        fingerprint = f"{mac}:{hostname}:{platform_str}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:32]
    
    def setup_owner(
        self,
        passphrase: str,
        gmail: str,
        phone: str,
        passphrase_2: str = None
    ) -> Dict[str, Any]:
        """
        Setup owner identity (Computer + Passphrase + Gmail + Phone)
        """
        import socket
        
        if len(passphrase) < 6:
            return {"status": "error", "message": "Passphrase must be 6+ chars"}
        
        if "@" not in gmail:
            return {"status": "error", "message": "Invalid email"}
        
        if len(phone) < 10:
            return {"status": "error", "message": "Invalid phone"}
        
        # Store hashed values
        self.config.computer_id = self.get_computer_id()
        self.config.computer_name = socket.gethostname()
        self.config.passphrase_hash = hashlib.sha256(passphrase.encode()).hexdigest()
        self.config.gmail_hash = hashlib.sha256(gmail.lower().encode()).hexdigest()
        self.config.phone_hash = hashlib.sha256(phone.encode()).hexdigest()
        self.config.owner_configured = True
        
        if passphrase_2 and len(passphrase_2) >= 6:
            self.config.passphrase_2_hash = hashlib.sha256(passphrase_2.encode()).hexdigest()
        
        self._save_config()
        
        return {
            "status": "success",
            "computer": self.config.computer_name,
            "message": "Owner identity configured"
        }
    
    def verify_owner(
        self,
        passphrase: str,
        gmail: str,
        phone: str,
        passphrase_2: str = None
    ) -> Tuple[bool, str]:
        """
        Verify owner identity
        
        Checks: Computer + Passphrase + Gmail + Phone
        """
        
        if not self.config.owner_configured:
            return False, "Owner not configured"
        
        # Check lockout
        if self.config.lockout_until > time.time():
            remaining = int(self.config.lockout_until - time.time())
            return False, f"🔒 LOCKED OUT: {remaining}s remaining"
        
        # Verify computer
        if self.get_computer_id() != self.config.computer_id:
            self._log_event("WRONG_COMPUTER", "Access from different computer")
            return False, "🚨 Wrong computer!"
        
        # Verify passphrase
        if hashlib.sha256(passphrase.encode()).hexdigest() != self.config.passphrase_hash:
            self._handle_failed_attempt()
            return False, "❌ Wrong passphrase"
        
        # Verify passphrase 2 if configured
        if self.config.passphrase_2_hash:
            if not passphrase_2:
                return False, "❌ Second passphrase required"
            if hashlib.sha256(passphrase_2.encode()).hexdigest() != self.config.passphrase_2_hash:
                self._handle_failed_attempt()
                return False, "❌ Wrong second passphrase"
        
        # Verify gmail
        if hashlib.sha256(gmail.lower().encode()).hexdigest() != self.config.gmail_hash:
            self._handle_failed_attempt()
            return False, "❌ Wrong gmail"
        
        # Verify phone
        if hashlib.sha256(phone.encode()).hexdigest() != self.config.phone_hash:
            self._handle_failed_attempt()
            return False, "❌ Wrong phone"
        
        # Success!
        self.config.failed_attempts = 0
        self._log_event("OWNER_VERIFIED", "Full verification successful")
        return True, "✅ Owner verified"
    
    def _handle_failed_attempt(self):
        """Handle failed verification attempt"""
        self.config.failed_attempts += 1
        
        if self.config.failed_attempts >= self.config.max_attempts:
            self.config.lockout_until = time.time() + self.config.lockout_duration
            self._log_event("LOCKOUT", "Too many failed attempts")
    
    # ========================================
    # CONFIG & LOGGING
    # ========================================
    
    def _log_event(self, event_type: str, details: str):
        """Log security event"""
        self.security_log.append({
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        })
    
    def _save_config(self):
        """Save config to file"""
        os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        
        config_data = {
            "enabled": self.config.enabled,
            "computer_id": self.config.computer_id,
            "computer_name": self.config.computer_name,
            "passphrase_hash": self.config.passphrase_hash,
            "passphrase_2_hash": self.config.passphrase_2_hash,
            "gmail_hash": self.config.gmail_hash,
            "phone_hash": self.config.phone_hash,
            "owner_configured": self.config.owner_configured
        }
        
        with open(self._config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def _load_config(self):
        """Load config from file"""
        if not os.path.exists(self._config_file):
            return
        
        try:
            with open(self._config_file, 'r') as f:
                data = json.load(f)
            
            self.config.enabled = data.get("enabled", False)
            self.config.computer_id = data.get("computer_id")
            self.config.computer_name = data.get("computer_name")
            self.config.passphrase_hash = data.get("passphrase_hash")
            self.config.passphrase_2_hash = data.get("passphrase_2_hash")
            self.config.gmail_hash = data.get("gmail_hash")
            self.config.phone_hash = data.get("phone_hash")
            self.config.owner_configured = data.get("owner_configured", False)
        except:
            pass
    
    def status(self) -> str:
        """Get current status"""
        if not self.config.enabled:
            return "🔴 DIVE GUARD: DISABLED"
        
        if self.config.owner_configured:
            return f"🛡️ DIVE GUARD: ENABLED (Owner: {self.config.computer_name})"
        else:
            return "🛡️ DIVE GUARD: ENABLED (Owner not configured)"


# ========================================
# QUICK ACCESS
# ========================================

# Global instance
_guard = None

def get_guard() -> DiveGuard:
    """Get global Dive Guard instance"""
    global _guard
    if _guard is None:
        _guard = DiveGuard()
    return _guard

def is_enabled() -> bool:
    """Quick check if enabled"""
    return get_guard().is_enabled()

def check(action: str) -> Tuple[bool, str]:
    """Quick action check"""
    return get_guard().check_action(action)


# ========================================
# REFERENCE
# ========================================

"""
🛡️ DIVE GUARD - Quick Reference

STATUS: Currently OFF (ENABLED = False)

To ENABLE:
    from core.algorithms.operational.dive_guard import get_guard
    guard = get_guard()
    guard.enable()

To DISABLE:
    guard.disable()

To SETUP OWNER:
    guard.setup_owner(
        passphrase="my_secret",
        gmail="owner@gmail.com",
        phone="+84912345678",
        passphrase_2="optional_second"
    )

To CHECK ACTION:
    allowed, msg = guard.check_action("reveal_password")

To VERIFY AND EXECUTE:
    allowed, msg = guard.verify_and_execute(
        "reveal_password",
        passphrase="my_secret",
        gmail="owner@gmail.com",
        phone="+84912345678"
    )

ACTIONS THAT REQUIRE PERMISSION (when ENABLED):
- login, logout
- reveal_password, reveal_api_key, reveal_secret, reveal_token
- share_credentials, export_credentials
- verify_phone, verify_email

EVERYTHING ELSE: Auto-execute!
"""
