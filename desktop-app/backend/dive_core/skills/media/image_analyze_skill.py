"""Image Analyze Skill — OCR, object detection, image description."""
import os, base64, json, urllib.request
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class ImageAnalyzeSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="image-analyze", description="Analyze images: OCR, describe, detect objects",
            category=SkillCategory.MEDIA, version="1.0.0",
            input_schema={"image_path": {"type": "string"}, "url": {"type": "string"}, "action": {"type": "string"}},
            output_schema={"description": "string", "text": "string", "objects": "list"},
            tags=["image", "analyze", "ocr", "detect", "describe", "vision"],
            trigger_patterns=[r"analyze\s+image", r"what.?s\s+in", r"ocr", r"describe\s+image"],
            combo_compatible=["web-screenshot", "note-taker", "email-send"],
            combo_position="middle", cost_per_call=0.01)

    def _execute(self, inputs, context=None):
        image_path = inputs.get("image_path", "")
        url = inputs.get("url", "")
        action = inputs.get("action", "describe")
        
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            # Basic local analysis without API
            info = {}
            if image_path and os.path.exists(image_path):
                info["file"] = image_path
                info["size_bytes"] = os.path.getsize(image_path)
                ext = os.path.splitext(image_path)[1].lower()
                info["format"] = ext
                # Try to read image dimensions via header bytes
                try:
                    with open(image_path, "rb") as f:
                        header = f.read(32)
                    if header[:8] == b'\x89PNG\r\n\x1a\n':
                        import struct
                        w, h = struct.unpack('>II', header[16:24])
                        info["width"], info["height"] = w, h
                except: pass
                info["simulated"] = True
                info["note"] = "Set OPENAI_API_KEY for AI-powered analysis."
            elif url:
                info = {"url": url, "simulated": True, "note": "Set OPENAI_API_KEY"}
            else:
                return AlgorithmResult("failure", None, {"error": "No image_path or url"})
            return AlgorithmResult("success", info, {"skill": "image-analyze"})
        
        try:
            # Use GPT-4 Vision
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            elif url:
                image_content = {"type": "image_url", "image_url": {"url": url}}
            else:
                return AlgorithmResult("failure", None, {"error": "No image provided"})
            
            data = json.dumps({"model": "gpt-4o", "messages": [{"role": "user", "content": [
                {"type": "text", "text": f"Action: {action}. Describe this image in detail."},
                image_content]}], "max_tokens": 500}).encode()
            req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            desc = result["choices"][0]["message"]["content"]
            return AlgorithmResult("success", {"description": desc, "action": action}, {"skill": "image-analyze"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
