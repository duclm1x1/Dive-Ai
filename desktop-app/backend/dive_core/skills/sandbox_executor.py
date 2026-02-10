"""
Sandbox Execution Wrapper — Run untrusted code safely in Docker containers.
OpenClaw parity: sandboxed skill execution for security.
"""
import subprocess, json, os, tempfile, time, uuid
from typing import Dict, Any, Optional


class SandboxExecutor:
    """Execute code in isolated Docker containers for safety."""

    def __init__(self, image: str = "python:3.12-slim", timeout: int = 30,
                 memory_limit: str = "256m", cpu_limit: str = "0.5"):
        self.image = image
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self._containers: list = []

    def is_available(self) -> bool:
        """Check if Docker is available."""
        try:
            r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return r.returncode == 0
        except:
            return False

    def execute_code(self, code: str, language: str = "python",
                     inputs: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute code in a sandboxed container."""
        if not self.is_available():
            return {"error": "Docker not available", "sandbox": False,
                    "note": "Install Docker for sandboxed execution"}

        container_name = f"dive-sandbox-{uuid.uuid4().hex[:8]}"
        
        try:
            # Write code to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False,
                                              dir=tempfile.gettempdir()) as f:
                if inputs:
                    f.write(f"import json\ninputs = json.loads('''{json.dumps(inputs)}''')\n")
                f.write(code)
                code_path = f.name

            # Run in Docker
            cmd = [
                "docker", "run",
                "--name", container_name,
                "--rm",
                "--memory", self.memory_limit,
                "--cpus", self.cpu_limit,
                "--network", "none",  # No network access
                "--read-only",        # Read-only filesystem
                "--tmpfs", "/tmp:rw,size=64m",
                "-v", f"{code_path}:/app/run.py:ro",
                self.image,
                "python", "/app/run.py",
            ]

            start = time.time()
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            duration = round(time.time() - start, 3)

            return {
                "success": r.returncode == 0,
                "stdout": r.stdout[:5000],
                "stderr": r.stderr[:2000],
                "exit_code": r.returncode,
                "duration": duration,
                "sandbox": True,
                "container": container_name,
                "limits": {"memory": self.memory_limit, "cpu": self.cpu_limit,
                           "network": "none", "filesystem": "read-only"},
            }
        except subprocess.TimeoutExpired:
            # Kill the container
            subprocess.run(["docker", "kill", container_name], capture_output=True)
            return {"error": "Execution timed out", "timeout": self.timeout, "sandbox": True}
        except Exception as e:
            return {"error": str(e), "sandbox": True}
        finally:
            # Clean up temp file
            try: os.unlink(code_path)
            except: pass

    def execute_skill(self, skill_code_path: str, inputs: Dict) -> Dict[str, Any]:
        """Execute a skill file in sandbox."""
        with open(skill_code_path, 'r') as f:
            code = f.read()

        wrapper = f"""
import json, sys
{code}

# Find the skill class
import inspect
for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    if hasattr(cls, '_execute') and name != 'BaseSkill':
        skill = cls()
        result = skill.execute(json.loads('''{json.dumps(inputs)}'''))
        print(json.dumps({{"status": result.status, "data": result.data}}))
        break
"""
        return self.execute_code(wrapper)

    def cleanup(self):
        """Remove any lingering sandbox containers."""
        try:
            r = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=dive-sandbox", "-q"],
                capture_output=True, text=True, timeout=5
            )
            containers = r.stdout.strip().split("\n")
            for c in containers:
                if c:
                    subprocess.run(["docker", "rm", "-f", c], capture_output=True, timeout=5)
        except:
            pass

    def get_stats(self) -> Dict:
        """Get sandbox system stats."""
        available = self.is_available()
        return {
            "available": available,
            "image": self.image,
            "timeout": self.timeout,
            "memory_limit": self.memory_limit,
            "cpu_limit": self.cpu_limit,
            "security": {
                "network": "disabled",
                "filesystem": "read-only",
                "tmpfs": "64MB",
            },
        }
