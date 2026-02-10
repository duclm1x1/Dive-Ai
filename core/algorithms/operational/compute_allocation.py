"""
⚡ DYNAMIC COMPUTE ALLOCATION (DCA)
Intelligent resource allocation for multi-agent systems

Based on V28's layer2_dynamiccomputeallocation.py + dca/
"""

import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class ResourceType(Enum):
    """Types of computational resources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    TOKEN_BUDGET = "token_budget"
    API_QUOTA = "api_quota"
    TIME = "time"


@dataclass
class ComputeResource:
    """A computational resource"""
    type: ResourceType
    total: float
    used: float = 0.0
    reserved: float = 0.0
    
    @property
    def available(self) -> float:
        return max(0, self.total - self.used - self.reserved)
    
    @property
    def utilization(self) -> float:
        """Utilization percentage (0-100)"""
        if self.total == 0:
            return 0.0
        return (self.used / self.total) * 100


@dataclass
class AllocationRequest:
    """Request for resource allocation"""
    task_id: str
    priority: int  # 1-10
    resources_needed: Dict[ResourceType, float]
    estimated_duration: float  # seconds
    preemptable: bool = False


@dataclass
class Allocation:
    """An allocation of resources"""
    task_id: str
    resources: Dict[ResourceType, float]
    timestamp: float
    expires_at: float


class ComputeAllocationAlgorithm(BaseAlgorithm):
    """
    ⚡ Dynamic Compute Allocation (DCA)
    
    Intelligently allocates computational resources across:
    - Multiple agents
    - Parallel tasks
    - Different models (Opus, Codex, GLM)
    - Resource-constrained environments
    
    Features:
    - Priority-based allocation
    - Load balancing
    - Resource preemption
    - Budget management
    
    From V28: DCA module (10/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ComputeAllocation",
            name="Dynamic Compute Allocation (DCA)",
            level="operational",
            category="resource_management",
            version="1.0",
            description="Intelligent resource allocation for multi-agent systems",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("request", "object", True, "Allocation request"),
                    IOField("available_resources", "object", False, "Available resources"),
                    IOField("strategy", "string", False, "Allocation strategy (default: priority)")
                ],
                outputs=[
                    IOField("allocated", "boolean", True, "Resources allocated"),
                    IOField("allocation", "object", True, "Allocation details"),
                    IOField("utilization", "object", True, "Resource utilization")
                ]
            ),
            
            steps=[
                "1. Assess available resources",
                "2. Evaluate request priority",
                "3. Check if allocation possible",
                "4. Apply allocation strategy",
                "5. Reserve resources",
                "6. Track utilization",
                "7. Enable preemption if needed"
            ],
            
            tags=["allocation", "dca", "resources", "optimization"]
        )
        
        # Default resource pool
        self.resources = {
            ResourceType.CPU: ComputeResource(ResourceType.CPU, total=100.0),
            ResourceType.MEMORY: ComputeResource(ResourceType.MEMORY, total=16384.0),  # MB
            ResourceType.TOKEN_BUDGET: ComputeResource(ResourceType.TOKEN_BUDGET, total=1000000),
            ResourceType.API_QUOTA: ComputeResource(ResourceType.API_QUOTA, total=1000),
            ResourceType.TIME: ComputeResource(ResourceType.TIME, total=3600.0)  # seconds
        }
        
        self.allocations: List[Allocation] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute resource allocation"""
        import time
        
        request_data = params.get("request", {})
        custom_resources = params.get("available_resources")
        strategy = params.get("strategy", "priority")
        
        if not request_data:
            return AlgorithmResult(status="error", error="No allocation request provided")
        
        # Parse request
        allocation_request = self._parse_request(request_data)
        
        print(f"\n⚡ Dynamic Compute Allocation (DCA)")
        print(f"   Task: {allocation_request.task_id}, Priority: {allocation_request.priority}")
        print(f"   Strategy: {strategy}")
        
        # Update resources if custom provided
        if custom_resources:
            self._update_resources(custom_resources)
        
        # Check if allocation possible
        can_allocate, missing_resources = self._can_allocate(allocation_request)
        
        if not can_allocate:
            print(f"   ❌ Cannot allocate - missing: {missing_resources}")
            
            # Try preemption if high priority
            if allocation_request.priority >= 8:
                print(f"   🔄 Attempting preemption...")
                freed = self._preempt_lower_priority(allocation_request)
                can_allocate, _ = self._can_allocate(allocation_request)
        
        if can_allocate:
            # Allocate resources
            allocation = self._allocate_resources(allocation_request)
            print(f"   ✅ Allocated successfully")
            
            # Calculate utilization
            utilization = self._calculate_utilization()
            
            return AlgorithmResult(
                status="success",
                data={
                    "allocated": True,
                    "allocation": self._allocation_to_dict(allocation),
                    "utilization": utilization,
                    "strategy": strategy
                }
            )
        else:
            return AlgorithmResult(
                status="partial",
                data={
                    "allocated": False,
                    "missing_resources": missing_resources,
                    "utilization": self._calculate_utilization()
                },
                error="Insufficient resources"
            )
    
    def _parse_request(self, data: Dict) -> AllocationRequest:
        """Parse allocation request from dict"""
        resources = {}
        for key, value in data.get("resources", {}).items():
            if isinstance(key, str):
                # Convert string to enum
                try:
                    res_type = ResourceType[key.upper()]
                    resources[res_type] = float(value)
                except (KeyError, ValueError):
                    pass
        
        return AllocationRequest(
            task_id=data.get("task_id", "task_" + str(id(data))),
            priority=int(data.get("priority", 5)),
            resources_needed=resources,
            estimated_duration=float(data.get("duration", 60.0)),
            preemptable=bool(data.get("preemptable", False))
        )
    
    def _update_resources(self, custom_resources: Dict):
        """Update resource pool with custom values"""
        for key, value in custom_resources.items():
            if isinstance(key, str):
                try:
                    res_type = ResourceType[key.upper()]
                    if res_type in self.resources:
                        self.resources[res_type].total = float(value)
                except (KeyError, ValueError):
                    pass
    
    def _can_allocate(self, request: AllocationRequest) -> tuple[bool, Dict]:
        """Check if allocation is possible"""
        missing = {}
        
        for res_type, amount in request.resources_needed.items():
            if res_type not in self.resources:
                missing[res_type.value] = amount
                continue
            
            resource = self.resources[res_type]
            if resource.available < amount:
                missing[res_type.value] = amount - resource.available
        
        return len(missing) == 0, missing
    
    def _allocate_resources(self, request: AllocationRequest) -> Allocation:
        """Allocate resources for request"""
        import time
        
        # Reserve resources
        for res_type, amount in request.resources_needed.items():
            if res_type in self.resources:
                self.resources[res_type].used += amount
        
        # Create allocation
        allocation = Allocation(
            task_id=request.task_id,
            resources=request.resources_needed.copy(),
            timestamp=time.time(),
            expires_at=time.time() + request.estimated_duration
        )
        
        self.allocations.append(allocation)
        
        return allocation
    
    def _preempt_lower_priority(self, request: AllocationRequest) -> bool:
        """Preempt lower priority allocations"""
        # Find preemptable allocations
        preemptable = [a for a in self.allocations 
                      if hasattr(a, 'preemptable') and a.preemptable]
        
        if not preemptable:
            return False
        
        # Free resources from lowest priority
        for allocation in preemptable[:1]:  # Preempt one
            self._free_allocation(allocation)
        
        return True
    
    def _free_allocation(self, allocation: Allocation):
        """Free resources from an allocation"""
        for res_type, amount in allocation.resources.items():
            if res_type in self.resources:
                self.resources[res_type].used = max(0, 
                    self.resources[res_type].used - amount)
        
        if allocation in self.allocations:
            self.allocations.remove(allocation)
    
    def _calculate_utilization(self) -> Dict:
        """Calculate current resource utilization"""
        utilization = {}
        
        for res_type, resource in self.resources.items():
            utilization[res_type.value] = {
                "total": resource.total,
                "used": resource.used,
                "available": resource.available,
                "utilization_percent": resource.utilization
            }
        
        return utilization
    
    def _allocation_to_dict(self, allocation: Allocation) -> Dict:
        """Convert allocation to dict"""
        return {
            "task_id": allocation.task_id,
            "resources": {k.value: v for k, v in allocation.resources.items()},
            "timestamp": allocation.timestamp,
            "expires_at": allocation.expires_at
        }


def register(algorithm_manager):
    """Register Compute Allocation Algorithm"""
    algo = ComputeAllocationAlgorithm()
    algorithm_manager.register("ComputeAllocation", algo)
    print("✅ ComputeAllocation Algorithm registered")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("⚡ DYNAMIC COMPUTE ALLOCATION TEST")
    print("="*60)
    
    algo = ComputeAllocationAlgorithm()
    
    result = algo.execute({
        "request": {
            "task_id": "coding_task_1",
            "priority": 8,
            "resources": {
                "cpu": 30.0,
                "memory": 2048.0,
                "token_budget": 50000
            },
            "duration": 120.0
        },
        "strategy": "priority"
    })
    
    print(f"\n📊 Result: {result.status}")
    if result.status == "success":
        print(f"   Allocated: {result.data['allocated']}")
        print(f"\n   Utilization:")
        for res, info in result.data['utilization'].items():
            print(f"   {res}: {info['utilization_percent']:.1f}% ({info['used']}/{info['total']})")
    
    print("\n" + "="*60)
