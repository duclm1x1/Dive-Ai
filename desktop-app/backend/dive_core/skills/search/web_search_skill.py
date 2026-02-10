"""Web Search Skill — Multi-engine web search."""
import urllib.request
import urllib.parse
import json
import re
from typing import Dict, Any, Optional
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class WebSearchSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="web-search", description="Search the web using DuckDuckGo API",
            category=SkillCategory.SEARCH, version="1.0.0",
            input_schema={"query": {"type": "string", "required": True}, "limit": {"type": "integer"}},
            output_schema={"results": "list", "total": "integer"},
            tags=["search", "web", "google", "find", "lookup"],
            trigger_patterns=[r"search\s+(for|the|web)", r"find\s+info", r"look\s?up", r"google"],
            combo_compatible=["deep-research", "web-browse", "note-taker"],
            combo_position="start", cost_per_call=0.0,
        )

    def _execute(self, inputs, context=None):
        query = inputs.get("query", "")
        limit = inputs.get("limit", 10)
        if not query:
            return AlgorithmResult("failure", None, {"error": "No query"})

        try:
            # DuckDuckGo instant answer API
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())

            results = []
            # Abstract
            if data.get("Abstract"):
                results.append({"title": data.get("Heading", ""), "snippet": data["Abstract"],
                                "url": data.get("AbstractURL", ""), "source": data.get("AbstractSource", "")})
            # Related topics
            for topic in data.get("RelatedTopics", [])[:limit]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({"title": topic.get("Text", "")[:100], "snippet": topic.get("Text", ""),
                                    "url": topic.get("FirstURL", ""), "source": "DuckDuckGo"})

            return AlgorithmResult("success", {"results": results[:limit], "total": len(results), "query": query},
                                   {"skill": "web-search", "results": len(results)})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "skill": "web-search"})
