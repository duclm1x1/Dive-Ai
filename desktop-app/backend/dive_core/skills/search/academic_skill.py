"""Academic Search Skill — Search arXiv for research papers."""
import urllib.request, urllib.parse, json, re
from typing import Dict, Any
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class AcademicSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="academic-search", description="Search arXiv for academic papers",
            category=SkillCategory.SEARCH, version="1.0.0",
            input_schema={"query": {"type": "string", "required": True}, "max_results": {"type": "integer"}},
            output_schema={"papers": "list"},
            tags=["academic", "arxiv", "paper", "research", "scholar"],
            trigger_patterns=[r"arxiv", r"paper\s+about", r"research\s+on", r"academic"],
            combo_compatible=["deep-research", "note-taker", "email-send"],
            combo_position="start", cost_per_call=0.0,
        )

    def _execute(self, inputs, context=None):
        query = inputs.get("query", "")
        max_r = inputs.get("max_results", 5)
        try:
            url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={max_r}"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml = resp.read().decode()

            papers = []
            entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
            for entry in entries:
                title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                link = re.search(r'<id>(.*?)</id>', entry)
                published = re.search(r'<published>(.*?)</published>', entry)
                authors = re.findall(r'<name>(.*?)</name>', entry)
                papers.append({
                    "title": title.group(1).strip() if title else "",
                    "summary": summary.group(1).strip()[:500] if summary else "",
                    "url": link.group(1) if link else "",
                    "published": published.group(1) if published else "",
                    "authors": authors[:5],
                })
            return AlgorithmResult("success", {"papers": papers, "total": len(papers), "query": query},
                                   {"skill": "academic-search"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
