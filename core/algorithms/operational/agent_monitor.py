"""
👁️ AGENT MONITOR
Monitor agent health, performance, and behavior

Based on V28's core_engine/agent_monitor.py
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


class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentMetrics:
    """Metrics for an agent"""
    agent_id: str
    status: AgentStatus
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_response_time: float = 0.0
    last_heartbeat: float = 0.0
    memory_usage_mb: float = 0.0
    error_rate: float = 0.0


class AgentMonitorAlgorithm(BaseAlgorithm):
    """
    👁️ Agent Monitor
    
    Monitors all agents:
    - Health checks
    - Performance metrics
    - Behavior analysis
    - Alert generation
    
    From V28: core_engine/agent_monitor.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AgentMonitor",
            name="Agent Monitor",
            level="operational",
            category="monitoring",
            version="1.0",
            description="Monitor agent health and performance",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "register/heartbeat/check/report"),
                    IOField("agent_id", "string", False, "Agent identifier"),
                    IOField("metrics", "object", False, "Agent metrics")
                ],
                outputs=[
                    IOField("result", "object", True, "Monitoring result")
                ]
            ),
            steps=["Collect metrics", "Analyze health", "Detect anomalies", "Generate alerts"],
            tags=["monitoring", "agents", "health", "metrics"]
        )
        
        self.agents: Dict[str, AgentMetrics] = {}
        self.alerts: List[Dict] = []
        self.heartbeat_timeout = 60  # seconds
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "check")
        agent_id = params.get("agent_id", "")
        
        print(f"\n👁️ Agent Monitor")
        
        if action == "register":
            return self._register_agent(agent_id, params.get("metrics", {}))
        elif action == "heartbeat":
            return self._heartbeat(agent_id, params.get("metrics", {}))
        elif action == "check":
            return self._check_health(agent_id)
        elif action == "report":
            return self._generate_report()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _register_agent(self, agent_id: str, metrics: Dict) -> AlgorithmResult:
        if not agent_id:
            agent_id = f"agent_{len(self.agents)}"
        
        self.agents[agent_id] = AgentMetrics(
            agent_id=agent_id,
            status=AgentStatus.IDLE,
            last_heartbeat=time.time()
        )
        
        print(f"   Registered: {agent_id}")
        
        return AlgorithmResult(
            status="success",
            data={"registered": agent_id, "total_agents": len(self.agents)}
        )
    
    def _heartbeat(self, agent_id: str, metrics: Dict) -> AlgorithmResult:
        if agent_id not in self.agents:
            self._register_agent(agent_id, metrics)
        
        agent = self.agents[agent_id]
        agent.last_heartbeat = time.time()
        agent.status = AgentStatus(metrics.get("status", "active"))
        
        # Update metrics
        if "tasks_completed" in metrics:
            agent.tasks_completed = metrics["tasks_completed"]
        if "tasks_failed" in metrics:
            agent.tasks_failed = metrics["tasks_failed"]
        if "response_time" in metrics:
            agent.avg_response_time = metrics["response_time"]
        if "memory_mb" in metrics:
            agent.memory_usage_mb = metrics["memory_mb"]
        
        # Calculate error rate
        total = agent.tasks_completed + agent.tasks_failed
        if total > 0:
            agent.error_rate = agent.tasks_failed / total
        
        return AlgorithmResult(
            status="success",
            data={"heartbeat": True, "agent": agent_id}
        )
    
    def _check_health(self, agent_id: str = "") -> AlgorithmResult:
        now = time.time()
        
        if agent_id:
            if agent_id not in self.agents:
                return AlgorithmResult(
                    status="success",
                    data={"agent": agent_id, "status": "unknown"}
                )
            
            agent = self.agents[agent_id]
            is_online = (now - agent.last_heartbeat) < self.heartbeat_timeout
            
            return AlgorithmResult(
                status="success",
                data={
                    "agent": agent_id,
                    "status": agent.status.value if is_online else "offline",
                    "online": is_online,
                    "metrics": {
                        "completed": agent.tasks_completed,
                        "failed": agent.tasks_failed,
                        "error_rate": agent.error_rate,
                        "avg_response_time": agent.avg_response_time
                    }
                }
            )
        
        # Check all agents
        healthy = 0
        unhealthy = []
        
        for aid, agent in self.agents.items():
            is_online = (now - agent.last_heartbeat) < self.heartbeat_timeout
            if is_online and agent.error_rate < 0.2:
                healthy += 1
            else:
                unhealthy.append(aid)
                if not is_online:
                    agent.status = AgentStatus.OFFLINE
        
        print(f"   Health: {healthy}/{len(self.agents)} healthy")
        
        return AlgorithmResult(
            status="success",
            data={
                "total_agents": len(self.agents),
                "healthy": healthy,
                "unhealthy": unhealthy
            }
        )
    
    def _generate_report(self) -> AlgorithmResult:
        total_completed = sum(a.tasks_completed for a in self.agents.values())
        total_failed = sum(a.tasks_failed for a in self.agents.values())
        avg_response = sum(a.avg_response_time for a in self.agents.values()) / len(self.agents) if self.agents else 0
        
        return AlgorithmResult(
            status="success",
            data={
                "summary": {
                    "total_agents": len(self.agents),
                    "total_tasks_completed": total_completed,
                    "total_tasks_failed": total_failed,
                    "overall_error_rate": total_failed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0,
                    "avg_response_time_ms": avg_response
                },
                "agents": [
                    {"id": a.agent_id, "status": a.status.value, "completed": a.tasks_completed}
                    for a in self.agents.values()
                ]
            }
        )


def register(algorithm_manager):
    algo = AgentMonitorAlgorithm()
    algorithm_manager.register("AgentMonitor", algo)
    print("✅ AgentMonitor registered")


if __name__ == "__main__":
    algo = AgentMonitorAlgorithm()
    algo.execute({"action": "register", "agent_id": "opus_agent"})
    algo.execute({"action": "heartbeat", "agent_id": "opus_agent", "metrics": {"status": "active", "tasks_completed": 5}})
    result = algo.execute({"action": "check"})
    print(f"Healthy: {result.data['healthy']}/{result.data['total_agents']}")
