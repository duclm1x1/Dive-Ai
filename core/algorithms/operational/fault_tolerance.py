"""
🛡️ FAULT TOLERANCE
Automatic fault detection and recovery for multi-agent systems

Based on V28's layer4_faulttolerance.py
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


class FaultType(Enum):
    TIMEOUT = "timeout"
    ERROR = "error"
    CRASH = "crash"
    OVERLOAD = "overload"
    NETWORK = "network"


@dataclass
class FaultEvent:
    """A fault event"""
    timestamp: float
    fault_type: FaultType
    component: str
    details: str
    recovered: bool = False


@dataclass
class ComponentHealth:
    """Health status of a component"""
    component_id: str
    status: str  # "healthy", "degraded", "failed"
    last_check: float
    failure_count: int = 0
    recovery_attempts: int = 0


class FaultToleranceAlgorithm(BaseAlgorithm):
    """
    🛡️ Fault Tolerance System
    
    Provides resilience through:
    - Health monitoring
    - Automatic failover
    - Circuit breakers
    - Recovery strategies
    
    From V28: layer4_faulttolerance.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="FaultTolerance",
            name="Fault Tolerance",
            level="operational",
            category="resilience",
            version="1.0",
            description="Automatic fault detection and recovery",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "check/report_fault/recover"),
                    IOField("component", "string", False, "Component ID"),
                    IOField("fault", "object", False, "Fault details")
                ],
                outputs=[
                    IOField("result", "object", True, "Fault tolerance result")
                ]
            ),
            steps=["Monitor components", "Detect faults", "Apply recovery", "Update status"],
            tags=["fault-tolerance", "resilience", "recovery", "monitoring"]
        )
        
        self.components: Dict[str, ComponentHealth] = {}
        self.faults: List[FaultEvent] = []
        self.circuit_breakers: Dict[str, bool] = {}  # True = open (blocking)
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "check")
        component_id = params.get("component", "")
        fault_data = params.get("fault", {})
        
        print(f"\n🛡️ Fault Tolerance")
        
        if action == "check":
            return self._check_health(component_id)
        elif action == "report_fault":
            return self._report_fault(component_id, fault_data)
        elif action == "recover":
            return self._attempt_recovery(component_id)
        elif action == "status":
            return self._get_status()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _check_health(self, component_id: str) -> AlgorithmResult:
        if component_id:
            health = self.components.get(component_id)
            if health:
                return AlgorithmResult(
                    status="success",
                    data={
                        "component": component_id,
                        "status": health.status,
                        "failures": health.failure_count,
                        "circuit_open": self.circuit_breakers.get(component_id, False)
                    }
                )
            return AlgorithmResult(status="success", data={"component": component_id, "status": "unknown"})
        
        # Check all
        statuses = {
            cid: {"status": h.status, "failures": h.failure_count}
            for cid, h in self.components.items()
        }
        
        healthy = sum(1 for h in self.components.values() if h.status == "healthy")
        total = len(self.components)
        
        print(f"   Components: {healthy}/{total} healthy")
        
        return AlgorithmResult(
            status="success",
            data={
                "total_components": total,
                "healthy": healthy,
                "degraded": sum(1 for h in self.components.values() if h.status == "degraded"),
                "failed": sum(1 for h in self.components.values() if h.status == "failed"),
                "components": statuses
            }
        )
    
    def _report_fault(self, component_id: str, fault_data: Dict) -> AlgorithmResult:
        if not component_id:
            return AlgorithmResult(status="error", error="Component ID required")
        
        fault_type = FaultType(fault_data.get("type", "error"))
        
        event = FaultEvent(
            timestamp=time.time(),
            fault_type=fault_type,
            component=component_id,
            details=fault_data.get("details", "")
        )
        self.faults.append(event)
        
        # Update component health
        if component_id not in self.components:
            self.components[component_id] = ComponentHealth(
                component_id=component_id,
                status="healthy",
                last_check=time.time()
            )
        
        health = self.components[component_id]
        health.failure_count += 1
        health.last_check = time.time()
        
        # Update status based on failures
        if health.failure_count >= 5:
            health.status = "failed"
            self.circuit_breakers[component_id] = True  # Open circuit
        elif health.failure_count >= 2:
            health.status = "degraded"
        
        print(f"   Fault: {component_id} - {fault_type.value} (count: {health.failure_count})")
        
        return AlgorithmResult(
            status="success",
            data={
                "recorded": True,
                "component_status": health.status,
                "circuit_open": self.circuit_breakers.get(component_id, False)
            }
        )
    
    def _attempt_recovery(self, component_id: str) -> AlgorithmResult:
        if not component_id or component_id not in self.components:
            return AlgorithmResult(status="error", error="Component not found")
        
        health = self.components[component_id]
        health.recovery_attempts += 1
        
        # Simulate recovery (success rate decreases with attempts)
        import random
        success_rate = 0.9 - (health.recovery_attempts * 0.1)
        recovered = random.random() < success_rate
        
        if recovered:
            health.status = "healthy"
            health.failure_count = 0
            self.circuit_breakers[component_id] = False
            print(f"   ✅ Recovery successful: {component_id}")
        else:
            print(f"   ❌ Recovery failed: {component_id}")
        
        return AlgorithmResult(
            status="success",
            data={
                "recovered": recovered,
                "attempts": health.recovery_attempts,
                "status": health.status
            }
        )
    
    def _get_status(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "total_faults": len(self.faults),
                "recent_faults": [
                    {"component": f.component, "type": f.fault_type.value}
                    for f in self.faults[-5:]
                ],
                "open_circuits": [k for k, v in self.circuit_breakers.items() if v]
            }
        )


def register(algorithm_manager):
    algo = FaultToleranceAlgorithm()
    algorithm_manager.register("FaultTolerance", algo)
    print("✅ FaultTolerance registered")


if __name__ == "__main__":
    algo = FaultToleranceAlgorithm()
    algo.execute({"action": "report_fault", "component": "agent-1", "fault": {"type": "timeout"}})
    algo.execute({"action": "report_fault", "component": "agent-1", "fault": {"type": "timeout"}})
    result = algo.execute({"action": "check", "component": "agent-1"})
    print(f"Status: {result.data['status']}")
