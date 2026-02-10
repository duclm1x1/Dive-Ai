"""Data Analyzer Skill — Analyze CSV/JSON data, basic stats."""
import json, csv, os, io
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class DataSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="data-analyzer", description="Analyze CSV/JSON data: stats, summary, filtering",
            category=SkillCategory.PRODUCTIVITY, version="1.0.0",
            input_schema={"file_path": {"type": "string"}, "data": {"type": "any"}, "action": {"type": "string"}},
            output_schema={"analysis": "dict", "summary": "string"},
            tags=["data", "analyze", "csv", "json", "statistics", "chart"],
            trigger_patterns=[r"analyze\s+data", r"csv", r"json\s+data", r"statistics", r"data\s+summary"],
            combo_compatible=["web-scrape", "file-manager", "note-taker", "email-send"],
            combo_position="middle")

    def _execute(self, inputs, context=None):
        data = inputs.get("data")
        file_path = inputs.get("file_path", "")
        action = inputs.get("action", "summary")
        
        # Load data from file if needed
        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            with open(file_path, "r", encoding="utf-8") as f:
                if ext == ".json":
                    data = json.load(f)
                elif ext == ".csv":
                    reader = csv.DictReader(f)
                    data = list(reader)
                else:
                    data = f.read()
        
        if data is None:
            return AlgorithmResult("failure", None, {"error": "No data provided"})
        
        # Analyze
        analysis = {"type": type(data).__name__}
        
        if isinstance(data, list):
            analysis["count"] = len(data)
            if data and isinstance(data[0], dict):
                analysis["columns"] = list(data[0].keys())
                analysis["sample"] = data[:3]
                # Numeric stats
                for col in analysis["columns"]:
                    values = []
                    for row in data:
                        try: values.append(float(row[col]))
                        except: pass
                    if values:
                        analysis[f"{col}_stats"] = {
                            "min": min(values), "max": max(values),
                            "avg": round(sum(values)/len(values), 2), "count": len(values),
                        }
        elif isinstance(data, dict):
            analysis["keys"] = list(data.keys())[:20]
            analysis["size"] = len(json.dumps(data))
        elif isinstance(data, str):
            analysis["length"] = len(data)
            analysis["lines"] = data.count("\n") + 1
            analysis["words"] = len(data.split())
        
        summary = f"Data analysis: {analysis.get('type')} with {analysis.get('count', 'N/A')} items"
        return AlgorithmResult("success", {"analysis": analysis, "summary": summary}, {"skill": "data-analyzer"})
