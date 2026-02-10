"""
Dive AI V29 - Memory V5 System
Unified Memory consolidating ALL 11 memory files

Integrated from:
1. dive_memory_3file_complete.py - Project-based 3-file system
2. dive_memory_brain.py - Central unified brain
3. hybrid_memory.py - Local + Supabase sync
4. high_performance_memory.py - Fast caching
5. memory_batch.py - Batch operations
6. dive_memory_indexer.py - Indexing
7. dive_memory_search_enhanced.py - Enhanced search
8. dive_memory_change_tracker.py - Change tracking
9. dive_update_memory_integration.py - Update integration
10. cache_manager.py - Caching
11. memory_v2.py - Algorithm portfolio (base)

Core Storage:
- SQLite for structured data (algorithms, executions, theses)
- File-based for project knowledge (3-file system)
- Cloud sync optional (Supabase)
"""

import sqlite3
import json
import os
import time
import hashlib
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from enum import Enum


# ==========================================
# ENUMS & DATA CLASSES
# ==========================================

class MemoryType(Enum):
    """Types of memory entries"""
    CONVERSATION = "conversation"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"
    USER_PREF = "user_preference"
    TASK = "task"
    ALGORITHM = "algorithm"
    EXECUTION = "execution"
    THESIS = "thesis"


@dataclass
class GPAScore:
    """GPA Score for action evaluation"""
    goal_alignment: float
    plan_alignment: float
    action_quality: float
    overall: float
    
    @staticmethod
    def calculate(goal: float, plan: float, action: float) -> 'GPAScore':
        overall = goal * 0.4 + plan * 0.3 + action * 0.3
        return GPAScore(goal, plan, action, overall)


@dataclass
class ProcessKPIs:
    """Process KPIs for workflow evaluation"""
    lead_time: float
    wasted_action_ratio: float
    path_complexity: float
    final_success_rate: float
    overall_score: float


@dataclass
class AlgorithmRecord:
    """Algorithm record in portfolio"""
    algorithm_id: str
    name: str
    tier: str
    category: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    base_score: float = 0.5
    success_rate: float = 0.5
    avg_execution_time: float = 0.0
    total_executions: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExecutionRecord:
    """Execution history record"""
    execution_id: str
    algorithm_id: str
    task_type: str
    task_description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    gpa_score: float
    goal_alignment: float
    plan_alignment: float
    action_quality: float
    execution_time_ms: float
    resources_used: Dict[str, Any]
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ThesisRecord:
    """Strategic thesis record (V4)"""
    thesis_id: str
    statement: str
    supporting_evidence: List[str]
    perspectives_analyzed: List[str]
    recommended_approach: str
    expected_outcomes: List[str]
    confidence_score: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MemoryEntry:
    """Generic memory entry for local storage"""
    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    synced: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "synced": self.synced
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'MemoryEntry':
        return MemoryEntry(
            id=data["id"],
            type=MemoryType(data["type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            synced=data.get("synced", False)
        )


# ==========================================
# PROJECT LAYER (from dive_memory_3file_complete)
# ==========================================

class ProjectMemory:
    """
    Project-based 3-file memory system
    Each project has: FULL.md, CRITERIA.md, CHANGELOG.md
    """
    
    def __init__(self, memory_root: Path):
        self.memory_root = memory_root / "projects"
        self.memory_root.mkdir(parents=True, exist_ok=True)
        self.loaded_projects = {}
    
    def get_project_files(self, project: str) -> Dict[str, Path]:
        """Get the 3 files for a project"""
        project_upper = project.upper().replace('-', '_')
        return {
            'full': self.memory_root / f"{project_upper}_FULL.md",
            'criteria': self.memory_root / f"{project_upper}_CRITERIA.md",
            'changelog': self.memory_root / f"{project_upper}_CHANGELOG.md"
        }
    
    def load_project(self, project: str) -> Dict[str, str]:
        """Load all 3 files for a project"""
        files = self.get_project_files(project)
        content = {'full': '', 'criteria': '', 'changelog': ''}
        
        for key, file_path in files.items():
            if file_path.exists():
                content[key] = file_path.read_text(encoding='utf-8')
        
        self.loaded_projects[project] = content
        return content
    
    def initialize_project(self, project: str, description: str = "") -> bool:
        """Initialize a new project with template files"""
        files = self.get_project_files(project)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create FULL template
        if not files['full'].exists():
            template = f"""---
project: {project.replace('-', ' ').title()}
version: 1.0
status: Development
created: {today}
---

# {project.replace('-', ' ').title()} - Complete Knowledge

## Overview
{description or 'Project knowledge base.'}

## Architecture
[System architecture description]

## Features
- Feature 1
- Feature 2

## Technical Details
[Technical specifications]
"""
            files['full'].write_text(template, encoding='utf-8')
        
        # Create CRITERIA template
        if not files['criteria'].exists():
            template = f"""---
project: {project.replace('-', ' ').title()}
type: criteria
created: {today}
---

# {project.replace('-', ' ').title()} - Execution Guidelines

## Decision Tree
[When to do what]

## Best Practices
1. Practice 1
2. Practice 2

## Known Issues
[Document issues and solutions]
"""
            files['criteria'].write_text(template, encoding='utf-8')
        
        # Create CHANGELOG template
        if not files['changelog'].exists():
            template = f"""---
project: {project.replace('-', ' ').title()}
type: changelog
created: {today}
---

# {project.replace('-', ' ').title()} - Change Log

## {today}
### Added
- Initial project setup
"""
            files['changelog'].write_text(template, encoding='utf-8')
        
        return True
    
    def log_change(self, project: str, change_type: str, description: str):
        """Log a change to CHANGELOG"""
        files = self.get_project_files(project)
        changelog = files['changelog']
        
        if not changelog.exists():
            self.initialize_project(project)
        
        content = changelog.read_text(encoding='utf-8')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        new_entry = f"\n## {timestamp}\n### {change_type}\n- {description}\n"
        
        # Insert after header
        insert_pos = content.find("\n## ") 
        if insert_pos > 0:
            content = content[:insert_pos] + new_entry + content[insert_pos:]
        else:
            content += new_entry
        
        changelog.write_text(content, encoding='utf-8')
    
    def list_projects(self) -> List[str]:
        """List all projects"""
        projects = set()
        for f in self.memory_root.glob("*_FULL.md"):
            name = f.stem.replace("_FULL", "").lower().replace("_", "-")
            projects.add(name)
        return sorted(projects)


# ==========================================
# BRAIN LAYER (from dive_memory_brain)
# ==========================================

class BrainMemory:
    """
    Central Brain - Check before actions, generate recommendations
    """
    
    def __init__(self, db_conn_func):
        self._get_conn = db_conn_func
    
    def check_before_file_modify(self, file_path: str) -> Dict[str, Any]:
        """Check memory before modifying a file"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM file_history 
            WHERE file_path = ? 
            ORDER BY timestamp DESC LIMIT 10
        ''', (file_path,))
        
        history = cursor.fetchall()
        conn.close()
        
        return {
            "file_path": file_path,
            "history_count": len(history),
            "recent_changes": [dict(h) for h in history[:5]],
            "recommendation": self._generate_file_recommendation(history)
        }
    
    def check_before_task_execute(self, task_description: str) -> Dict[str, Any]:
        """Check memory before executing a task"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Search similar tasks
        keywords = task_description.lower().split()[:5]
        conditions = ' OR '.join(['task_description LIKE ?' for _ in keywords])
        params = [f'%{kw}%' for kw in keywords]
        
        cursor.execute(f'''
            SELECT * FROM execution_history 
            WHERE {conditions}
            ORDER BY timestamp DESC LIMIT 10
        ''', params)
        
        similar = cursor.fetchall()
        conn.close()
        
        return {
            "task": task_description,
            "similar_tasks": len(similar),
            "history": [dict(s) for s in similar[:5]],
            "recommendation": self._generate_task_recommendation(similar)
        }
    
    def store_file_change(self, file_path: str, action: str, description: str, result: str):
        """Store file change history"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO file_history (file_path, action, description, result, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_path, action, description, result, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _generate_file_recommendation(self, history) -> str:
        if not history:
            return "No history. Proceed carefully."
        return f"Found {len(history)} related changes. Check patterns."
    
    def _generate_task_recommendation(self, similar) -> str:
        if not similar:
            return "New task type. Document outcomes."
        successes = sum(1 for s in similar if s.get('success'))
        return f"{successes}/{len(similar)} similar tasks succeeded."


# ==========================================
# LOCAL CACHE LAYER (from hybrid_memory)
# ==========================================

class LocalCache:
    """Fast local memory cache with keyword indexing"""
    
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path / "cache"
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.entries: Dict[str, MemoryEntry] = {}
        self.keyword_index: Dict[str, List[str]] = {}
        self._load_all()
    
    def add(self, entry: MemoryEntry):
        """Add entry to cache"""
        self.entries[entry.id] = entry
        self._index_entry(entry)
        self._persist(entry)
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        return self.entries.get(entry_id)
    
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search by keywords"""
        keywords = query.lower().split()
        matched_ids = set()
        
        for kw in keywords:
            for indexed_kw, ids in self.keyword_index.items():
                if kw in indexed_kw:
                    matched_ids.update(ids)
        
        results = []
        for mid in matched_ids:
            entry = self.entries.get(mid)
            if entry:
                score = sum(1 for kw in keywords if kw in entry.content.lower())
                results.append((entry, score))
        
        results.sort(key=lambda x: (x[1], x[0].created_at), reverse=True)
        return [r[0] for r in results[:limit]]
    
    def get_unsynced(self) -> List[MemoryEntry]:
        return [e for e in self.entries.values() if not e.synced]
    
    def mark_synced(self, entry_id: str):
        if entry_id in self.entries:
            self.entries[entry_id].synced = True
            self._persist(self.entries[entry_id])
    
    def _index_entry(self, entry: MemoryEntry):
        import re
        words = re.findall(r'\b\w{3,}\b', entry.content.lower())[:20]
        for w in words:
            if w not in self.keyword_index:
                self.keyword_index[w] = []
            if entry.id not in self.keyword_index[w]:
                self.keyword_index[w].append(entry.id)
    
    def _persist(self, entry: MemoryEntry):
        file_path = self.cache_path / f"{entry.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_all(self):
        for f in self.cache_path.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                entry = MemoryEntry.from_dict(data)
                self.entries[entry.id] = entry
                self._index_entry(entry)
            except Exception:
                pass
    
    def stats(self) -> Dict:
        return {
            "total_entries": len(self.entries),
            "unsynced": len(self.get_unsynced()),
            "keywords_indexed": len(self.keyword_index)
        }


# ==========================================
# CLOUD SYNC LAYER (from hybrid_memory)
# ==========================================

class CloudSync:
    """Optional Supabase cloud sync"""
    
    SUPABASE_CONFIG = {
        "url": "https://xmnbqofwlgedftjnwbit.supabase.co",
        "service_key": "sb_secret_ec8LpMT4hFnSuwsmeDy7bw_h-fNhPHZ"
    }
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        try:
            from supabase import create_client
            self.client = create_client(
                self.SUPABASE_CONFIG["url"],
                self.SUPABASE_CONFIG["service_key"]
            )
        except:
            self.client = None
    
    def is_connected(self) -> bool:
        return self.client is not None
    
    def sync_entry(self, entry: MemoryEntry) -> bool:
        if not self.client:
            return False
        try:
            data = entry.to_dict()
            data["synced_at"] = datetime.utcnow().isoformat()
            self.client.table("dive_ai_memory").upsert(data).execute()
            return True
        except:
            return False
    
    def sync_all(self, entries: List[MemoryEntry]) -> Tuple[int, int]:
        success = failed = 0
        for e in entries:
            if self.sync_entry(e):
                success += 1
            else:
                failed += 1
        return success, failed


# ==========================================
# MAIN MEMORY V5 CLASS
# ==========================================

class MemoryV5:
    """
    Dive AI V29 - Unified Memory V5 System
    
    Consolidates ALL 11 memory files into single interface:
    - SQLite: Algorithms, Executions, Theses, File History
    - Files: Project-based 3-file system
    - Cache: Fast local memory with indexing
    - Cloud: Optional Supabase sync
    
    Usage:
        memory = MemoryV5("data/dive_ai_v5")
        
        # Project operations
        memory.project.initialize_project("my-app")
        memory.project.log_change("my-app", "Added", "New feature")
        
        # Algorithm operations
        memory.register_algorithm(algo_record)
        memory.save_execution(exec_record)
        
        # Brain operations
        memory.brain.check_before_file_modify("/path/to/file")
        
        # Cache operations
        memory.cache.search("topic")
        
        # Cloud sync
        memory.sync_to_cloud()
    """
    
    def __init__(self, base_path: str = "data/dive_ai_v5"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.base_path / "memory_v5.db"
        self._lock = threading.Lock()
        
        # Initialize layers
        self._init_database()
        self.project = ProjectMemory(self.base_path)
        self.brain = BrainMemory(self._get_connection)
        self.cache = LocalCache(self.base_path)
        self.cloud = CloudSync()
        
        self._computer_id = self._get_computer_id()
        
        print(f"💾 Memory V5 initialized: {self.base_path}")
        print(f"   SQLite: {self.db_path}")
        print(f"   Projects: {self.project.memory_root}")
        print(f"   Cache: {self.cache.cache_path}")
        print(f"   Cloud: {'Connected' if self.cloud.is_connected() else 'Offline'}")
    
    def _get_computer_id(self) -> str:
        import platform
        import socket
        mac = format(uuid.getnode(), '012X')
        hostname = socket.gethostname()
        return hashlib.sha256(f"{mac}:{hostname}".encode()).hexdigest()[:16]
    
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize SQLite schema"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Algorithms table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS algorithms (
                    algorithm_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    parameters TEXT,
                    tags TEXT,
                    base_score REAL DEFAULT 0.5,
                    success_rate REAL DEFAULT 0.5,
                    avg_execution_time REAL DEFAULT 0,
                    total_executions INTEGER DEFAULT 0,
                    created_at TEXT
                )
            ''')
            
            # Execution history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS execution_history (
                    execution_id TEXT PRIMARY KEY,
                    algorithm_id TEXT,
                    task_type TEXT,
                    task_description TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    gpa_score REAL,
                    goal_alignment REAL,
                    plan_alignment REAL,
                    action_quality REAL,
                    execution_time_ms REAL,
                    resources_used TEXT,
                    success INTEGER,
                    timestamp TEXT
                )
            ''')
            
            # File history (for Brain)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    action TEXT,
                    description TEXT,
                    result TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Meta-Algorithms
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meta_algorithms (
                    meta_algorithm_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT,
                    workflow_graph TEXT,
                    success_rate REAL DEFAULT 0.5,
                    total_executions INTEGER DEFAULT 0,
                    created_at TEXT
                )
            ''')
            
            # Workflow executions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    meta_algorithm_id TEXT,
                    initial_request TEXT,
                    execution_log TEXT,
                    lead_time REAL,
                    wasted_action_ratio REAL,
                    path_complexity REAL,
                    final_success_rate REAL,
                    overall_score REAL,
                    timestamp TEXT
                )
            ''')
            
            # Theses (V4)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS theses (
                    thesis_id TEXT PRIMARY KEY,
                    statement TEXT,
                    supporting_evidence TEXT,
                    perspectives_analyzed TEXT,
                    recommended_approach TEXT,
                    expected_outcomes TEXT,
                    confidence_score REAL,
                    created_at TEXT
                )
            ''')
            
            # Knowledge graph entities
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT,
                    name TEXT,
                    properties TEXT,
                    created_at TEXT
                )
            ''')
            
            # Knowledge graph relations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_relations (
                    relation_id TEXT PRIMARY KEY,
                    from_entity TEXT,
                    to_entity TEXT,
                    relation_type TEXT,
                    properties TEXT,
                    created_at TEXT
                )
            ''')
            
            # Indices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_exec_algo ON execution_history(algorithm_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_history(file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_algo_tier ON algorithms(tier)')
            
            conn.commit()
            conn.close()
    
    # ==========================================
    # ALGORITHM OPERATIONS
    # ==========================================
    
    def register_algorithm(self, record: AlgorithmRecord) -> bool:
        """Register algorithm to portfolio"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO algorithms 
                (algorithm_id, name, tier, category, description, parameters, tags,
                 base_score, success_rate, avg_execution_time, total_executions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.algorithm_id, record.name, record.tier, record.category,
                record.description, json.dumps(record.parameters), json.dumps(record.tags),
                record.base_score, record.success_rate, record.avg_execution_time,
                record.total_executions, record.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
    
    def get_algorithm(self, algorithm_id: str) -> Optional[AlgorithmRecord]:
        """Get algorithm by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM algorithms WHERE algorithm_id = ?', (algorithm_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return AlgorithmRecord(
                algorithm_id=row['algorithm_id'],
                name=row['name'],
                tier=row['tier'],
                category=row['category'],
                description=row['description'],
                parameters=json.loads(row['parameters'] or '{}'),
                tags=json.loads(row['tags'] or '[]'),
                base_score=row['base_score'],
                success_rate=row['success_rate'],
                avg_execution_time=row['avg_execution_time'],
                total_executions=row['total_executions'],
                created_at=row['created_at']
            )
        return None
    
    def get_algorithms_by_tier(self, tier: str) -> List[AlgorithmRecord]:
        """Get all algorithms in a tier"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM algorithms WHERE tier = ?', (tier,))
        rows = cursor.fetchall()
        conn.close()
        
        return [AlgorithmRecord(
            algorithm_id=r['algorithm_id'], name=r['name'], tier=r['tier'],
            category=r['category'], description=r['description'],
            parameters=json.loads(r['parameters'] or '{}'),
            tags=json.loads(r['tags'] or '[]'),
            base_score=r['base_score'], success_rate=r['success_rate'],
            avg_execution_time=r['avg_execution_time'],
            total_executions=r['total_executions'], created_at=r['created_at']
        ) for r in rows]
    
    def get_all_algorithms(self) -> List[AlgorithmRecord]:
        """Get all algorithms"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM algorithms ORDER BY tier, name')
        rows = cursor.fetchall()
        conn.close()
        
        return [AlgorithmRecord(
            algorithm_id=r['algorithm_id'], name=r['name'], tier=r['tier'],
            category=r['category'], description=r['description'],
            parameters=json.loads(r['parameters'] or '{}'),
            tags=json.loads(r['tags'] or '[]'),
            base_score=r['base_score'], success_rate=r['success_rate'],
            avg_execution_time=r['avg_execution_time'],
            total_executions=r['total_executions'], created_at=r['created_at']
        ) for r in rows]
    
    # ==========================================
    # EXECUTION OPERATIONS
    # ==========================================
    
    def save_execution(self, record: ExecutionRecord) -> bool:
        """Save execution record and update algorithm stats"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO execution_history 
                (execution_id, algorithm_id, task_type, task_description, input_data,
                 output_data, gpa_score, goal_alignment, plan_alignment, action_quality,
                 execution_time_ms, resources_used, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.execution_id, record.algorithm_id, record.task_type,
                record.task_description, json.dumps(record.input_data),
                json.dumps(record.output_data), record.gpa_score,
                record.goal_alignment, record.plan_alignment, record.action_quality,
                record.execution_time_ms, json.dumps(record.resources_used),
                1 if record.success else 0, record.timestamp
            ))
            
            # Update algorithm stats
            cursor.execute('''
                UPDATE algorithms SET
                    total_executions = total_executions + 1,
                    success_rate = (success_rate * total_executions + ?) / (total_executions + 1),
                    avg_execution_time = (avg_execution_time * total_executions + ?) / (total_executions + 1)
                WHERE algorithm_id = ?
            ''', (1.0 if record.success else 0.0, record.execution_time_ms, record.algorithm_id))
            
            conn.commit()
            conn.close()
            return True
    
    def get_execution_history(self, algorithm_id: str = None, limit: int = 100) -> List[dict]:
        """Get execution history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if algorithm_id:
            cursor.execute(
                'SELECT * FROM execution_history WHERE algorithm_id = ? ORDER BY timestamp DESC LIMIT ?',
                (algorithm_id, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM execution_history ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def calculate_historical_cost(self, algorithm_id: str) -> float:
        """Calculate g(A) for A* heuristic"""
        algo = self.get_algorithm(algorithm_id)
        if not algo or algo.total_executions == 0:
            return 0.5
        
        gpa_cost = 1.0 - (self._get_avg_gpa(algorithm_id) or 0.5)
        time_cost = min(algo.avg_execution_time / 10000, 1.0)
        success_cost = 1.0 - algo.success_rate
        
        return gpa_cost * 0.5 + time_cost * 0.2 + success_cost * 0.3
    
    def _get_avg_gpa(self, algorithm_id: str) -> float:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT AVG(gpa_score) as avg FROM execution_history WHERE algorithm_id = ?',
            (algorithm_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row['avg'] if row and row['avg'] else 0.5
    
    # ==========================================
    # THESIS OPERATIONS (V4)
    # ==========================================
    
    def save_thesis(self, record: ThesisRecord) -> bool:
        """Save strategic thesis"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO theses 
                (thesis_id, statement, supporting_evidence, perspectives_analyzed,
                 recommended_approach, expected_outcomes, confidence_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.thesis_id, record.statement,
                json.dumps(record.supporting_evidence),
                json.dumps(record.perspectives_analyzed),
                record.recommended_approach,
                json.dumps(record.expected_outcomes),
                record.confidence_score, record.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
    
    def get_similar_theses(self, keywords: List[str], limit: int = 5) -> List[ThesisRecord]:
        """Get theses matching keywords"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        conditions = ' OR '.join(['statement LIKE ?' for _ in keywords])
        params = [f'%{kw}%' for kw in keywords] + [limit]
        
        cursor.execute(
            f'SELECT * FROM theses WHERE {conditions} ORDER BY confidence_score DESC LIMIT ?',
            params
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ThesisRecord(
            thesis_id=r['thesis_id'],
            statement=r['statement'],
            supporting_evidence=json.loads(r['supporting_evidence'] or '[]'),
            perspectives_analyzed=json.loads(r['perspectives_analyzed'] or '[]'),
            recommended_approach=r['recommended_approach'],
            expected_outcomes=json.loads(r['expected_outcomes'] or '[]'),
            confidence_score=r['confidence_score'],
            created_at=r['created_at']
        ) for r in rows]
    
    # ==========================================
    # CONVERSATION & KNOWLEDGE (via cache)
    # ==========================================
    
    def store_conversation(self, user_input: str, response: str) -> str:
        """Store conversation to cache"""
        entry = MemoryEntry(
            id=f"{self._computer_id[:8]}_{int(time.time()*1000)}",
            type=MemoryType.CONVERSATION,
            content=f"User: {user_input}\nAssistant: {response}",
            metadata={"user_input": user_input, "response": response[:500]}
        )
        self.cache.add(entry)
        return entry.id
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search across cache"""
        entries = self.cache.search(query, limit)
        return [e.to_dict() for e in entries]
    
    # ==========================================
    # CLOUD SYNC
    # ==========================================
    
    def sync_to_cloud(self) -> Dict:
        """Sync unsynced entries to cloud"""
        unsynced = self.cache.get_unsynced()
        
        if not unsynced:
            return {"status": "no_changes", "synced": 0}
        
        if not self.cloud.is_connected():
            return {"status": "offline", "pending": len(unsynced)}
        
        success, failed = self.cloud.sync_all(unsynced)
        
        for entry in unsynced:
            if success > 0:
                self.cache.mark_synced(entry.id)
                success -= 1
        
        return {"status": "synced", "synced": success, "failed": failed}
    
    # ==========================================
    # STATISTICS
    # ==========================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Algorithms
        cursor.execute('SELECT COUNT(*) as count FROM algorithms')
        stats['total_algorithms'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT tier, COUNT(*) as count FROM algorithms GROUP BY tier')
        stats['algorithms_by_tier'] = {r['tier']: r['count'] for r in cursor.fetchall()}
        
        # Executions
        cursor.execute('SELECT COUNT(*) as count FROM execution_history')
        stats['total_executions'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT AVG(gpa_score) as avg FROM execution_history')
        row = cursor.fetchone()
        stats['avg_gpa_score'] = row['avg'] if row['avg'] else 0
        
        # Theses
        cursor.execute('SELECT COUNT(*) as count FROM theses')
        stats['total_theses'] = cursor.fetchone()['count']
        
        conn.close()
        
        # Add other stats
        stats['projects'] = len(self.project.list_projects())
        stats['cache'] = self.cache.stats()
        stats['cloud_connected'] = self.cloud.is_connected()
        
        return stats
    
    def print_stats(self):
        """Print memory statistics"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 50)
        print("💾 MEMORY V5 STATISTICS")
        print("=" * 50)
        print(f"   📊 Algorithms: {stats['total_algorithms']}")
        for tier, count in stats.get('algorithms_by_tier', {}).items():
            print(f"      - {tier}: {count}")
        print(f"   📈 Executions: {stats['total_executions']}")
        print(f"   📝 Avg GPA: {stats['avg_gpa_score']:.2f}")
        print(f"   💡 Theses: {stats['total_theses']}")
        print(f"   📁 Projects: {stats['projects']}")
        print(f"   🗂️  Cache: {stats['cache']['total_entries']} entries")
        print(f"   ☁️  Cloud: {'Connected' if stats['cloud_connected'] else 'Offline'}")
        print("=" * 50)


# ==========================================
# SINGLETON
# ==========================================

_memory_v5_instance = None

def get_memory_v5(base_path: str = "data/dive_ai_v5") -> MemoryV5:
    """Get or create Memory V5 singleton"""
    global _memory_v5_instance
    if _memory_v5_instance is None:
        _memory_v5_instance = MemoryV5(base_path)
    return _memory_v5_instance


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("💾 MEMORY V5 UNIFIED SYSTEM TEST")
    print("=" * 60)
    
    memory = get_memory_v5("data/test_memory_v5")
    
    # Test project operations
    print("\n📁 Testing Project Layer...")
    memory.project.initialize_project("test-project", "A test project")
    memory.project.log_change("test-project", "Added", "Initial setup")
    print(f"   Projects: {memory.project.list_projects()}")
    
    # Test algorithm registration
    print("\n🧠 Testing Algorithm Layer...")
    algo = AlgorithmRecord(
        algorithm_id="TestAlgo",
        name="Test Algorithm",
        tier="operation",
        category="testing",
        description="Test algorithm"
    )
    memory.register_algorithm(algo)
    print(f"   Registered: {algo.algorithm_id}")
    
    # Test execution
    print("\n📊 Testing Execution Layer...")
    exec_record = ExecutionRecord(
        execution_id=str(uuid.uuid4()),
        algorithm_id="TestAlgo",
        task_type="test",
        task_description="Test execution",
        input_data={"test": True},
        output_data={"result": "ok"},
        gpa_score=0.85,
        goal_alignment=0.9,
        plan_alignment=0.8,
        action_quality=0.85,
        execution_time_ms=150,
        resources_used={},
        success=True
    )
    memory.save_execution(exec_record)
    print(f"   Saved execution: {exec_record.execution_id}")
    
    # Test cache
    print("\n🗂️  Testing Cache Layer...")
    memory.store_conversation("Hello", "Hi there!")
    results = memory.search("Hello")
    print(f"   Search results: {len(results)}")
    
    # Test brain
    print("\n🧠 Testing Brain Layer...")
    brain_check = memory.brain.check_before_task_execute("test task")
    print(f"   Brain check: {brain_check['recommendation']}")
    
    # Print stats
    memory.print_stats()
    
    # Test g(A) calculation
    g_cost = memory.calculate_historical_cost("TestAlgo")
    print(f"\n📐 g(A) for TestAlgo: {g_cost:.3f}")
    
    print("\n✅ Memory V5 test completed!")
