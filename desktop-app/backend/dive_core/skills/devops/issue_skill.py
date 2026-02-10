"""Issue Tracker Skill — GitHub Issues management."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class IssueSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="issue-tracker", description="GitHub Issues: list, create, close, comment",
            category=SkillCategory.GIT, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "repo": {"type": "string"},
                          "title": {"type": "string"}, "body": {"type": "string"}, "issue_number": {"type": "integer"}},
            output_schema={"issues": "list", "issue": "dict"},
            tags=["issue", "github", "bug", "feature", "track"],
            trigger_patterns=[r"issue\s+", r"bug\s+report", r"create\s+issue", r"close\s+issue"],
            combo_compatible=["git-ops", "pr-manager", "telegram-bot"],
            combo_position="any")

    def _execute(self, inputs, context=None):
        token = os.environ.get("GITHUB_TOKEN", "")
        repo = inputs.get("repo", "")
        action = inputs.get("action", "list")
        
        if not token:
            return AlgorithmResult("success", {"simulated": True, "action": action,
                "note": "Set GITHUB_TOKEN env var."}, {"skill": "issue-tracker"})
        
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json",
                   "User-Agent": "DiveAI/29.7"}
        base = f"https://api.github.com/repos/{repo}"
        
        try:
            if action == "list":
                req = urllib.request.Request(f"{base}/issues?state=open&per_page=15", headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    issues = json.loads(resp.read())
                data = [{"number": i["number"], "title": i["title"], "state": i["state"],
                         "user": i["user"]["login"], "labels": [l["name"] for l in i.get("labels", [])]}
                        for i in issues if "pull_request" not in i]
                return AlgorithmResult("success", {"issues": data, "total": len(data)}, {"skill": "issue-tracker"})
            
            elif action == "create":
                data = json.dumps({"title": inputs.get("title", ""), "body": inputs.get("body", ""),
                                   "labels": inputs.get("labels", [])}).encode()
                req = urllib.request.Request(f"{base}/issues", data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    issue = json.loads(resp.read())
                return AlgorithmResult("success", {"issue": {"number": issue["number"], "url": issue["html_url"]}},
                                       {"skill": "issue-tracker"})
            
            elif action == "close":
                num = inputs.get("issue_number", 1)
                data = json.dumps({"state": "closed"}).encode()
                req = urllib.request.Request(f"{base}/issues/{num}", data=data, headers=headers, method="PATCH")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    issue = json.loads(resp.read())
                return AlgorithmResult("success", {"closed": num}, {"skill": "issue-tracker"})
            
            return AlgorithmResult("failure", None, {"error": "action: list/create/close"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
