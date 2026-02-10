"""Dive Tracker - Track tasks, resources, costs"""
import time, json, sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Task:
    id: str
    name: str
    started: float
    completed: Optional[float] = None

class DiveTracker:
    def __init__(self, db="tracking/dive_tracker.db"):
        self.db = Path(db)
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.active = {}
        conn = sqlite3.connect(str(self.db))
        conn.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, name TEXT, started REAL, completed REAL, duration REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS resources (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, type TEXT, usage REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS costs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, operation TEXT, cost REAL)")
        conn.commit()
        conn.close()
        print("✅ Dive Tracker initialized")
    
    def start_task(self, task_id: str, name: str):
        task = Task(task_id, name, time.time())
        self.active[task_id] = task
        conn = sqlite3.connect(str(self.db))
        conn.execute("INSERT INTO tasks (id, name, started) VALUES (?, ?, ?)", (task_id, name, task.started))
        conn.commit()
        conn.close()
        return task
    
    def complete_task(self, task_id: str):
        if task_id in self.active:
            task = self.active[task_id]
            task.completed = time.time()
            duration = task.completed - task.started
            conn = sqlite3.connect(str(self.db))
            conn.execute("UPDATE tasks SET completed = ?, duration = ? WHERE id = ?", (task.completed, duration, task_id))
            conn.commit()
            conn.close()
            del self.active[task_id]
    
    def track_resource(self, type: str, usage: float):
        conn = sqlite3.connect(str(self.db))
        conn.execute("INSERT INTO resources (timestamp, type, usage) VALUES (?, ?, ?)", (time.time(), type, usage))
        conn.commit()
        conn.close()
    
    def track_cost(self, operation: str, cost: float):
        conn = sqlite3.connect(str(self.db))
        conn.execute("INSERT INTO costs (timestamp, operation, cost) VALUES (?, ?, ?)", (time.time(), operation, cost))
        conn.commit()
        conn.close()
    
    def get_stats(self):
        conn = sqlite3.connect(str(self.db))
        total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        total_cost = conn.execute("SELECT SUM(cost) FROM costs").fetchone()[0] or 0
        conn.close()
        return {"total_tasks": total_tasks, "active": len(self.active), "total_cost": f"${total_cost:.2f}"}
