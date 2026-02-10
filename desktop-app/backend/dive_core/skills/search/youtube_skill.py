"""YouTube Search Skill — Search and get video info."""
import urllib.request, urllib.parse, json, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class YoutubeSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="youtube-search", description="Search YouTube videos",
            category=SkillCategory.SEARCH, version="1.0.0",
            input_schema={"query": {"type": "string", "required": True}},
            output_schema={"videos": "list"},
            tags=["youtube", "video", "watch", "tutorial"],
            trigger_patterns=[r"youtube", r"video\s+about", r"watch"],
            combo_compatible=["note-taker", "deep-research"], combo_position="start")

    def _execute(self, inputs, context=None):
        query = inputs.get("query", "")
        try:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            video_ids = re.findall(r'"videoId":"([^"]{11})"', html)
            titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"', html)
            seen = set()
            videos = []
            for vid, title in zip(video_ids, titles):
                if vid not in seen and len(videos) < 10:
                    seen.add(vid)
                    videos.append({"id": vid, "title": title, "url": f"https://youtu.be/{vid}"})
            return AlgorithmResult("success", {"videos": videos, "total": len(videos), "query": query},
                                   {"skill": "youtube-search"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
