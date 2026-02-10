"""Browser Skill — Headless browser via urllib/subprocess."""
import subprocess
import urllib.request
import json
from typing import Dict, Any, Optional
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ...specs import VerificationResult
from ..skill_spec import SkillSpec, SkillCategory


def _verify_browse(data):
    if not data or not isinstance(data, dict):
        return VerificationResult(False, 0.0, "No data", {})
    has_content = bool(data.get("content") or data.get("html"))
    return VerificationResult(has_content, 1.0 if has_content else 0.0,
                              "Content retrieved" if has_content else "Empty response",
                              {"length": len(str(data.get("content", "")))})


class BrowserSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="web-browse", description="Fetch webpage content via HTTP",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"url": {"type": "string", "required": True}},
            output_schema={"content": "string", "status_code": "integer"},
            tags=["browser", "web", "http", "fetch"],
            trigger_patterns=[r"browse\s", r"open\s+url", r"fetch\s+page", r"visit\s"],
            combo_compatible=["web-scrape", "web-screenshot", "data-analyzer"],
            combo_position="start", cost_per_call=0.0,
            verifier=_verify_browse,
        )

    def _execute(self, inputs, context=None):
        url = inputs.get("url", "")
        if not url.startswith("http"):
            url = "https://" + url
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="replace")[:50000]
                return AlgorithmResult("success", {"content": content, "status_code": resp.status, "url": url},
                                       {"skill": "web-browse", "bytes": len(content)})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "skill": "web-browse"})
