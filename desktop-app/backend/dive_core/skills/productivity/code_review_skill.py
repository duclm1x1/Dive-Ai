"""Code Review Skill — Analyze code quality and suggest improvements."""
import os, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CodeReviewSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="code-review", description="Review code quality, find issues, suggest improvements",
            category=SkillCategory.PRODUCTIVITY, version="1.0.0",
            input_schema={"file_path": {"type": "string"}, "code": {"type": "string"}, "language": {"type": "string"}},
            output_schema={"issues": "list", "score": "float", "suggestions": "list"},
            tags=["code", "review", "quality", "lint", "check"],
            trigger_patterns=[r"review\s+code", r"code\s+quality", r"check\s+code", r"lint"],
            combo_compatible=["git-ops", "file-manager", "prompt-optimizer"],
            combo_position="middle", cost_per_call=0.0)

    def _execute(self, inputs, context=None):
        code = inputs.get("code", "")
        file_path = inputs.get("file_path", "")
        
        if file_path and os.path.exists(file_path) and not code:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read(50000)
        
        if not code:
            return AlgorithmResult("failure", None, {"error": "No code to review"})
        
        issues = []
        suggestions = []
        lines = code.split("\n")
        
        # Line length check
        long_lines = [i+1 for i, l in enumerate(lines) if len(l) > 120]
        if long_lines:
            issues.append({"type": "style", "severity": "low", "message": f"{len(long_lines)} lines exceed 120 chars",
                          "lines": long_lines[:5]})
        
        # TODO/FIXME/HACK
        for i, line in enumerate(lines):
            for marker in ["TODO", "FIXME", "HACK", "XXX"]:
                if marker in line:
                    issues.append({"type": "todo", "severity": "info", "message": line.strip()[:100], "line": i+1})
        
        # Common patterns
        if "import *" in code:
            issues.append({"type": "import", "severity": "medium", "message": "Wildcard import detected"})
        if re.search(r'except\s*:', code):
            issues.append({"type": "error-handling", "severity": "high", "message": "Bare except clause found"})
        if "eval(" in code and "debug" not in file_path.lower():
            issues.append({"type": "security", "severity": "high", "message": "eval() usage detected"})
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', code):
            issues.append({"type": "security", "severity": "critical", "message": "Hardcoded password detected"})
        
        # Metrics
        total_lines = len(lines)
        blank_lines = sum(1 for l in lines if not l.strip())
        comment_lines = sum(1 for l in lines if l.strip().startswith("#") or l.strip().startswith("//"))
        
        # Score
        critical = sum(1 for i in issues if i.get("severity") == "critical")
        high = sum(1 for i in issues if i.get("severity") == "high")
        score = max(0, 10 - critical*3 - high*1.5 - len(issues)*0.2)
        
        return AlgorithmResult("success", {
            "issues": issues[:20], "score": round(score, 1),
            "metrics": {"total_lines": total_lines, "blank_lines": blank_lines,
                        "comment_lines": comment_lines, "issue_count": len(issues)},
            "suggestions": suggestions,
        }, {"skill": "code-review"})
