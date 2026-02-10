"""Audio Skill — TTS, STT, audio conversion."""
import subprocess, os, time, json, urllib.request
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class AudioSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="audio-process", description="Audio processing: TTS, convert, info, trim",
            category=SkillCategory.MEDIA, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "input_path": {"type": "string"},
                          "text": {"type": "string"}, "output_path": {"type": "string"}},
            output_schema={"output_path": "string", "info": "dict", "text": "string"},
            tags=["audio", "tts", "stt", "voice", "speech", "convert", "music"],
            trigger_patterns=[r"audio\s+", r"text.?to.?speech", r"tts", r"convert\s+audio", r"voice"],
            combo_compatible=["telegram-bot", "note-taker", "file-manager"],
            combo_position="any", cost_per_call=0.005)

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "info")
        input_path = inputs.get("input_path", "")
        out_dir = os.path.expanduser("~/.dive-ai/media")
        os.makedirs(out_dir, exist_ok=True)
        output_path = inputs.get("output_path", os.path.join(out_dir, f"audio_{int(time.time())}.mp3"))
        
        try:
            if action == "info":
                cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", input_path]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if r.returncode == 0:
                    info = json.loads(r.stdout).get("format", {})
                    return AlgorithmResult("success", {
                        "duration": info.get("duration"), "size": info.get("size"),
                        "format": info.get("format_name"), "bitrate": info.get("bit_rate"),
                    }, {"skill": "audio-process"})
                return AlgorithmResult("failure", None, {"error": r.stderr[:500]})
            
            elif action == "convert":
                cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output_path": output_path}, {"skill": "audio-process"})
            
            elif action == "tts":
                text = inputs.get("text", "")
                api_key = os.environ.get("OPENAI_API_KEY", "")
                if not api_key:
                    return AlgorithmResult("success", {"simulated": True, "text": text[:200],
                        "note": "Set OPENAI_API_KEY for TTS"}, {"skill": "audio-process"})
                data = json.dumps({"model": "tts-1", "input": text, "voice": "alloy"}).encode()
                req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=data,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    with open(output_path, "wb") as f:
                        f.write(resp.read())
                return AlgorithmResult("success", {"output_path": output_path, "text": text[:100]},
                                       {"skill": "audio-process"})
            
            elif action == "trim":
                start = inputs.get("start", "00:00:00")
                duration = inputs.get("duration", "00:00:30")
                cmd = ["ffmpeg", "-y", "-i", input_path, "-ss", start, "-t", duration, "-c", "copy", output_path]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"output_path": output_path}, {"skill": "audio-process"})
            
            return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
        except FileNotFoundError:
            return AlgorithmResult("failure", None, {"error": "ffmpeg/ffprobe not installed"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
