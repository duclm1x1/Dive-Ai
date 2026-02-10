"""Terraform/IaC Skill — Infrastructure as Code operations."""
import subprocess, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class TerraformSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="terraform", description="Terraform IaC: init, plan, apply, destroy, state",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "path": {"type": "string"},
                          "var": {"type": "dict"}, "target": {"type": "string"}},
            output_schema={"output": "string", "changes": "dict"},
            tags=["terraform", "iac", "infrastructure", "provision", "hcl", "cloud"],
            trigger_patterns=[r"terraform\s+", r"iac\s+", r"infrastructure\s+code"],
            combo_compatible=["cloud-deploy", "k8s-manager", "slack-bot"],
            combo_position="end")

    def _tf(self, args, cwd=None, timeout=120):
        return subprocess.run(["terraform"] + args, capture_output=True, text=True, timeout=timeout, cwd=cwd)

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "plan")
        path = inputs.get("path", ".")
        var_args = []
        for k, v in inputs.get("var", {}).items():
            var_args.extend(["-var", f"{k}={v}"])
        try:
            if action == "init":
                r = self._tf(["init", "-no-color"], cwd=path)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output": r.stdout[-3000:]}, {"skill": "terraform"})
            elif action == "plan":
                r = self._tf(["plan", "-no-color"] + var_args, cwd=path)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output": r.stdout[-3000:]}, {"skill": "terraform"})
            elif action == "apply":
                auto = ["-auto-approve"] if inputs.get("auto_approve") else []
                r = self._tf(["apply", "-no-color"] + auto + var_args, cwd=path)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output": r.stdout[-3000:]}, {"skill": "terraform"})
            elif action == "destroy":
                auto = ["-auto-approve"] if inputs.get("auto_approve") else []
                r = self._tf(["destroy", "-no-color"] + auto, cwd=path)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output": r.stdout[-3000:]}, {"skill": "terraform"})
            elif action == "state":
                r = self._tf(["state", "list"], cwd=path)
                resources = [l.strip() for l in r.stdout.split("\n") if l.strip()]
                return AlgorithmResult("success", {"resources": resources, "total": len(resources)}, {"skill": "terraform"})
            elif action == "output":
                r = self._tf(["output", "-json"], cwd=path)
                if r.returncode == 0:
                    return AlgorithmResult("success", json.loads(r.stdout), {"skill": "terraform"})
            elif action == "validate":
                r = self._tf(["validate", "-json"], cwd=path)
                if r.returncode == 0:
                    return AlgorithmResult("success", json.loads(r.stdout), {"skill": "terraform"})
            elif action == "fmt":
                r = self._tf(["fmt", "-recursive"], cwd=path)
                return AlgorithmResult("success", {"formatted": r.stdout.strip().split("\n")}, {"skill": "terraform"})
            return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
        except FileNotFoundError:
            return AlgorithmResult("failure", None, {"error": "terraform CLI not installed"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
