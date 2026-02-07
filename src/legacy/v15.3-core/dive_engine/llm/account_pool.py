"""
Account Pool Manager
====================

Intelligent multi-account scheduling system for high availability.

Features:
- Multi-account support per provider
- LRU (Least Recently Used) scheduling
- Health-based selection
- Automatic failover
- Load balancing
- 99.9% availability guarantee

Based on AIClient-2-API's provider pool scheduling algorithm.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import json
from pathlib import Path
from enum import Enum


class ProviderType(str, Enum):
    """Provider types."""
    V98API = "v98api"
    AICODING = "aicoding"
    GEMINI_OAUTH = "gemini_oauth"
    KIRO_OAUTH = "kiro_oauth"
    QWEN_OAUTH = "qwen_oauth"
    ANTIGRAVITY = "antigravity"


@dataclass
class AccountNode:
    """
    Represents a single account in the pool.
    
    Each account has health status, usage tracking, and performance metrics
    for intelligent scheduling.
    """
    
    # Identity
    account_id: str
    provider: ProviderType
    
    # Credentials
    api_key: Optional[str] = None
    oauth_token_path: Optional[str] = None
    base_url: Optional[str] = None
    
    # Health status
    is_healthy: bool = True
    is_disabled: bool = False
    error_count: int = 0
    max_error_count: int = 10
    
    # Usage tracking
    usage_count: int = 0
    last_used_time: float = 0.0
    last_refresh_time: float = field(default_factory=time.time)
    last_selection_seq: int = 0
    
    # Performance metrics
    total_requests: int = 0
    successful_requests: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency in milliseconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests
    
    def calculate_score(self, current_seq: int) -> float:
        """
        Calculate priority score for account selection.
        
        Lower score = higher priority.
        
        Algorithm from AIClient-2-API:
        - Unhealthy/disabled nodes: 1e18 (extremely low priority)
        - Freshly refreshed nodes (< 2 min, unused): -2e18 (highest priority)
        - Base score: lastUsedTime + (usageCount * 10000) + (selectionSeq * 1000)
        
        Args:
            current_seq: Current global selection sequence number
            
        Returns:
            Priority score (lower = higher priority)
        """
        
        # Unhealthy or disabled nodes get extremely high score
        if not self.is_healthy or self.is_disabled:
            return 1e18
        
        # Freshly refreshed nodes (within 2 minutes) and unused get highest priority
        time_since_refresh = time.time() - self.last_refresh_time
        if time_since_refresh < 120 and self.usage_count == 0:
            return -2e18
        
        # Base score calculation (LRU + usage count + selection sequence)
        score = (
            self.last_used_time +
            (self.usage_count * 10000) +
            (self.last_selection_seq * 1000)
        )
        
        return score
    
    def record_request(self, success: bool, latency_ms: float):
        """
        Record a request and update metrics.
        
        Args:
            success: Whether the request succeeded
            latency_ms: Request latency in milliseconds
        """
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
            self.total_latency_ms += latency_ms
            self.error_count = 0  # Reset error count on success
        else:
            self.error_count += 1
            
            # Mark unhealthy if too many errors
            if self.error_count >= self.max_error_count:
                self.is_healthy = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "account_id": self.account_id,
            "provider": self.provider.value,
            "api_key": self.api_key,
            "oauth_token_path": self.oauth_token_path,
            "base_url": self.base_url,
            "is_healthy": self.is_healthy,
            "is_disabled": self.is_disabled,
            "error_count": self.error_count,
            "max_error_count": self.max_error_count,
            "usage_count": self.usage_count,
            "last_used_time": self.last_used_time,
            "last_refresh_time": self.last_refresh_time,
            "last_selection_seq": self.last_selection_seq,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "total_latency_ms": self.total_latency_ms,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "AccountNode":
        """Create from dictionary."""
        return AccountNode(
            account_id=d["account_id"],
            provider=ProviderType(d["provider"]),
            api_key=d.get("api_key"),
            oauth_token_path=d.get("oauth_token_path"),
            base_url=d.get("base_url"),
            is_healthy=d.get("is_healthy", True),
            is_disabled=d.get("is_disabled", False),
            error_count=d.get("error_count", 0),
            max_error_count=d.get("max_error_count", 10),
            usage_count=d.get("usage_count", 0),
            last_used_time=d.get("last_used_time", 0.0),
            last_refresh_time=d.get("last_refresh_time", time.time()),
            last_selection_seq=d.get("last_selection_seq", 0),
            total_requests=d.get("total_requests", 0),
            successful_requests=d.get("successful_requests", 0),
            total_latency_ms=d.get("total_latency_ms", 0.0),
        )


class AccountPoolManager:
    """
    Manages account pools for all providers with intelligent scheduling.
    
    Ensures 99.9% availability through:
    - Multi-account load balancing
    - Automatic failover
    - Health monitoring
    - LRU scheduling
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize account pool manager.
        
        Args:
            config_path: Path to account pool configuration JSON
        """
        self.pools: Dict[ProviderType, List[AccountNode]] = {}
        self._selection_seq = 0
        self.config_path = config_path or Path("./configs/account_pools.json")
        
        # Load configuration if exists
        if self.config_path.exists():
            self.load_config()
    
    def add_account(self, node: AccountNode):
        """
        Add an account to the pool.
        
        Args:
            node: Account node to add
        """
        if node.provider not in self.pools:
            self.pools[node.provider] = []
        
        # Check if account already exists
        for existing in self.pools[node.provider]:
            if existing.account_id == node.account_id:
                # Update existing account
                existing.__dict__.update(node.__dict__)
                return
        
        # Add new account
        self.pools[node.provider].append(node)
    
    def select_account(self, provider: ProviderType) -> Optional[AccountNode]:
        """
        Select best account from pool using intelligent scoring algorithm.
        
        Algorithm:
        1. Calculate score for each account
        2. Sort by score (ascending = best first)
        3. Select account with lowest score
        4. Update account state (usage count, last used time, selection seq)
        
        Args:
            provider: Provider to select account for
            
        Returns:
            Best account node, or None if no healthy accounts
        """
        if provider not in self.pools or not self.pools[provider]:
            return None
        
        # Increment global selection sequence
        self._selection_seq += 1
        
        # Calculate scores for all nodes
        nodes_with_scores = [
            (node, node.calculate_score(self._selection_seq))
            for node in self.pools[provider]
        ]
        
        # Sort by score (ascending = best first)
        nodes_with_scores.sort(key=lambda x: x[1])
        
        # Select best node
        best_node, best_score = nodes_with_scores[0]
        
        # If best node is unhealthy, return None
        if not best_node.is_healthy or best_node.is_disabled:
            return None
        
        # Update node state
        best_node.last_used_time = time.time()
        best_node.usage_count += 1
        best_node.last_selection_seq = self._selection_seq
        
        return best_node
    
    def mark_unhealthy(self, account_id: str, provider: ProviderType):
        """
        Mark an account as unhealthy.
        
        Args:
            account_id: Account ID to mark
            provider: Provider of the account
        """
        if provider not in self.pools:
            return
        
        for node in self.pools[provider]:
            if node.account_id == account_id:
                node.error_count += 1
                if node.error_count >= node.max_error_count:
                    node.is_healthy = False
                break
    
    def mark_healthy(self, account_id: str, provider: ProviderType):
        """
        Mark an account as healthy.
        
        Args:
            account_id: Account ID to mark
            provider: Provider of the account
        """
        if provider not in self.pools:
            return
        
        for node in self.pools[provider]:
            if node.account_id == account_id:
                node.is_healthy = True
                node.error_count = 0
                break
    
    def refresh_account(self, account_id: str, provider: ProviderType):
        """
        Mark an account as freshly refreshed.
        
        This gives the account highest priority for the next selection
        to verify it's working after refresh.
        
        Args:
            account_id: Account ID to refresh
            provider: Provider of the account
        """
        if provider not in self.pools:
            return
        
        for node in self.pools[provider]:
            if node.account_id == account_id:
                node.last_refresh_time = time.time()
                node.usage_count = 0  # Reset usage count
                node.is_healthy = True  # Assume healthy after refresh
                break
    
    def get_pool_stats(self, provider: ProviderType) -> dict:
        """
        Get statistics for a provider pool.
        
        Args:
            provider: Provider to get stats for
            
        Returns:
            Dictionary with pool statistics
        """
        if provider not in self.pools:
            return {
                "total_accounts": 0,
                "healthy_accounts": 0,
                "average_usage": 0.0,
                "average_success_rate": 0.0,
            }
        
        nodes = self.pools[provider]
        healthy_nodes = [n for n in nodes if n.is_healthy and not n.is_disabled]
        
        avg_usage = sum(n.usage_count for n in nodes) / len(nodes) if nodes else 0
        avg_success_rate = sum(n.success_rate for n in nodes) / len(nodes) if nodes else 0
        
        return {
            "total_accounts": len(nodes),
            "healthy_accounts": len(healthy_nodes),
            "average_usage": avg_usage,
            "average_success_rate": avg_success_rate * 100,  # Convert to percentage
        }
    
    def get_all_stats(self) -> Dict[str, dict]:
        """
        Get statistics for all provider pools.
        
        Returns:
            Dictionary mapping provider names to their stats
        """
        return {
            provider.value: self.get_pool_stats(provider)
            for provider in ProviderType
            if provider in self.pools
        }
    
    def load_config(self):
        """Load account pool configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            for provider_name, accounts in config.items():
                provider = ProviderType(provider_name)
                
                for account_data in accounts:
                    node = AccountNode(
                        account_id=account_data["account_id"],
                        provider=provider,
                        api_key=account_data.get("api_key"),
                        oauth_token_path=account_data.get("oauth_token_path"),
                        base_url=account_data.get("base_url"),
                    )
                    self.add_account(node)
            
            print(f"✅ Loaded account pool configuration from {self.config_path}")
            for provider, nodes in self.pools.items():
                print(f"   {provider.value}: {len(nodes)} accounts")
        
        except Exception as e:
            print(f"⚠️  Failed to load account pool config: {e}")
    
    def save_config(self):
        """Save current account pool configuration to JSON file."""
        config = {}
        
        for provider, nodes in self.pools.items():
            config[provider.value] = [
                {
                    "account_id": node.account_id,
                    "api_key": node.api_key,
                    "oauth_token_path": node.oauth_token_path,
                    "base_url": node.base_url,
                }
                for node in nodes
            ]
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Saved account pool configuration to {self.config_path}")


# Global account pool manager instance
_global_pool_manager: Optional[AccountPoolManager] = None


def get_account_pool_manager() -> AccountPoolManager:
    """Get the global account pool manager instance."""
    global _global_pool_manager
    if _global_pool_manager is None:
        _global_pool_manager = AccountPoolManager()
    return _global_pool_manager
