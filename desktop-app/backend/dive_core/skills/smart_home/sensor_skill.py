"""Sensor Monitor Skill — Read system sensors (temp, battery, etc)."""
import platform, subprocess
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SensorSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="sensor-monitor", description="Monitor system sensors: battery, temperature, power",
            category=SkillCategory.SMART_HOME, version="1.0.0",
            input_schema={"sensor": {"type": "string"}},
            output_schema={"battery": "dict", "temperature": "dict", "sensors": "list"},
            tags=["sensor", "battery", "temperature", "power", "monitor", "health"],
            trigger_patterns=[r"battery", r"temperature", r"sensor\s+", r"power\s+status"],
            combo_compatible=["system-info", "scheduler", "telegram-bot"], combo_position="start")

    def _execute(self, inputs, context=None):
        sensor = inputs.get("sensor", "all")
        result = {}
        
        # Try psutil first
        try:
            import psutil
            if sensor in ("all", "battery"):
                bat = psutil.sensors_battery()
                if bat:
                    result["battery"] = {"percent": bat.percent, "plugged": bat.power_plugged,
                                         "secs_left": bat.secsleft if bat.secsleft != -1 else None}
            if sensor in ("all", "temperature"):
                try:
                    temps = psutil.sensors_temperatures()
                    result["temperatures"] = {k: [{"label": t.label, "current": t.current, "high": t.high}
                                                   for t in v] for k, v in temps.items()} if temps else {}
                except: result["temperatures"] = {"note": "Not available on this platform"}
            if sensor in ("all", "fans"):
                try:
                    fans = psutil.sensors_fans()
                    result["fans"] = {k: [{"label": f.label, "current": f.current} for f in v]
                                      for k, v in fans.items()} if fans else {}
                except: pass
        except ImportError:
            # Fallback for Windows without psutil
            if platform.system() == "Windows":
                try:
                    r = subprocess.run(["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining,BatteryStatus"],
                                      capture_output=True, text=True, timeout=5)
                    result["battery_raw"] = r.stdout.strip()
                except: pass
            result["note"] = "Install psutil for detailed sensor data: pip install psutil"
        
        if not result:
            result = {"note": "No sensor data available on this platform", "sensor": sensor}
        
        return AlgorithmResult("success", result, {"skill": "sensor-monitor"})
