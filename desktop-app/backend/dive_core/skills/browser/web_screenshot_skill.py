"""Web Screenshot Skill — Take screenshots of URLs or desktop."""
import subprocess
import os
import base64
import time
from typing import Dict, Any, Optional
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class WebScreenshotSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="web-screenshot", description="Capture screenshot of URL or current desktop",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"url": {"type": "string"}, "desktop": {"type": "boolean"}},
            output_schema={"image_path": "string", "image_base64": "string"},
            tags=["screenshot", "capture", "image", "visual"],
            trigger_patterns=[r"screenshot", r"capture\s+screen", r"snap\s+page"],
            combo_compatible=["web-scrape", "data-analyzer"],
            combo_position="any", cost_per_call=0.0,
        )

    def _execute(self, inputs, context=None):
        desktop = inputs.get("desktop", False)
        url = inputs.get("url", "")
        
        if desktop or not url:
            # Desktop screenshot via pyautogui
            try:
                import pyautogui
                screenshot_dir = os.path.expanduser("~/.dive-ai/screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                fname = f"screen_{int(time.time())}.png"
                fpath = os.path.join(screenshot_dir, fname)
                img = pyautogui.screenshot()
                img.save(fpath)
                
                with open(fpath, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                
                return AlgorithmResult("success", {
                    "image_path": fpath, "image_base64": b64[:100] + "...",
                    "type": "desktop", "size": os.path.getsize(fpath),
                }, {"skill": "web-screenshot"})
            except Exception as e:
                return AlgorithmResult("failure", None, {"error": str(e), "skill": "web-screenshot"})
        else:
            # URL screenshot — use Edge/Chrome in headless mode
            screenshot_dir = os.path.expanduser("~/.dive-ai/screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            fname = f"web_{int(time.time())}.png"
            fpath = os.path.join(screenshot_dir, fname)
            
            # Try msedge first (Windows), then chrome
            browsers = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            ]
            browser = None
            for b in browsers:
                if os.path.exists(b):
                    browser = b
                    break
            
            if not browser:
                return AlgorithmResult("failure", None, {"error": "No browser found", "skill": "web-screenshot"})
            
            try:
                subprocess.run([
                    browser, "--headless", "--disable-gpu",
                    f"--screenshot={fpath}", f"--window-size=1920,1080", url
                ], timeout=30, capture_output=True)
                
                if os.path.exists(fpath):
                    return AlgorithmResult("success", {
                        "image_path": fpath, "type": "url", "url": url,
                        "size": os.path.getsize(fpath),
                    }, {"skill": "web-screenshot"})
                else:
                    return AlgorithmResult("failure", None, {"error": "Screenshot not saved"})
            except Exception as e:
                return AlgorithmResult("failure", None, {"error": str(e)})
