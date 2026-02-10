"""File Manager Skill — Advanced file operations."""
import os, shutil, glob, json, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class FileSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="file-manager", description="Advanced file operations: list, read, write, copy, move, search",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "path": {"type": "string"},
                          "content": {"type": "string"}, "dest": {"type": "string"}, "pattern": {"type": "string"}},
            output_schema={"result": "string", "files": "list"},
            tags=["file", "read", "write", "copy", "move", "delete", "search"],
            trigger_patterns=[r"file\s", r"read\s+file", r"write\s+to", r"list\s+files", r"find\s+file"],
            combo_compatible=["data-analyzer", "git-ops", "code-review"],
            combo_position="any")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "list")
        path = inputs.get("path", ".")
        content = inputs.get("content", "")
        dest = inputs.get("dest", "")
        pattern = inputs.get("pattern", "*")
        
        try:
            if action == "list":
                entries = []
                for e in os.listdir(path):
                    fp = os.path.join(path, e)
                    entries.append({"name": e, "is_dir": os.path.isdir(fp),
                                    "size": os.path.getsize(fp) if os.path.isfile(fp) else 0})
                return AlgorithmResult("success", {"files": entries[:200], "total": len(entries), "path": path},
                                       {"skill": "file-manager"})
            elif action == "read":
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read(100000)
                return AlgorithmResult("success", {"content": text, "size": os.path.getsize(path), "path": path},
                                       {"skill": "file-manager"})
            elif action == "write":
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return AlgorithmResult("success", {"written": True, "path": path, "size": len(content)},
                                       {"skill": "file-manager"})
            elif action == "copy":
                shutil.copy2(path, dest)
                return AlgorithmResult("success", {"copied": True, "from": path, "to": dest}, {"skill": "file-manager"})
            elif action == "move":
                shutil.move(path, dest)
                return AlgorithmResult("success", {"moved": True, "from": path, "to": dest}, {"skill": "file-manager"})
            elif action == "search":
                matches = glob.glob(os.path.join(path, "**", pattern), recursive=True)
                return AlgorithmResult("success", {"files": matches[:100], "total": len(matches)}, {"skill": "file-manager"})
            elif action == "info":
                stat = os.stat(path)
                return AlgorithmResult("success", {"path": path, "size": stat.st_size,
                    "modified": time.ctime(stat.st_mtime), "is_dir": os.path.isdir(path)}, {"skill": "file-manager"})
            else:
                return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
