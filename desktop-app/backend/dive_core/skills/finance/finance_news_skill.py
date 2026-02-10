"""Financial News Skill — Dedicated finance/market news."""
import urllib.request, json, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class FinanceNewsSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="finance-news", description="Get financial and market news",
            category=SkillCategory.FINANCE, version="1.0.0",
            input_schema={"query": {"type": "string"}, "limit": {"type": "integer"}},
            output_schema={"articles": "list", "total": "integer"},
            tags=["finance", "news", "market", "business", "economy"],
            trigger_patterns=[r"finance\s+news", r"market\s+news", r"business\s+news", r"economy"],
            combo_compatible=["data-analyzer", "telegram-bot", "email-send"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        query = inputs.get("query", "stock market finance")
        limit = inputs.get("limit", 10)
        
        try:
            from urllib.parse import quote
            url = f"https://duckduckgo.com/news.js?q={quote(query + ' finance')}&df=d&o=json"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            
            articles = []
            for r in data.get("results", [])[:limit]:
                articles.append({
                    "title": r.get("title", ""), "url": r.get("url", ""),
                    "source": r.get("source", ""), "date": r.get("date", ""),
                    "snippet": r.get("body", "")[:200],
                })
            return AlgorithmResult("success", {"articles": articles, "total": len(articles), "query": query},
                                   {"skill": "finance-news"})
        except Exception as e:
            # Fallback
            return AlgorithmResult("success", {
                "articles": [], "total": 0, "query": query,
                "note": f"Search unavailable: {e}",
            }, {"skill": "finance-news"})
