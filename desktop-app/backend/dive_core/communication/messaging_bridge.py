"""
Dive AI Messaging Bridge — Unified interface for Telegram, Discord, Webhooks.
Receives commands from messaging apps → routes to skills → replies with results.
"""
import os
import json
import time
import threading
import urllib.request
from typing import Dict, Any, Optional, Callable, List


class MessageHandler:
    """Base handler for incoming messages."""
    def __init__(self, skill_executor: Callable = None):
        self.skill_executor = skill_executor
        self.message_log: List[Dict] = []

    def process(self, text: str, metadata: Dict = None) -> str:
        """Process incoming message → route to skill → return result."""
        self.message_log.append({"text": text, "time": time.time(), "meta": metadata})
        
        if self.skill_executor:
            result = self.skill_executor(text)
            return str(result)
        return f"Received: {text}"


class TelegramBridge:
    """Telegram Bot listener using long-polling."""
    
    def __init__(self, token: str = None, handler: MessageHandler = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.handler = handler or MessageHandler()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._offset = 0

    @property
    def configured(self) -> bool:
        return bool(self.token)

    def start(self):
        if not self.configured:
            return {"error": "TELEGRAM_BOT_TOKEN not set"}
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        return {"status": "started"}

    def stop(self):
        self._running = False
        return {"status": "stopped"}

    def _poll_loop(self):
        base = f"https://api.telegram.org/bot{self.token}"
        while self._running:
            try:
                url = f"{base}/getUpdates?offset={self._offset}&timeout=10"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                
                for update in data.get("result", []):
                    self._offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "")
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    
                    if text and chat_id:
                        reply = self.handler.process(text, {"platform": "telegram", "chat_id": chat_id})
                        self._send(chat_id, reply)
            except Exception:
                time.sleep(5)

    def _send(self, chat_id: str, text: str):
        base = f"https://api.telegram.org/bot{self.token}"
        data = json.dumps({"chat_id": chat_id, "text": text[:4096]}).encode()
        req = urllib.request.Request(f"{base}/sendMessage", data=data,
                                     headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=10)
        except: pass

    def status(self) -> Dict:
        return {"platform": "telegram", "running": self._running, "configured": self.configured,
                "messages_processed": len(self.handler.message_log)}


class DiscordBridge:
    """Discord webhook-based bridge."""
    
    def __init__(self, webhook_url: str = None, handler: MessageHandler = None):
        self.webhook_url = webhook_url or os.environ.get("DISCORD_WEBHOOK", "")
        self.handler = handler or MessageHandler()

    @property
    def configured(self) -> bool:
        return bool(self.webhook_url)

    def send(self, message: str) -> Dict:
        if not self.configured:
            return {"error": "DISCORD_WEBHOOK not set"}
        try:
            data = json.dumps({"content": message[:2000]}).encode()
            req = urllib.request.Request(self.webhook_url, data=data,
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10)
            return {"sent": True}
        except Exception as e:
            return {"sent": False, "error": str(e)}

    def status(self) -> Dict:
        return {"platform": "discord", "configured": self.configured}


class MessagingBridge:
    """Unified messaging bridge managing all platforms."""
    
    def __init__(self, skill_executor: Callable = None):
        self.handler = MessageHandler(skill_executor)
        self.telegram = TelegramBridge(handler=self.handler)
        self.discord = DiscordBridge(handler=self.handler)

    def connect(self, platform: str, **kwargs) -> Dict:
        if platform == "telegram":
            if kwargs.get("token"):
                self.telegram.token = kwargs["token"]
            return self.telegram.start()
        elif platform == "discord":
            if kwargs.get("webhook_url"):
                self.discord.webhook_url = kwargs["webhook_url"]
            return {"status": "discord ready (webhook mode)"}
        return {"error": f"Unknown platform: {platform}"}

    def send(self, platform: str, message: str, **kwargs) -> Dict:
        if platform == "telegram":
            chat_id = kwargs.get("chat_id", os.environ.get("TELEGRAM_CHAT_ID", ""))
            self.telegram._send(chat_id, message)
            return {"sent": True, "platform": "telegram"}
        elif platform == "discord":
            return self.discord.send(message)
        return {"error": f"Unknown platform: {platform}"}

    def status(self) -> Dict:
        return {
            "telegram": self.telegram.status(),
            "discord": self.discord.status(),
            "total_messages": len(self.handler.message_log),
        }
