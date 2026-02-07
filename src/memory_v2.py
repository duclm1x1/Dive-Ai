"""
Dive AI Memory System V2 - Persistent Storage & Knowledge Graphs
Upgrade: Episodic + Semantic + Procedural + Knowledge Graph Storage
"""

import json
import sqlite3
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib


class MemoryType(Enum):
    """Memory types in Dive AI"""
    EPISODIC = "episodic"      # Events and experiences
    SEMANTIC = "semantic"       # Facts and knowledge
    PROCEDURAL = "procedural"   # Skills and procedures
    WORKING = "working"         # Short-term working memory


@dataclass
class MemoryEntry:
    """Base memory entry"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: str
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(
                f"{self.content}{self.timestamp}".encode()
            ).hexdigest()[:16]


@dataclass
class KnowledgeNode:
    """Node in knowledge graph"""
    id: str
    label: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class KnowledgeEdge:
    """Edge in knowledge graph"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


class PersistentMemoryStore:
    """Persistent memory storage using SQLite"""
    
    def __init__(self, db_path: str = "dive_memory.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Memory entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance REAL,
                tags TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Knowledge graph nodes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                node_type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Knowledge graph edges
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL,
                properties TEXT,
                FOREIGN KEY(source_id) REFERENCES knowledge_nodes(id),
                FOREIGN KEY(target_id) REFERENCES knowledge_nodes(id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory_entries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_type ON knowledge_nodes(node_type)")
        
        self.conn.commit()
    
    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store memory entry"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memory_entries
                (id, content, memory_type, timestamp, importance, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                entry.content,
                entry.memory_type.value,
                entry.timestamp,
                entry.importance,
                json.dumps(entry.tags),
                json.dumps(entry.metadata)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory entry by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM memory_entries WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return MemoryEntry(
                    id=row[0],
                    content=row[1],
                    memory_type=MemoryType(row[2]),
                    timestamp=row[3],
                    importance=row[4],
                    tags=json.loads(row[5]),
                    metadata=json.loads(row[6])
                )
        except Exception as e:
            print(f"Error retrieving memory: {e}")
        
        return None
    
    def search_memories(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories by content"""
        try:
            cursor = self.conn.cursor()
            
            if memory_type:
                cursor.execute("""
                    SELECT * FROM memory_entries
                    WHERE content LIKE ? AND memory_type = ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", memory_type.value, limit))
            else:
                cursor.execute("""
                    SELECT * FROM memory_entries
                    WHERE content LIKE ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
            
            rows = cursor.fetchall()
            entries = []
            
            for row in rows:
                entries.append(MemoryEntry(
                    id=row[0],
                    content=row[1],
                    memory_type=MemoryType(row[2]),
                    timestamp=row[3],
                    importance=row[4],
                    tags=json.loads(row[5]),
                    metadata=json.loads(row[6])
                ))
            
            return entries
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class KnowledgeGraph:
    """Knowledge graph for semantic relationships"""
    
    def __init__(self, db_path: str = "dive_knowledge.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize knowledge graph database"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                node_type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Edges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL,
                properties TEXT,
                FOREIGN KEY(source_id) REFERENCES nodes(id),
                FOREIGN KEY(target_id) REFERENCES nodes(id)
            )
        """)
        
        self.conn.commit()
    
    def add_node(self, node: KnowledgeNode) -> bool:
        """Add node to knowledge graph"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO nodes
                (id, label, node_type, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node.id,
                node.label,
                node.node_type,
                json.dumps(node.properties),
                node.created_at,
                node.updated_at
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding node: {e}")
            return False
    
    def add_edge(self, edge: KnowledgeEdge) -> bool:
        """Add edge to knowledge graph"""
        try:
            cursor = self.conn.cursor()
            edge_id = f"{edge.source_id}_{edge.target_id}_{edge.relation_type}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO edges
                (id, source_id, target_id, relation_type, weight, properties)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                edge_id,
                edge.source_id,
                edge.target_id,
                edge.relation_type,
                edge.weight,
                json.dumps(edge.properties)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding edge: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get node by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            
            if row:
                return KnowledgeNode(
                    id=row[0],
                    label=row[1],
                    node_type=row[2],
                    properties=json.loads(row[3]),
                    created_at=row[4],
                    updated_at=row[5]
                )
        except Exception as e:
            print(f"Error getting node: {e}")
        
        return None
    
    def find_related_nodes(
        self,
        node_id: str,
        relation_type: Optional[str] = None,
        depth: int = 1
    ) -> List[KnowledgeNode]:
        """Find nodes related to given node"""
        related = []
        visited = set()
        
        def traverse(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            try:
                cursor = self.conn.cursor()
                
                if relation_type:
                    cursor.execute("""
                        SELECT target_id FROM edges
                        WHERE source_id = ? AND relation_type = ?
                    """, (current_id, relation_type))
                else:
                    cursor.execute("""
                        SELECT target_id FROM edges
                        WHERE source_id = ?
                    """, (current_id,))
                
                for row in cursor.fetchall():
                    target_id = row[0]
                    node = self.get_node(target_id)
                    if node:
                        related.append(node)
                    
                    if current_depth < depth:
                        traverse(target_id, current_depth + 1)
            except Exception as e:
                print(f"Error traversing: {e}")
        
        traverse(node_id, 1)
        return related
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class DiveMemorySystem:
    """Unified Dive AI Memory System"""
    
    def __init__(self):
        self.version = "2.0.0"
        self.episodic_store = PersistentMemoryStore("episodic_memory.db")
        self.semantic_store = PersistentMemoryStore("semantic_memory.db")
        self.procedural_store = PersistentMemoryStore("procedural_memory.db")
        self.knowledge_graph = KnowledgeGraph("knowledge_graph.db")
        self.working_memory: Dict[str, Any] = {}
    
    def store_episodic_memory(self, content: str, tags: List[str] = None, metadata: Dict = None):
        """Store episodic memory (events/experiences)"""
        entry = MemoryEntry(
            id="",
            content=content,
            memory_type=MemoryType.EPISODIC,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        return self.episodic_store.store_memory(entry)
    
    def store_semantic_memory(self, content: str, tags: List[str] = None, metadata: Dict = None):
        """Store semantic memory (facts/knowledge)"""
        entry = MemoryEntry(
            id="",
            content=content,
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        return self.semantic_store.store_memory(entry)
    
    def store_procedural_memory(self, content: str, tags: List[str] = None, metadata: Dict = None):
        """Store procedural memory (skills/procedures)"""
        entry = MemoryEntry(
            id="",
            content=content,
            memory_type=MemoryType.PROCEDURAL,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        return self.procedural_store.store_memory(entry)
    
    def recall_memory(self, query: str, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        """Recall memories based on query"""
        results = []
        
        if memory_type is None or memory_type == MemoryType.EPISODIC:
            results.extend(self.episodic_store.search_memories(query, memory_type=MemoryType.EPISODIC if memory_type else None))
        
        if memory_type is None or memory_type == MemoryType.SEMANTIC:
            results.extend(self.semantic_store.search_memories(query, memory_type=MemoryType.SEMANTIC if memory_type else None))
        
        if memory_type is None or memory_type == MemoryType.PROCEDURAL:
            results.extend(self.procedural_store.search_memories(query, memory_type=MemoryType.PROCEDURAL if memory_type else None))
        
        return sorted(results, key=lambda x: x.importance, reverse=True)
    
    def add_knowledge(self, subject: str, relation: str, obj: str, properties: Dict = None):
        """Add knowledge to graph (subject-relation-object)"""
        # Add nodes
        subject_node = KnowledgeNode(
            id=hashlib.md5(subject.encode()).hexdigest()[:16],
            label=subject,
            node_type="entity"
        )
        object_node = KnowledgeNode(
            id=hashlib.md5(obj.encode()).hexdigest()[:16],
            label=obj,
            node_type="entity"
        )
        
        self.knowledge_graph.add_node(subject_node)
        self.knowledge_graph.add_node(object_node)
        
        # Add edge
        edge = KnowledgeEdge(
            source_id=subject_node.id,
            target_id=object_node.id,
            relation_type=relation,
            properties=properties or {}
        )
        self.knowledge_graph.add_edge(edge)
    
    def query_knowledge(self, entity: str) -> List[KnowledgeNode]:
        """Query knowledge graph for related entities"""
        entity_id = hashlib.md5(entity.encode()).hexdigest()[:16]
        return self.knowledge_graph.find_related_nodes(entity_id, depth=2)
    
    def store_working_memory(self, key: str, value: Any):
        """Store in working memory (short-term)"""
        self.working_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve_working_memory(self, key: str) -> Optional[Any]:
        """Retrieve from working memory"""
        if key in self.working_memory:
            return self.working_memory[key]["value"]
        return None
    
    def clear_working_memory(self):
        """Clear working memory"""
        self.working_memory.clear()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            "version": self.version,
            "working_memory_size": len(self.working_memory),
            "episodic_store": "Active",
            "semantic_store": "Active",
            "procedural_store": "Active",
            "knowledge_graph": "Active"
        }
    
    def cleanup(self):
        """Cleanup and close connections"""
        self.episodic_store.close()
        self.semantic_store.close()
        self.procedural_store.close()
        self.knowledge_graph.close()


# Export
__all__ = [
    'DiveMemorySystem',
    'MemoryType',
    'MemoryEntry',
    'KnowledgeNode',
    'KnowledgeEdge',
    'PersistentMemoryStore',
    'KnowledgeGraph'
]
