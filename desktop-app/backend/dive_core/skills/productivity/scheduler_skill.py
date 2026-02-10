"""Scheduler Skill — Cron-like scheduled task execution."""
import json, os, time, threading
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SchedulerSkill(BaseSkill):
    _schedules = []  # Class-level persistent schedules
    _running = False
    _thread = None

    def _build_spec(self):
        return SkillSpec(name="scheduler", description="Schedule skills/combos to run at intervals",
            category=SkillCategory.PRODUCTIVITY, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "skill_name": {"type": "string"},
                          "interval_seconds": {"type": "integer"}, "params": {"type": "dict"},
                          "schedule_id": {"type": "string"}},
            output_schema={"schedules": "list", "result": "string"},
            tags=["schedule", "cron", "timer", "periodic", "automate"],
            trigger_patterns=[r"schedule\s+", r"every\s+\d+", r"cron", r"periodic", r"automate"],
            combo_compatible=["system-info", "news-search", "email-send"], combo_position="end")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "list")
        
        if action == "add":
            sched = {
                "id": str(int(time.time())),
                "skill_name": inputs.get("skill_name", ""),
                "interval_seconds": inputs.get("interval_seconds", 3600),
                "params": inputs.get("params", {}),
                "created": time.strftime("%Y-%m-%d %H:%M"),
                "last_run": None, "run_count": 0, "active": True,
            }
            SchedulerSkill._schedules.append(sched)
            return AlgorithmResult("success", {"added": sched, "total": len(SchedulerSkill._schedules)},
                                   {"skill": "scheduler"})
        
        elif action == "list":
            return AlgorithmResult("success", {"schedules": SchedulerSkill._schedules,
                "total": len(SchedulerSkill._schedules),
                "active": sum(1 for s in SchedulerSkill._schedules if s.get("active"))},
                {"skill": "scheduler"})
        
        elif action == "remove":
            sid = inputs.get("schedule_id", "")
            SchedulerSkill._schedules = [s for s in SchedulerSkill._schedules if s["id"] != sid]
            return AlgorithmResult("success", {"removed": sid}, {"skill": "scheduler"})
        
        elif action == "pause":
            sid = inputs.get("schedule_id", "")
            for s in SchedulerSkill._schedules:
                if s["id"] == sid: s["active"] = False
            return AlgorithmResult("success", {"paused": sid}, {"skill": "scheduler"})
        
        elif action == "resume":
            sid = inputs.get("schedule_id", "")
            for s in SchedulerSkill._schedules:
                if s["id"] == sid: s["active"] = True
            return AlgorithmResult("success", {"resumed": sid}, {"skill": "scheduler"})
        
        return AlgorithmResult("failure", None, {"error": "Unknown action: add/list/remove/pause/resume"})
