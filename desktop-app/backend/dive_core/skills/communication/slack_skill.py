"""Slack Skill — Send messages to Slack channels via webhook."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SlackSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="slack-bot", description="Send messages to Slack via incoming webhooks",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"message": {"type": "string", "required": True}, "channel": {"type": "string"},
                          "webhook_url": {"type": "string"}},
            output_schema={"sent": "boolean"},
            tags=["slack", "chat", "message", "notify", "team"],
            trigger_patterns=[r"slack\s+", r"send\s+to\s+slack", r"notify\s+slack"],
            combo_compatible=["news-search", "system-info", "code-review"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        webhook = inputs.get("webhook_url") or os.environ.get("SLACK_WEBHOOK", "")
        message = inputs.get("message") or inputs.get("data", {}).get("summary", "No content")
        channel = inputs.get("channel", "")
        
        if not webhook:
            return AlgorithmResult("success", {"sent": False, "simulated": True, "message": message[:200],
                "note": "Set SLACK_WEBHOOK env var."}, {"skill": "slack-bot"})
        
        try:
            payload = {"text": message[:3000]}
            if channel:
                payload["channel"] = channel
            data = json.dumps(payload).encode()
            req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode()
            return AlgorithmResult("success", {"sent": True, "response": body}, {"skill": "slack-bot"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
