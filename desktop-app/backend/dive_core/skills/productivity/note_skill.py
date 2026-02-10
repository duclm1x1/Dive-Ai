"""Note Taker Skill — Capture, organize, and search notes."""
import json, os, time, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class NoteSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="note-taker", description="Create, search, and manage notes",
            category=SkillCategory.PRODUCTIVITY, version="1.0.0",
            input_schema={"action": {"type": "string"}, "content": {"type": "string"},
                          "title": {"type": "string"}, "query": {"type": "string"}, "tags": {"type": "list"}},
            output_schema={"notes": "list", "result": "string"},
            tags=["note", "write", "capture", "save", "document"],
            trigger_patterns=[r"note\s", r"write\s+down", r"save\s+note", r"take\s+notes"],
            combo_compatible=["deep-research", "email-read", "memory-query"], combo_position="end")

    def _notes_dir(self):
        d = os.path.expanduser("~/.dive-ai/notes")
        os.makedirs(d, exist_ok=True)
        return d

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "save")
        
        if action == "save":
            title = inputs.get("title", f"Note_{int(time.time())}")
            content = inputs.get("content") or inputs.get("data", {}).get("summary", "")
            tags = inputs.get("tags", [])
            
            note = {"title": title, "content": content, "tags": tags,
                    "created": time.strftime("%Y-%m-%d %H:%M"), "id": str(int(time.time()))}
            fpath = os.path.join(self._notes_dir(), f"{note['id']}.json")
            with open(fpath, "w", encoding="utf-8") as f: json.dump(note, f, indent=2, ensure_ascii=False)
            return AlgorithmResult("success", {"saved": True, "note": note}, {"skill": "note-taker"})
        
        elif action == "list":
            notes = []
            for fname in sorted(os.listdir(self._notes_dir()), reverse=True)[:20]:
                if fname.endswith(".json"):
                    with open(os.path.join(self._notes_dir(), fname), "r") as f:
                        n = json.load(f)
                        notes.append({"title": n.get("title"), "id": n.get("id"), "created": n.get("created")})
            return AlgorithmResult("success", {"notes": notes, "total": len(notes)}, {"skill": "note-taker"})
        
        elif action == "search":
            query = inputs.get("query", "").lower()
            results = []
            for fname in os.listdir(self._notes_dir()):
                if fname.endswith(".json"):
                    with open(os.path.join(self._notes_dir(), fname), "r") as f:
                        n = json.load(f)
                    if query in json.dumps(n).lower():
                        results.append(n)
            return AlgorithmResult("success", {"results": results[:10], "total": len(results)}, {"skill": "note-taker"})
        
        return AlgorithmResult("failure", None, {"error": "Unknown action"})
