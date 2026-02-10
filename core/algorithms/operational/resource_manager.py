"""
💾 RESOURCE MANAGER
Manage system resources efficiently

Based on V28's core_engine/resource_manager.py
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class ResourceType(Enum):
    MEMORY = "memory"
    CPU = "cpu"
    GPU = "gpu"
    TOKENS = "tokens"
    API_CALLS = "api_calls"
    STORAGE = "storage"


@dataclass
class ResourcePool:
    """A pool of resources"""
    type: ResourceType
    total: float
    allocated: float = 0.0
    reserved: float = 0.0


class ResourceManagerAlgorithm(BaseAlgorithm):
    """
    💾 Resource Manager
    
    Manages system resources:
    - Resource pools
    - Allocation tracking
    - Quota management
    - Usage optimization
    
    From V28: core_engine/resource_manager.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ResourceManager",
            name="Resource Manager",
            level="operational",
            category="system",
            version="1.0",
            description="Manage system resources efficiently",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "allocate/release/status/reserve"),
                    IOField("resource_type", "string", False, "Type of resource"),
                    IOField("amount", "number", False, "Amount to allocate/release")
                ],
                outputs=[
                    IOField("result", "object", True, "Resource operation result")
                ]
            ),
            steps=["Check availability", "Allocate/release", "Update tracking", "Optimize"],
            tags=["resource", "memory", "management", "allocation"]
        )
        
        # Initialize resource pools
        self.pools: Dict[ResourceType, ResourcePool] = {
            ResourceType.MEMORY: ResourcePool(ResourceType.MEMORY, 8192),  # MB
            ResourceType.CPU: ResourcePool(ResourceType.CPU, 100),  # %
            ResourceType.TOKENS: ResourcePool(ResourceType.TOKENS, 1000000),
            ResourceType.API_CALLS: ResourcePool(ResourceType.API_CALLS, 1000)
        }
        
        self.allocation_history: List[Dict] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n💾 Resource Manager")
        
        if action == "allocate":
            return self._allocate(params.get("resource_type", ""), params.get("amount", 0))
        elif action == "release":
            return self._release(params.get("resource_type", ""), params.get("amount", 0))
        elif action == "reserve":
            return self._reserve(params.get("resource_type", ""), params.get("amount", 0))
        elif action == "status":
            return self._get_status()
        elif action == "optimize":
            return self._optimize()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _allocate(self, resource_type: str, amount: float) -> AlgorithmResult:
        try:
            rtype = ResourceType(resource_type)
        except ValueError:
            return AlgorithmResult(status="error", error=f"Unknown resource type: {resource_type}")
        
        pool = self.pools[rtype]
        available = pool.total - pool.allocated - pool.reserved
        
        if amount > available:
            return AlgorithmResult(
                status="insufficient",
                data={"requested": amount, "available": available}
            )
        
        pool.allocated += amount
        self.allocation_history.append({
            "type": resource_type,
            "action": "allocate",
            "amount": amount,
            "timestamp": time.time()
        })
        
        print(f"   Allocated: {amount} {resource_type}")
        
        return AlgorithmResult(
            status="success",
            data={
                "allocated": amount,
                "type": resource_type,
                "remaining": pool.total - pool.allocated - pool.reserved
            }
        )
    
    def _release(self, resource_type: str, amount: float) -> AlgorithmResult:
        try:
            rtype = ResourceType(resource_type)
        except ValueError:
            return AlgorithmResult(status="error", error=f"Unknown resource type: {resource_type}")
        
        pool = self.pools[rtype]
        release_amount = min(amount, pool.allocated)
        pool.allocated -= release_amount
        
        self.allocation_history.append({
            "type": resource_type,
            "action": "release",
            "amount": release_amount,
            "timestamp": time.time()
        })
        
        return AlgorithmResult(
            status="success",
            data={"released": release_amount, "type": resource_type}
        )
    
    def _reserve(self, resource_type: str, amount: float) -> AlgorithmResult:
        try:
            rtype = ResourceType(resource_type)
        except ValueError:
            return AlgorithmResult(status="error", error=f"Unknown resource type: {resource_type}")
        
        pool = self.pools[rtype]
        available = pool.total - pool.allocated - pool.reserved
        
        if amount > available:
            return AlgorithmResult(status="insufficient", data={"available": available})
        
        pool.reserved += amount
        return AlgorithmResult(status="success", data={"reserved": amount})
    
    def _get_status(self) -> AlgorithmResult:
        status = {}
        for rtype, pool in self.pools.items():
            status[rtype.value] = {
                "total": pool.total,
                "allocated": pool.allocated,
                "reserved": pool.reserved,
                "available": pool.total - pool.allocated - pool.reserved,
                "utilization": (pool.allocated + pool.reserved) / pool.total
            }
        
        return AlgorithmResult(status="success", data=status)
    
    def _optimize(self) -> AlgorithmResult:
        optimizations = []
        
        for rtype, pool in self.pools.items():
            utilization = (pool.allocated + pool.reserved) / pool.total
            
            if utilization > 0.9:
                optimizations.append({
                    "resource": rtype.value,
                    "action": "scale_up",
                    "reason": f"High utilization: {utilization:.0%}"
                })
            elif utilization < 0.2 and pool.allocated > 0:
                optimizations.append({
                    "resource": rtype.value,
                    "action": "release_unused",
                    "reason": f"Low utilization: {utilization:.0%}"
                })
        
        return AlgorithmResult(
            status="success",
            data={"optimizations": optimizations}
        )


def register(algorithm_manager):
    algo = ResourceManagerAlgorithm()
    algorithm_manager.register("ResourceManager", algo)
    print("✅ ResourceManager registered")


if __name__ == "__main__":
    algo = ResourceManagerAlgorithm()
    algo.execute({"action": "allocate", "resource_type": "memory", "amount": 1024})
    result = algo.execute({"action": "status"})
    print(f"Memory utilization: {result.data['memory']['utilization']:.1%}")
