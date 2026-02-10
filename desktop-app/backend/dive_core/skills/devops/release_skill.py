"""Release Management Skill — GitHub releases, tags, changelog."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class ReleaseSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="release-manager", description="GitHub releases: create, list, tags, changelog",
            category=SkillCategory.GIT, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "repo": {"type": "string", "required": True},
                          "tag": {"type": "string"}, "name": {"type": "string"}, "body": {"type": "string"}},
            output_schema={"release": "dict", "releases": "list"},
            tags=["release", "tag", "changelog", "version", "github", "deploy"],
            trigger_patterns=[r"release\s+", r"new\s+version", r"create\s+tag", r"changelog"],
            combo_compatible=["ci-cd", "slack-bot", "telegram-bot"],
            combo_position="end")

    def _gh(self, method, path, data=None):
        token = os.environ.get("GITHUB_TOKEN", "")
        headers = {"User-Agent": "DiveAI/29.7", "Accept": "application/vnd.github.v3+json"}
        if token: headers["Authorization"] = f"token {token}"
        url = f"https://api.github.com{path}"
        body = json.dumps(data).encode() if data else None
        if body: headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "list")
        repo = inputs.get("repo", "")
        if not repo:
            return AlgorithmResult("failure", None, {"error": "repo required"})
        try:
            if action == "list":
                data = self._gh("GET", f"/repos/{repo}/releases?per_page=10")
                releases = [{"tag": r["tag_name"], "name": r.get("name", ""), "published": r.get("published_at"),
                             "draft": r.get("draft"), "url": r.get("html_url")} for r in data[:10]]
                return AlgorithmResult("success", {"releases": releases, "repo": repo}, {"skill": "release-manager"})
            elif action == "latest":
                data = self._gh("GET", f"/repos/{repo}/releases/latest")
                return AlgorithmResult("success", {"tag": data["tag_name"], "name": data.get("name"),
                    "published": data.get("published_at"), "body": data.get("body", "")[:2000]}, {"skill": "release-manager"})
            elif action == "create":
                tag = inputs.get("tag", "")
                if not tag: return AlgorithmResult("failure", None, {"error": "tag required"})
                data = self._gh("POST", f"/repos/{repo}/releases", {"tag_name": tag,
                    "name": inputs.get("name", tag), "body": inputs.get("body", ""),
                    "draft": inputs.get("draft", False), "prerelease": inputs.get("prerelease", False)})
                return AlgorithmResult("success", {"created": True, "tag": data["tag_name"],
                    "url": data.get("html_url")}, {"skill": "release-manager"})
            elif action == "tags":
                data = self._gh("GET", f"/repos/{repo}/tags?per_page=20")
                tags = [{"name": t["name"], "sha": t["commit"]["sha"][:7]} for t in data[:20]]
                return AlgorithmResult("success", {"tags": tags, "repo": repo}, {"skill": "release-manager"})
            elif action == "changelog":
                data = self._gh("GET", f"/repos/{repo}/commits?per_page=30")
                entries = [f"- {c['commit']['message'].split(chr(10))[0]} ({c['sha'][:7]})" for c in data[:30]]
                return AlgorithmResult("success", {"changelog": "\n".join(entries), "commits": len(entries)}, {"skill": "release-manager"})
            return AlgorithmResult("failure", None, {"error": "action: list/latest/create/tags/changelog"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
