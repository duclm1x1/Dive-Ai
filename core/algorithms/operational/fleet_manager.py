"""
🚀 FLEET MANAGER
Manage a fleet of parallel agent instances

Based on V28's core_engine/fleet_manager.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class AgentRole(Enum):
    LEADER = "leader"
    WORKER = "worker"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"


@dataclass
class FleetAgent:
    """An agent in the fleet"""
    id: str
    role: AgentRole
    capacity: int = 5
    current_tasks: int = 0
    specialization: List[str] = field(default_factory=list)
    performance_score: float = 1.0


@dataclass
class FleetTask:
    """A task for the fleet"""
    id: str
    assigned_agent: Optional[str] = None
    status: str = "pending"
    requirements: List[str] = field(default_factory=list)


class FleetManagerAlgorithm(BaseAlgorithm):
    """
    🚀 Fleet Manager
    
    Manages parallel agent fleet:
    - Agent provisioning
    - Task distribution
    - Specialization matching
    - Fleet scaling
    
    From V28: core_engine/fleet_manager.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="FleetManager",
            name="Fleet Manager",
            level="operational",
            category="orchestration",
            version="1.0",
            description="Manage parallel agent fleet",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "spawn/assign/scale/status"),
                    IOField("agent", "object", False, "Agent configuration"),
                    IOField("task", "object", False, "Task to assign")
                ],
                outputs=[
                    IOField("result", "object", True, "Fleet management result")
                ]
            ),
            steps=["Manage agents", "Match tasks", "Balance load", "Scale as needed"],
            tags=["fleet", "agents", "parallel", "scaling"]
        )
        
        self.agents: Dict[str, FleetAgent] = {}
        self.tasks: Dict[str, FleetTask] = {}
        self.min_agents = 1
        self.max_agents = 10
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n🚀 Fleet Manager")
        
        if action == "spawn":
            return self._spawn_agent(params.get("agent", {}))
        elif action == "assign":
            return self._assign_task(params.get("task", {}))
        elif action == "scale":
            return self._scale_fleet(params.get("target_size", 0))
        elif action == "status":
            return self._get_status()
        elif action == "terminate":
            return self._terminate_agent(params.get("agent_id", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _spawn_agent(self, config: Dict) -> AlgorithmResult:
        if len(self.agents) >= self.max_agents:
            return AlgorithmResult(status="error", error="Fleet at maximum capacity")
        
        agent = FleetAgent(
            id=config.get("id", f"agent_{len(self.agents)}"),
            role=AgentRole(config.get("role", "worker")),
            capacity=config.get("capacity", 5),
            specialization=config.get("specialization", [])
        )
        self.agents[agent.id] = agent
        
        print(f"   Spawned: {agent.id} ({agent.role.value})")
        
        return AlgorithmResult(
            status="success",
            data={"spawned": agent.id, "fleet_size": len(self.agents)}
        )
    
    def _assign_task(self, task_data: Dict) -> AlgorithmResult:
        task = FleetTask(
            id=task_data.get("id", f"task_{len(self.tasks)}"),
            requirements=task_data.get("requirements", [])
        )
        
        # Find best agent
        best_agent = self._find_best_agent(task)
        
        if not best_agent:
            self.tasks[task.id] = task
            return AlgorithmResult(
                status="queued",
                data={"task": task.id, "reason": "No available agent"}
            )
        
        # Assign
        task.assigned_agent = best_agent.id
        task.status = "assigned"
        best_agent.current_tasks += 1
        self.tasks[task.id] = task
        
        print(f"   Assigned: {task.id} → {best_agent.id}")
        
        return AlgorithmResult(
            status="success",
            data={
                "task": task.id,
                "assigned_to": best_agent.id,
                "agent_load": best_agent.current_tasks
            }
        )
    
    def _find_best_agent(self, task: FleetTask) -> Optional[FleetAgent]:
        available = [a for a in self.agents.values() if a.current_tasks < a.capacity]
        
        if not available:
            return None
        
        # Score by specialization match and current load
        def score(agent: FleetAgent) -> float:
            spec_match = sum(1 for r in task.requirements if r in agent.specialization)
            load_factor = 1 - (agent.current_tasks / agent.capacity)
            return spec_match * 10 + load_factor * agent.performance_score
        
        return max(available, key=score)
    
    def _scale_fleet(self, target_size: int) -> AlgorithmResult:
        current = len(self.agents)
        target = max(self.min_agents, min(self.max_agents, target_size))
        
        actions_taken = []
        
        if target > current:
            # Scale up
            for i in range(target - current):
                result = self._spawn_agent({"role": "worker"})
                actions_taken.append(f"spawned:{result.data.get('spawned')}")
        elif target < current:
            # Scale down (remove idle agents)
            idle = [a for a in self.agents.values() if a.current_tasks == 0]
            for agent in idle[:current - target]:
                del self.agents[agent.id]
                actions_taken.append(f"terminated:{agent.id}")
        
        return AlgorithmResult(
            status="success",
            data={
                "previous_size": current,
                "new_size": len(self.agents),
                "actions": actions_taken
            }
        )
    
    def _terminate_agent(self, agent_id: str) -> AlgorithmResult:
        if agent_id not in self.agents:
            return AlgorithmResult(status="error", error="Agent not found")
        
        if len(self.agents) <= self.min_agents:
            return AlgorithmResult(status="error", error="Cannot go below minimum fleet size")
        
        del self.agents[agent_id]
        
        return AlgorithmResult(
            status="success",
            data={"terminated": agent_id, "fleet_size": len(self.agents)}
        )
    
    def _get_status(self) -> AlgorithmResult:
        total_capacity = sum(a.capacity for a in self.agents.values())
        total_load = sum(a.current_tasks for a in self.agents.values())
        
        return AlgorithmResult(
            status="success",
            data={
                "fleet_size": len(self.agents),
                "total_capacity": total_capacity,
                "current_load": total_load,
                "utilization": total_load / total_capacity if total_capacity > 0 else 0,
                "pending_tasks": sum(1 for t in self.tasks.values() if t.status == "pending"),
                "agents": [
                    {"id": a.id, "role": a.role.value, "load": a.current_tasks, "capacity": a.capacity}
                    for a in self.agents.values()
                ]
            }
        )


def register(algorithm_manager):
    algo = FleetManagerAlgorithm()
    algorithm_manager.register("FleetManager", algo)
    print("✅ FleetManager registered")


if __name__ == "__main__":
    algo = FleetManagerAlgorithm()
    algo.execute({"action": "spawn", "agent": {"role": "leader", "specialization": ["planning"]}})
    algo.execute({"action": "spawn", "agent": {"role": "worker", "specialization": ["coding"]}})
    algo.execute({"action": "assign", "task": {"id": "task_1", "requirements": ["coding"]}})
    result = algo.execute({"action": "status"})
    print(f"Fleet: {result.data['fleet_size']} agents, {result.data['utilization']:.1%} utilized")
