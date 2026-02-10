"""Deep Research Skill — Multi-source research with citations."""
import time
from typing import Dict, Any
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class DeepResearchSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="deep-research", description="Multi-source research combining web, academic, and local data",
            category=SkillCategory.SEARCH, version="1.0.0",
            input_schema={"topic": {"type": "string", "required": True}, "depth": {"type": "string"}},
            output_schema={"summary": "string", "sources": "list", "key_findings": "list"},
            tags=["research", "deep", "analysis", "comprehensive"],
            trigger_patterns=[r"research\s", r"deep\s+dive", r"investigate", r"analyze\s+topic"],
            combo_compatible=["note-taker", "email-send", "prompt-optimizer"],
            combo_position="middle", cost_per_call=0.001)

    def _execute(self, inputs, context=None):
        topic = inputs.get("topic") or inputs.get("query", "")
        data = inputs.get("data", {})
        
        # Aggregate from previous combo steps
        sources = []
        findings = []
        
        if isinstance(data, dict):
            # From web-search
            for r in data.get("results", []):
                sources.append({"url": r.get("url", ""), "title": r.get("title", "")})
                findings.append(r.get("snippet", ""))
            # From academic-search
            for p in data.get("papers", []):
                sources.append({"url": p.get("url", ""), "title": p.get("title", "")})
                findings.append(p.get("summary", ""))
            # From youtube
            for v in data.get("videos", []):
                sources.append({"url": v.get("url", ""), "title": v.get("title", "")})

        summary = f"Research on '{topic}': Found {len(sources)} sources with {len(findings)} key findings."
        if findings:
            summary += "\n\nKey findings:\n" + "\n".join(f"- {f[:200]}" for f in findings[:10])

        return AlgorithmResult("success", {
            "topic": topic, "summary": summary, "sources": sources[:20],
            "key_findings": findings[:10], "source_count": len(sources),
        }, {"skill": "deep-research"})
