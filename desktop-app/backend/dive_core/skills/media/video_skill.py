"""Video Processing Skill — Trim, convert, extract frames."""
import subprocess, os, time, json
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class VideoSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="video-process", description="Process videos: trim, convert, extract frames, info",
            category=SkillCategory.MEDIA, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "input_path": {"type": "string"},
                          "output_path": {"type": "string"}, "start": {"type": "string"}, "duration": {"type": "string"}},
            output_schema={"output_path": "string", "info": "dict"},
            tags=["video", "convert", "trim", "frames", "ffmpeg", "media"],
            trigger_patterns=[r"video\s+", r"trim\s+video", r"convert\s+video", r"extract\s+frames"],
            combo_compatible=["file-manager", "image-analyze", "telegram-bot"],
            combo_position="middle")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "info")
        input_path = inputs.get("input_path", "")
        out_dir = os.path.expanduser("~/.dive-ai/media")
        os.makedirs(out_dir, exist_ok=True)
        output_path = inputs.get("output_path", os.path.join(out_dir, f"out_{int(time.time())}.mp4"))
        
        try:
            if action == "info":
                cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", input_path]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if r.returncode == 0:
                    info = json.loads(r.stdout)
                    fmt = info.get("format", {})
                    return AlgorithmResult("success", {
                        "duration": fmt.get("duration"), "size": fmt.get("size"),
                        "format": fmt.get("format_name"), "streams": len(info.get("streams", [])),
                    }, {"skill": "video-process"})
                return AlgorithmResult("failure", None, {"error": r.stderr[:500]})
            
            elif action == "trim":
                start = inputs.get("start", "00:00:00")
                duration = inputs.get("duration", "00:00:30")
                cmd = ["ffmpeg", "-y", "-i", input_path, "-ss", start, "-t", duration, "-c", "copy", output_path]
            elif action == "convert":
                cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
            elif action == "frames":
                frame_dir = output_path.replace(".mp4", "_frames")
                os.makedirs(frame_dir, exist_ok=True)
                cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "fps=1", os.path.join(frame_dir, "frame_%04d.png")]
                output_path = frame_dir
            elif action == "thumbnail":
                output_path = output_path.replace(".mp4", ".jpg")
                cmd = ["ffmpeg", "-y", "-i", input_path, "-ss", "00:00:01", "-vframes", "1", output_path]
            else:
                return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
            
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return AlgorithmResult("success" if r.returncode == 0 else "failure",
                {"output_path": output_path, "action": action}, {"skill": "video-process"})
        except FileNotFoundError:
            return AlgorithmResult("failure", None, {"error": "ffmpeg/ffprobe not installed"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
