"""PR Manager Skill — GitHub Pull Request management."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class PRSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="pr-manager", description="GitHub PR management: list, create, review, merge",
            category=SkillCategory.GIT, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "repo": {"type": "string"},
                          "title": {"type": "string"}, "body": {"type": "string"}, "pr_number": {"type": "integer"}},
            output_schema={"prs": "list", "pr": "dict"},
            tags=["pr", "pull-request", "github", "review", "merge"],
            trigger_patterns=[r"pull\s+request", r"pr\s+", r"merge\s+", r"create\s+pr"],
            combo_compatible=["git-ops", "code-review", "telegram-bot"],
            combo_position="any")

    def _execute(self, inputs, context=None):
        token = os.environ.get("GITHUB_TOKEN", "")
        repo = inputs.get("repo", "")  # e.g., "duclm1x1/Dive-AI2"
        action = inputs.get("action", "list")
        
        if not token:
            return AlgorithmResult("success", {"simulated": True, "action": action, "repo": repo,
                "note": "Set GITHUB_TOKEN env var."}, {"skill": "pr-manager"})
        
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json",
                   "User-Agent": "DiveAI/29.7"}
        base = f"https://api.github.com/repos/{repo}"
        
        try:
            if action == "list":
                url = f"{base}/pulls?state=open&per_page=10"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    prs = json.loads(resp.read())
                data = [{"number": p["number"], "title": p["title"], "state": p["state"],
                         "user": p["user"]["login"], "created": p["created_at"]} for p in prs]
                return AlgorithmResult("success", {"prs": data, "total": len(data)}, {"skill": "pr-manager"})
            
            elif action == "create":
                data = json.dumps({"title": inputs.get("title", ""), "body": inputs.get("body", ""),
                                   "head": inputs.get("head", ""), "base": inputs.get("base", "main")}).encode()
                req = urllib.request.Request(f"{base}/pulls", data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    pr = json.loads(resp.read())
                return AlgorithmResult("success", {"pr": {"number": pr["number"], "url": pr["html_url"]}},
                                       {"skill": "pr-manager"})
            
            elif action == "get":
                num = inputs.get("pr_number", 1)
                req = urllib.request.Request(f"{base}/pulls/{num}", headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    pr = json.loads(resp.read())
                return AlgorithmResult("success", {"pr": {"number": pr["number"], "title": pr["title"],
                    "state": pr["state"], "mergeable": pr.get("mergeable"), "files": pr.get("changed_files")}},
                    {"skill": "pr-manager"})
            
            return AlgorithmResult("failure", None, {"error": "action: list/create/get"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
