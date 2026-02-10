"""
💾 PERSISTENT MEMORY SYSTEM
SQLite-based storage for agent states, tasks, and execution history
"""

import os
import sys
import json
import sqlite3
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import contextmanager

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class AgentState:
    """Agent state record"""
    agent_id: int
    role: str
    status: str
    current_task: Optional[str]
    tasks_completed: int
    uptime_hours: float
    last_active: str
    specializations: str  # JSON string


@dataclass
class TaskRecord:
    """Task history record"""
    task_id: str
    description: str
    priority: int
    status: str
    assigned_agents: str  # JSON array
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[str]
    error: Optional[str]


@dataclass
class ExecutionLog:
    """Execution log entry"""
    log_id: str
    timestamp: str
    agent_id: int
    action: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: int
    status: str
    response_preview: Optional[str]


class PersistentMemory:
    """
    💾 Persistent Memory System
    SQLite-based storage for Dive AI
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dive_ai.db")
        
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        print(f"💾 PersistentMemory initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Agent states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    agent_id INTEGER PRIMARY KEY,
                    role TEXT NOT NULL,
                    status TEXT DEFAULT 'idle',
                    current_task TEXT,
                    tasks_completed INTEGER DEFAULT 0,
                    uptime_hours REAL DEFAULT 0,
                    last_active TEXT,
                    specializations TEXT
                )
            """)
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    priority INTEGER DEFAULT 3,
                    status TEXT DEFAULT 'pending',
                    assigned_agents TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error TEXT
                )
            """)
            
            # Execution logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    agent_id INTEGER,
                    action TEXT,
                    model TEXT,
                    provider TEXT,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0,
                    latency_ms INTEGER DEFAULT 0,
                    status TEXT,
                    response_preview TEXT
                )
            """)
            
            # Daily plans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_plans (
                    plan_date TEXT PRIMARY KEY,
                    timeline TEXT NOT NULL,
                    resource_allocation TEXT,
                    expected_outcomes TEXT,
                    actual_outcomes TEXT,
                    created_at TEXT
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON execution_logs(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_agent ON execution_logs(agent_id)")
            
            conn.commit()
    
    # ═══════════════════════════════════════════════════════════════════════
    # AGENT STATE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    def save_agent_state(self, agent: AgentState):
        """Save or update agent state"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_states
                    (agent_id, role, status, current_task, tasks_completed, 
                     uptime_hours, last_active, specializations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent.agent_id, agent.role, agent.status, agent.current_task,
                    agent.tasks_completed, agent.uptime_hours, agent.last_active,
                    agent.specializations
                ))
                conn.commit()
    
    def save_agent_states_batch(self, agents: List[AgentState]):
        """Save multiple agent states at once"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT OR REPLACE INTO agent_states
                    (agent_id, role, status, current_task, tasks_completed,
                     uptime_hours, last_active, specializations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [(
                    a.agent_id, a.role, a.status, a.current_task,
                    a.tasks_completed, a.uptime_hours, a.last_active,
                    a.specializations
                ) for a in agents])
                conn.commit()
    
    def get_agent_state(self, agent_id: int) -> Optional[AgentState]:
        """Get agent state by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_states WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            if row:
                return AgentState(**dict(row))
            return None
    
    def get_all_agent_states(self) -> List[AgentState]:
        """Get all agent states"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_states")
            return [AgentState(**dict(row)) for row in cursor.fetchall()]
    
    def get_agents_by_status(self, status: str) -> List[AgentState]:
        """Get agents by status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_states WHERE status = ?", (status,))
            return [AgentState(**dict(row)) for row in cursor.fetchall()]
    
    # ═══════════════════════════════════════════════════════════════════════
    # TASK OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    def save_task(self, task: TaskRecord):
        """Save or update task"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO tasks
                    (task_id, description, priority, status, assigned_agents,
                     created_at, started_at, completed_at, result, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.task_id, task.description, task.priority, task.status,
                    task.assigned_agents, task.created_at, task.started_at,
                    task.completed_at, task.result, task.error
                ))
                conn.commit()
    
    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """Get task by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return TaskRecord(**dict(row))
            return None
    
    def get_tasks_by_status(self, status: str, limit: int = 100) -> List[TaskRecord]:
        """Get tasks by status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY priority DESC, created_at DESC LIMIT ?",
                (status, limit)
            )
            return [TaskRecord(**dict(row)) for row in cursor.fetchall()]
    
    def get_recent_tasks(self, limit: int = 50) -> List[TaskRecord]:
        """Get recent tasks"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [TaskRecord(**dict(row)) for row in cursor.fetchall()]
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXECUTION LOG OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    def log_execution(self, log: ExecutionLog):
        """Log execution"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO execution_logs
                    (log_id, timestamp, agent_id, action, model, provider,
                     input_tokens, output_tokens, cost, latency_ms, status, response_preview)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log.log_id, log.timestamp, log.agent_id, log.action, log.model,
                    log.provider, log.input_tokens, log.output_tokens, log.cost,
                    log.latency_ms, log.status, log.response_preview
                ))
                conn.commit()
    
    def get_execution_logs(self, agent_id: Optional[int] = None, 
                           limit: int = 100) -> List[ExecutionLog]:
        """Get execution logs"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if agent_id is not None:
                cursor.execute(
                    "SELECT * FROM execution_logs WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (agent_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM execution_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            return [ExecutionLog(**dict(row)) for row in cursor.fetchall()]
    
    # ═══════════════════════════════════════════════════════════════════════
    # DAILY PLAN OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════
    
    def save_daily_plan(self, plan_date: str, timeline: Dict, 
                        resource_allocation: Dict, expected_outcomes: List[str]):
        """Save daily plan"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_plans
                    (plan_date, timeline, resource_allocation, expected_outcomes, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    plan_date,
                    json.dumps(timeline),
                    json.dumps(resource_allocation),
                    json.dumps(expected_outcomes),
                    datetime.now().isoformat()
                ))
                conn.commit()
    
    def get_daily_plan(self, plan_date: str) -> Optional[Dict]:
        """Get daily plan"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_plans WHERE plan_date = ?", (plan_date,))
            row = cursor.fetchone()
            if row:
                return {
                    "plan_date": row["plan_date"],
                    "timeline": json.loads(row["timeline"]),
                    "resource_allocation": json.loads(row["resource_allocation"]),
                    "expected_outcomes": json.loads(row["expected_outcomes"]),
                    "actual_outcomes": json.loads(row["actual_outcomes"]) if row["actual_outcomes"] else None
                }
            return None
    
    # ═══════════════════════════════════════════════════════════════════════
    # METRICS AND ANALYTICS
    # ═══════════════════════════════════════════════════════════════════════
    
    def record_metric(self, metric_type: str, value: float, metadata: Dict = None):
        """Record performance metric"""
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO performance_metrics (timestamp, metric_type, value, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    metric_type,
                    value,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
    
    def get_metrics(self, metric_type: str, limit: int = 100) -> List[Dict]:
        """Get metrics by type"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM performance_metrics WHERE metric_type = ? ORDER BY timestamp DESC LIMIT ?",
                (metric_type, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Agent stats
            cursor.execute("SELECT COUNT(*) as total, status, COUNT(*) as count FROM agent_states GROUP BY status")
            agent_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
            
            # Task stats
            cursor.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
            task_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
            
            # Cost stats
            cursor.execute("SELECT SUM(cost) as total_cost, SUM(input_tokens + output_tokens) as total_tokens FROM execution_logs")
            cost_row = cursor.fetchone()
            
            return {
                "agents": agent_stats,
                "tasks": task_stats,
                "total_cost": cost_row["total_cost"] or 0,
                "total_tokens": cost_row["total_tokens"] or 0
            }
    
    def search_memory(self, query: str, limit: int = 20) -> List[Dict]:
        """Search across all memory"""
        results = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Search tasks
            cursor.execute(
                "SELECT 'task' as type, task_id as id, description as content FROM tasks WHERE description LIKE ? LIMIT ?",
                (f"%{query}%", limit // 2)
            )
            results.extend([dict(row) for row in cursor.fetchall()])
            
            # Search logs
            cursor.execute(
                "SELECT 'log' as type, log_id as id, response_preview as content FROM execution_logs WHERE response_preview LIKE ? LIMIT ?",
                (f"%{query}%", limit // 2)
            )
            results.extend([dict(row) for row in cursor.fetchall()])
        
        return results


# Global memory instance
_memory: Optional[PersistentMemory] = None


def get_memory() -> PersistentMemory:
    """Get or create global memory instance"""
    global _memory
    if _memory is None:
        _memory = PersistentMemory()
    return _memory


if __name__ == "__main__":
    # Test
    memory = get_memory()
    
    print("\n🧪 Testing Persistent Memory...")
    
    # Save agent
    agent = AgentState(
        agent_id=1,
        role="build",
        status="idle",
        current_task=None,
        tasks_completed=5,
        uptime_hours=2.5,
        last_active=datetime.now().isoformat(),
        specializations=json.dumps(["coding", "architecture"])
    )
    memory.save_agent_state(agent)
    print("✅ Agent state saved")
    
    # Save task
    task = TaskRecord(
        task_id="task-001",
        description="Test task",
        priority=5,
        status="pending",
        assigned_agents=json.dumps([1, 2, 3]),
        created_at=datetime.now().isoformat(),
        started_at=None,
        completed_at=None,
        result=None,
        error=None
    )
    memory.save_task(task)
    print("✅ Task saved")
    
    # Get stats
    stats = memory.get_dashboard_stats()
    print(f"\n📊 Dashboard Stats: {json.dumps(stats, indent=2)}")
