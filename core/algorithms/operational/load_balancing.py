"""
⚖️ LOAD BALANCING
Distribute workload across agents/resources

Based on V28's layer4_loadbalancing.py
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


class BalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"
    RANDOM = "random"


@dataclass
class Worker:
    """A worker/agent that can handle tasks"""
    id: str
    weight: float = 1.0
    current_load: int = 0
    max_capacity: int = 10
    total_tasks: int = 0
    available: bool = True


class LoadBalancingAlgorithm(BaseAlgorithm):
    """
    ⚖️ Load Balancer
    
    Distributes tasks across workers:
    - Round robin
    - Least loaded
    - Weighted distribution
    - Capacity tracking
    
    From V28: layer4_loadbalancing.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="LoadBalancing",
            name="Load Balancing",
            level="operational",
            category="distribution",
            version="1.0",
            description="Distribute workload across agents",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "assign/register/release/stats"),
                    IOField("task", "object", False, "Task to assign"),
                    IOField("worker", "object", False, "Worker to register")
                ],
                outputs=[
                    IOField("result", "object", True, "Balancing result")
                ]
            ),
            steps=["Select strategy", "Find best worker", "Assign task", "Update load"],
            tags=["load-balancing", "distribution", "scaling"]
        )
        
        self.workers: Dict[str, Worker] = {}
        self.round_robin_index = 0
        self.strategy = BalancingStrategy.LEAST_LOADED
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "stats")
        task = params.get("task", {})
        worker_data = params.get("worker", {})
        
        print(f"\n⚖️ Load Balancing")
        
        if action == "register":
            return self._register_worker(worker_data)
        elif action == "assign":
            return self._assign_task(task)
        elif action == "release":
            return self._release_task(params.get("worker_id", ""))
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _register_worker(self, data: Dict) -> AlgorithmResult:
        worker = Worker(
            id=data.get("id", f"worker-{len(self.workers)}"),
            weight=data.get("weight", 1.0),
            max_capacity=data.get("capacity", 10)
        )
        self.workers[worker.id] = worker
        
        print(f"   Registered: {worker.id}")
        
        return AlgorithmResult(
            status="success",
            data={"registered": worker.id, "total_workers": len(self.workers)}
        )
    
    def _assign_task(self, task: Dict) -> AlgorithmResult:
        if not self.workers:
            return AlgorithmResult(status="error", error="No workers available")
        
        # Find available workers
        available = [w for w in self.workers.values() 
                    if w.available and w.current_load < w.max_capacity]
        
        if not available:
            return AlgorithmResult(status="error", error="All workers at capacity")
        
        # Select worker based on strategy
        if self.strategy == BalancingStrategy.ROUND_ROBIN:
            worker = self._round_robin(available)
        elif self.strategy == BalancingStrategy.LEAST_LOADED:
            worker = self._least_loaded(available)
        elif self.strategy == BalancingStrategy.WEIGHTED:
            worker = self._weighted(available)
        else:
            import random
            worker = random.choice(available)
        
        # Assign
        worker.current_load += 1
        worker.total_tasks += 1
        
        print(f"   Assigned to: {worker.id} (load: {worker.current_load}/{worker.max_capacity})")
        
        return AlgorithmResult(
            status="success",
            data={
                "assigned_to": worker.id,
                "worker_load": worker.current_load,
                "task_id": task.get("id", "unknown")
            }
        )
    
    def _round_robin(self, workers: List[Worker]) -> Worker:
        self.round_robin_index = (self.round_robin_index + 1) % len(workers)
        return workers[self.round_robin_index]
    
    def _least_loaded(self, workers: List[Worker]) -> Worker:
        return min(workers, key=lambda w: w.current_load / w.max_capacity)
    
    def _weighted(self, workers: List[Worker]) -> Worker:
        # Higher weight = more tasks
        return max(workers, key=lambda w: w.weight * (1 - w.current_load / w.max_capacity))
    
    def _release_task(self, worker_id: str) -> AlgorithmResult:
        if worker_id not in self.workers:
            return AlgorithmResult(status="error", error="Worker not found")
        
        worker = self.workers[worker_id]
        if worker.current_load > 0:
            worker.current_load -= 1
        
        return AlgorithmResult(
            status="success",
            data={"worker": worker_id, "new_load": worker.current_load}
        )
    
    def _get_stats(self) -> AlgorithmResult:
        if not self.workers:
            return AlgorithmResult(status="success", data={"workers": 0})
        
        total_load = sum(w.current_load for w in self.workers.values())
        total_capacity = sum(w.max_capacity for w in self.workers.values())
        
        return AlgorithmResult(
            status="success",
            data={
                "workers": len(self.workers),
                "total_load": total_load,
                "total_capacity": total_capacity,
                "utilization": total_load / total_capacity if total_capacity > 0 else 0,
                "per_worker": {
                    w.id: {"load": w.current_load, "capacity": w.max_capacity}
                    for w in self.workers.values()
                }
            }
        )


def register(algorithm_manager):
    algo = LoadBalancingAlgorithm()
    algorithm_manager.register("LoadBalancing", algo)
    print("✅ LoadBalancing registered")


if __name__ == "__main__":
    algo = LoadBalancingAlgorithm()
    algo.execute({"action": "register", "worker": {"id": "agent-1", "capacity": 5}})
    algo.execute({"action": "register", "worker": {"id": "agent-2", "capacity": 5}})
    algo.execute({"action": "assign", "task": {"id": "task-1"}})
    algo.execute({"action": "assign", "task": {"id": "task-2"}})
    result = algo.execute({"action": "stats"})
    print(f"Utilization: {result.data['utilization']:.1%}")
