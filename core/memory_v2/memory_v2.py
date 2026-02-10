"""
Dive AI V29 - Memory V2 System
SQLite-based persistent memory with Algorithm Portfolio, Execution History, and Knowledge Graph

Core Tables:
1. algorithms - Algorithm Portfolio with metadata
2. execution_history - Execution records with GPA scores
3. knowledge_entities - Knowledge graph entities
4. knowledge_relations - Knowledge graph relations
5. meta_algorithms - Workflow state graphs
6. workflow_executions - Workflow KPIs
7. theses - Strategic thesis storage (V4)
8. thesis_outcomes - Thesis learning data (V4)
"""

import sqlite3
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import threading


@dataclass
class GPAScore:
    """GPA Score for action evaluation"""
    goal_alignment: float  # 0-1
    plan_alignment: float  # 0-1
    action_quality: float  # 0-1
    overall: float  # weighted average
    
    @staticmethod
    def calculate(goal: float, plan: float, action: float) -> 'GPAScore':
        overall = goal * 0.4 + plan * 0.3 + action * 0.3
        return GPAScore(goal, plan, action, overall)


@dataclass
class ProcessKPIs:
    """Process Key Performance Indicators for workflow evaluation"""
    lead_time: float  # seconds
    wasted_action_ratio: float  # 0-1
    path_complexity: float  # 0-1
    final_success_rate: float  # 0-1
    overall_score: float  # 0-1


@dataclass
class AlgorithmRecord:
    """Algorithm record in portfolio"""
    algorithm_id: str
    name: str
    tier: str  # strategy, tactic, operation
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
    """Strategic thesis record"""
    thesis_id: str
    statement: str
    supporting_evidence: List[str]
    perspectives_analyzed: List[str]
    recommended_approach: str
    expected_outcomes: List[str]
    confidence_score: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MemoryV2:
    """
    Dive AI V29 - Memory V2 System
    
    SQLite-backed persistent memory with:
    - Algorithm Portfolio (algorithm metadata + performance)
    - Execution History (action logs + GPA scores)
    - Knowledge Graph (entities + relations)
    - Thesis Storage (V4 strategic learning)
    """
    
    def __init__(self, db_path: str = "data/dive_ai_v29.db"):
        """Initialize Memory V2"""
        self.db_path = db_path
        self._lock = threading.Lock()
        
        # Ensure directory exists
        Path(os.path.dirname(db_path) or '.').mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        print(f"💾 Memory V2 initialized: {db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-safe database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database schema"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 1. Algorithm Portfolio
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
            
            # 2. Execution History
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
                    timestamp TEXT,
                    FOREIGN KEY (algorithm_id) REFERENCES algorithms(algorithm_id)
                )
            ''')
            
            # 3. Knowledge Entities
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT,
                    name TEXT,
                    properties TEXT,
                    created_at TEXT
                )
            ''')
            
            # 4. Knowledge Relations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_relations (
                    relation_id TEXT PRIMARY KEY,
                    from_entity TEXT,
                    to_entity TEXT,
                    relation_type TEXT,
                    properties TEXT,
                    created_at TEXT,
                    FOREIGN KEY (from_entity) REFERENCES knowledge_entities(entity_id),
                    FOREIGN KEY (to_entity) REFERENCES knowledge_entities(entity_id)
                )
            ''')
            
            # 5. Meta-Algorithms (Workflow State Graphs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meta_algorithms (
                    meta_algorithm_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT,
                    workflow_graph TEXT,
                    description TEXT,
                    success_rate REAL DEFAULT 0.5,
                    avg_lead_time REAL DEFAULT 0,
                    total_executions INTEGER DEFAULT 0,
                    created_at TEXT
                )
            ''')
            
            # 6. Workflow Executions
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
                    timestamp TEXT,
                    FOREIGN KEY (meta_algorithm_id) REFERENCES meta_algorithms(meta_algorithm_id)
                )
            ''')
            
            # 7. Theses (V4)
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
            
            # 8. Thesis Outcomes (V4)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS thesis_outcomes (
                    outcome_id TEXT PRIMARY KEY,
                    thesis_id TEXT,
                    execution_id TEXT,
                    effectiveness_score REAL,
                    actual_vs_expected TEXT,
                    lessons_learned TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (thesis_id) REFERENCES theses(thesis_id),
                    FOREIGN KEY (execution_id) REFERENCES workflow_executions(execution_id)
                )
            ''')
            
            # Create indices for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_exec_algo ON execution_history(algorithm_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_exec_time ON execution_history(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_algo_tier ON algorithms(tier)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_meta ON workflow_executions(meta_algorithm_id)')
            
            conn.commit()
            conn.close()
    
    # ==========================================
    # ALGORITHM PORTFOLIO OPERATIONS
    # ==========================================
    
    def register_algorithm(self, record: AlgorithmRecord) -> bool:
        """Register or update an algorithm in the portfolio"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO algorithms 
                (algorithm_id, name, tier, category, description, parameters, tags, 
                 base_score, success_rate, avg_execution_time, total_executions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.algorithm_id,
                record.name,
                record.tier,
                record.category,
                record.description,
                json.dumps(record.parameters),
                json.dumps(record.tags),
                record.base_score,
                record.success_rate,
                record.avg_execution_time,
                record.total_executions,
                record.created_at
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
        
        return [
            AlgorithmRecord(
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
            for row in rows
        ]
    
    def get_all_algorithms(self) -> List[AlgorithmRecord]:
        """Get all algorithms in portfolio"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM algorithms ORDER BY tier, name')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            AlgorithmRecord(
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
            for row in rows
        ]
    
    def update_algorithm_stats(
        self, 
        algorithm_id: str, 
        success: bool, 
        execution_time_ms: float
    ):
        """Update algorithm statistics after execution"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute(
                'SELECT total_executions, success_rate, avg_execution_time FROM algorithms WHERE algorithm_id = ?',
                (algorithm_id,)
            )
            row = cursor.fetchone()
            
            if row:
                total = row['total_executions'] + 1
                # Running average for success rate
                old_rate = row['success_rate']
                new_rate = old_rate + (1.0 if success else 0.0 - old_rate) / total
                # Running average for execution time
                old_time = row['avg_execution_time']
                new_time = old_time + (execution_time_ms - old_time) / total
                
                cursor.execute('''
                    UPDATE algorithms 
                    SET total_executions = ?, success_rate = ?, avg_execution_time = ?
                    WHERE algorithm_id = ?
                ''', (total, new_rate, new_time, algorithm_id))
            
            conn.commit()
            conn.close()
    
    # ==========================================
    # EXECUTION HISTORY OPERATIONS
    # ==========================================
    
    def save_execution(self, record: ExecutionRecord) -> bool:
        """Save execution record"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO execution_history 
                (execution_id, algorithm_id, task_type, task_description, input_data, output_data,
                 gpa_score, goal_alignment, plan_alignment, action_quality, execution_time_ms,
                 resources_used, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.execution_id,
                record.algorithm_id,
                record.task_type,
                record.task_description,
                json.dumps(record.input_data),
                json.dumps(record.output_data),
                record.gpa_score,
                record.goal_alignment,
                record.plan_alignment,
                record.action_quality,
                record.execution_time_ms,
                json.dumps(record.resources_used),
                1 if record.success else 0,
                record.timestamp
            ))
            
            conn.commit()
            conn.close()
            
            # Update algorithm stats
            self.update_algorithm_stats(
                record.algorithm_id,
                record.success,
                record.execution_time_ms
            )
            
            return True
    
    def get_execution_history(
        self, 
        algorithm_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionRecord]:
        """Get execution history, optionally filtered by algorithm"""
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
        
        return [
            ExecutionRecord(
                execution_id=row['execution_id'],
                algorithm_id=row['algorithm_id'],
                task_type=row['task_type'],
                task_description=row['task_description'],
                input_data=json.loads(row['input_data'] or '{}'),
                output_data=json.loads(row['output_data'] or '{}'),
                gpa_score=row['gpa_score'],
                goal_alignment=row['goal_alignment'],
                plan_alignment=row['plan_alignment'],
                action_quality=row['action_quality'],
                execution_time_ms=row['execution_time_ms'],
                resources_used=json.loads(row['resources_used'] or '{}'),
                success=bool(row['success']),
                timestamp=row['timestamp']
            )
            for row in rows
        ]
    
    def get_algorithm_success_rate(self, algorithm_id: str) -> float:
        """Get success rate for an algorithm from history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT AVG(CAST(success AS REAL)) as rate FROM execution_history WHERE algorithm_id = ?',
            (algorithm_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return row['rate'] if row and row['rate'] else 0.5
    
    def get_algorithm_avg_gpa(self, algorithm_id: str) -> float:
        """Get average GPA score for an algorithm"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT AVG(gpa_score) as avg_gpa FROM execution_history WHERE algorithm_id = ?',
            (algorithm_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return row['avg_gpa'] if row and row['avg_gpa'] else 0.5
    
    # ==========================================
    # HISTORICAL COST CALCULATION (for A*)
    # ==========================================
    
    def calculate_historical_cost(self, algorithm_id: str) -> float:
        """
        Calculate g(A) for A* heuristic
        
        g(A) = Historical cost based on:
        - GPA score (lower is better cost)
        - Execution time
        - Success rate
        """
        algo = self.get_algorithm(algorithm_id)
        
        if not algo or algo.total_executions == 0:
            return 0.5  # Default neutral cost
        
        # Invert GPA score to get cost (higher GPA = lower cost)
        avg_gpa = self.get_algorithm_avg_gpa(algorithm_id)
        gpa_cost = 1.0 - avg_gpa
        
        # Normalize execution time (assuming 10s is max reasonable)
        time_cost = min(algo.avg_execution_time / 10000, 1.0)
        
        # Invert success rate to get cost
        success_cost = 1.0 - algo.success_rate
        
        # Weighted combination
        g_cost = gpa_cost * 0.5 + time_cost * 0.2 + success_cost * 0.3
        
        return g_cost
    
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
                record.thesis_id,
                record.statement,
                json.dumps(record.supporting_evidence),
                json.dumps(record.perspectives_analyzed),
                record.recommended_approach,
                json.dumps(record.expected_outcomes),
                record.confidence_score,
                record.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
    
    def get_similar_theses(self, keywords: List[str], limit: int = 5) -> List[ThesisRecord]:
        """Get theses matching keywords for learning"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Simple keyword matching
        conditions = ' OR '.join(['statement LIKE ?' for _ in keywords])
        params = [f'%{kw}%' for kw in keywords]
        params.append(limit)
        
        cursor.execute(
            f'SELECT * FROM theses WHERE {conditions} ORDER BY confidence_score DESC LIMIT ?',
            params
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            ThesisRecord(
                thesis_id=row['thesis_id'],
                statement=row['statement'],
                supporting_evidence=json.loads(row['supporting_evidence'] or '[]'),
                perspectives_analyzed=json.loads(row['perspectives_analyzed'] or '[]'),
                recommended_approach=row['recommended_approach'],
                expected_outcomes=json.loads(row['expected_outcomes'] or '[]'),
                confidence_score=row['confidence_score'],
                created_at=row['created_at']
            )
            for row in rows
        ]
    
    # ==========================================
    # STATISTICS
    # ==========================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Algorithm counts
        cursor.execute('SELECT COUNT(*) as count FROM algorithms')
        stats['total_algorithms'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT tier, COUNT(*) as count FROM algorithms GROUP BY tier')
        stats['algorithms_by_tier'] = {row['tier']: row['count'] for row in cursor.fetchall()}
        
        # Execution stats
        cursor.execute('SELECT COUNT(*) as count FROM execution_history')
        stats['total_executions'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT AVG(gpa_score) as avg FROM execution_history')
        row = cursor.fetchone()
        stats['avg_gpa_score'] = row['avg'] if row['avg'] else 0
        
        cursor.execute('SELECT AVG(CAST(success AS REAL)) as rate FROM execution_history')
        row = cursor.fetchone()
        stats['overall_success_rate'] = row['rate'] if row['rate'] else 0
        
        # Thesis stats
        cursor.execute('SELECT COUNT(*) as count FROM theses')
        stats['total_theses'] = cursor.fetchone()['count']
        
        conn.close()
        
        return stats
    
    def print_stats(self):
        """Print memory statistics"""
        stats = self.get_statistics()
        
        print("\n📊 Memory V2 Statistics")
        print("=" * 40)
        print(f"   Total Algorithms: {stats['total_algorithms']}")
        for tier, count in stats.get('algorithms_by_tier', {}).items():
            print(f"      - {tier}: {count}")
        print(f"   Total Executions: {stats['total_executions']}")
        print(f"   Avg GPA Score: {stats['avg_gpa_score']:.2f}")
        print(f"   Overall Success Rate: {stats['overall_success_rate']:.1%}")
        print(f"   Total Theses: {stats['total_theses']}")
        print("=" * 40)


# Singleton instance
_memory_v2_instance = None

def get_memory_v2(db_path: str = "data/dive_ai_v29.db") -> MemoryV2:
    """Get or create Memory V2 singleton"""
    global _memory_v2_instance
    if _memory_v2_instance is None:
        _memory_v2_instance = MemoryV2(db_path)
    return _memory_v2_instance


# Test
if __name__ == "__main__":
    # Initialize
    memory = get_memory_v2("data/test_memory_v2.db")
    
    # Register test algorithm
    algo = AlgorithmRecord(
        algorithm_id="test_algo_1",
        name="Test Algorithm",
        tier="operation",
        category="testing",
        description="A test algorithm",
        tags=["test", "demo"]
    )
    memory.register_algorithm(algo)
    
    # Save execution
    import uuid
    exec_record = ExecutionRecord(
        execution_id=str(uuid.uuid4()),
        algorithm_id="test_algo_1",
        task_type="test",
        task_description="Test execution",
        input_data={"test": True},
        output_data={"result": "success"},
        gpa_score=0.85,
        goal_alignment=0.9,
        plan_alignment=0.8,
        action_quality=0.85,
        execution_time_ms=150.5,
        resources_used={},
        success=True
    )
    memory.save_execution(exec_record)
    
    # Print stats
    memory.print_stats()
    
    # Test historical cost
    g_cost = memory.calculate_historical_cost("test_algo_1")
    print(f"\n   g(A) for test_algo_1: {g_cost:.3f}")
    
    print("\n✅ Memory V2 test completed!")
