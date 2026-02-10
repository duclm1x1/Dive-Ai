"""Discord Skill — Discord webhook/bot integration."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class DiscordSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="discord-bot", description="Send messages via Discord webhooks",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"message": {"type": "string", "required": True}, "webhook_url": {"type": "string"}},
            output_schema={"sent": "boolean"},
            tags=["discord", "chat", "webhook", "notify"],
            trigger_patterns=[r"discord", r"send\s+to\s+discord"],
            combo_compatible=["news-search", "system-info", "code-review"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        webhook = inputs.get("webhook_url") or os.environ.get("DISCORD_WEBHOOK", "")
        message = inputs.get("message") or inputs.get("data", {}).get("summary", "No content")
        
        if not webhook:
            return AlgorithmResult("success", {"sent": False, "simulated": True, "message": message[:200],
                "note": "Set DISCORD_WEBHOOK env var."}, {"skill": "discord-bot"})
        try:
            data = json.dumps({"content": message[:2000]}).encode()
            req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return AlgorithmResult("success", {"sent": True, "status": resp.status}, {"skill": "discord-bot"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
