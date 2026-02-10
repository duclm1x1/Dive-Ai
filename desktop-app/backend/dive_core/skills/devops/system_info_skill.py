"""System Info Skill — CPU, RAM, disk, network stats."""
import platform, os, subprocess, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SystemInfoSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="system-info", description="Get system information: CPU, RAM, disk, OS",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"metrics": {"type": "list"}},
            output_schema={"system": "dict"},
            tags=["system", "cpu", "ram", "disk", "memory", "info", "health"],
            trigger_patterns=[r"system\s+info", r"cpu\s+usage", r"ram", r"disk\s+space", r"health\s+check"],
            combo_compatible=["data-analyzer", "telegram-bot", "webhook-sender"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        try:
            info = {
                "os": platform.system(), "os_version": platform.version(),
                "arch": platform.machine(), "hostname": platform.node(),
                "python": platform.python_version(),
                "cpu_count": os.cpu_count(),
            }
            # Disk usage
            try:
                import shutil
                total, used, free = shutil.disk_usage("/")
                info["disk"] = {"total_gb": round(total/1e9, 1), "used_gb": round(used/1e9, 1),
                                "free_gb": round(free/1e9, 1), "percent": round(used/total*100, 1)}
            except: pass
            
            # Try psutil
            try:
                import psutil
                info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
                mem = psutil.virtual_memory()
                info["memory"] = {"total_gb": round(mem.total/1e9, 1), "used_gb": round(mem.used/1e9, 1),
                                  "percent": mem.percent}
                info["boot_time"] = time.ctime(psutil.boot_time())
            except ImportError:
                # Fallback: Windows systeminfo
                if platform.system() == "Windows":
                    try:
                        r = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/format:csv"],
                                          capture_output=True, text=True, timeout=5)
                        info["memory_raw"] = r.stdout.strip()
                    except: pass
            
            return AlgorithmResult("success", info, {"skill": "system-info"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
