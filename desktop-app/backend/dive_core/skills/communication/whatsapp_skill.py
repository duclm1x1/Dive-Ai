"""WhatsApp Skill — WhatsApp Business API integration."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class WhatsAppSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="whatsapp-bot", description="Send WhatsApp messages via Business API",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"to": {"type": "string", "required": True}, "message": {"type": "string", "required": True}},
            output_schema={"sent": "boolean", "message_id": "string"},
            tags=["whatsapp", "message", "chat", "notify", "phone"],
            trigger_patterns=[r"whatsapp", r"send\s+whatsapp", r"text\s+"],
            combo_compatible=["news-search", "system-info", "scheduler"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        token = os.environ.get("WHATSAPP_TOKEN", "")
        phone_id = os.environ.get("WHATSAPP_PHONE_ID", "")
        to = inputs.get("to", "")
        message = inputs.get("message") or inputs.get("data", {}).get("summary", "")
        
        if not token or not phone_id:
            return AlgorithmResult("success", {"sent": False, "simulated": True, "to": to, "message": message[:200],
                "note": "Set WHATSAPP_TOKEN and WHATSAPP_PHONE_ID env vars."}, {"skill": "whatsapp-bot"})
        
        try:
            url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
            data = json.dumps({"messaging_product": "whatsapp", "to": to,
                               "type": "text", "text": {"body": message[:4096]}}).encode()
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
            msg_id = result.get("messages", [{}])[0].get("id", "")
            return AlgorithmResult("success", {"sent": True, "message_id": msg_id}, {"skill": "whatsapp-bot"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
