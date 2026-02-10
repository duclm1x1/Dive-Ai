"""Docker Operations Skill — Build, run, manage containers."""
import subprocess
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class DockerSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="docker-ops", description="Docker: ps, images, build, run, stop, logs",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "image": {"type": "string"},
                          "container": {"type": "string"}, "path": {"type": "string"}},
            output_schema={"output": "string", "success": "boolean"},
            tags=["docker", "container", "build", "deploy"],
            trigger_patterns=[r"docker\s+", r"container", r"build\s+image"],
            combo_compatible=["git-ops", "webhook-sender", "system-info"],
            combo_position="middle")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "ps")
        image = inputs.get("image", "")
        container = inputs.get("container", "")
        path = inputs.get("path", ".")
        
        try:
            if action == "ps":
                cmd = ["docker", "ps", "-a", "--format", "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"]
            elif action == "images":
                cmd = ["docker", "images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"]
            elif action == "build" and image:
                cmd = ["docker", "build", "-t", image, path]
            elif action == "run" and image:
                cmd = ["docker", "run", "-d", image]
            elif action == "stop" and container:
                cmd = ["docker", "stop", container]
            elif action == "logs" and container:
                cmd = ["docker", "logs", "--tail", "50", container]
            elif action == "stats":
                cmd = ["docker", "stats", "--no-stream", "--format", "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"]
            else:
                return AlgorithmResult("failure", None, {"error": f"Need action+params: {action}"})

            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return AlgorithmResult("success" if r.returncode == 0 else "failure",
                {"output": (r.stdout + r.stderr)[:5000], "action": action, "returncode": r.returncode},
                {"skill": "docker-ops"})
        except FileNotFoundError:
            return AlgorithmResult("failure", None, {"error": "Docker not installed or not in PATH"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
