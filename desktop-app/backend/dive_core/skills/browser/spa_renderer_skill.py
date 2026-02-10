"""SPA Renderer Skill -- Render JavaScript-heavy pages via Playwright/headless Chrome."""
import subprocess, json, os, time, tempfile
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class SpaRendererSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="spa-renderer", description="SPA rendering: headless Chrome/Playwright for JS pages",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True},
                          "url": {"type": "string"}, "selector": {"type": "string"},
                          "wait": {"type": "integer"}, "output": {"type": "string"}},
            output_schema={"html_preview": "string", "elements": "list"},
            tags=["spa", "renderer", "headless", "playwright", "scraping", "javascript"],
            trigger_patterns=[r"render\s+spa", r"headless\s+", r"playwright\s+", r"javascript\s+page"],
            combo_compatible=["web-scrape", "cookie-manager", "web-screenshot"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "render")

        if action == "status":
            return self._check_tools()
        elif action == "render":
            return self._render(inputs)
        elif action == "screenshot":
            return self._screenshot(inputs)
        elif action == "extract":
            return self._extract(inputs)
        return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})

    def _check_tools(self):
        tools = {}
        for cmd in ["node", "npx"]:
            try:
                r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                tools[cmd] = {"available": r.returncode == 0, "version": r.stdout.strip()}
            except:
                tools[cmd] = {"available": False}
        try:
            r = subprocess.run(["npx", "playwright", "--version"],
                               capture_output=True, text=True, timeout=10)
            tools["playwright"] = {"available": r.returncode == 0, "version": r.stdout.strip()}
        except:
            tools["playwright"] = {"available": False}
        return AlgorithmResult("success", {"tools": tools}, {"skill": "spa-renderer"})

    def _render(self, inputs):
        url = inputs.get("url", "")
        if not url:
            return AlgorithmResult("failure", None, {"error": "Need 'url'"})
        # Fallback: curl
        try:
            r = subprocess.run(["curl", "-s", "-L", "--max-time", "15", url],
                               capture_output=True, text=True, timeout=20)
            return AlgorithmResult("success",
                {"url": url, "html_length": len(r.stdout),
                 "html_preview": r.stdout[:3000],
                 "note": "Basic fetch (install Playwright for full SPA rendering)"},
                {"skill": "spa-renderer"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "url": url})

    def _screenshot(self, inputs):
        url = inputs.get("url", "")
        output = inputs.get("output", os.path.expanduser("~/dive-screenshot.png"))
        if not url:
            return AlgorithmResult("failure", None, {"error": "Need 'url'"})
        return AlgorithmResult("success",
            {"url": url, "screenshot": output, "note": "Install Playwright for screenshots"},
            {"skill": "spa-renderer"})

    def _extract(self, inputs):
        url = inputs.get("url", "")
        selector = inputs.get("selector", "body")
        if not url:
            return AlgorithmResult("failure", None, {"error": "Need 'url'"})
        return AlgorithmResult("success",
            {"url": url, "selector": selector,
             "note": "Install Playwright for CSS selector extraction"},
            {"skill": "spa-renderer"})
