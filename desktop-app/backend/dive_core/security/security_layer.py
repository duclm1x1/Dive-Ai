"""
Dive AI — Security Hardening Layer
Prompt injection detection, input sanitization, skill vetting, audit logging.
"""
import re, os, json, hashlib, time
from datetime import datetime
from typing import Dict, Any, List, Optional


class SecurityLayer:
    """
    Multi-layer security system:
    1. Prompt injection detection
    2. Input sanitization
    3. Skill vetting/scanning
    4. Security audit logging
    """

    AUDIT_DIR = os.path.expanduser("~/.dive-ai/security")
    AUDIT_LOG = os.path.expanduser("~/.dive-ai/security/audit.jsonl")

    # Known prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?above",
        r"forget\s+(everything|all|your)\s+(instructions|rules|guidelines)",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"new\s+instructions?\s*:",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        r"\[SYSTEM\]",
        r"override\s+(your\s+)?instructions",
        r"act\s+as\s+if\s+you\s+",
        r"pretend\s+(you\s+are|to\s+be)",
        r"do\s+not\s+follow\s+(your\s+)?(rules|instructions|guidelines)",
        r"jailbreak",
        r"DAN\s+mode",
        r"bypass\s+(your\s+)?restrictions",
        r"reveal\s+(your\s+)?(system|instructions|prompt)",
        r"output\s+(your\s+)?system\s+prompt",
        r"repeat\s+(your\s+)?instructions",
    ]

    # Dangerous code patterns in skills
    DANGEROUS_PATTERNS = [
        (r"subprocess\.call\(.+shell\s*=\s*True", "shell_injection", "high"),
        (r"os\.system\(", "os_command", "high"),
        (r"eval\(", "eval_usage", "medium"),
        (r"exec\(", "exec_usage", "medium"),
        (r"__import__\(", "dynamic_import", "medium"),
        (r"open\(.+['\"]w['\"]", "file_write", "low"),
        (r"requests\.get|urllib\.request|httpx\.", "network_access", "low"),
        (r"sqlite3\.connect|psycopg2|pymongo", "database_access", "low"),
        (r"API_KEY|SECRET|PASSWORD|TOKEN", "credential_exposure", "high"),
        (r"pickle\.loads?\(", "pickle_deserialize", "high"),
        (r"yaml\.load\(.*Loader", "yaml_unsafe_load", "medium"),
        (r"rm\s+-rf|rmtree|shutil\.rmtree", "destructive_delete", "high"),
    ]

    def __init__(self):
        os.makedirs(self.AUDIT_DIR, exist_ok=True)
        self._blocked = 0
        self._scanned = 0
        self._alerts: List[Dict] = []

    # ── Prompt Injection Detection ──────────────────────

    def check_injection(self, text: str) -> Dict[str, Any]:
        """Check text for prompt injection patterns."""
        text_lower = text.lower()
        detections = []

        for pattern in self.INJECTION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                detections.append({
                    "pattern": pattern,
                    "matches": len(matches) if isinstance(matches[0], str) else len(matches),
                    "severity": "high",
                })

        is_safe = len(detections) == 0
        result = {
            "safe": is_safe,
            "detections": detections,
            "risk_score": min(len(detections) * 0.3, 1.0),
            "text_length": len(text),
        }

        if not is_safe:
            self._blocked += 1
            self._log_audit("injection_detected", {
                "text_preview": text[:200],
                "detections": len(detections),
            })

        return result

    # ── Input Sanitization ──────────────────────────────

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to remove potential injection attempts."""
        sanitized = text
        # Remove system-like markers
        sanitized = re.sub(r"<\s*/?system\s*>", "", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"\[SYSTEM\]", "", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"\[INST\]", "", sanitized, flags=re.IGNORECASE)
        # Remove explicit instruction overrides
        sanitized = re.sub(r"(?i)new\s+instructions?\s*:", "note:", sanitized)
        return sanitized.strip()

    # ── Skill Scanning ──────────────────────────────────

    def scan_skill(self, file_path: str) -> Dict[str, Any]:
        """Scan a skill file for dangerous patterns."""
        if not os.path.exists(file_path):
            return {"safe": False, "error": "File not found"}

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        self._scanned += 1
        findings = []

        for pattern, name, severity in self.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                findings.append({
                    "type": name,
                    "severity": severity,
                    "count": len(matches),
                    "pattern": pattern,
                })

        # Calculate risk score
        risk = 0
        for f in findings:
            if f["severity"] == "high": risk += 0.4
            elif f["severity"] == "medium": risk += 0.2
            else: risk += 0.1

        # Checksum
        file_hash = hashlib.sha256(content.encode()).hexdigest()

        result = {
            "safe": risk < 0.5,
            "risk_score": min(risk, 1.0),
            "findings": findings,
            "total_findings": len(findings),
            "high_risk": sum(1 for f in findings if f["severity"] == "high"),
            "file": file_path,
            "hash": file_hash,
            "lines": content.count("\n") + 1,
        }

        if not result["safe"]:
            self._log_audit("unsafe_skill", {
                "file": file_path, "risk": risk,
                "high_risk": result["high_risk"],
            })
            self._alerts.append(result)

        return result

    def scan_directory(self, directory: str) -> Dict[str, Any]:
        """Scan all Python files in a directory."""
        results = {"total": 0, "safe": 0, "unsafe": 0, "files": []}
        for root, _, files in os.walk(directory):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    r = self.scan_skill(path)
                    results["total"] += 1
                    if r.get("safe", False):
                        results["safe"] += 1
                    else:
                        results["unsafe"] += 1
                    results["files"].append({
                        "file": f, "safe": r.get("safe"),
                        "risk": r.get("risk_score", 0),
                        "findings": r.get("total_findings", 0),
                    })
        return results

    # ── Audit Logging ───────────────────────────────────

    def _log_audit(self, event_type: str, details: Dict):
        """Append to security audit log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details,
        }
        with open(self.AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_audit_log(self, last_n: int = 50) -> List[Dict]:
        """Read recent audit log entries."""
        if not os.path.exists(self.AUDIT_LOG):
            return []
        entries = []
        with open(self.AUDIT_LOG) as f:
            for line in f:
                if line.strip():
                    try: entries.append(json.loads(line))
                    except: pass
        return entries[-last_n:]

    # ── Stats ───────────────────────────────────────────

    def get_stats(self) -> Dict:
        return {
            "blocked_injections": self._blocked,
            "skills_scanned": self._scanned,
            "active_alerts": len(self._alerts),
            "audit_log": self.AUDIT_LOG,
            "injection_patterns": len(self.INJECTION_PATTERNS),
            "dangerous_patterns": len(self.DANGEROUS_PATTERNS),
        }
