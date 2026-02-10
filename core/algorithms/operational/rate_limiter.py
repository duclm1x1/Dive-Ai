"""
⏱️ RATE LIMITER
Control request rates

Based on V28's core_engine/rate_limiter.py
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
class RateLimitBucket:
    """A rate limit bucket"""
    key: str
    tokens: float
    max_tokens: float
    refill_rate: float  # tokens per second
    last_update: float


class RateLimiterAlgorithm(BaseAlgorithm):
    """
    ⏱️ Rate Limiter
    
    Controls request rates:
    - Token bucket algorithm
    - Per-key limits
    - Burst handling
    - Backoff calculation
    
    From V28: core_engine/rate_limiter.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="RateLimiter",
            name="Rate Limiter",
            level="operational",
            category="control",
            version="1.0",
            description="Control request rates",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "check/consume/config"),
                    IOField("key", "string", False, "Rate limit key"),
                    IOField("tokens", "number", False, "Tokens to consume")
                ],
                outputs=[
                    IOField("allowed", "boolean", True, "Whether request is allowed")
                ]
            ),
            steps=["Refill tokens", "Check availability", "Consume tokens", "Calculate backoff"],
            tags=["rate-limit", "throttle", "control"]
        )
        
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.default_max = 100
        self.default_rate = 10  # tokens per second
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "check")
        
        print(f"\n⏱️ Rate Limiter")
        
        if action == "check":
            return self._check(params.get("key", "default"), params.get("tokens", 1))
        elif action == "consume":
            return self._consume(params.get("key", "default"), params.get("tokens", 1))
        elif action == "config":
            return self._configure(
                params.get("key", "default"),
                params.get("max_tokens", self.default_max),
                params.get("refill_rate", self.default_rate)
            )
        elif action == "status":
            return self._get_status(params.get("key"))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _get_bucket(self, key: str) -> RateLimitBucket:
        if key not in self.buckets:
            self.buckets[key] = RateLimitBucket(
                key=key,
                tokens=self.default_max,
                max_tokens=self.default_max,
                refill_rate=self.default_rate,
                last_update=time.time()
            )
        return self.buckets[key]
    
    def _refill(self, bucket: RateLimitBucket):
        now = time.time()
        elapsed = now - bucket.last_update
        refill = elapsed * bucket.refill_rate
        bucket.tokens = min(bucket.max_tokens, bucket.tokens + refill)
        bucket.last_update = now
    
    def _check(self, key: str, tokens: int) -> AlgorithmResult:
        bucket = self._get_bucket(key)
        self._refill(bucket)
        
        allowed = bucket.tokens >= tokens
        
        return AlgorithmResult(
            status="success",
            data={
                "allowed": allowed,
                "available": bucket.tokens,
                "requested": tokens,
                "wait_time": 0 if allowed else (tokens - bucket.tokens) / bucket.refill_rate
            }
        )
    
    def _consume(self, key: str, tokens: int) -> AlgorithmResult:
        bucket = self._get_bucket(key)
        self._refill(bucket)
        
        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            
            print(f"   Consumed: {tokens} tokens from {key}")
            
            return AlgorithmResult(
                status="allowed",
                data={
                    "consumed": tokens,
                    "remaining": bucket.tokens,
                    "key": key
                }
            )
        
        wait_time = (tokens - bucket.tokens) / bucket.refill_rate
        
        return AlgorithmResult(
            status="limited",
            data={
                "requested": tokens,
                "available": bucket.tokens,
                "wait_time": wait_time,
                "retry_after": wait_time
            }
        )
    
    def _configure(self, key: str, max_tokens: float, refill_rate: float) -> AlgorithmResult:
        bucket = self._get_bucket(key)
        bucket.max_tokens = max_tokens
        bucket.refill_rate = refill_rate
        
        return AlgorithmResult(
            status="success",
            data={
                "key": key,
                "max_tokens": max_tokens,
                "refill_rate": refill_rate
            }
        )
    
    def _get_status(self, key: str = None) -> AlgorithmResult:
        if key:
            bucket = self._get_bucket(key)
            self._refill(bucket)
            return AlgorithmResult(
                status="success",
                data={
                    "key": key,
                    "tokens": bucket.tokens,
                    "max": bucket.max_tokens,
                    "rate": bucket.refill_rate,
                    "utilization": 1 - (bucket.tokens / bucket.max_tokens)
                }
            )
        
        return AlgorithmResult(
            status="success",
            data={
                "buckets": [
                    {"key": b.key, "tokens": b.tokens, "max": b.max_tokens}
                    for b in self.buckets.values()
                ],
                "count": len(self.buckets)
            }
        )


def register(algorithm_manager):
    algo = RateLimiterAlgorithm()
    algorithm_manager.register("RateLimiter", algo)
    print("✅ RateLimiter registered")


if __name__ == "__main__":
    algo = RateLimiterAlgorithm()
    
    # Configure rate limit
    algo.execute({"action": "config", "key": "api", "max_tokens": 10, "refill_rate": 2})
    
    # Consume some tokens
    for i in range(5):
        result = algo.execute({"action": "consume", "key": "api", "tokens": 3})
        print(f"Request {i+1}: {result.status} - {result.data.get('remaining', result.data.get('wait_time'))}")
