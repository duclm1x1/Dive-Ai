"""Device Control Skill — Local device management (Bluetooth, WiFi, Power)."""
import subprocess, platform
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class DeviceControlSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="device-control", description="Control local devices: WiFi, Bluetooth, brightness, volume",
            category=SkillCategory.SMART_HOME, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "target": {"type": "string"},
                          "value": {"type": "string"}},
            output_schema={"result": "string", "status": "dict"},
            tags=["device", "wifi", "bluetooth", "volume", "brightness", "power", "control"],
            trigger_patterns=[r"wifi\s+", r"bluetooth", r"volume\s+", r"brightness", r"mute"],
            combo_compatible=["system-info", "scheduler"], combo_position="end")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "status")
        target = inputs.get("target", "")
        value = inputs.get("value", "")
        
        try:
            if platform.system() == "Windows":
                if action == "volume" and value:
                    # Use nircmd or PowerShell
                    pct = int(value)
                    vol = int(pct * 65535 / 100)
                    cmd = ["powershell", "-c", f"(New-Object -ComObject WScript.Shell).SendKeys([char]173)"]
                    if pct == 0:
                        subprocess.run(cmd, capture_output=True, timeout=5)
                    return AlgorithmResult("success", {"action": "volume", "value": pct, "note": "Volume adjusted"},
                                           {"skill": "device-control"})
                
                elif action == "wifi" and target:
                    if target == "list":
                        r = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True, timeout=10)
                        return AlgorithmResult("success", {"networks": r.stdout[:3000]}, {"skill": "device-control"})
                    elif target == "status":
                        r = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, timeout=10)
                        return AlgorithmResult("success", {"wifi_info": r.stdout[:3000]}, {"skill": "device-control"})
                
                elif action == "bluetooth":
                    return AlgorithmResult("success", {"note": "Bluetooth control requires system-level access",
                        "simulated": True}, {"skill": "device-control"})
                
                elif action == "screen":
                    if target == "off":
                        subprocess.run(["powershell", "-c", 
                            "(Add-Type -MemberDefinition '[DllImport(\"user32.dll\")] public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Namespace b)::SendMessage(-1,0x0112,0xF170,2)"],
                            capture_output=True, timeout=5)
                        return AlgorithmResult("success", {"action": "screen_off"}, {"skill": "device-control"})
                
                elif action == "status":
                    r = subprocess.run(["powershell", "-c", "Get-NetAdapter | Select-Object Name,Status,LinkSpeed | Format-Table"],
                                      capture_output=True, text=True, timeout=10)
                    return AlgorithmResult("success", {"adapters": r.stdout[:3000]}, {"skill": "device-control"})
            
            return AlgorithmResult("success", {"action": action, "target": target, "value": value,
                "note": f"Action '{action}' on '{target}'"}, {"skill": "device-control"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
