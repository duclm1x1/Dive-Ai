"""Webhook Sender Skill — POST to any webhook URL."""
import urllib.request, json
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class WebhookSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="webhook-sender", description="Send data to any webhook URL",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"url": {"type": "string", "required": True}, "payload": {"type": "dict"}},
            output_schema={"status_code": "integer", "response": "string"},
            tags=["webhook", "POST", "api", "notify", "http"],
            trigger_patterns=[r"webhook", r"post\s+to", r"send\s+to\s+url"],
            combo_compatible=["data-analyzer", "system-info", "web-search"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        url = inputs.get("url", "")
        payload = inputs.get("payload") or inputs.get("data", {})
        if not url:
            return AlgorithmResult("failure", None, {"error": "No URL"})
        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="replace")[:5000]
                return AlgorithmResult("success", {"status_code": resp.status, "response": body}, {"skill": "webhook-sender"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
