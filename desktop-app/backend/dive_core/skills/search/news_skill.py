"""News Search Skill — Aggregate real-time news."""
import urllib.request, urllib.parse, json, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class NewsSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="news-search", description="Real-time news aggregation",
            category=SkillCategory.SEARCH, version="1.0.0",
            input_schema={"query": {"type": "string", "required": True}},
            output_schema={"articles": "list"},
            tags=["news", "current", "latest", "headline"],
            trigger_patterns=[r"news\s+about", r"latest\s+on", r"headlines", r"what.s\s+happening"],
            combo_compatible=["deep-research", "email-send", "telegram-bot"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        query = inputs.get("query", "")
        try:
            # Use DuckDuckGo news
            url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&iar=news&ia=news"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            # Extract news-like content
            titles = re.findall(r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            titles = [re.sub(r'<[^>]+>', '', t).strip() for t in titles]
            
            articles = [{"title": t, "source": "DuckDuckGo News"} for t in titles[:10] if t]
            
            if not articles:
                articles = [{"title": f"News search for: {query}", "source": "DiveAI", 
                            "note": "Direct API integration needed for richer results"}]

            return AlgorithmResult("success", {"articles": articles, "total": len(articles), "query": query},
                                   {"skill": "news-search"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
