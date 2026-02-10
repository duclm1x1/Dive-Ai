"""Multi-Agent Dev Skill -- Coordinate multiple AI agents for development."""
import json, os, time, uuid
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class MultiAgentDevSkill(BaseSkill):
    _projects = {}
    _agents = {}

    def _build_spec(self):
        return SkillSpec(name="multi-agent-dev", description="Multi-agent dev: planning, delegation, review, merge",
            category=SkillCategory.CODING, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "project": {"type": "string"},
                          "task_id": {"type": "string"}, "agent_id": {"type": "string"},
                          "description": {"type": "string"}, "code": {"type": "string"}, "file": {"type": "string"}},
            output_schema={"plan": "dict", "tasks": "list"},
            tags=["multi-agent", "development", "collaboration", "planning", "review"],
            trigger_patterns=[r"multi.?agent", r"delegate\s+", r"code\s+review", r"plan\s+project"],
            combo_compatible=["code-review", "ci-cd", "slack-bot"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "plan")
        if action == "plan":
            return self._plan(inputs)
        elif action == "delegate":
            return self._delegate(inputs)
        elif action == "status":
            return self._status(inputs)
        elif action == "review":
            return self._review(inputs)
        elif action == "merge":
            return self._merge(inputs)
        elif action == "list":
            return AlgorithmResult("success",
                {"projects": list(self._projects.keys()), "agents": list(self._agents.keys())},
                {"skill": "multi-agent-dev"})
        return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})

    def _plan(self, inputs):
        project = inputs.get("project", f"project-{uuid.uuid4().hex[:6]}")
        desc = inputs.get("description", "")
        tasks = inputs.get("tasks", [])
        if not tasks and desc:
            tasks = [{"id": f"task-{i+1}", "name": t.strip(), "status": "pending",
                      "assigned_to": None} for i, t in enumerate(desc.split(","))]
        plan = {"project": project, "tasks": tasks, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "status": "planned"}
        self._projects[project] = plan
        return AlgorithmResult("success",
            {"project": project, "total_tasks": len(tasks), "plan": plan},
            {"skill": "multi-agent-dev"})

    def _delegate(self, inputs):
        project = inputs.get("project", "")
        task_id = inputs.get("task_id", "")
        agent_id = inputs.get("agent_id", f"agent-{uuid.uuid4().hex[:4]}")
        if project not in self._projects:
            return AlgorithmResult("failure", None, {"error": f"Project '{project}' not found"})
        for task in self._projects[project].get("tasks", []):
            if task.get("id") == task_id:
                task["assigned_to"] = agent_id
                task["status"] = "assigned"
                self._agents.setdefault(agent_id, {"tasks": []})
                self._agents[agent_id]["tasks"].append({"project": project, "task_id": task_id})
                return AlgorithmResult("success",
                    {"delegated": True, "task": task, "agent": agent_id},
                    {"skill": "multi-agent-dev"})
        return AlgorithmResult("failure", None, {"error": f"Task '{task_id}' not found"})

    def _status(self, inputs):
        project = inputs.get("project", "")
        if project in self._projects:
            tasks = self._projects[project].get("tasks", [])
            return AlgorithmResult("success", {
                "project": project, "total": len(tasks),
                "pending": sum(1 for t in tasks if t.get("status") == "pending"),
                "assigned": sum(1 for t in tasks if t.get("status") == "assigned"),
                "completed": sum(1 for t in tasks if t.get("status") == "completed"),
            }, {"skill": "multi-agent-dev"})
        return AlgorithmResult("success",
            {"projects": list(self._projects.keys()), "total": len(self._projects)},
            {"skill": "multi-agent-dev"})

    def _review(self, inputs):
        code = inputs.get("code", "")
        file_path = inputs.get("file", "")
        if file_path and os.path.exists(file_path):
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                code = f.read()
        if not code:
            return AlgorithmResult("failure", None, {"error": "Need 'code' or 'file'"})
        lines = code.split("\n")
        issues = []
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append({"line": i+1, "type": "style", "msg": "Line too long"})
            if "TODO" in line or "FIXME" in line:
                issues.append({"line": i+1, "type": "todo", "msg": line.strip()[:80]})
            if "password" in line.lower() and "=" in line:
                issues.append({"line": i+1, "type": "security", "msg": "Possible hardcoded password"})
            if "eval(" in line:
                issues.append({"line": i+1, "type": "security", "msg": "eval() usage"})
        return AlgorithmResult("success", {
            "lines": len(lines), "issues": issues[:20], "issue_count": len(issues),
            "quality_score": max(0, 10 - len(issues)),
        }, {"skill": "multi-agent-dev"})

    def _merge(self, inputs):
        project = inputs.get("project", "")
        if project not in self._projects:
            return AlgorithmResult("failure", None, {"error": f"Project '{project}' not found"})
        tasks = self._projects[project].get("tasks", [])
        completed = [t for t in tasks if t.get("status") == "completed"]
        pending = [t for t in tasks if t.get("status") != "completed"]
        return AlgorithmResult("success", {
            "project": project, "merged": len(completed), "remaining": len(pending),
            "complete": len(pending) == 0,
        }, {"skill": "multi-agent-dev"})
