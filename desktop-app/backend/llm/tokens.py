"""
Token Tracker - Tracks token usage across all V98 calls

Features:
- Per-model tracking
- Cost estimation
- Usage limits
- Reporting
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class TokenUsage:
    """Single token usage record"""
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    cost_usd: float = 0.0


@dataclass
class ModelPricing:
    """Model pricing in USD per 1M tokens"""
    input_price: float
    output_price: float


# Pricing for Claude models (approximate)
MODEL_PRICING = {
    "claude-opus-4-6-thinking": ModelPricing(15.0, 75.0),
    "claude-opus-4-6": ModelPricing(15.0, 75.0),
    "claude-sonnet-4-5": ModelPricing(3.0, 15.0),
    "claude-sonnet-4-5-thinking": ModelPricing(3.0, 15.0),
    "claude-opus-4-5": ModelPricing(15.0, 75.0),
    "claude-opus-4-5-thinking": ModelPricing(15.0, 75.0),
}

# Default pricing for unknown models
DEFAULT_PRICING = ModelPricing(5.0, 25.0)


class TokenTracker:
    """
    Tracks token usage across all V98 calls
    
    Usage:
        tracker = TokenTracker()
        tracker.record("claude-opus-4-6-thinking", 100, 500)
        print(tracker.get_stats())
    """
    
    def __init__(self, 
                 daily_limit: int = 1_000_000,
                 hourly_limit: int = 100_000):
        self.records: List[TokenUsage] = []
        self.daily_limit = daily_limit
        self.hourly_limit = hourly_limit
    
    def record(self, 
               model: str,
               input_tokens: int = 0,
               output_tokens: int = 0,
               total_tokens: int = None) -> TokenUsage:
        """Record token usage"""
        
        if total_tokens is None:
            total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
        cost = (
            (input_tokens / 1_000_000) * pricing.input_price +
            (output_tokens / 1_000_000) * pricing.output_price
        )
        
        usage = TokenUsage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost
        )
        
        self.records.append(usage)
        return usage
    
    def get_usage(self, 
                  since: datetime = None,
                  model: str = None) -> Dict:
        """Get usage statistics"""
        
        records = self.records
        
        if since:
            records = [r for r in records if r.timestamp >= since]
        
        if model:
            records = [r for r in records if r.model == model]
        
        if not records:
            return {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "requests": 0
            }
        
        return {
            "total_tokens": sum(r.total_tokens for r in records),
            "input_tokens": sum(r.input_tokens for r in records),
            "output_tokens": sum(r.output_tokens for r in records),
            "cost_usd": sum(r.cost_usd for r in records),
            "requests": len(records)
        }
    
    def get_hourly_usage(self) -> Dict:
        """Get usage in last hour"""
        since = datetime.now() - timedelta(hours=1)
        return self.get_usage(since=since)
    
    def get_daily_usage(self) -> Dict:
        """Get usage today"""
        since = datetime.now().replace(hour=0, minute=0, second=0)
        return self.get_usage(since=since)
    
    def get_model_breakdown(self) -> Dict[str, Dict]:
        """Get usage breakdown by model"""
        models = set(r.model for r in self.records)
        return {model: self.get_usage(model=model) for model in models}
    
    def check_limits(self) -> Dict:
        """Check if usage limits are exceeded"""
        hourly = self.get_hourly_usage()
        daily = self.get_daily_usage()
        
        return {
            "hourly_limit": self.hourly_limit,
            "hourly_used": hourly["total_tokens"],
            "hourly_remaining": max(0, self.hourly_limit - hourly["total_tokens"]),
            "hourly_exceeded": hourly["total_tokens"] > self.hourly_limit,
            "daily_limit": self.daily_limit,
            "daily_used": daily["total_tokens"],
            "daily_remaining": max(0, self.daily_limit - daily["total_tokens"]),
            "daily_exceeded": daily["total_tokens"] > self.daily_limit
        }
    
    def can_proceed(self, estimated_tokens: int = 1000) -> bool:
        """Check if we can proceed with estimated token usage"""
        limits = self.check_limits()
        return (
            limits["hourly_remaining"] >= estimated_tokens and
            limits["daily_remaining"] >= estimated_tokens
        )
    
    def get_stats(self) -> Dict:
        """Get full statistics"""
        return {
            "total": self.get_usage(),
            "hourly": self.get_hourly_usage(),
            "daily": self.get_daily_usage(),
            "by_model": self.get_model_breakdown(),
            "limits": self.check_limits()
        }
    
    def clear_old(self, days: int = 7):
        """Clear records older than N days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.records = [r for r in self.records if r.timestamp >= cutoff]


# Singleton tracker
_tracker = None

def get_tracker() -> TokenTracker:
    """Get singleton tracker"""
    global _tracker
    if _tracker is None:
        _tracker = TokenTracker()
    return _tracker


def record_usage(model: str, input_tokens: int = 0, output_tokens: int = 0):
    """Quick record helper"""
    return get_tracker().record(model, input_tokens, output_tokens)


def get_usage_stats() -> Dict:
    """Quick stats helper"""
    return get_tracker().get_stats()
