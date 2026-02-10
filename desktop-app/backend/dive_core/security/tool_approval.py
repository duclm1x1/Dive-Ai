"""
Dive AI — Tool Approval System
Surpass Feature #5: Risk-based human-in-the-loop for dangerous operations.

OpenClaw requires blanket approval. Dive AI adds:
  - 3-tier risk classification: LOW (auto), MEDIUM (log), HIGH (require approval)
  - Pattern-based risk scoring with explanations
  - Auto-approve whitelist per session
  - Approval queue with configurable timeout
  - Full audit trail integration
"""

import re
import time
import uuid
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Callable
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"         # Auto-approve
    MEDIUM = "medium"   # Log and proceed
    HIGH = "high"       # Require explicit approval


@dataclass
class ApprovalRequest:
    """A pending tool approval request."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str = ""
    arguments: Dict = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = 0.0
    risk_reasons: List[str] = field(default_factory=list)
    session_id: str = ""
    created_at: float = field(default_factory=time.time)
    status: str = "pending"      # pending | approved | denied | timeout
    decided_at: Optional[float] = None
    decided_by: str = ""         # "auto" | "user" | "timeout"


# ── Risk Patterns ─────────────────────────────────────────────

HIGH_RISK_PATTERNS = [
    # File system destruction
    (r'rm\s+-rf', "Recursive file deletion", 0.9),
    (r'rmdir|shutil\.rmtree|os\.remove', "File/directory deletion", 0.8),
    (r'format\s+[a-zA-Z]:', "Disk formatting", 1.0),
    # System commands
    (r'sudo|runas|admin', "Elevated privilege execution", 0.9),
    (r'shutdown|reboot|restart', "System shutdown/reboot", 0.9),
    (r'taskkill|kill\s+-9|pkill', "Process termination", 0.8),
    # Registry/system config
    (r'reg\s+(add|delete)|regedit', "Registry modification", 0.9),
    (r'chmod\s+777|icacls.*everyone', "Permission change (open)", 0.8),
    # Network/exfiltration
    (r'curl.*\|\s*sh|wget.*\|\s*bash', "Remote code execution", 1.0),
    (r'nc\s+-l|ncat|netcat', "Network listener", 0.8),
    (r'scp\s|rsync.*-e\s+ssh', "Remote file transfer", 0.7),
    # Credentials
    (r'password|api.?key|secret|token|credential', "Credential access", 0.7),
    (r'\.env|\.ssh|\.aws|\.credentials', "Sensitive file access", 0.8),
    # Code execution
    (r'eval\(|exec\(|__import__', "Dynamic code execution", 0.8),
    (r'subprocess\.call|os\.system|os\.popen', "Shell command execution", 0.7),
]

MEDIUM_RISK_PATTERNS = [
    (r'pip\s+install|npm\s+install|apt\s+install', "Package installation", 0.5),
    (r'git\s+push|git\s+force', "Git push operation", 0.4),
    (r'docker\s+run|docker\s+exec', "Docker operation", 0.5),
    (r'open\(.*["\']w', "File write operation", 0.4),
    (r'http[s]?://(?!localhost)', "External URL access", 0.3),
    (r'send.*(email|message|notification)', "Communication action", 0.4),
    (r'database|sql|query|insert|update|delete', "Database operation", 0.4),
    (r'cron|schedule|at\s+\d', "Scheduled task creation", 0.5),
]

LOW_RISK_PATTERNS = [
    (r'ls|dir|cat|type|head|tail|grep|find', "Read-only file listing", 0.1),
    (r'echo|print|console\.log', "Output display", 0.05),
    (r'pwd|whoami|hostname|date', "System info query", 0.05),
    (r'git\s+(status|log|diff|branch)', "Git read operations", 0.1),
    (r'http[s]?://localhost', "Local URL access", 0.1),
]


class ToolApproval:
    """
    Risk-based tool approval system for Dive AI.

    Surpasses OpenClaw's blanket approval by:
      - Auto-approving safe operations (no user friction)
      - Explaining risk reasons for each decision
      - Per-session whitelist learning
      - Configurable timeout with safe default (deny)
    """

    DEFAULT_TIMEOUT = 60  # seconds

    def __init__(self):
        self._pending: Dict[str, ApprovalRequest] = {}
        self._history: List[ApprovalRequest] = []
        self._session_whitelist: Dict[str, Set[str]] = {}  # session → approved tools
        self._global_whitelist: Set[str] = set()
        self._approval_callback: Optional[Callable] = None
        self._stats = {
            "auto_approved": 0,
            "user_approved": 0,
            "denied": 0,
            "timed_out": 0,
            "total_requests": 0,
        }

    # ── Risk Assessment ───────────────────────────────────────

    def assess_risk(self, tool_name: str, arguments: Dict = None) -> Dict:
        """Assess the risk level of a tool call."""
        # Serialize everything to check patterns against
        check_text = f"{tool_name} {json.dumps(arguments or {})}"
        reasons = []
        max_score = 0.0
        level = RiskLevel.LOW

        # Check HIGH risk patterns
        for pattern, reason, score in HIGH_RISK_PATTERNS:
            if re.search(pattern, check_text, re.IGNORECASE):
                reasons.append(f"HIGH: {reason}")
                max_score = max(max_score, score)
                level = RiskLevel.HIGH

        # Check MEDIUM risk patterns (only if not already HIGH)
        if level != RiskLevel.HIGH:
            for pattern, reason, score in MEDIUM_RISK_PATTERNS:
                if re.search(pattern, check_text, re.IGNORECASE):
                    reasons.append(f"MEDIUM: {reason}")
                    max_score = max(max_score, score)
                    level = RiskLevel.MEDIUM

        # Check LOW risk patterns (informational)
        for pattern, reason, score in LOW_RISK_PATTERNS:
            if re.search(pattern, check_text, re.IGNORECASE):
                if level == RiskLevel.LOW:
                    reasons.append(f"LOW: {reason}")
                    max_score = max(max_score, score)

        if not reasons:
            reasons.append("No risk patterns detected")

        return {
            "level": level.value,
            "score": round(max_score, 2),
            "reasons": reasons,
            "tool": tool_name,
        }

    # ── Approval Flow ─────────────────────────────────────────

    def request_approval(self, tool_name: str, arguments: Dict = None,
                         session_id: str = "") -> ApprovalRequest:
        """Request approval for a tool call."""
        risk = self.assess_risk(tool_name, arguments)
        risk_level = RiskLevel(risk["level"])

        req = ApprovalRequest(
            tool_name=tool_name,
            arguments=arguments or {},
            risk_level=risk_level,
            risk_score=risk["score"],
            risk_reasons=risk["reasons"],
            session_id=session_id,
        )

        self._stats["total_requests"] += 1

        # Auto-approve LOW risk
        if risk_level == RiskLevel.LOW:
            req.status = "approved"
            req.decided_at = time.time()
            req.decided_by = "auto"
            self._stats["auto_approved"] += 1
            self._history.append(req)
            return req

        # Auto-approve whitelisted tools
        if tool_name in self._global_whitelist:
            req.status = "approved"
            req.decided_at = time.time()
            req.decided_by = "auto (whitelist)"
            self._stats["auto_approved"] += 1
            self._history.append(req)
            return req

        # Check session whitelist
        if session_id and tool_name in self._session_whitelist.get(session_id, set()):
            req.status = "approved"
            req.decided_at = time.time()
            req.decided_by = "auto (session whitelist)"
            self._stats["auto_approved"] += 1
            self._history.append(req)
            return req

        # MEDIUM risk: log and auto-approve
        if risk_level == RiskLevel.MEDIUM:
            req.status = "approved"
            req.decided_at = time.time()
            req.decided_by = "auto (medium risk)"
            self._stats["auto_approved"] += 1
            self._history.append(req)
            return req

        # HIGH risk: queue for approval
        self._pending[req.request_id] = req
        return req

    def approve(self, request_id: str, session_id: str = "") -> Dict:
        """Approve a pending request."""
        req = self._pending.pop(request_id, None)
        if not req:
            return {"success": False, "error": "Request not found or expired"}

        req.status = "approved"
        req.decided_at = time.time()
        req.decided_by = "user"
        self._stats["user_approved"] += 1
        self._history.append(req)

        # Add to session whitelist for future auto-approval
        if session_id:
            if session_id not in self._session_whitelist:
                self._session_whitelist[session_id] = set()
            self._session_whitelist[session_id].add(req.tool_name)

        return {"success": True, "request_id": request_id, "status": "approved"}

    def deny(self, request_id: str, reason: str = "") -> Dict:
        """Deny a pending request."""
        req = self._pending.pop(request_id, None)
        if not req:
            return {"success": False, "error": "Request not found or expired"}

        req.status = "denied"
        req.decided_at = time.time()
        req.decided_by = "user"
        self._stats["denied"] += 1
        self._history.append(req)
        return {"success": True, "request_id": request_id, "status": "denied"}

    def check_timeouts(self) -> List[str]:
        """Check for timed-out approval requests (deny by default)."""
        timed_out = []
        now = time.time()
        for rid, req in list(self._pending.items()):
            if now - req.created_at > self.DEFAULT_TIMEOUT:
                req.status = "timeout"
                req.decided_at = now
                req.decided_by = "timeout"
                self._stats["timed_out"] += 1
                self._history.append(req)
                del self._pending[rid]
                timed_out.append(rid)
        return timed_out

    # ── Whitelist Management ──────────────────────────────────

    def whitelist_tool(self, tool_name: str) -> Dict:
        """Add a tool to the global auto-approve whitelist."""
        self._global_whitelist.add(tool_name)
        return {"success": True, "tool": tool_name, "whitelisted": True}

    def remove_whitelist(self, tool_name: str) -> Dict:
        """Remove a tool from the global whitelist."""
        self._global_whitelist.discard(tool_name)
        return {"success": True, "tool": tool_name, "whitelisted": False}

    def get_whitelist(self) -> List[str]:
        """Get global whitelist."""
        return sorted(self._global_whitelist)

    # ── Quick Check ───────────────────────────────────────────

    def is_approved(self, tool_name: str, arguments: Dict = None,
                    session_id: str = "") -> bool:
        """Quick check if a tool call would be auto-approved."""
        req = self.request_approval(tool_name, arguments, session_id)
        return req.status == "approved"

    # ── Stats ─────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        return {
            **self._stats,
            "pending": len(self._pending),
            "global_whitelist": len(self._global_whitelist),
            "session_whitelists": len(self._session_whitelist),
            "history_size": len(self._history),
        }

    def get_pending(self) -> List[Dict]:
        """Get all pending approval requests."""
        return [{
            "request_id": r.request_id,
            "tool": r.tool_name,
            "risk_level": r.risk_level.value,
            "risk_score": r.risk_score,
            "reasons": r.risk_reasons,
            "waiting_seconds": round(time.time() - r.created_at, 1),
        } for r in self._pending.values()]

    def get_recent_history(self, limit: int = 20) -> List[Dict]:
        """Get recent approval history."""
        return [{
            "tool": r.tool_name,
            "risk_level": r.risk_level.value,
            "status": r.status,
            "decided_by": r.decided_by,
            "time": time.strftime("%H:%M:%S", time.localtime(r.created_at)),
        } for r in self._history[-limit:]]
