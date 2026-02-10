"""Web Scraper Skill — Extract structured data from HTML."""
import re
from typing import Dict, Any, Optional
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ...specs import VerificationResult
from ..skill_spec import SkillSpec, SkillCategory


class ScraperSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="web-scrape", description="Extract text, links, and structured data from HTML",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"html": {"type": "string"}, "url": {"type": "string"},
                          "selector": {"type": "string"}},
            output_schema={"text": "string", "links": "list", "headings": "list"},
            tags=["scrape", "extract", "html", "parse"],
            trigger_patterns=[r"scrape\s", r"extract\s+from", r"parse\s+html"],
            combo_compatible=["data-analyzer", "note-taker", "email-send"],
            combo_position="middle", cost_per_call=0.0,
        )

    def _execute(self, inputs, context=None):
        html = inputs.get("html") or inputs.get("content") or inputs.get("data", "")
        if not html:
            return AlgorithmResult("failure", None, {"error": "No HTML content", "skill": "web-scrape"})
        
        # Extract text (strip tags)
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Extract links
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        
        # Extract headings
        headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html, re.DOTALL)
        headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        return AlgorithmResult("success", {
            "text": text[:20000], "links": links[:100],
            "headings": headings[:50], "title": title,
        }, {"skill": "web-scrape", "text_len": len(text), "links": len(links)})
