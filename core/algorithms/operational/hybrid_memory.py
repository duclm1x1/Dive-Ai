"""
💾 DIVE AI HYBRID MEMORY
Local-first with Supabase sync (OpenClaw-inspired)

Storage:
1. LOCAL - Fast, offline-capable, primary storage
2. SUPABASE - Cloud sync, cross-device, backup

Features:
- Local-first (works offline)
- Background Supabase sync
- Conflict resolution (local wins)
- Conversation history
- Semantic search
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Supabase configuration
SUPABASE_CONFIG = {
    "url": "https://xmnbqofwlgedftjnwbit.supabase.co",
    "anon_key": "sb_publishable_oglpWGS9HVyB3g4R04keXQ_9eAA_PQn",
    "service_key": "sb_secret_ec8LpMT4hFnSuwsmeDy7bw_h-fNhPHZ"
}


class MemoryType(Enum):
    """Types of memory entries"""
    CONVERSATION = "conversation"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"
    USER_PREF = "user_preference"
    TASK = "task"


@dataclass
class MemoryEntry:
    """A single memory entry"""
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


class LocalMemoryStore:
    """
    📁 Local-first memory storage
    Fast, offline-capable, primary storage
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'memory'
        )
        os.makedirs(self.base_path, exist_ok=True)
        
        # In-memory cache
        self.cache: Dict[str, MemoryEntry] = {}
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> [memory_ids]
        
        # Load existing memories
        self._load_all()
    
    def add(self, entry: MemoryEntry) -> bool:
        """Add memory entry"""
        self.cache[entry.id] = entry
        self._index_entry(entry)
        self._persist(entry)
        return True
    
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory by ID"""
        return self.cache.get(memory_id)
    
    def search(self, query: str, limit: int = 10, type_filter: MemoryType = None) -> List[MemoryEntry]:
        """Search memories by keyword"""
        query_lower = query.lower()
        keywords = query_lower.split()
        
        # Find matching memory IDs
        matched_ids = set()
        for kw in keywords:
            for indexed_kw, ids in self.keyword_index.items():
                if kw in indexed_kw:
                    matched_ids.update(ids)
        
        # Get entries and score
        results = []
        for mid in matched_ids:
            entry = self.cache.get(mid)
            if entry:
                if type_filter and entry.type != type_filter:
                    continue
                
                # Simple relevance score
                score = sum(1 for kw in keywords if kw in entry.content.lower())
                results.append((entry, score))
        
        # Sort by score (desc) then by time (desc)
        results.sort(key=lambda x: (x[1], x[0].created_at), reverse=True)
        
        return [r[0] for r in results[:limit]]
    
    def get_conversations(self, limit: int = 20) -> List[MemoryEntry]:
        """Get recent conversations"""
        convos = [e for e in self.cache.values() if e.type == MemoryType.CONVERSATION]
        convos.sort(key=lambda x: x.created_at, reverse=True)
        return convos[:limit]
    
    def get_unsynced(self) -> List[MemoryEntry]:
        """Get entries not yet synced to cloud"""
        return [e for e in self.cache.values() if not e.synced]
    
    def mark_synced(self, memory_id: str):
        """Mark entry as synced"""
        if memory_id in self.cache:
            self.cache[memory_id].synced = True
            self._persist(self.cache[memory_id])
    
    def delete(self, memory_id: str) -> bool:
        """Delete memory entry"""
        if memory_id in self.cache:
            entry = self.cache.pop(memory_id)
            self._remove_from_index(entry)
            
            # Delete file
            file_path = os.path.join(self.base_path, f"{memory_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        return False
    
    def _index_entry(self, entry: MemoryEntry):
        """Add entry to keyword index"""
        keywords = self._extract_keywords(entry.content)
        for kw in keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = []
            if entry.id not in self.keyword_index[kw]:
                self.keyword_index[kw].append(entry.id)
    
    def _remove_from_index(self, entry: MemoryEntry):
        """Remove entry from keyword index"""
        for ids in self.keyword_index.values():
            if entry.id in ids:
                ids.remove(entry.id)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords for indexing"""
        import re
        words = re.findall(r'\b\w{3,}\b', text.lower())
        # Remove common words
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out'}
        return [w for w in words if w not in stopwords][:20]
    
    def _persist(self, entry: MemoryEntry):
        """Save entry to disk"""
        file_path = os.path.join(self.base_path, f"{entry.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_all(self):
        """Load all memories from disk"""
        if not os.path.exists(self.base_path):
            return
        
        for filename in os.listdir(self.base_path):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(self.base_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    entry = MemoryEntry.from_dict(data)
                    self.cache[entry.id] = entry
                    self._index_entry(entry)
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
    
    def stats(self) -> Dict:
        """Get memory stats"""
        return {
            "total_entries": len(self.cache),
            "by_type": {
                t.value: len([e for e in self.cache.values() if e.type == t])
                for t in MemoryType
            },
            "unsynced": len(self.get_unsynced()),
            "keywords_indexed": len(self.keyword_index)
        }


class SupabaseMemorySync:
    """
    ☁️ Supabase cloud sync
    Background sync, cross-device, backup
    """
    
    def __init__(self):
        self.url = SUPABASE_CONFIG["url"]
        self.key = SUPABASE_CONFIG["service_key"]
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client
            self.client = create_client(self.url, self.key)
            print("☁️ Supabase connected")
        except ImportError:
            print("⚠️ Supabase not installed. Run: pip install supabase")
            self.client = None
        except Exception as e:
            print(f"⚠️ Supabase connection failed: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if connected to Supabase"""
        return self.client is not None
    
    def sync_entry(self, entry: MemoryEntry) -> bool:
        """Sync single entry to Supabase"""
        if not self.client:
            return False
        
        try:
            data = entry.to_dict()
            data["synced_at"] = datetime.utcnow().isoformat()
            
            # Upsert to Supabase
            self.client.table("dive_ai_memory").upsert(data).execute()
            return True
        except Exception as e:
            print(f"⚠️ Sync failed for {entry.id}: {e}")
            return False
    
    def sync_all(self, entries: List[MemoryEntry]) -> Tuple[int, int]:
        """Sync multiple entries, return (success, failed) count"""
        if not self.client:
            return 0, len(entries)
        
        success = 0
        failed = 0
        
        for entry in entries:
            if self.sync_entry(entry):
                success += 1
            else:
                failed += 1
        
        return success, failed
    
    def fetch_all(self) -> List[Dict]:
        """Fetch all memories from Supabase"""
        if not self.client:
            return []
        
        try:
            response = self.client.table("dive_ai_memory").select("*").execute()
            return response.data
        except Exception as e:
            print(f"⚠️ Fetch failed: {e}")
            return []
    
    def delete_entry(self, memory_id: str) -> bool:
        """Delete entry from Supabase"""
        if not self.client:
            return False
        
        try:
            self.client.table("dive_ai_memory").delete().eq("id", memory_id).execute()
            return True
        except:
            return False


class HybridMemory:
    """
    💾 Hybrid Memory System
    
    Local-first with Supabase sync
    
    Usage:
        memory = HybridMemory()
        
        # Store conversation
        memory.store_conversation("user input", "assistant response")
        
        # Search memories
        results = memory.search("calculator app")
        
        # Sync to cloud
        memory.sync_to_cloud()
    """
    
    def __init__(self):
        self.local = LocalMemoryStore()
        self.cloud = SupabaseMemorySync()
        self._computer_id = self._get_computer_id()
    
    def _get_computer_id(self) -> str:
        """Get unique computer identifier"""
        import platform
        import socket
        import uuid
        
        mac = format(uuid.getnode(), '012X')
        hostname = socket.gethostname()
        return hashlib.sha256(f"{mac}:{hostname}".encode()).hexdigest()[:16]
    
    def _generate_id(self) -> str:
        """Generate unique memory ID"""
        timestamp = int(time.time() * 1000)
        random_part = hashlib.md5(os.urandom(8)).hexdigest()[:8]
        return f"{self._computer_id[:8]}_{timestamp}_{random_part}"
    
    # ========================================
    # CONVERSATION MEMORY
    # ========================================
    
    def store_conversation(self, user_input: str, assistant_response: str, metadata: Dict = None) -> str:
        """Store a conversation turn"""
        entry = MemoryEntry(
            id=self._generate_id(),
            type=MemoryType.CONVERSATION,
            content=f"User: {user_input}\nAssistant: {assistant_response}",
            metadata={
                "user_input": user_input,
                "assistant_response": assistant_response[:500],  # Limit size
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        )
        self.local.add(entry)
        return entry.id
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        entries = self.local.get_conversations(limit)
        return [
            {
                "user": e.metadata.get("user_input", ""),
                "assistant": e.metadata.get("assistant_response", ""),
                "timestamp": e.metadata.get("timestamp", "")
            }
            for e in entries
        ]
    
    # ========================================
    # KNOWLEDGE MEMORY
    # ========================================
    
    def store_knowledge(self, topic: str, content: str, source: str = None) -> str:
        """Store knowledge/fact"""
        entry = MemoryEntry(
            id=self._generate_id(),
            type=MemoryType.KNOWLEDGE,
            content=f"{topic}: {content}",
            metadata={
                "topic": topic,
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.local.add(entry)
        return entry.id
    
    # ========================================
    # PROJECT MEMORY
    # ========================================
    
    def store_project_info(self, project_name: str, info: str, file_path: str = None) -> str:
        """Store project-related information"""
        entry = MemoryEntry(
            id=self._generate_id(),
            type=MemoryType.PROJECT,
            content=f"Project {project_name}: {info}",
            metadata={
                "project": project_name,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.local.add(entry)
        return entry.id
    
    # ========================================
    # USER PREFERENCES
    # ========================================
    
    def store_preference(self, key: str, value: Any) -> str:
        """Store user preference"""
        entry = MemoryEntry(
            id=f"pref_{key}",  # Use stable ID for preferences
            type=MemoryType.USER_PREF,
            content=f"Preference {key} = {value}",
            metadata={"key": key, "value": value}
        )
        self.local.add(entry)
        return entry.id
    
    def get_preference(self, key: str) -> Optional[Any]:
        """Get user preference"""
        entry = self.local.get(f"pref_{key}")
        if entry:
            return entry.metadata.get("value")
        return None
    
    # ========================================
    # SEARCH
    # ========================================
    
    def search(self, query: str, limit: int = 10, type_filter: str = None) -> List[Dict]:
        """Search across all memories"""
        filter_type = MemoryType(type_filter) if type_filter else None
        entries = self.local.search(query, limit, filter_type)
        
        return [
            {
                "id": e.id,
                "type": e.type.value,
                "content": e.content[:200],
                "metadata": e.metadata,
                "created_at": e.created_at
            }
            for e in entries
        ]
    
    # ========================================
    # SYNC
    # ========================================
    
    def sync_to_cloud(self) -> Dict:
        """Sync unsynced entries to Supabase"""
        unsynced = self.local.get_unsynced()
        
        if not unsynced:
            return {"status": "no_changes", "synced": 0}
        
        if not self.cloud.is_connected():
            return {"status": "offline", "pending": len(unsynced)}
        
        success, failed = self.cloud.sync_all(unsynced)
        
        # Mark successful entries as synced
        for entry in unsynced:
            if success > 0:
                self.local.mark_synced(entry.id)
                success -= 1
        
        return {
            "status": "synced",
            "synced": success,
            "failed": failed
        }
    
    def pull_from_cloud(self) -> Dict:
        """Pull memories from Supabase"""
        if not self.cloud.is_connected():
            return {"status": "offline"}
        
        cloud_entries = self.cloud.fetch_all()
        imported = 0
        
        for data in cloud_entries:
            if data["id"] not in self.local.cache:
                entry = MemoryEntry.from_dict(data)
                entry.synced = True
                self.local.add(entry)
                imported += 1
        
        return {"status": "success", "imported": imported}
    
    # ========================================
    # STATS
    # ========================================
    
    def stats(self) -> Dict:
        """Get memory statistics"""
        local_stats = self.local.stats()
        return {
            "local": local_stats,
            "cloud_connected": self.cloud.is_connected(),
            "computer_id": self._computer_id[:8]
        }


# ========================================
# ALGORITHM WRAPPER
# ========================================

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class HybridMemoryAlgorithm(BaseAlgorithm):
    """Hybrid Memory Algorithm - Local + Supabase"""
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="HybridMemory",
            name="Hybrid Memory",
            level="operational",
            category="memory",
            version="1.0",
            description="Local-first memory with Supabase cloud sync",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("operation", "string", True, "add/search/sync/stats"),
                    IOField("data", "object", False, "Operation data")
                ],
                outputs=[
                    IOField("result", "object", True, "Operation result")
                ]
            ),
            
            steps=[
                "1. Parse operation type",
                "2. Execute on local storage",
                "3. Queue for cloud sync if needed",
                "4. Return result"
            ],
            
            tags=["memory", "storage", "supabase", "hybrid"]
        )
        
        self.memory = HybridMemory()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute memory operation"""
        operation = params.get("operation", "stats")
        data = params.get("data", {})
        
        try:
            if operation == "add_conversation":
                mid = self.memory.store_conversation(
                    data.get("user_input", ""),
                    data.get("assistant_response", "")
                )
                return AlgorithmResult(status="success", data={"id": mid})
            
            elif operation == "search":
                results = self.memory.search(
                    data.get("query", ""),
                    data.get("limit", 10)
                )
                return AlgorithmResult(status="success", data={"results": results})
            
            elif operation == "sync":
                result = self.memory.sync_to_cloud()
                return AlgorithmResult(status="success", data=result)
            
            elif operation == "stats":
                stats = self.memory.stats()
                return AlgorithmResult(status="success", data=stats)
            
            elif operation == "recent":
                convos = self.memory.get_recent_conversations(data.get("limit", 10))
                return AlgorithmResult(status="success", data={"conversations": convos})
            
            else:
                return AlgorithmResult(status="error", error=f"Unknown operation: {operation}")
        
        except Exception as e:
            return AlgorithmResult(status="error", error=str(e))


def register(algorithm_manager):
    """Register Hybrid Memory Algorithm"""
    algo = HybridMemoryAlgorithm()
    algorithm_manager.register("HybridMemory", algo)
    print("✅ HybridMemory Algorithm registered (Local + Supabase)")


# ========================================
# TEST
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("💾 HYBRID MEMORY TEST")
    print("="*60)
    
    memory = HybridMemory()
    
    # Test conversation storage
    print("\n📝 Storing conversations...")
    memory.store_conversation(
        "tạo calculator app giống iPhone",
        "Đã tạo calculator app với HTML/CSS/JS..."
    )
    memory.store_conversation(
        "test dive ai",
        "Tất cả 25 tests đều passed!"
    )
    
    # Test search
    print("\n🔍 Searching 'calculator'...")
    results = memory.search("calculator")
    for r in results:
        print(f"   → {r['content'][:50]}...")
    
    # Test recent
    print("\n📜 Recent conversations:")
    for c in memory.get_recent_conversations(3):
        print(f"   → User: {c['user'][:30]}...")
    
    # Stats
    print("\n📊 Stats:")
    stats = memory.stats()
    print(f"   Local entries: {stats['local']['total_entries']}")
    print(f"   Cloud connected: {stats['cloud_connected']}")
    
    print("\n" + "="*60)
