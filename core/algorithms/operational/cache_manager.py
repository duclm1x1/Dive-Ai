"""
🗃️ CACHE MANAGER
Manage caching for performance

Based on V28's core_engine/cache_manager.py
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class CacheEntry:
    """A cache entry"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    hits: int = 0


class CacheManagerAlgorithm(BaseAlgorithm):
    """
    🗃️ Cache Manager
    
    Manages caching:
    - Key-value storage
    - TTL management
    - LRU eviction
    - Hit/miss tracking
    
    From V28: core_engine/cache_manager.py
    """
    
    def __init__(self, max_size: int = 1000):
        self.spec = AlgorithmSpec(
            algorithm_id="CacheManager",
            name="Cache Manager",
            level="operational",
            category="performance",
            version="1.0",
            description="Manage caching for performance",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "get/set/delete/clear"),
                    IOField("key", "string", False, "Cache key"),
                    IOField("value", "any", False, "Value to cache")
                ],
                outputs=[
                    IOField("result", "any", True, "Cache operation result")
                ]
            ),
            steps=["Check cache", "Apply TTL", "Evict if needed", "Return result"],
            tags=["cache", "performance", "storage"]
        )
        
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.stats = {"hits": 0, "misses": 0}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "stats")
        
        print(f"\n🗃️ Cache Manager")
        
        if action == "get":
            return self._get(params.get("key", ""))
        elif action == "set":
            return self._set(
                params.get("key", ""),
                params.get("value"),
                params.get("ttl")
            )
        elif action == "delete":
            return self._delete(params.get("key", ""))
        elif action == "clear":
            return self._clear()
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _get(self, key: str) -> AlgorithmResult:
        if not key:
            return AlgorithmResult(status="error", error="Key required")
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check expiration
            if entry.expires_at and time.time() > entry.expires_at:
                del self.cache[key]
                self.stats["misses"] += 1
                return AlgorithmResult(status="miss", data={"key": key, "expired": True})
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            entry.hits += 1
            self.stats["hits"] += 1
            
            return AlgorithmResult(
                status="hit",
                data={"key": key, "value": entry.value, "hits": entry.hits}
            )
        
        self.stats["misses"] += 1
        return AlgorithmResult(status="miss", data={"key": key})
    
    def _set(self, key: str, value: Any, ttl: Optional[int] = None) -> AlgorithmResult:
        if not key:
            return AlgorithmResult(status="error", error="Key required")
        
        # Evict if needed
        while len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        now = time.time()
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl if ttl else None
        )
        
        return AlgorithmResult(
            status="success",
            data={"key": key, "ttl": ttl, "size": len(self.cache)}
        )
    
    def _delete(self, key: str) -> AlgorithmResult:
        if key in self.cache:
            del self.cache[key]
            return AlgorithmResult(status="success", data={"deleted": key})
        return AlgorithmResult(status="error", error="Key not found")
    
    def _clear(self) -> AlgorithmResult:
        count = len(self.cache)
        self.cache.clear()
        self.stats = {"hits": 0, "misses": 0}
        return AlgorithmResult(status="success", data={"cleared": count})
    
    def _get_stats(self) -> AlgorithmResult:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return AlgorithmResult(
            status="success",
            data={
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate
            }
        )


def register(algorithm_manager):
    algo = CacheManagerAlgorithm()
    algorithm_manager.register("CacheManager", algo)
    print("✅ CacheManager registered")


if __name__ == "__main__":
    algo = CacheManagerAlgorithm()
    algo.execute({"action": "set", "key": "user:123", "value": {"name": "Alice"}, "ttl": 3600})
    result = algo.execute({"action": "get", "key": "user:123"})
    print(f"Cache hit: {result.status == 'hit'}")
    
    stats = algo.execute({"action": "stats"})
    print(f"Hit rate: {stats.data['hit_rate']:.0%}")
