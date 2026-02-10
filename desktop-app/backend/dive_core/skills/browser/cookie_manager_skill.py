"""Cookie Manager Skill -- Manage browser cookies and sessions."""
import json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class CookieManagerSkill(BaseSkill):
    _cookies = {}

    def _build_spec(self):
        return SkillSpec(name="cookie-manager", description="Cookie management: get, set, delete, export, import",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True},
                          "domain": {"type": "string"}, "name": {"type": "string"}, "value": {"type": "string"}},
            output_schema={"cookies": "dict", "domains": "list"},
            tags=["cookie", "browser", "session", "auth", "web"],
            trigger_patterns=[r"cookie\s+", r"set\s+cookie", r"get\s+cookie", r"browser\s+session"],
            combo_compatible=["web-browse", "web-scrape", "form-fill", "spa-renderer"],
            combo_position="start")

    def _cookie_file(self):
        d = os.path.expanduser("~/.dive-ai/cookies")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "cookies.json")

    def _load(self):
        f = self._cookie_file()
        if os.path.exists(f):
            try:
                with open(f) as fh: self._cookies = json.load(fh)
            except: pass

    def _save(self):
        with open(self._cookie_file(), "w") as f: json.dump(self._cookies, f, indent=2)

    def _execute(self, inputs, context=None):
        self._load()
        action = inputs.get("action", "list")

        if action == "set":
            domain = inputs.get("domain", "")
            name = inputs.get("name", "")
            value = inputs.get("value", "")
            if not domain or not name:
                return AlgorithmResult("failure", None, {"error": "Need 'domain' and 'name'"})
            self._cookies.setdefault(domain, {})
            self._cookies[domain][name] = {
                "value": value, "path": inputs.get("path", "/"),
                "secure": inputs.get("secure", False),
                "set_at": time.strftime("%Y-%m-%d %H:%M:%S")}
            self._save()
            return AlgorithmResult("success",
                {"set": True, "domain": domain, "name": name},
                {"skill": "cookie-manager"})

        elif action == "get":
            domain = inputs.get("domain", "")
            name = inputs.get("name", "")
            if domain in self._cookies:
                if name:
                    cookie = self._cookies[domain].get(name)
                    return AlgorithmResult("success",
                        {"cookie": cookie, "domain": domain, "name": name},
                        {"skill": "cookie-manager"})
                return AlgorithmResult("success",
                    {"cookies": self._cookies[domain], "domain": domain},
                    {"skill": "cookie-manager"})
            return AlgorithmResult("failure", None, {"error": f"No cookies for {domain}"})

        elif action == "delete":
            domain = inputs.get("domain", "")
            name = inputs.get("name", "")
            if domain in self._cookies:
                if name and name in self._cookies[domain]:
                    del self._cookies[domain][name]
                    self._save()
                    return AlgorithmResult("success", {"deleted": True, "name": name}, {"skill": "cookie-manager"})
                elif not name:
                    del self._cookies[domain]
                    self._save()
                    return AlgorithmResult("success", {"deleted": True, "domain": domain}, {"skill": "cookie-manager"})
            return AlgorithmResult("failure", None, {"error": "Cookie not found"})

        elif action == "list":
            total = sum(len(v) for v in self._cookies.values())
            return AlgorithmResult("success",
                {"domains": list(self._cookies.keys()), "total_cookies": total,
                 "by_domain": {d: len(v) for d, v in self._cookies.items()}},
                {"skill": "cookie-manager"})

        elif action == "export":
            return AlgorithmResult("success",
                {"cookies": self._cookies, "format": "json"},
                {"skill": "cookie-manager"})

        elif action == "clear":
            count = sum(len(v) for v in self._cookies.values())
            self._cookies = {}
            self._save()
            return AlgorithmResult("success", {"cleared": True, "count": count}, {"skill": "cookie-manager"})

        return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
