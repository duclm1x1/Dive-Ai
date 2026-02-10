"""Git Operations Skill — Clone, commit, push, status, log."""
import subprocess, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class GitSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="git-ops", description="Git operations: status, log, commit, push, pull, clone",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "path": {"type": "string"},
                          "message": {"type": "string"}, "url": {"type": "string"}},
            output_schema={"output": "string", "success": "boolean"},
            tags=["git", "version", "commit", "push", "pull", "clone"],
            trigger_patterns=[r"git\s+", r"commit", r"push\s+to", r"clone\s+repo"],
            combo_compatible=["code-review", "docker-ops", "webhook-sender"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "status")
        path = inputs.get("path", os.getcwd())
        message = inputs.get("message", "Auto-commit by Dive AI")
        url = inputs.get("url", "")
        
        SAFE = {"status", "log", "diff", "branch", "remote", "show", "stash"}
        
        try:
            if action == "status":
                cmd = ["git", "status", "--short"]
            elif action == "log":
                cmd = ["git", "log", "--oneline", "-10"]
            elif action == "diff":
                cmd = ["git", "diff", "--stat"]
            elif action == "branch":
                cmd = ["git", "branch", "-a"]
            elif action == "commit":
                subprocess.run(["git", "add", "-A"], cwd=path, capture_output=True, timeout=10)
                cmd = ["git", "commit", "-m", message]
            elif action == "push":
                cmd = ["git", "push"]
            elif action == "pull":
                cmd = ["git", "pull"]
            elif action == "clone" and url:
                cmd = ["git", "clone", url, path]
            else:
                return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})

            result = subprocess.run(cmd, cwd=path, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            return AlgorithmResult("success" if success else "failure",
                {"output": output[:5000], "action": action, "returncode": result.returncode},
                {"skill": "git-ops"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
