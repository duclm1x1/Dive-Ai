"""
🔧 RECOVERY HANDLER
Handle system recovery from failures

Based on V28's core_engine/recovery_handler.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class RecoveryStrategy(Enum):
    RETRY = "retry"
    ROLLBACK = "rollback"
    FAILOVER = "failover"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    SKIP = "skip"


@dataclass
class RecoveryAttempt:
    """A recovery attempt record"""
    id: str
    error_type: str
    strategy: RecoveryStrategy
    success: bool
    duration: float
    timestamp: float


class RecoveryHandlerAlgorithm(BaseAlgorithm):
    """
    🔧 Recovery Handler
    
    Handles system recovery:
    - Failure detection
    - Recovery strategies
    - Automatic retries
    - Graceful degradation
    
    From V28: core_engine/recovery_handler.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="RecoveryHandler",
            name="Recovery Handler",
            level="operational",
            category="reliability",
            version="1.0",
            description="Handle system recovery from failures",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "recover/analyze/configure"),
                    IOField("error", "object", False, "Error to recover from"),
                    IOField("strategy", "string", False, "Recovery strategy")
                ],
                outputs=[
                    IOField("result", "object", True, "Recovery result")
                ]
            ),
            steps=["Detect failure", "Select strategy", "Execute recovery", "Verify success"],
            tags=["recovery", "reliability", "resilience", "failure"]
        )
        
        self.attempts: List[RecoveryAttempt] = []
        self.strategy_map: Dict[str, RecoveryStrategy] = {
            "timeout": RecoveryStrategy.RETRY,
            "connection": RecoveryStrategy.FAILOVER,
            "validation": RecoveryStrategy.SKIP,
            "resource": RecoveryStrategy.GRACEFUL_DEGRADATION,
            "critical": RecoveryStrategy.ROLLBACK
        }
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "recover")
        
        print(f"\n🔧 Recovery Handler")
        
        if action == "recover":
            return self._recover(params.get("error", {}), params.get("strategy"))
        elif action == "analyze":
            return self._analyze_failures()
        elif action == "configure":
            return self._configure_strategy(params.get("error_type", ""), params.get("strategy", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _recover(self, error: Dict, strategy_override: Optional[str]) -> AlgorithmResult:
        error_type = error.get("type", "unknown")
        error_msg = error.get("message", "")
        
        # Determine strategy
        if strategy_override:
            strategy = RecoveryStrategy(strategy_override)
        else:
            strategy = self._select_strategy(error_type)
        
        start = time.time()
        success = False
        recovery_result = {}
        
        # Execute recovery
        if strategy == RecoveryStrategy.RETRY:
            max_retries = 3
            for attempt in range(max_retries):
                # Simulate retry
                time.sleep(0.1)
                if attempt == max_retries - 1:  # Succeed on last try
                    success = True
                    recovery_result = {"retries": attempt + 1}
                    break
        
        elif strategy == RecoveryStrategy.ROLLBACK:
            # Simulate rollback
            success = True
            recovery_result = {"rolled_back": True, "checkpoint": "last_known_good"}
        
        elif strategy == RecoveryStrategy.FAILOVER:
            success = True
            recovery_result = {"failover_to": "backup_service"}
        
        elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            success = True
            recovery_result = {"degraded_mode": True, "features_disabled": ["caching"]}
        
        elif strategy == RecoveryStrategy.SKIP:
            success = True
            recovery_result = {"skipped": True}
        
        duration = time.time() - start
        
        attempt = RecoveryAttempt(
            id=f"rec_{len(self.attempts)}",
            error_type=error_type,
            strategy=strategy,
            success=success,
            duration=duration,
            timestamp=time.time()
        )
        self.attempts.append(attempt)
        
        print(f"   {strategy.value} → {'Success' if success else 'Failed'}")
        
        return AlgorithmResult(
            status="success" if success else "failed",
            data={
                "strategy_used": strategy.value,
                "success": success,
                "duration": duration,
                "result": recovery_result
            }
        )
    
    def _select_strategy(self, error_type: str) -> RecoveryStrategy:
        # Check exact match
        if error_type in self.strategy_map:
            return self.strategy_map[error_type]
        
        # Check containing
        for key, strategy in self.strategy_map.items():
            if key in error_type.lower():
                return strategy
        
        return RecoveryStrategy.RETRY  # Default
    
    def _analyze_failures(self) -> AlgorithmResult:
        if not self.attempts:
            return AlgorithmResult(status="success", data={"analysis": "No failures recorded"})
        
        by_type = {}
        by_strategy = {}
        
        for attempt in self.attempts:
            # By type
            if attempt.error_type not in by_type:
                by_type[attempt.error_type] = {"count": 0, "successes": 0}
            by_type[attempt.error_type]["count"] += 1
            if attempt.success:
                by_type[attempt.error_type]["successes"] += 1
            
            # By strategy
            strat = attempt.strategy.value
            if strat not in by_strategy:
                by_strategy[strat] = {"count": 0, "successes": 0}
            by_strategy[strat]["count"] += 1
            if attempt.success:
                by_strategy[strat]["successes"] += 1
        
        return AlgorithmResult(
            status="success",
            data={
                "total_attempts": len(self.attempts),
                "by_type": by_type,
                "by_strategy": by_strategy,
                "overall_success_rate": sum(1 for a in self.attempts if a.success) / len(self.attempts)
            }
        )
    
    def _configure_strategy(self, error_type: str, strategy: str) -> AlgorithmResult:
        if not error_type or not strategy:
            return AlgorithmResult(status="error", error="Both error_type and strategy required")
        
        self.strategy_map[error_type] = RecoveryStrategy(strategy)
        
        return AlgorithmResult(
            status="success",
            data={"configured": error_type, "strategy": strategy}
        )


def register(algorithm_manager):
    algo = RecoveryHandlerAlgorithm()
    algorithm_manager.register("RecoveryHandler", algo)
    print("✅ RecoveryHandler registered")


if __name__ == "__main__":
    algo = RecoveryHandlerAlgorithm()
    result = algo.execute({"action": "recover", "error": {"type": "timeout", "message": "API timeout"}})
    print(f"Recovery: {result.data['strategy_used']} → {result.data['success']}")
