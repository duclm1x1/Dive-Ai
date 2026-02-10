"""Repo Monitor Skill — Watch GitHub repos for events, commits, stars."""
import urllib.request, json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class RepoMonitorSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="repo-monitor", description="Monitor GitHub repos: commits, events, stars, releases",
            category=SkillCategory.GIT, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "repo": {"type": "string", "required": True}},
            output_schema={"events": "list", "commits": "list", "stats": "dict"},
            tags=["github", "repo", "monitor", "watch", "commit", "star", "release", "event"],
            trigger_patterns=[r"watch\s+repo", r"monitor\s+", r"recent\s+commits", r"repo\s+events"],
            combo_compatible=["telegram-bot", "slack-bot", "scheduler", "email-send"],
            combo_position="start")

    def _gh(self, path, timeout=10):
        token = os.environ.get("GITHUB_TOKEN", "")
        headers = {"User-Agent": "DiveAI/29.7", "Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        url = f"https://api.github.com{path}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "events")
        repo = inputs.get("repo", "")

        if not repo:
            return AlgorithmResult("failure", None, {"error": "repo required (owner/name)"})

        try:
            if action == "events":
                data = self._gh(f"/repos/{repo}/events?per_page=15")
                events = [{"type": e["type"], "actor": e["actor"]["login"],
                           "created": e["created_at"],
                           "payload_action": e.get("payload", {}).get("action", "")}
                          for e in data[:15]]
                return AlgorithmResult("success", {"events": events, "repo": repo}, {"skill": "repo-monitor"})

            elif action == "commits":
                data = self._gh(f"/repos/{repo}/commits?per_page=10")
                commits = [{"sha": c["sha"][:7], "message": c["commit"]["message"][:100],
                            "author": c["commit"]["author"]["name"],
                            "date": c["commit"]["author"]["date"]}
                           for c in data[:10]]
                return AlgorithmResult("success", {"commits": commits, "repo": repo}, {"skill": "repo-monitor"})

            elif action == "stats":
                data = self._gh(f"/repos/{repo}")
                return AlgorithmResult("success", {
                    "repo": repo, "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"), "watchers": data.get("watchers_count"),
                    "open_issues": data.get("open_issues_count"),
                    "language": data.get("language"), "size": data.get("size"),
                    "updated": data.get("updated_at"),
                    "default_branch": data.get("default_branch"),
                }, {"skill": "repo-monitor"})

            elif action == "releases":
                data = self._gh(f"/repos/{repo}/releases?per_page=5")
                releases = [{"tag": r["tag_name"], "name": r.get("name", ""),
                             "published": r.get("published_at"), "draft": r.get("draft"),
                             "prerelease": r.get("prerelease"),
                             "assets": len(r.get("assets", []))}
                            for r in data[:5]]
                return AlgorithmResult("success", {"releases": releases, "repo": repo}, {"skill": "repo-monitor"})

            elif action == "contributors":
                data = self._gh(f"/repos/{repo}/contributors?per_page=10")
                contributors = [{"login": c["login"], "contributions": c["contributions"]}
                                for c in data[:10]]
                return AlgorithmResult("success", {"contributors": contributors, "repo": repo},
                                       {"skill": "repo-monitor"})

            elif action == "branches":
                data = self._gh(f"/repos/{repo}/branches?per_page=20")
                branches = [{"name": b["name"], "protected": b.get("protected", False)}
                            for b in data[:20]]
                return AlgorithmResult("success", {"branches": branches, "repo": repo}, {"skill": "repo-monitor"})

            return AlgorithmResult("failure", None, {"error": "action: events/commits/stats/releases/contributors/branches"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "repo": repo})
