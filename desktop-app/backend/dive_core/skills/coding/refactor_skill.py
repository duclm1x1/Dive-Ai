"""Refactor Skill — Multi-file code refactoring: rename, extract, move."""
import os, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class RefactorSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="code-refactor", description="Refactor code: rename symbols, extract functions, find-replace",
            category=SkillCategory.CODING, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "path": {"type": "string"},
                          "old_name": {"type": "string"}, "new_name": {"type": "string"}, "pattern": {"type": "string"}},
            output_schema={"files_changed": "list", "total_replacements": "integer"},
            tags=["refactor", "rename", "extract", "move", "restructure", "replace"],
            trigger_patterns=[r"refactor\s+", r"rename\s+", r"replace\s+all", r"extract\s+function"],
            combo_compatible=["code-review", "git-ops", "file-manager"],
            combo_position="middle")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "rename")
        path = inputs.get("path", ".")
        old_name = inputs.get("old_name", "")
        new_name = inputs.get("new_name", "")
        pattern = inputs.get("pattern", "*.py")
        
        if action == "rename" and old_name and new_name:
            import glob
            files_changed = []
            total = 0
            for fpath in glob.glob(os.path.join(path, "**", pattern), recursive=True):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    count = content.count(old_name)
                    if count > 0:
                        new_content = content.replace(old_name, new_name)
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        files_changed.append({"file": fpath, "replacements": count})
                        total += count
                except: pass
            
            return AlgorithmResult("success", {
                "files_changed": files_changed, "total_replacements": total,
                "old_name": old_name, "new_name": new_name,
            }, {"skill": "code-refactor"})
        
        elif action == "find":
            import glob
            matches = []
            for fpath in glob.glob(os.path.join(path, "**", pattern), recursive=True):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if old_name in line:
                                matches.append({"file": fpath, "line": i, "content": line.strip()[:200]})
                except: pass
            return AlgorithmResult("success", {"matches": matches[:50], "total": len(matches)},
                                   {"skill": "code-refactor"})
        
        elif action == "stats":
            import glob
            stats = {"files": 0, "lines": 0, "chars": 0}
            by_ext = {}
            for fpath in glob.glob(os.path.join(path, "**", "*"), recursive=True):
                if os.path.isfile(fpath):
                    ext = os.path.splitext(fpath)[1]
                    by_ext[ext] = by_ext.get(ext, 0) + 1
                    stats["files"] += 1
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()
                        stats["lines"] += content.count("\n")
                        stats["chars"] += len(content)
                    except: pass
            stats["by_extension"] = dict(sorted(by_ext.items(), key=lambda x: -x[1])[:10])
            return AlgorithmResult("success", stats, {"skill": "code-refactor"})
        
        return AlgorithmResult("failure", None, {"error": "action: rename/find/stats"})
