"""
Provider Performance Tracker
=============================

Tracks performance metrics for each provider and dynamically adjusts
priority based on real-world performance (latency, success rate, cost).

This ensures that the best-performing provider is always prioritized,
rather than using fixed priorities.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ProviderName(str, Enum):
    """Provider names."""
    V98API = "v98api"
    AICODING = "aicoding"
    GEMINI_OAUTH = "gemini_oauth"
    KIRO_OAUTH = "kiro_oauth"
    QWEN_OAUTH = "qwen_oauth"
    ANTIGRAVITY = "antigravity"


@dataclass
class ProviderMetrics:
    """Performance metrics for a provider."""
    provider: ProviderName
    
    # Success metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency metrics (ms)
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    
    # Cost metrics
    total_cost: float = 0.0
    
    # Availability
    consecutive_failures: int = 0
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    
    # Health status
    is_healthy: bool = True
    health_check_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_requests == 0:
            return 1.0  # Assume healthy if no requests yet
        return self.successful_requests / self.total_requests
    
    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency in milliseconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests
    
    @property
    def avg_cost_per_request(self) -> float:
        """Calculate average cost per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_cost / self.total_requests
    
    def calculate_score(self) -> float:
        """
        Calculate provider score for prioritization.
        
        Lower score = higher priority.
        
        Formula:
        score = (1 - success_rate) * 1000 +
                (avg_latency_ms / 100) +
                (consecutive_failures * 100) +
                (avg_cost_per_request * 10)
        """
        if not self.is_healthy:
            return 1e9  # Extremely high score for unhealthy providers
        
        # Success rate penalty (0-1000)
        success_penalty = (1 - self.success_rate) * 1000
        
        # Latency penalty (normalized to ~0-10 for typical 0-1000ms)
        latency_penalty = self.avg_latency_ms / 100
        
        # Consecutive failures penalty
        failure_penalty = self.consecutive_failures * 100
        
        # Cost penalty
        cost_penalty = self.avg_cost_per_request * 10
        
        return success_penalty + latency_penalty + failure_penalty + cost_penalty


class PerformanceTracker:
    """
    Tracks performance metrics for all providers and dynamically
    adjusts priorities.
    """
    
    def __init__(self):
        self.metrics: Dict[ProviderName, ProviderMetrics] = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize metrics for all providers."""
        for provider in ProviderName:
            self.metrics[provider] = ProviderMetrics(provider=provider)
    
    def record_request(
        self,
        provider: ProviderName,
        success: bool,
        latency_ms: float,
        cost: float = 0.0,
    ):
        """
        Record a request and update metrics.
        
        Args:
            provider: Provider name
            success: Whether the request succeeded
            latency_ms: Request latency in milliseconds
            cost: Request cost in USD
        """
        metrics = self.metrics[provider]
        
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
            metrics.consecutive_failures = 0
            metrics.last_success_time = time.time()
            
            # Update latency metrics
            metrics.total_latency_ms += latency_ms
            metrics.min_latency_ms = min(metrics.min_latency_ms, latency_ms)
            metrics.max_latency_ms = max(metrics.max_latency_ms, latency_ms)
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
            metrics.last_failure_time = time.time()
            
            # Mark as unhealthy if too many consecutive failures
            if metrics.consecutive_failures >= 5:
                metrics.is_healthy = False
        
        # Update cost
        metrics.total_cost += cost
    
    def mark_unhealthy(self, provider: ProviderName):
        """Mark a provider as unhealthy."""
        self.metrics[provider].is_healthy = False
        self.metrics[provider].consecutive_failures += 1
    
    def mark_healthy(self, provider: ProviderName):
        """Mark a provider as healthy."""
        self.metrics[provider].is_healthy = True
        self.metrics[provider].consecutive_failures = 0
    
    def get_sorted_providers(self) -> List[ProviderName]:
        """
        Get providers sorted by performance score (best first).
        
        Returns:
            List of provider names sorted by score (ascending)
        """
        providers_with_scores = [
            (provider, metrics.calculate_score())
            for provider, metrics in self.metrics.items()
        ]
        
        # Sort by score (ascending = best first)
        providers_with_scores.sort(key=lambda x: x[1])
        
        return [provider for provider, _ in providers_with_scores]
    
    def get_best_provider(self) -> Optional[ProviderName]:
        """Get the best performing provider."""
        sorted_providers = self.get_sorted_providers()
        
        # Return first healthy provider
        for provider in sorted_providers:
            if self.metrics[provider].is_healthy:
                return provider
        
        return None
    
    def get_metrics(self, provider: ProviderName) -> ProviderMetrics:
        """Get metrics for a specific provider."""
        return self.metrics[provider]
    
    def get_all_metrics(self) -> Dict[ProviderName, ProviderMetrics]:
        """Get metrics for all providers."""
        return self.metrics.copy()
    
    def get_stats_summary(self) -> Dict[str, any]:
        """Get a summary of all provider stats."""
        sorted_providers = self.get_sorted_providers()
        
        summary = {
            "best_provider": sorted_providers[0].value if sorted_providers else None,
            "provider_rankings": [],
        }
        
        for provider in sorted_providers:
            metrics = self.metrics[provider]
            summary["provider_rankings"].append({
                "provider": provider.value,
                "score": round(metrics.calculate_score(), 2),
                "success_rate": round(metrics.success_rate * 100, 2),
                "avg_latency_ms": round(metrics.avg_latency_ms, 2),
                "total_requests": metrics.total_requests,
                "is_healthy": metrics.is_healthy,
            })
        
        return summary
    
    def reset_metrics(self, provider: Optional[ProviderName] = None):
        """
        Reset metrics for a provider or all providers.
        
        Args:
            provider: Provider to reset, or None to reset all
        """
        if provider:
            self.metrics[provider] = ProviderMetrics(provider=provider)
        else:
            self._init_providers()


# Global performance tracker instance
_global_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = PerformanceTracker()
    return _global_tracker
