"""Process Manager Skill — List, kill, monitor processes."""
import subprocess, platform
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class ProcessSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="process-manager", description="List, monitor, and manage system processes",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "pid": {"type": "integer"},
                          "name": {"type": "string"}},
            output_schema={"processes": "list", "result": "string"},
            tags=["process", "kill", "task", "monitor", "pid"],
            trigger_patterns=[r"process", r"kill\s+", r"running\s+tasks", r"task\s*manager"],
            combo_compatible=["system-info", "webhook-sender"], combo_position="any")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "list")
        pid = inputs.get("pid")
        name = inputs.get("name", "")
        
        try:
            if action == "list":
                if platform.system() == "Windows":
                    cmd = ["tasklist", "/FO", "CSV", "/NH"]
                else:
                    cmd = ["ps", "aux", "--sort=-pmem"]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                lines = r.stdout.strip().split("\n")[:30]
                return AlgorithmResult("success", {"processes": lines, "total": len(lines)}, {"skill": "process-manager"})
            
            elif action == "find" and name:
                if platform.system() == "Windows":
                    cmd = ["tasklist", "/FI", f"IMAGENAME eq {name}*", "/FO", "CSV"]
                else:
                    cmd = ["pgrep", "-la", name]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return AlgorithmResult("success", {"output": r.stdout[:3000], "found": bool(r.stdout.strip())},
                                       {"skill": "process-manager"})
            
            elif action == "kill" and pid:
                if platform.system() == "Windows":
                    cmd = ["taskkill", "/PID", str(pid), "/F"]
                else:
                    cmd = ["kill", "-9", str(pid)]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output": r.stdout + r.stderr, "pid": pid}, {"skill": "process-manager"})
            else:
                return AlgorithmResult("failure", None, {"error": "Need action=list/find/kill + params"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
