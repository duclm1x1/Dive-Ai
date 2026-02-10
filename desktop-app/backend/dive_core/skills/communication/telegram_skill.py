"""Telegram Skill — Send/receive Telegram messages."""
import urllib.request, urllib.parse, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class TelegramSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="telegram-bot", description="Send and receive Telegram messages",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"action": {"type": "string"}, "chat_id": {"type": "string"},
                          "message": {"type": "string"}},
            output_schema={"sent": "boolean", "messages": "list"},
            tags=["telegram", "chat", "message", "notify", "bot"],
            trigger_patterns=[r"telegram", r"send\s+to\s+telegram", r"notify\s+via\s+telegram"],
            combo_compatible=["news-search", "system-info", "data-analyzer"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = inputs.get("chat_id") or os.environ.get("TELEGRAM_CHAT_ID", "")
        action = inputs.get("action", "send")
        message = inputs.get("message") or inputs.get("data", {}).get("summary", "")
        
        if not token:
            return AlgorithmResult("success", {
                "sent": False, "simulated": True, "message": message[:200],
                "note": "Set TELEGRAM_BOT_TOKEN env var.",
            }, {"skill": "telegram-bot"})
        
        base = f"https://api.telegram.org/bot{token}"
        try:
            if action == "send" and chat_id and message:
                url = f"{base}/sendMessage"
                data = json.dumps({"chat_id": chat_id, "text": message[:4096], "parse_mode": "Markdown"}).encode()
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read())
                return AlgorithmResult("success", {"sent": result.get("ok", False), "message_id": result.get("result", {}).get("message_id")},
                                       {"skill": "telegram-bot"})
            elif action == "get_updates":
                url = f"{base}/getUpdates?limit=10"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    result = json.loads(resp.read())
                messages = [{"text": u["message"]["text"], "from": u["message"]["from"].get("first_name", ""),
                             "chat_id": str(u["message"]["chat"]["id"])}
                            for u in result.get("result", []) if "message" in u and "text" in u["message"]]
                return AlgorithmResult("success", {"messages": messages, "total": len(messages)}, {"skill": "telegram-bot"})
            else:
                return AlgorithmResult("success", {"note": "Specify action=send/get_updates, chat_id, message"}, {"skill": "telegram-bot"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
