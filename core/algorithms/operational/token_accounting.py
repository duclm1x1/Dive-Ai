"""
📊 TOKEN ACCOUNTING (TA)
Track and analyze token usage across conversations

Based on V28's layer3_tokenaccounting.py + ta/
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class TokenEntry:
    """A token usage entry"""
    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    task_id: str = ""


class TokenAccountingAlgorithm(BaseAlgorithm):
    """
    📊 Token Accounting (TA)
    
    Tracks token usage for cost analysis:
    - Per-model usage
    - Per-task usage
    - Cost calculation
    - Budget alerts
    
    From V28: TA module (8/10 priority)
    """
    
    COSTS = {
        "claude-opus-4.6": {"input": 0.015, "output": 0.075},
        "gpt-5.2-codex": {"input": 0.001, "output": 0.008},
        "glm-4.6v": {"input": 0.003, "output": 0.006},
        "default": {"input": 0.001, "output": 0.002}
    }
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="TokenAccounting",
            name="Token Accounting (TA)",
            level="operational",
            category="monitoring",
            version="1.0",
            description="Track and analyze token usage",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "record/report/reset"),
                    IOField("entry", "object", False, "Token entry to record")
                ],
                outputs=[
                    IOField("result", "object", True, "Accounting result")
                ]
            ),
            steps=["Parse action", "Update ledger", "Calculate costs", "Return stats"],
            tags=["tokens", "accounting", "costs", "monitoring"]
        )
        
        self.ledger: List[TokenEntry] = []
        self.budget = {"daily": 10.0, "monthly": 100.0}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "report")
        entry_data = params.get("entry", {})
        
        print(f"\n📊 Token Accounting (TA)")
        
        if action == "record":
            return self._record(entry_data)
        elif action == "report":
            return self._report()
        elif action == "reset":
            return self._reset()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _record(self, data: Dict) -> AlgorithmResult:
        model = data.get("model", "default")
        input_tokens = data.get("input_tokens", 0)
        output_tokens = data.get("output_tokens", 0)
        
        costs = self.COSTS.get(model, self.COSTS["default"])
        cost = (input_tokens / 1_000_000 * costs["input"] + 
                output_tokens / 1_000_000 * costs["output"])
        
        entry = TokenEntry(
            timestamp=time.time(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            task_id=data.get("task_id", "")
        )
        self.ledger.append(entry)
        
        print(f"   Recorded: {input_tokens}+{output_tokens} tokens, ${cost:.4f}")
        
        return AlgorithmResult(
            status="success",
            data={
                "entry": {"tokens": input_tokens + output_tokens, "cost": cost},
                "total_entries": len(self.ledger)
            }
        )
    
    def _report(self) -> AlgorithmResult:
        if not self.ledger:
            return AlgorithmResult(
                status="success",
                data={"summary": "No usage recorded", "total_cost": 0}
            )
        
        # Aggregate by model
        by_model = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0})
        for entry in self.ledger:
            by_model[entry.model]["input"] += entry.input_tokens
            by_model[entry.model]["output"] += entry.output_tokens
            by_model[entry.model]["cost"] += entry.cost
        
        total_cost = sum(e.cost for e in self.ledger)
        total_tokens = sum(e.input_tokens + e.output_tokens for e in self.ledger)
        
        # Daily usage (last 24h)
        day_ago = time.time() - 86400
        daily_cost = sum(e.cost for e in self.ledger if e.timestamp > day_ago)
        
        print(f"   Total: {total_tokens} tokens, ${total_cost:.4f}")
        
        return AlgorithmResult(
            status="success",
            data={
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "daily_cost": daily_cost,
                "by_model": dict(by_model),
                "budget_remaining": {
                    "daily": self.budget["daily"] - daily_cost,
                    "monthly": self.budget["monthly"] - total_cost
                },
                "entries_count": len(self.ledger)
            }
        )
    
    def _reset(self) -> AlgorithmResult:
        count = len(self.ledger)
        self.ledger = []
        return AlgorithmResult(
            status="success",
            data={"reset": True, "entries_cleared": count}
        )


def register(algorithm_manager):
    algo = TokenAccountingAlgorithm()
    algorithm_manager.register("TokenAccounting", algo)
    print("✅ TokenAccounting registered")


if __name__ == "__main__":
    algo = TokenAccountingAlgorithm()
    
    # Record some usage
    algo.execute({"action": "record", "entry": {
        "model": "claude-opus-4.6", "input_tokens": 5000, "output_tokens": 2000
    }})
    algo.execute({"action": "record", "entry": {
        "model": "gpt-5.2-codex", "input_tokens": 3000, "output_tokens": 1500
    }})
    
    # Get report
    result = algo.execute({"action": "report"})
    print(f"Report: ${result.data['total_cost']:.4f} total")
