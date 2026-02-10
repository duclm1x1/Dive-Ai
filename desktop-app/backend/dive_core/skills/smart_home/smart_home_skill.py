"""Smart Home Skill — Home Assistant integration."""
import urllib.request, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SmartHomeSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="smart-home", description="Control smart home via Home Assistant API",
            category=SkillCategory.SMART_HOME, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "entity_id": {"type": "string"},
                          "service": {"type": "string"}, "data": {"type": "dict"}},
            output_schema={"state": "string", "entities": "list"},
            tags=["home", "smart", "light", "switch", "automation", "iot", "hass"],
            trigger_patterns=[r"turn\s+(on|off)", r"light\s+", r"smart\s+home", r"home\s+assistant"],
            combo_compatible=["scheduler", "telegram-bot"], combo_position="end")

    def _execute(self, inputs, context=None):
        ha_url = os.environ.get("HA_URL", "http://homeassistant.local:8123")
        ha_token = os.environ.get("HA_TOKEN", "")
        action = inputs.get("action", "states")
        entity_id = inputs.get("entity_id", "")
        
        if not ha_token:
            return AlgorithmResult("success", {"simulated": True, "action": action, "entity_id": entity_id,
                "note": "Set HA_URL and HA_TOKEN for Home Assistant."}, {"skill": "smart-home"})
        
        headers = {"Authorization": f"Bearer {ha_token}", "Content-Type": "application/json"}
        try:
            if action == "states":
                url = f"{ha_url}/api/states"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    states = json.loads(resp.read())
                entities = [{"entity_id": s["entity_id"], "state": s["state"],
                            "name": s.get("attributes", {}).get("friendly_name", "")}
                           for s in states[:30]]
                return AlgorithmResult("success", {"entities": entities, "total": len(states)}, {"skill": "smart-home"})
            
            elif action in ("turn_on", "turn_off", "toggle"):
                service = action
                domain = entity_id.split(".")[0] if "." in entity_id else "light"
                url = f"{ha_url}/api/services/{domain}/{service}"
                data = json.dumps({"entity_id": entity_id}).encode()
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read())
                return AlgorithmResult("success", {"action": service, "entity_id": entity_id, "done": True},
                                       {"skill": "smart-home"})
            
            elif action == "call_service":
                service = inputs.get("service", "")
                domain, svc = service.split(".", 1) if "." in service else (service, "")
                s_data = inputs.get("data", {})
                url = f"{ha_url}/api/services/{domain}/{svc}"
                data = json.dumps(s_data).encode()
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read())
                return AlgorithmResult("success", {"service": service, "result": str(result)[:500]},
                                       {"skill": "smart-home"})
            
            return AlgorithmResult("failure", None, {"error": "action: states/turn_on/turn_off/toggle/call_service"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
