"""CI/CD Skill — Run CI/CD pipelines via GitHub Actions."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CICDSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="ci-cd", description="Trigger and monitor GitHub Actions CI/CD pipelines",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "repo": {"type": "string"},
                          "workflow": {"type": "string"}, "branch": {"type": "string"}},
            output_schema={"runs": "list", "status": "string"},
            tags=["ci", "cd", "pipeline", "deploy", "actions", "workflow", "build"],
            trigger_patterns=[r"ci.?cd", r"pipeline", r"deploy\s+", r"github\s+actions", r"trigger\s+build"],
            combo_compatible=["git-ops", "pr-manager", "telegram-bot"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        token = os.environ.get("GITHUB_TOKEN", "")
        repo = inputs.get("repo", "")
        action = inputs.get("action", "list")
        
        if not token:
            return AlgorithmResult("success", {"simulated": True, "action": action,
                "note": "Set GITHUB_TOKEN env var."}, {"skill": "ci-cd"})
        
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json",
                   "User-Agent": "DiveAI/29.7"}
        base = f"https://api.github.com/repos/{repo}"
        
        try:
            if action == "list":
                req = urllib.request.Request(f"{base}/actions/runs?per_page=10", headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                runs = [{"id": r["id"], "name": r["name"], "status": r["status"],
                         "conclusion": r.get("conclusion"), "branch": r["head_branch"],
                         "created": r["created_at"]} for r in data.get("workflow_runs", [])]
                return AlgorithmResult("success", {"runs": runs, "total": len(runs)}, {"skill": "ci-cd"})
            
            elif action == "trigger":
                workflow = inputs.get("workflow", "")
                branch = inputs.get("branch", "main")
                url = f"{base}/actions/workflows/{workflow}/dispatches"
                data = json.dumps({"ref": branch}).encode()
                req = urllib.request.Request(url, data=data, headers=headers)
                urllib.request.urlopen(req, timeout=10)
                return AlgorithmResult("success", {"triggered": True, "workflow": workflow, "branch": branch},
                                       {"skill": "ci-cd"})
            
            elif action == "status":
                req = urllib.request.Request(f"{base}/actions/runs?per_page=1", headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                latest = data.get("workflow_runs", [{}])[0]
                return AlgorithmResult("success", {
                    "latest_run": latest.get("name"), "status": latest.get("status"),
                    "conclusion": latest.get("conclusion"), "url": latest.get("html_url"),
                }, {"skill": "ci-cd"})
            
            return AlgorithmResult("failure", None, {"error": "action: list/trigger/status"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
