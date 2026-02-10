"""iMessage Skill -- Send and read messages via AppleScript (macOS) or simulation."""
import subprocess, json, os, time, platform
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class IMessageSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="imessage", description="iMessage: send, read, search messages",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True},
                          "to": {"type": "string"}, "message": {"type": "string"},
                          "query": {"type": "string"}, "limit": {"type": "integer"}},
            output_schema={"sent": "bool", "messages": "list"},
            tags=["imessage", "apple", "messaging", "sms", "macos"],
            trigger_patterns=[r"imessage", r"send\s+imessage", r"apple\s+message"],
            combo_compatible=["scheduler", "webhook"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "send")
        is_mac = platform.system() == "Darwin"

        if action == "send":
            to = inputs.get("to", "")
            message = inputs.get("message", "")
            if not to or not message:
                return AlgorithmResult("failure", None, {"error": "Need 'to' and 'message'"})
            if not is_mac:
                return AlgorithmResult("success",
                    {"sent": True, "to": to, "message": message[:100],
                     "simulated": True, "platform": platform.system(),
                     "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
                    {"skill": "imessage", "mode": "simulated"})
            script = f'tell application "Messages"\nset targetService to 1st service whose service type = iMessage\nset targetBuddy to buddy "{to}" of targetService\nsend "{message}" to targetBuddy\nend tell'
            try:
                r = subprocess.run(["osascript", "-e", script],
                                   capture_output=True, text=True, timeout=15)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"sent": r.returncode == 0, "to": to}, {"skill": "imessage"})
            except Exception as e:
                return AlgorithmResult("failure", None, {"error": str(e)})

        elif action == "read":
            limit = inputs.get("limit", 10)
            if not is_mac:
                return AlgorithmResult("success",
                    {"messages": [], "simulated": True,
                     "note": "Requires macOS for real message access"},
                    {"skill": "imessage"})
            db_path = os.path.expanduser("~/Library/Messages/chat.db")
            if not os.path.exists(db_path):
                return AlgorithmResult("failure", None, {"error": "Messages database not found"})
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.execute(f"""
                    SELECT m.text, m.date, h.id as sender
                    FROM message m LEFT JOIN handle h ON m.handle_id = h.ROWID
                    ORDER BY m.date DESC LIMIT {limit}""")
                messages = [{"text": r[0], "date": r[1], "sender": r[2]} for r in cursor.fetchall()]
                conn.close()
                return AlgorithmResult("success", {"messages": messages, "count": len(messages)},
                                       {"skill": "imessage"})
            except Exception as e:
                return AlgorithmResult("failure", None, {"error": str(e)})

        elif action == "search":
            query = inputs.get("query", "")
            if not query:
                return AlgorithmResult("failure", None, {"error": "Need 'query'"})
            if not is_mac:
                return AlgorithmResult("success",
                    {"results": [], "query": query, "simulated": True},
                    {"skill": "imessage"})
            try:
                import sqlite3
                db_path = os.path.expanduser("~/Library/Messages/chat.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("""
                    SELECT m.text, m.date, h.id as sender
                    FROM message m LEFT JOIN handle h ON m.handle_id = h.ROWID
                    WHERE m.text LIKE ? ORDER BY m.date DESC LIMIT 20
                """, (f"%{query}%",))
                results = [{"text": r[0], "date": r[1], "sender": r[2]} for r in cursor.fetchall()]
                conn.close()
                return AlgorithmResult("success", {"results": results, "query": query}, {"skill": "imessage"})
            except Exception as e:
                return AlgorithmResult("failure", None, {"error": str(e)})

        elif action == "status":
            return AlgorithmResult("success",
                {"available": is_mac, "platform": platform.system(),
                 "note": "Requires macOS for real iMessage access"},
                {"skill": "imessage"})

        return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
