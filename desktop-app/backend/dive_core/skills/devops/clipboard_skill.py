"""Clipboard Skill — Copy/paste text, history."""
import subprocess, platform, os, json, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class ClipboardSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="clipboard", description="Clipboard: copy, paste, history",
            category=SkillCategory.SYSTEM, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "text": {"type": "string"}},
            output_schema={"text": "string", "history": "list"},
            tags=["clipboard", "copy", "paste", "text", "clip"],
            trigger_patterns=[r"copy\s+to\s+clipboard", r"paste", r"clipboard", r"clip\s+"],
            combo_compatible=["file-manager", "web-scrape", "note-taker"],
            combo_position="any")

    def _history_file(self):
        d = os.path.expanduser("~/.dive-ai/clipboard")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "history.json")

    def _load_history(self):
        f = self._history_file()
        if os.path.exists(f):
            with open(f) as fh: return json.load(fh)
        return []

    def _save_history(self, hist):
        with open(self._history_file(), "w") as f: json.dump(hist[-50:], f)

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "paste")
        text = inputs.get("text", "")

        try:
            if action == "copy" and text:
                if platform.system() == "Windows":
                    process = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
                    process.communicate(text.encode("utf-16-le"))
                elif platform.system() == "Darwin":
                    subprocess.run(["pbcopy"], input=text.encode(), check=True)
                else:
                    subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)

                hist = self._load_history()
                hist.append({"text": text[:500], "time": time.strftime("%Y-%m-%d %H:%M:%S")})
                self._save_history(hist)
                return AlgorithmResult("success", {"copied": True, "length": len(text)}, {"skill": "clipboard"})

            elif action == "paste":
                if platform.system() == "Windows":
                    r = subprocess.run(["powershell", "-c", "Get-Clipboard"], capture_output=True, text=True, timeout=5)
                    content = r.stdout.strip()
                elif platform.system() == "Darwin":
                    r = subprocess.run(["pbpaste"], capture_output=True, text=True)
                    content = r.stdout
                else:
                    r = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True)
                    content = r.stdout
                return AlgorithmResult("success", {"text": content[:5000], "length": len(content)}, {"skill": "clipboard"})

            elif action == "history":
                hist = self._load_history()
                return AlgorithmResult("success", {"history": hist[-10:], "total": len(hist)}, {"skill": "clipboard"})

            elif action == "clear":
                if platform.system() == "Windows":
                    subprocess.run(["powershell", "-c", "Set-Clipboard -Value $null"], capture_output=True, timeout=5)
                return AlgorithmResult("success", {"cleared": True}, {"skill": "clipboard"})

            return AlgorithmResult("failure", None, {"error": "action: copy/paste/history/clear"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
