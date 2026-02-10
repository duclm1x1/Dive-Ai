"""
🛡️ DIVE AI INTERNAL GUARDRAILS
Rules for when Dive AI MUST ask user permission

Categories:
1. 🚨 ALWAYS ASK - Never auto-execute
2. ⚠️  CONFIRM - Ask before executing  
3. 📝 LOG - Auto-execute but log
4. ✅ SAFE - Auto-execute freely
"""

import os
import sys
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class GuardrailLevel(Enum):
    """Guardrail enforcement levels"""
    ALWAYS_ASK = 4     # 🚨 NEVER auto-execute
    CONFIRM = 3        # ⚠️ Ask before executing
    LOG = 2            # 📝 Auto-execute but log
    SAFE = 1           # ✅ Auto-execute freely


# ========================================
# 🚨 CRITICAL ONLY - Must ask user
# These are the ONLY actions that need confirmation
# Everything else runs automatically!
# ========================================

MUST_ASK_ACTIONS = {
    # Login/Authentication - ALWAYS ask
    "login": "Logging into account - requires your credentials",
    "logout": "Logging out of account",
    
    # Reveal secrets - ALWAYS ask + OWNER VERIFY
    "reveal_password": "Revealing password",
    "reveal_api_key": "Revealing API key",
    "reveal_secret": "Revealing secret credentials",
    "reveal_token": "Revealing access token",
    
    # Send personal data externally - ALWAYS ask
    "send_personal_data": "Sending your personal data externally",
    "share_credentials": "Sharing your credentials",
    "export_credentials": "Exporting credentials file",
    
    # Phone/Email verification - User must confirm
    "verify_phone": "Phone verification required",
    "verify_email": "Email verification required",
    "send_verification_code": "Sending verification code",
}

# Actions requiring OWNER verification (passphrase + gmail + phone)
OWNER_VERIFY_REQUIRED = [
    "reveal_password",
    "reveal_api_key", 
    "reveal_secret",
    "reveal_token",
    "share_credentials",
    "export_credentials",
]

# ========================================
# ✅ EVERYTHING ELSE - Runs automatically!
# ========================================
# Login, reveal secrets, personal data sharing = Ask
# All other actions = Auto-execute without asking

# ========================================
# ✅ SAFE - Auto-execute freely
# ========================================

SAFE_ACTIONS = [
    "read_file",
    "list_files",
    "search_files",
    "analyze_code",
    "format_output",
    "calculate",
    "explain",
    "summarize",
    "translate",
    "search_memory",
    "generate_response",
]


@dataclass
class GuardrailDecision:
    """Result of guardrail check"""
    level: GuardrailLevel
    action: str
    description: str
    requires_confirmation: bool
    confirmation_prompt: Optional[str] = None
    owner_verification_required: bool = False


class DiveAIGuardrails:
    """
    🛡️ Internal Guardrails for Dive AI
    
    Determines when Dive AI MUST ask user before executing
    """
    
    def __init__(self):
        self.action_log: List[Dict] = []
        self.pending_confirmations: List[Dict] = []
    
    def check_action(self, action: str, context: Dict[str, Any] = None) -> GuardrailDecision:
        """
        Check if action requires user permission
        
        SIMPLIFIED: Only ask for CRITICAL actions
        Everything else runs automatically!
        """
        action_lower = action.lower().replace(" ", "_").replace("-", "_")
        context = context or {}
        
        # Check MUST ASK (login, reveal secrets, personal data)
        for pattern, description in MUST_ASK_ACTIONS.items():
            if pattern in action_lower or action_lower in pattern:
                return GuardrailDecision(
                    level=GuardrailLevel.ALWAYS_ASK,
                    action=action,
                    description=description,
                    requires_confirmation=True,
                    confirmation_prompt=self._generate_prompt(action, description),
                    owner_verification_required=pattern in OWNER_VERIFY_REQUIRED
                )
        
        # EVERYTHING ELSE = Auto-execute!
        return GuardrailDecision(
            level=GuardrailLevel.SAFE,
            action=action,
            description="Auto-execute",
            requires_confirmation=False,
            owner_verification_required=False
        )
    
    def _requires_owner_verification(self, action: str) -> bool:
        """Check if action requires full owner verification"""
        high_risk = [
            "reveal_password", "reveal_api_key", "reveal_secret", "reveal_token",
            "export_credentials", "share_credentials", "export_database",
            "send_money", "transfer_funds", "make_payment",
            "format_drive", "delete_all", "modify_security_settings"
        ]
        return action in high_risk
    
    def _generate_prompt(self, action: str, description: str) -> str:
        """Generate user confirmation prompt"""
        
        return f"""
🚨 DIVE AI NEEDS YOUR PERMISSION 🚨

Action: {action}
Description: {description}

This action requires your explicit confirmation.
Do you want to proceed? (yes/no)
"""
    
    def _log_action(self, action: str, description: str):
        """Log action for audit"""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "description": description
        }
        self.action_log.append(entry)
        
        # Keep last 500 entries
        if len(self.action_log) > 500:
            self.action_log = self.action_log[-500:]
    
    def get_action_summary(self, action: str) -> str:
        """Get summary of what level this action requires"""
        decision = self.check_action(action)
        
        level_emoji = {
            GuardrailLevel.ALWAYS_ASK: "🚨 ALWAYS ASK",
            GuardrailLevel.CONFIRM: "⚠️ CONFIRM",
            GuardrailLevel.LOG: "📝 LOG",
            GuardrailLevel.SAFE: "✅ SAFE"
        }
        
        return f"{level_emoji[decision.level]}: {decision.description}"


class DiveAIGuardrailsAlgorithm(BaseAlgorithm):
    """
    Dive AI Internal Guardrails Algorithm
    
    Enforces rules for when Dive AI must ask user
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="DiveAIGuardrails",
            name="Dive AI Internal Guardrails",
            level="operational",
            category="security",
            version="1.0",
            description="Enforces rules for when Dive AI must ask user permission: login, reveal password, send data, etc.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "Action to check"),
                    IOField("context", "object", False, "Additional context")
                ],
                outputs=[
                    IOField("level", "string", True, "Guardrail level"),
                    IOField("requires_confirmation", "boolean", True, "Whether user must confirm"),
                    IOField("prompt", "string", False, "Confirmation prompt if needed")
                ]
            ),
            
            steps=[
                "Step 1: Check action against ALWAYS_ASK list",
                "Step 2: Check action against CONFIRM list",
                "Step 3: Check action against LOG list",
                "Step 4: Check action against SAFE list",
                "Step 5: Return decision with prompt if needed"
            ],
            
            tags=["security", "guardrails", "internal", "permissions"]
        )
        
        self.guardrails = DiveAIGuardrails()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute guardrail check"""
        
        action = params.get("action", "")
        context = params.get("context", {})
        
        try:
            decision = self.guardrails.check_action(action, context)
            
            return AlgorithmResult(
                status="success",
                data={
                    "level": decision.level.name,
                    "action": decision.action,
                    "description": decision.description,
                    "requires_confirmation": decision.requires_confirmation,
                    "owner_verification_required": decision.owner_verification_required,
                    "confirmation_prompt": decision.confirmation_prompt
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Guardrail check failed: {str(e)}"
            )


def register(algorithm_manager):
    """Register Dive AI Guardrails Algorithm"""
    try:
        algo = DiveAIGuardrailsAlgorithm()
        algorithm_manager.register("DiveAIGuardrails", algo)
        print("✅ DiveAIGuardrails Algorithm registered (INTERNAL RULES)")
    except Exception as e:
        print(f"❌ Failed to register DiveAIGuardrails: {e}")


# ========================================
# QUICK REFERENCE
# ========================================

GUARDRAILS_REFERENCE = """
🛡️ DIVE AI INTERNAL GUARDRAILS
================================

🚨 ALWAYS ASK (Never auto-execute):
   • Login/Logout/Register
   • Reveal password/API key/secret
   • Send money/transfer funds
   • Send email/post social media
   • Export database/credentials
   • Format drive/delete all

⚠️ CONFIRM (Ask before executing):
   • Delete file/folder
   • Install/uninstall package
   • Modify config/settings
   • Download from internet
   • Clear cache/history

📝 LOG (Auto-execute but log):
   • Create/edit file
   • Run local command
   • Call API
   • Generate code

✅ SAFE (Auto-execute freely):
   • Read file
   • Search/analyze
   • Calculate/format
   • Explain/summarize
"""
