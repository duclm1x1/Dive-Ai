"""Form Fill Skill — Detect and fill web forms."""
from typing import Dict, Any, Optional
import re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class FormFillSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="form-fill", description="Detect and auto-fill web form fields",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"html": {"type": "string"}, "fields": {"type": "dict"}},
            output_schema={"filled_fields": "dict", "form_action": "string"},
            tags=["form", "fill", "input", "automation"],
            trigger_patterns=[r"fill\s+form", r"fill\s+in", r"auto.?fill"],
            combo_compatible=["web-browse", "web-screenshot"],
            combo_position="middle", cost_per_call=0.0,
        )

    def _execute(self, inputs, context=None):
        html = inputs.get("html") or inputs.get("content") or inputs.get("data", "")
        user_fields = inputs.get("fields", {})
        
        # Find form fields in HTML
        input_fields = re.findall(
            r'<input[^>]*name=["\']([^"\']+)["\'][^>]*type=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        input_fields += re.findall(
            r'<input[^>]*type=["\']([^"\']+)["\'][^>]*name=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        textarea_fields = re.findall(r'<textarea[^>]*name=["\']([^"\']+)["\']', html)
        select_fields = re.findall(r'<select[^>]*name=["\']([^"\']+)["\']', html)
        
        # Form action
        form_action = ""
        action_match = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', html)
        if action_match:
            form_action = action_match.group(1)
        
        # Map detected fields
        detected = {}
        for name, ftype in input_fields:
            detected[name] = {"type": ftype, "value": user_fields.get(name, "")}
        for name in textarea_fields:
            detected[name] = {"type": "textarea", "value": user_fields.get(name, "")}
        for name in select_fields:
            detected[name] = {"type": "select", "value": user_fields.get(name, "")}

        return AlgorithmResult("success", {
            "filled_fields": detected, "form_action": form_action,
            "total_fields": len(detected), "filled_count": sum(1 for v in detected.values() if v["value"]),
        }, {"skill": "form-fill"})
