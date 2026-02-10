"""
⏱️ TOKEN SCHEDULER (ITS)
Intelligent Token Scheduling for optimal API usage

Based on V28's layer2_intelligenttokenscheduling.py + its/
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = field(default_factory=time.time)
    
    def consume(self, amount: int) -> bool:
        self._refill()
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now


@dataclass
class TokenRequest:
    """A request for tokens"""
    id: str
    tokens_needed: int
    priority: int
    timestamp: float
    model: str


class TokenSchedulerAlgorithm(BaseAlgorithm):
    """
    ⏱️ Intelligent Token Scheduler (ITS)
    
    Manages token usage across API calls:
    - Rate limiting
    - Priority queuing  
    - Budget management
    - Cost optimization
    
    From V28: ITS module (8/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="TokenScheduler",
            name="Token Scheduler (ITS)",
            level="operational",
            category="resource_management",
            version="1.0",
            description="Intelligent token scheduling and rate limiting",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("request", "object", True, "Token request"),
                    IOField("budget", "object", False, "Token budget limits")
                ],
                outputs=[
                    IOField("approved", "boolean", True, "Request approved"),
                    IOField("wait_time", "number", True, "Wait time if queued")
                ]
            ),
            steps=["Check budget", "Evaluate priority", "Apply rate limit", "Queue or approve"],
            tags=["tokens", "scheduling", "rate-limiting", "its"]
        )
        
        # Token buckets per model
        self.buckets = {
            "claude-opus-4.6": TokenBucket(100000, 100000, 1000),
            "gpt-5.2-codex": TokenBucket(150000, 150000, 1500),
            "glm-4.6v": TokenBucket(200000, 200000, 2000),
            "default": TokenBucket(50000, 50000, 500)
        }
        
        # Request queue
        self.queue: deque = deque(maxlen=1000)
        
        # Usage tracking
        self.usage = {"total": 0, "by_model": {}}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        request_data = params.get("request", {})
        budget = params.get("budget", {})
        
        request = TokenRequest(
            id=request_data.get("id", str(time.time())),
            tokens_needed=request_data.get("tokens", 1000),
            priority=request_data.get("priority", 5),
            timestamp=time.time(),
            model=request_data.get("model", "default")
        )
        
        print(f"\n⏱️ Token Scheduler (ITS)")
        print(f"   Request: {request.tokens_needed} tokens for {request.model}")
        
        # Check budget
        budget_limit = budget.get("max_tokens", float('inf'))
        if self.usage["total"] + request.tokens_needed > budget_limit:
            return AlgorithmResult(
                status="rejected",
                data={"approved": False, "reason": "Budget exceeded", "wait_time": -1}
            )
        
        # Get bucket
        bucket = self.buckets.get(request.model, self.buckets["default"])
        
        # Try to consume
        if bucket.consume(request.tokens_needed):
            # Track usage
            self.usage["total"] += request.tokens_needed
            self.usage["by_model"][request.model] = (
                self.usage["by_model"].get(request.model, 0) + request.tokens_needed
            )
            
            print(f"   ✅ Approved immediately")
            
            return AlgorithmResult(
                status="success",
                data={
                    "approved": True,
                    "wait_time": 0,
                    "usage": self.usage,
                    "remaining": bucket.tokens
                }
            )
        else:
            # Calculate wait time
            tokens_short = request.tokens_needed - bucket.tokens
            wait_time = tokens_short / bucket.refill_rate
            
            # Queue high priority
            if request.priority >= 7:
                self.queue.appendleft(request)
            else:
                self.queue.append(request)
            
            print(f"   ⏳ Queued (wait: {wait_time:.1f}s)")
            
            return AlgorithmResult(
                status="queued",
                data={
                    "approved": False,
                    "wait_time": wait_time,
                    "queue_position": len(self.queue),
                    "remaining": bucket.tokens
                }
            )
    
    def get_usage_stats(self) -> Dict:
        return {
            "total_tokens": self.usage["total"],
            "by_model": self.usage["by_model"],
            "queue_size": len(self.queue),
            "buckets": {
                name: {"tokens": b.tokens, "capacity": b.capacity}
                for name, b in self.buckets.items()
            }
        }


def register(algorithm_manager):
    algo = TokenSchedulerAlgorithm()
    algorithm_manager.register("TokenScheduler", algo)
    print("✅ TokenScheduler registered")


if __name__ == "__main__":
    algo = TokenSchedulerAlgorithm()
    result = algo.execute({
        "request": {"tokens": 5000, "model": "claude-opus-4.6", "priority": 8},
        "budget": {"max_tokens": 1000000}
    })
    print(f"Approved: {result.data['approved']}")
