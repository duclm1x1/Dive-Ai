"""
Dive Memory V4 - Doc-First, Never Forget Architecture

Philosophy:
- Doc first, code later
- Read before write
- Never forget
- Context accumulation
- Token efficiency

Architecture:
User Request → Orchestrator (reads memory) → Memory V4 → Coder (context-aware) → Memory (saves) → Loop

Author: Dive AI Team
Version: 4.0.0
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading


@dataclass
class Doc:
    """Documentation entry"""
    id: str
    path: str  # @doc/project/feature
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    version: int
    references: List[str]  # Other docs referenced
    
    
@dataclass
class Task:
    """Task with acceptance criteria"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    doc_references: List[str]  # @doc/... references
    status: str  # pending, in_progress, done
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    result: Optional[str]


@dataclass
class Decision:
    """Decision record"""
    id: str
    title: str
    context: str
    options: List[Dict[str, Any]]
    chosen: str
    rationale: str
    doc_reference: Optional[str]
    created_at: str


@dataclass
class Execution:
    """Execution result"""
    id: str
    task_id: str
    agent: str
    input: str
    output: str
    success: bool
    duration: float
    tokens_used: int
    created_at: str


class DiveMemoryV4:
    """
    Dive Memory V4 - Doc-First, Never Forget
    
    Features:
    - Doc-first workflow
    - @doc/... references
    - Auto-read task state
    - Knowledge accumulation
    - Token efficiency
    - Multi-threaded
    - SQLite + Markdown
    """
    
    def __init__(self, base_path: str = "memory"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "dive_memory_v4.db"
        self.docs_path = self.base_path / "docs"
        self.tasks_path = self.base_path / "tasks"
        self.decisions_path = self.base_path / "decisions"
        self.executions_path = self.base_path / "executions"
        
        # Create directories
        for path in [self.docs_path, self.tasks_path, self.decisions_path, self.executions_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        # Thread lock
        self._lock = threading.Lock()
        
        print("✅ Dive Memory V4 initialized")
        print(f"   Base path: {self.base_path}")
        print(f"   Database: {self.db_path}")
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Docs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docs (
                id TEXT PRIMARY KEY,
                path TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                tags TEXT,
                created_at TEXT,
                updated_at TEXT,
                version INTEGER,
                doc_refs TEXT
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT,
                doc_references TEXT,
                created_at TEXT,
                updated_at TEXT,
                completed_at TEXT
            )
        """)
        
        # Decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                chosen TEXT,
                doc_reference TEXT,
                created_at TEXT
            )
        """)
        
        # Executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                agent TEXT,
                success INTEGER,
                duration REAL,
                tokens_used INTEGER,
                created_at TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_path ON docs(path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_task ON executions(task_id)")
        
        conn.commit()
        conn.close()
    
    # ==================== DOC OPERATIONS ====================
    
    def create_doc(self, path: str, title: str, content: str, tags: List[str] = None) -> Doc:
        """
        Create documentation (doc-first workflow)
        
        Args:
            path: @doc/project/feature
            title: Document title
            content: Markdown content
            tags: Tags for categorization
            
        Returns:
            Doc object
        """
        with self._lock:
            doc_id = hashlib.md5(path.encode()).hexdigest()[:12]
            now = datetime.now().isoformat()
            
            doc = Doc(
                id=doc_id,
                path=path,
                title=title,
                content=content,
                tags=tags or [],
                created_at=now,
                updated_at=now,
                version=1,
                references=self._extract_doc_references(content)
            )
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO docs 
                (id, path, title, tags, created_at, updated_at, version, doc_refs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.id, doc.path, doc.title, 
                json.dumps(doc.tags),
                doc.created_at, doc.updated_at, doc.version,
                json.dumps(doc.references)
            ))
            conn.commit()
            conn.close()
            
            # Save to markdown file
            doc_file = self.docs_path / f"{doc_id}.md"
            with open(doc_file, 'w') as f:
                f.write(f"# {doc.title}\n\n")
                f.write(f"**Path**: {doc.path}\n")
                f.write(f"**Tags**: {', '.join(doc.tags)}\n")
                f.write(f"**Created**: {doc.created_at}\n")
                f.write(f"**Version**: {doc.version}\n\n")
                f.write("---\n\n")
                f.write(doc.content)
            
            print(f"✅ Doc created: {doc.path}")
            return doc
    
    def read_doc(self, path: str) -> Optional[Doc]:
        """
        Read documentation by path
        
        Args:
            path: @doc/project/feature
            
        Returns:
            Doc object or None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docs WHERE path = ?", (path,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Read content from file
        doc_id = row[0]
        doc_file = self.docs_path / f"{doc_id}.md"
        
        if not doc_file.exists():
            return None
        
        with open(doc_file, 'r') as f:
            content = f.read()
            # Extract content after ---
            parts = content.split('---\n\n', 1)
            actual_content = parts[1] if len(parts) > 1 else content
        
        return Doc(
            id=row[0],
            path=row[1],
            title=row[2],
            tags=json.loads(row[3]) if row[3] else [],
            created_at=row[4],
            updated_at=row[5],
            version=row[6],
            references=json.loads(row[7]) if row[7] else [],
            content=actual_content
        )
    
    def update_doc(self, path: str, content: str) -> Doc:
        """Update documentation"""
        doc = self.read_doc(path)
        if not doc:
            raise ValueError(f"Doc not found: {path}")
        
        with self._lock:
            doc.content = content
            doc.updated_at = datetime.now().isoformat()
            doc.version += 1
            doc.references = self._extract_doc_references(content)
            
            # Update database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE docs 
                SET updated_at = ?, version = ?, doc_refs = ?
                WHERE path = ?
            """, (doc.updated_at, doc.version, json.dumps(doc.references), path))
            conn.commit()
            conn.close()
            
            # Update file
            doc_file = self.docs_path / f"{doc.id}.md"
            with open(doc_file, 'w') as f:
                f.write(f"# {doc.title}\n\n")
                f.write(f"**Path**: {doc.path}\n")
                f.write(f"**Tags**: {', '.join(doc.tags)}\n")
                f.write(f"**Updated**: {doc.updated_at}\n")
                f.write(f"**Version**: {doc.version}\n\n")
                f.write("---\n\n")
                f.write(doc.content)
            
            print(f"✅ Doc updated: {doc.path} (v{doc.version})")
            return doc
    
    def search_docs(self, query: str = None, tags: List[str] = None) -> List[Doc]:
        """Search documentation"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if tags:
            # Search by tags
            docs = []
            cursor.execute("SELECT * FROM docs")
            for row in cursor.fetchall():
                doc_tags = json.loads(row[3]) if row[3] else []
                if any(tag in doc_tags for tag in tags):
                    doc = self.read_doc(row[1])
                    if doc:
                        docs.append(doc)
            conn.close()
            return docs
        
        if query:
            # Full-text search (simple)
            cursor.execute("SELECT * FROM docs WHERE title LIKE ? OR path LIKE ?", 
                          (f"%{query}%", f"%{query}%"))
            rows = cursor.fetchall()
            conn.close()
            
            docs = []
            for row in rows:
                doc = self.read_doc(row[1])
                if doc:
                    docs.append(doc)
            return docs
        
        # Return all
        cursor.execute("SELECT * FROM docs")
        rows = cursor.fetchall()
        conn.close()
        
        docs = []
        for row in rows:
            doc = self.read_doc(row[1])
            if doc:
                docs.append(doc)
        return docs
    
    # ==================== TASK OPERATIONS ====================
    
    def create_task(self, title: str, description: str, 
                   acceptance_criteria: List[str],
                   doc_references: List[str] = None) -> Task:
        """
        Create task with acceptance criteria and doc references
        
        Args:
            title: Task title
            description: Task description
            acceptance_criteria: List of acceptance criteria
            doc_references: List of @doc/... references
            
        Returns:
            Task object
        """
        with self._lock:
            task_id = hashlib.md5(f"{title}{datetime.now()}".encode()).hexdigest()[:12]
            now = datetime.now().isoformat()
            
            task = Task(
                id=task_id,
                title=title,
                description=description,
                acceptance_criteria=acceptance_criteria,
                doc_references=doc_references or [],
                status="pending",
                created_at=now,
                updated_at=now,
                completed_at=None,
                result=None
            )
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks 
                (id, title, status, doc_references, created_at, updated_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id, task.title, task.status,
                json.dumps(task.doc_references),
                task.created_at, task.updated_at, task.completed_at
            ))
            conn.commit()
            conn.close()
            
            # Save to markdown file
            task_file = self.tasks_path / f"{task_id}.md"
            with open(task_file, 'w') as f:
                f.write(f"# {task.title}\n\n")
                f.write(f"**Status**: {task.status}\n")
                f.write(f"**Created**: {task.created_at}\n\n")
                f.write("## Description\n\n")
                f.write(f"{task.description}\n\n")
                f.write("## Acceptance Criteria\n\n")
                for i, criterion in enumerate(task.acceptance_criteria, 1):
                    f.write(f"{i}. [ ] {criterion}\n")
                f.write("\n## Doc References\n\n")
                for ref in task.doc_references:
                    f.write(f"- {ref}\n")
            
            print(f"✅ Task created: {task.title}")
            return task
    
    def read_task(self, task_id: str) -> Optional[Task]:
        """Read task by ID"""
        task_file = self.tasks_path / f"{task_id}.md"
        if not task_file.exists():
            return None
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Parse markdown file
        with open(task_file, 'r') as f:
            content = f.read()
        
        # Extract components (simplified)
        lines = content.split('\n')
        description = ""
        criteria = []
        references = []
        result = None
        
        in_desc = False
        in_criteria = False
        in_refs = False
        in_result = False
        
        for line in lines:
            if line.startswith("## Description"):
                in_desc = True
                in_criteria = False
                in_refs = False
                in_result = False
            elif line.startswith("## Acceptance Criteria"):
                in_desc = False
                in_criteria = True
                in_refs = False
                in_result = False
            elif line.startswith("## Doc References"):
                in_desc = False
                in_criteria = False
                in_refs = True
                in_result = False
            elif line.startswith("## Result"):
                in_desc = False
                in_criteria = False
                in_refs = False
                in_result = True
            elif in_desc and line.strip():
                description += line + "\n"
            elif in_criteria and line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                criteria.append(line.split("] ", 1)[1] if "] " in line else line)
            elif in_refs and line.strip().startswith("-"):
                references.append(line.strip()[2:])
            elif in_result and line.strip():
                result = (result or "") + line + "\n"
        
        return Task(
            id=row[0],
            title=row[1],
            description=description.strip(),
            acceptance_criteria=criteria,
            doc_references=json.loads(row[3]) if row[3] else [],
            status=row[2],
            created_at=row[4],
            updated_at=row[5],
            completed_at=row[6],
            result=result
        )
    
    def update_task_status(self, task_id: str, status: str, result: str = None):
        """Update task status"""
        with self._lock:
            now = datetime.now().isoformat()
            completed_at = now if status == "done" else None
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET status = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
            """, (status, now, completed_at, task_id))
            conn.commit()
            conn.close()
            
            # Update file
            task = self.read_task(task_id)
            if task:
                task_file = self.tasks_path / f"{task_id}.md"
                with open(task_file, 'w') as f:
                    f.write(f"# {task.title}\n\n")
                    f.write(f"**Status**: {status}\n")
                    f.write(f"**Created**: {task.created_at}\n")
                    f.write(f"**Updated**: {now}\n")
                    if completed_at:
                        f.write(f"**Completed**: {completed_at}\n")
                    f.write("\n## Description\n\n")
                    f.write(f"{task.description}\n\n")
                    f.write("## Acceptance Criteria\n\n")
                    for i, criterion in enumerate(task.acceptance_criteria, 1):
                        check = "x" if status == "done" else " "
                        f.write(f"{i}. [{check}] {criterion}\n")
                    f.write("\n## Doc References\n\n")
                    for ref in task.doc_references:
                        f.write(f"- {ref}\n")
                    if result:
                        f.write("\n## Result\n\n")
                        f.write(result)
            
            print(f"✅ Task updated: {task_id} → {status}")
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE status = 'pending'")
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.read_task(tid) for tid in task_ids if self.read_task(tid)]
    
    # ==================== DECISION OPERATIONS ====================
    
    def record_decision(self, title: str, context: str, 
                       options: List[Dict[str, Any]], 
                       chosen: str, rationale: str,
                       doc_reference: str = None) -> Decision:
        """Record a decision"""
        with self._lock:
            decision_id = hashlib.md5(f"{title}{datetime.now()}".encode()).hexdigest()[:12]
            now = datetime.now().isoformat()
            
            decision = Decision(
                id=decision_id,
                title=title,
                context=context,
                options=options,
                chosen=chosen,
                rationale=rationale,
                doc_reference=doc_reference,
                created_at=now
            )
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decisions 
                (id, title, chosen, doc_reference, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (decision.id, decision.title, decision.chosen, decision.doc_reference, decision.created_at))
            conn.commit()
            conn.close()
            
            # Save to markdown
            decision_file = self.decisions_path / f"{decision_id}.md"
            with open(decision_file, 'w') as f:
                f.write(f"# {decision.title}\n\n")
                f.write(f"**Created**: {decision.created_at}\n")
                if decision.doc_reference:
                    f.write(f"**Doc**: {decision.doc_reference}\n")
                f.write("\n## Context\n\n")
                f.write(f"{decision.context}\n\n")
                f.write("## Options\n\n")
                for i, opt in enumerate(decision.options, 1):
                    f.write(f"{i}. **{opt.get('name', f'Option {i}')}**\n")
                    f.write(f"   - {opt.get('description', '')}\n")
                f.write(f"\n## Chosen\n\n")
                f.write(f"**{decision.chosen}**\n\n")
                f.write("## Rationale\n\n")
                f.write(decision.rationale)
            
            print(f"✅ Decision recorded: {decision.title}")
            return decision
    
    # ==================== EXECUTION OPERATIONS ====================
    
    def record_execution(self, task_id: str, agent: str, 
                        input_data: str, output_data: str,
                        success: bool, duration: float, 
                        tokens_used: int) -> Execution:
        """Record execution result"""
        with self._lock:
            exec_id = hashlib.md5(f"{task_id}{datetime.now()}".encode()).hexdigest()[:12]
            now = datetime.now().isoformat()
            
            execution = Execution(
                id=exec_id,
                task_id=task_id,
                agent=agent,
                input=input_data,
                output=output_data,
                success=success,
                duration=duration,
                tokens_used=tokens_used,
                created_at=now
            )
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO executions 
                (id, task_id, agent, success, duration, tokens_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.id, execution.task_id, execution.agent,
                1 if execution.success else 0,
                execution.duration, execution.tokens_used, execution.created_at
            ))
            conn.commit()
            conn.close()
            
            # Save to markdown
            exec_file = self.executions_path / f"{exec_id}.md"
            with open(exec_file, 'w') as f:
                f.write(f"# Execution: {task_id}\n\n")
                f.write(f"**Agent**: {execution.agent}\n")
                f.write(f"**Success**: {execution.success}\n")
                f.write(f"**Duration**: {execution.duration:.2f}s\n")
                f.write(f"**Tokens**: {execution.tokens_used}\n")
                f.write(f"**Created**: {execution.created_at}\n\n")
                f.write("## Input\n\n```\n")
                f.write(execution.input)
                f.write("\n```\n\n## Output\n\n```\n")
                f.write(execution.output)
                f.write("\n```")
            
            print(f"✅ Execution recorded: {exec_id}")
            return execution
    
    # ==================== HELPER METHODS ====================
    
    def _extract_doc_references(self, content: str) -> List[str]:
        """Extract @doc/... references from content"""
        import re
        pattern = r'@doc/[\w/\-]+'
        return list(set(re.findall(pattern, content)))
    
    def get_context_for_task(self, task_id: str) -> str:
        """
        Get full context for a task (auto-read workflow)
        
        This is what AI reads before starting work:
        - Task description
        - Acceptance criteria
        - Referenced docs
        - Previous decisions
        - Previous executions
        
        Returns:
            Complete context as markdown
        """
        task = self.read_task(task_id)
        if not task:
            return "Task not found"
        
        context = f"# Task Context: {task.title}\n\n"
        context += f"**Status**: {task.status}\n\n"
        context += "## Description\n\n"
        context += f"{task.description}\n\n"
        context += "## Acceptance Criteria\n\n"
        for i, criterion in enumerate(task.acceptance_criteria, 1):
            context += f"{i}. {criterion}\n"
        
        # Add referenced docs
        if task.doc_references:
            context += "\n## Referenced Documentation\n\n"
            for ref in task.doc_references:
                doc = self.read_doc(ref)
                if doc:
                    context += f"### {doc.title} ({ref})\n\n"
                    context += doc.content + "\n\n"
        
        # Add previous executions
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM executions 
            WHERE task_id = ? 
            ORDER BY created_at DESC 
            LIMIT 3
        """, (task_id,))
        exec_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if exec_ids:
            context += "\n## Previous Attempts\n\n"
            for exec_id in exec_ids:
                exec_file = self.executions_path / f"{exec_id}.md"
                if exec_file.exists():
                    with open(exec_file, 'r') as f:
                        context += f.read() + "\n\n"
        
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM docs")
        docs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        tasks_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
        tasks_done = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM decisions")
        decisions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM executions")
        executions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(tokens_used) FROM executions")
        total_tokens = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "docs": docs_count,
            "tasks": tasks_count,
            "tasks_done": tasks_done,
            "decisions": decisions_count,
            "executions": executions_count,
            "total_tokens": total_tokens,
            "completion_rate": f"{(tasks_done/tasks_count*100):.1f}%" if tasks_count > 0 else "0%"
        }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Initialize
    memory = DiveMemoryV4("memory")
    
    # Doc-first workflow
    print("\n=== DOC-FIRST WORKFLOW ===")
    
    # 1. Create documentation first
    doc = memory.create_doc(
        path="@doc/dive-ai/cache-system",
        title="Dive Cache System Design",
        content="""
# Dive Cache System

## Overview
Multi-level caching system for Dive AI.

## Architecture
- Level 1: Memory (LRU)
- Level 2: Disk (SQLite)
- Level 3: Distributed (Redis)

## Implementation
See @doc/dive-ai/implementation-guide for details.

## Performance Goals
- 10-100x faster repeated operations
- 80-95% cache hit rate
- <5ms latency
""",
        tags=["cache", "performance", "architecture"]
    )
    
    # 2. Create task with reference to doc
    task = memory.create_task(
        title="Implement Dive Cache System",
        description="Implement multi-level caching as designed in documentation",
        acceptance_criteria=[
            "Memory cache with LRU eviction",
            "Disk cache with SQLite",
            "Cache hit rate > 80%",
            "Latency < 5ms",
            "Unit tests with 100% coverage"
        ],
        doc_references=["@doc/dive-ai/cache-system"]
    )
    
    # 3. AI reads context before starting
    context = memory.get_context_for_task(task.id)
    print(f"\n📖 Context for AI:\n{context[:500]}...")
    
    # 4. Record execution
    execution = memory.record_execution(
        task_id=task.id,
        agent="Dive Coder",
        input_data="Implement cache system",
        output_data="Cache system implemented with all features",
        success=True,
        duration=120.5,
        tokens_used=5000
    )
    
    # 5. Update task status
    memory.update_task_status(task.id, "done", "Cache system implemented successfully")
    
    # 6. Record decision
    decision = memory.record_decision(
        title="Choose cache eviction policy",
        context="Need to decide on cache eviction policy",
        options=[
            {"name": "LRU", "description": "Least Recently Used"},
            {"name": "LFU", "description": "Least Frequently Used"},
            {"name": "FIFO", "description": "First In First Out"}
        ],
        chosen="LRU",
        rationale="LRU provides best balance of simplicity and effectiveness",
        doc_reference="@doc/dive-ai/cache-system"
    )
    
    # Stats
    print("\n=== MEMORY STATS ===")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ Dive Memory V4 demo complete!")
