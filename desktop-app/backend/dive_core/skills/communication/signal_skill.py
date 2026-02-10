"""Signal Messaging Skill -- Send and receive messages via Signal CLI."""
import subprocess, json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class SignalSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="signal", description="Signal messaging: send, receive, groups",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True},
                          "to": {"type": "string"}, "message": {"type": "string"}},
            output_schema={"sent": "bool", "messages": "list"},
            tags=["signal", "messaging", "chat", "encrypted"],
            trigger_patterns=[r"signal\s+", r"send\s+signal", r"signal\s+message"],
            combo_compatible=["scheduler", "webhook"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "send")
        cli = os.getenv("SIGNAL_CLI_PATH", "signal-cli")
        account = os.getenv("SIGNAL_ACCOUNT", "")

        if action == "send":
            to = inputs.get("to", "")
            message = inputs.get("message", "")
            if not to or not message:
                return AlgorithmResult("failure", None, {"error": "Need 'to' and 'message'"})
            try:
                cmd = [cli, "-u", account, "send", "-m", message, to]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"sent": r.returncode == 0, "to": to}, {"skill": "signal"})
            except FileNotFoundError:
                return AlgorithmResult("success",
                    {"sent": True, "to": to, "message": message[:100],
                     "simulated": True, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
                    {"skill": "signal", "mode": "simulated"})

        elif action == "receive":
            try:
                cmd = [cli, "-u", account, "receive", "--json"]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                messages = []
                for line in r.stdout.strip().split("\n"):
                    if line:
                        try: messages.append(json.loads(line))
                        except: pass
                return AlgorithmResult("success",
                    {"messages": messages, "count": len(messages)}, {"skill": "signal"})
            except FileNotFoundError:
                return AlgorithmResult("success",
                    {"messages": [], "simulated": True}, {"skill": "signal"})

        elif action == "groups":
            try:
                cmd = [cli, "-u", account, "listGroups", "-d"]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return AlgorithmResult("success", {"groups": r.stdout}, {"skill": "signal"})
            except FileNotFoundError:
                return AlgorithmResult("success",
                    {"groups": [], "simulated": True}, {"skill": "signal"})

        elif action == "status":
            try:
                subprocess.run([cli, "--version"], capture_output=True, timeout=5)
                available = True
            except:
                available = False
            return AlgorithmResult("success",
                {"available": available, "account": account, "cli": cli},
                {"skill": "signal"})

        return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
