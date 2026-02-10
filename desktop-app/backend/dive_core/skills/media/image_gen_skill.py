"""Image Generation Skill — Generate images via API (DALL-E, Stable Diffusion)."""
import urllib.request, json, os, base64, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class ImageGenSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="image-gen", description="Generate images from text prompts via AI APIs",
            category=SkillCategory.MEDIA, version="1.0.0",
            input_schema={"prompt": {"type": "string", "required": True}, "size": {"type": "string"},
                          "model": {"type": "string"}, "save_path": {"type": "string"}},
            output_schema={"image_path": "string", "url": "string"},
            tags=["image", "generate", "ai", "art", "picture", "dalle"],
            trigger_patterns=[r"generate\s+image", r"create\s+image", r"draw\s+", r"image\s+of"],
            combo_compatible=["prompt-optimizer", "telegram-bot", "discord-bot"],
            combo_position="end", cost_per_call=0.02)

    def _execute(self, inputs, context=None):
        prompt = inputs.get("prompt", "")
        size = inputs.get("size", "1024x1024")
        model = inputs.get("model", "dall-e-3")
        save_dir = os.path.expanduser("~/.dive-ai/generated")
        os.makedirs(save_dir, exist_ok=True)
        save_path = inputs.get("save_path", os.path.join(save_dir, f"img_{int(time.time())}.png"))
        
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return AlgorithmResult("success", {
                "simulated": True, "prompt": prompt[:200], "size": size, "model": model,
                "note": "Set OPENAI_API_KEY to generate real images.",
            }, {"skill": "image-gen"})
        
        try:
            url = "https://api.openai.com/v1/images/generations"
            data = json.dumps({"model": model, "prompt": prompt, "size": size, "n": 1,
                               "response_format": "b64_json"}).encode()
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            
            b64 = result["data"][0]["b64_json"]
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(b64))
            
            return AlgorithmResult("success", {"image_path": save_path, "prompt": prompt[:100], "model": model},
                                   {"skill": "image-gen"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
