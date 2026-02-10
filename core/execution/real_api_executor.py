"""
🔌 REAL API EXECUTION ENGINE
Connects 512 agents to real V98/AICoding APIs with rate limiting and cost tracking
"""

import os
import sys
import time
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class APICall:
    """Represents a single API call"""
    call_id: str
    agent_id: int
    model: str
    provider: str  # 'v98' or 'aicoding'
    messages: List[Dict]
    timestamp: datetime = field(default_factory=datetime.now)
    response: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    status: str = "pending"  # pending, running, success, failed


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    tokens_per_minute: int = 100000
    concurrent_requests: int = 10


class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait(self, tokens: int = 1, timeout: float = 60.0) -> bool:
        """Wait for tokens to become available"""
        start = time.time()
        while time.time() - start < timeout:
            if self.acquire(tokens):
                return True
            time.sleep(0.1)
        return False


class CostTracker:
    """Tracks API costs"""
    
    # Cost per 1K tokens (approximate)
    COSTS = {
        "claude-opus-4-6": {"input": 0.015, "output": 0.075},
        "claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015},
        "gpt-5.1-codex": {"input": 0.01, "output": 0.03},
        "gpt-5.1": {"input": 0.005, "output": 0.015},
        "glm-4.6v": {"input": 0.001, "output": 0.002},
        "default": {"input": 0.002, "output": 0.006}
    }
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.calls_by_model: Dict[str, int] = {}
        self.lock = threading.Lock()
    
    def add_usage(self, model: str, input_tokens: int, output_tokens: int):
        """Add usage to tracker"""
        with self.lock:
            costs = self.COSTS.get(model, self.COSTS["default"])
            cost = (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1000
            
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost
            self.calls_by_model[model] = self.calls_by_model.get(model, 0) + 1
            
            return cost
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary"""
        with self.lock:
            return {
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_input_tokens + self.total_output_tokens,
                "total_cost_usd": round(self.total_cost, 4),
                "calls_by_model": dict(self.calls_by_model)
            }


class RealAPIExecutor:
    """
    🚀 Real API Execution Engine
    Executes agent requests against real V98/AICoding APIs
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        
        # Rate limiters
        self.v98_limiter = TokenBucket(
            rate=self.config.requests_per_minute / 60,
            capacity=self.config.requests_per_minute
        )
        self.aicoding_limiter = TokenBucket(
            rate=self.config.requests_per_minute / 60,
            capacity=self.config.requests_per_minute
        )
        
        # Cost tracking
        self.cost_tracker = CostTracker()
        
        # Call history
        self.call_history: deque = deque(maxlen=1000)
        
        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=self.config.concurrent_requests)
        
        # API clients
        self.v98_client = None
        self.aicoding_client = None
        self._init_clients()
        
        print(f"✅ RealAPIExecutor initialized")
        print(f"   Rate limit: {self.config.requests_per_minute} req/min")
        print(f"   Concurrent: {self.config.concurrent_requests} requests")
    
    def _init_clients(self):
        """Initialize API clients"""
        try:
            from core.v98_client import V98Client
            self.v98_client = V98Client()
            print(f"   ✅ V98 Client ready")
        except Exception as e:
            print(f"   ⚠️  V98 Client: {e}")
        
        try:
            # AICoding client initialization
            self.aicoding_api_key = os.getenv("AICODING_API_KEY", "YOUR_AICODING_API_KEY_HERECJCk")
            self.aicoding_base_url = "https://aicoding.io.vn"
            print(f"   ✅ AICoding Client ready")
        except Exception as e:
            print(f"   ⚠️  AICoding Client: {e}")
    
    def execute_v98(self, agent_id: int, model: str, messages: List[Dict], 
                    temperature: float = 0.7, max_tokens: int = 2000) -> APICall:
        """Execute request via V98 API"""
        import requests
        
        call = APICall(
            call_id=f"v98-{agent_id}-{int(time.time()*1000)}",
            agent_id=agent_id,
            model=model,
            provider="v98",
            messages=messages
        )
        
        # Wait for rate limit
        if not self.v98_limiter.wait(1):
            call.status = "rate_limited"
            return call
        
        call.status = "running"
        start_time = time.time()
        
        try:
            api_key = os.getenv("V98_API_KEY", "sk-oQr0PQXVXT0jQ5Jcfp6XAjwQfHvTd2TQ5TGD20G8xNcPGm2Z")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://v98store.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60
            )
            
            call.latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                call.response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                call.tokens_used = usage.get("total_tokens", 0)
                call.cost = self.cost_tracker.add_usage(
                    model,
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0)
                )
                call.status = "success"
            else:
                call.status = "failed"
                call.response = f"Error: {response.status_code}"
                
        except Exception as e:
            call.status = "failed"
            call.response = str(e)
            call.latency_ms = int((time.time() - start_time) * 1000)
        
        self.call_history.append(call)
        return call
    
    def execute_aicoding(self, agent_id: int, model: str, messages: List[Dict],
                         temperature: float = 0.7, max_tokens: int = 2000,
                         format: str = "openai") -> APICall:
        """Execute request via AICoding API"""
        import requests
        
        call = APICall(
            call_id=f"aicoding-{agent_id}-{int(time.time()*1000)}",
            agent_id=agent_id,
            model=model,
            provider="aicoding",
            messages=messages
        )
        
        # Wait for rate limit
        if not self.aicoding_limiter.wait(1):
            call.status = "rate_limited"
            return call
        
        call.status = "running"
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.aicoding_api_key}",
                "Content-Type": "application/json"
            }
            
            if format == "anthropic":
                # Anthropic format
                endpoint = f"{self.aicoding_base_url}/anthropic/v1/messages"
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens
                }
            else:
                # OpenAI format
                endpoint = f"{self.aicoding_base_url}/v1/chat/completions"
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            
            call.latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                
                if format == "anthropic":
                    call.response = data.get("content", [{}])[0].get("text", "")
                    usage = data.get("usage", {})
                    call.tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                else:
                    call.response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    usage = data.get("usage", {})
                    call.tokens_used = usage.get("total_tokens", 0)
                
                call.cost = self.cost_tracker.add_usage(
                    model,
                    usage.get("prompt_tokens", usage.get("input_tokens", 0)),
                    usage.get("completion_tokens", usage.get("output_tokens", 0))
                )
                call.status = "success"
            else:
                call.status = "failed"
                call.response = f"Error: {response.status_code}"
                
        except Exception as e:
            call.status = "failed"
            call.response = str(e)
            call.latency_ms = int((time.time() - start_time) * 1000)
        
        self.call_history.append(call)
        return call
    
    def execute_batch(self, requests: List[Dict]) -> List[APICall]:
        """Execute batch of requests in parallel"""
        futures = []
        
        for req in requests:
            provider = req.get("provider", "v98")
            if provider == "v98":
                future = self.executor.submit(
                    self.execute_v98,
                    req["agent_id"],
                    req["model"],
                    req["messages"],
                    req.get("temperature", 0.7),
                    req.get("max_tokens", 2000)
                )
            else:
                future = self.executor.submit(
                    self.execute_aicoding,
                    req["agent_id"],
                    req["model"],
                    req["messages"],
                    req.get("temperature", 0.7),
                    req.get("max_tokens", 2000),
                    req.get("format", "openai")
                )
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"  ❌ Batch request failed: {e}")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        recent_calls = list(self.call_history)
        success_count = sum(1 for c in recent_calls if c.status == "success")
        failed_count = sum(1 for c in recent_calls if c.status == "failed")
        avg_latency = sum(c.latency_ms for c in recent_calls) / len(recent_calls) if recent_calls else 0
        
        return {
            "total_calls": len(recent_calls),
            "success_rate": success_count / len(recent_calls) * 100 if recent_calls else 0,
            "failed_count": failed_count,
            "avg_latency_ms": int(avg_latency),
            "cost": self.cost_tracker.get_summary()
        }


# Global executor instance
_executor: Optional[RealAPIExecutor] = None


def get_executor() -> RealAPIExecutor:
    """Get or create global executor"""
    global _executor
    if _executor is None:
        _executor = RealAPIExecutor()
    return _executor


if __name__ == "__main__":
    # Test
    executor = get_executor()
    
    print("\n🧪 Testing Real API Execution...")
    
    # Test V98
    result = executor.execute_v98(
        agent_id=1,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in 5 words"}]
    )
    print(f"\n📡 V98 Test: {result.status}")
    print(f"   Response: {result.response[:100] if result.response else 'None'}...")
    print(f"   Latency: {result.latency_ms}ms")
    
    # Stats
    stats = executor.get_stats()
    print(f"\n📊 Stats: {json.dumps(stats, indent=2)}")
