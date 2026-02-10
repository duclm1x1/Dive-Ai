"""Task Manager Skill — Create, track, complete tasks."""
import json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class TaskSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="task-manager", description="Create, list, complete, and delete tasks",
            category=SkillCategory.PRODUCTIVITY, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "title": {"type": "string"},
                          "task_id": {"type": "string"}, "priority": {"type": "string"}},
            output_schema={"tasks": "list", "result": "string"},
            tags=["task", "todo", "manage", "track", "plan"],
            trigger_patterns=[r"task\s", r"todo", r"add\s+task", r"complete\s+task", r"my\s+tasks"],
            combo_compatible=["note-taker", "email-send", "scheduler"], combo_position="any")

    def _get_tasks_file(self):
        d = os.path.expanduser("~/.dive-ai/tasks")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "tasks.json")

    def _load(self):
        f = self._get_tasks_file()
        if os.path.exists(f):
            with open(f, "r") as fh: return json.load(fh)
        return []

    def _save(self, tasks):
        with open(self._get_tasks_file(), "w") as f: json.dump(tasks, f, indent=2)

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "list")
        tasks = self._load()
        
        if action == "add":
            t = {"id": str(int(time.time())), "title": inputs.get("title", "Untitled"),
                 "priority": inputs.get("priority", "medium"), "status": "pending",
                 "created": time.strftime("%Y-%m-%d %H:%M")}
            tasks.append(t)
            self._save(tasks)
            return AlgorithmResult("success", {"added": t, "total": len(tasks)}, {"skill": "task-manager"})
        elif action == "list":
            return AlgorithmResult("success", {"tasks": tasks, "total": len(tasks),
                "pending": sum(1 for t in tasks if t.get("status") == "pending")}, {"skill": "task-manager"})
        elif action == "complete":
            tid = inputs.get("task_id", "")
            for t in tasks:
                if t["id"] == tid: t["status"] = "done"; t["completed"] = time.strftime("%Y-%m-%d %H:%M")
            self._save(tasks)
            return AlgorithmResult("success", {"completed": tid, "total": len(tasks)}, {"skill": "task-manager"})
        elif action == "delete":
            tid = inputs.get("task_id", "")
            tasks = [t for t in tasks if t["id"] != tid]
            self._save(tasks)
            return AlgorithmResult("success", {"deleted": tid, "remaining": len(tasks)}, {"skill": "task-manager"})
        return AlgorithmResult("failure", None, {"error": "Unknown action"})
