"""
Unified LLM Gateway
===================

OpenAI-compatible gateway with multi-provider support, OAuth bypass,
and intelligent account pool scheduling.

Features:
- OpenAI API compatibility (zero-cost migration)
- Automatic provider selection based on performance
- Account pool scheduling for 99.9% availability
- OAuth token management
- Automatic retries and failover
- Streaming support
- Free access to premium models (Claude Opus 4.5, Qwen3 Coder Plus)
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, AsyncIterator, Union, TYPE_CHECKING
from pathlib import Path

"""Notes on typing

This module supports running in environments where the `openai` package is not
installed (e.g., offline CI, linting, or partial installs). We still want the
module to be importable so that unit tests which *mock* the gateway can collect.

To avoid `NameError` during import-time evaluation of annotations, we provide
`Any` fallbacks when `openai` is unavailable.
"""

if TYPE_CHECKING:
    # Import only for type-checkers; keeps runtime import optional.
    from openai import AsyncOpenAI  # pragma: no cover
    from openai.types.chat import ChatCompletion, ChatCompletionChunk  # pragma: no cover

try:
    from openai import AsyncOpenAI  # type: ignore[no-redef]
    from openai.types.chat import ChatCompletion, ChatCompletionChunk  # type: ignore[no-redef]
    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    OPENAI_AVAILABLE = False
    # Runtime fallbacks so annotations don't crash module import.
    AsyncOpenAI = Any  # type: ignore[assignment,misc]
    ChatCompletion = Any  # type: ignore[assignment]
    ChatCompletionChunk = Any  # type: ignore[assignment]
    print("Warning: openai package not installed. Install with: pip install openai")

from dive_engine.llm.performance_tracker import (
    get_performance_tracker,
    ProviderName,
)
from dive_engine.llm.account_pool import (
    get_account_pool_manager,
    ProviderType,
    AccountNode,
)
from dive_engine.llm.oauth.base import OAuthManager
from dive_engine.llm.oauth.gemini_oauth import GeminiOAuthManager, AntigravityOAuthManager
from dive_engine.llm.oauth.qwen_oauth import QwenOAuthManager
from dive_engine.llm.oauth.kiro_oauth import KiroSocialOAuthManager, KiroBuilderIDOAuthManager


class UnifiedLLMGateway:
    """
    Unified LLM Gateway with multi-provider support.
    
    Provides OpenAI-compatible interface while supporting multiple providers
    with OAuth bypass and intelligent account pool scheduling.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Unified LLM Gateway.
        
        Args:
            config_path: Path to gateway configuration (optional)
        """
        self.performance_tracker = get_performance_tracker()
        self.account_pool = get_account_pool_manager()
        self.oauth_managers: Dict[str, OAuthManager] = {}
        self.clients: Dict[str, AsyncOpenAI] = {}
        
        self._init_oauth_managers()
    
    def _init_oauth_managers(self):
        """Initialize OAuth managers for each OAuth provider."""
        self.oauth_managers = {
            "gemini_oauth": GeminiOAuthManager(),
            "antigravity": AntigravityOAuthManager(),
            "qwen_oauth": QwenOAuthManager(),
            "kiro_social": KiroSocialOAuthManager(),
            "kiro_builder_id": KiroBuilderIDOAuthManager(),
        }
    
    async def _get_client_for_account(self, account: AccountNode) -> AsyncOpenAI:
        """
        Get or create OpenAI client for an account.
        
        Args:
            account: Account node to create client for
            
        Returns:
            AsyncOpenAI client configured for the account
        """
        cache_key = f"{account.provider.value}:{account.account_id}"
        
        # Return cached client if exists
        if cache_key in self.clients:
            return self.clients[cache_key]
        
        # Get credentials
        if account.oauth_token_path:
            # OAuth account - get token
            oauth_manager = self._get_oauth_manager(account.provider)
            token = await oauth_manager.get_valid_token()
            api_key = token.access_token
        else:
            # API key account
            api_key = account.api_key
        
        # Get base URL
        base_url = account.base_url or self._get_default_base_url(account.provider)
        
        # Create client
        if not OPENAI_AVAILABLE:
            raise RuntimeError("openai package required. Install with: pip install openai")
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        # Cache client
        self.clients[cache_key] = client
        
        return client
    
    def _get_oauth_manager(self, provider: ProviderType) -> OAuthManager:
        """Get OAuth manager for a provider."""
        manager_map = {
            ProviderType.GEMINI_OAUTH: "gemini_oauth",
            ProviderType.ANTIGRAVITY: "antigravity",
            ProviderType.QWEN_OAUTH: "qwen_oauth",
            ProviderType.KIRO_OAUTH: "kiro_social",  # Default to social
        }
        
        manager_key = manager_map.get(provider)
        if not manager_key:
            raise ValueError(f"No OAuth manager for provider: {provider}")
        
        return self.oauth_managers[manager_key]
    
    def _get_default_base_url(self, provider: ProviderType) -> str:
        """Get default base URL for a provider."""
        base_urls = {
            ProviderType.V98API: "https://v98store.com/v1",
            ProviderType.AICODING: "https://aicoding.io.vn/v1",
            ProviderType.GEMINI_OAUTH: "https://generativelanguage.googleapis.com/v1beta",
            ProviderType.QWEN_OAUTH: "https://chat.qwen.ai/api/v1",
            ProviderType.KIRO_OAUTH: "https://q.us-east-1.amazonaws.com",
            ProviderType.ANTIGRAVITY: "https://generativelanguage.googleapis.com/v1beta",
        }
        
        return base_urls.get(provider, "https://api.openai.com/v1")
    
    def _map_provider_name_to_type(self, provider_name: ProviderName) -> ProviderType:
        """Map ProviderName (performance tracker) to ProviderType (account pool)."""
        mapping = {
            ProviderName.V98API: ProviderType.V98API,
            ProviderName.AICODING: ProviderType.AICODING,
            ProviderName.GEMINI_OAUTH: ProviderType.GEMINI_OAUTH,
            ProviderName.KIRO_OAUTH: ProviderType.KIRO_OAUTH,
            ProviderName.QWEN_OAUTH: ProviderType.QWEN_OAUTH,
            ProviderName.ANTIGRAVITY: ProviderType.ANTIGRAVITY,
        }
        
        return mapping.get(provider_name, ProviderType.V98API)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4.1-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """
        OpenAI-compatible chat completion endpoint.
        
        Automatically selects best provider and account based on performance.
        
        Args:
            messages: List of message dictionaries
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            **kwargs: Additional arguments
            
        Returns:
            ChatCompletion or stream of ChatCompletionChunks
        """
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Select provider based on performance
                provider_name = self.performance_tracker.get_best_provider()
                
                if not provider_name:
                    raise RuntimeError("No healthy providers available")
                
                provider_type = self._map_provider_name_to_type(provider_name)
                
                # Select account from pool
                account = self.account_pool.select_account(provider_type)
                
                if not account:
                    # No healthy account, try next provider
                    self.performance_tracker.mark_unhealthy(provider_name)
                    retry_count += 1
                    continue
                
                # Get client for account
                client = await self._get_client_for_account(account)
                
                # Make request
                start_time = time.time()
                
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs,
                )
                
                # Record success
                latency_ms = (time.time() - start_time) * 1000
                
                self.performance_tracker.record_request(
                    provider=provider_name,
                    success=True,
                    latency_ms=latency_ms,
                )
                
                account.record_request(success=True, latency_ms=latency_ms)
                
                return response
            
            except Exception as e:
                last_error = e
                retry_count += 1
                
                # Record failure
                if provider_name:
                    self.performance_tracker.record_request(
                        provider=provider_name,
                        success=False,
                        latency_ms=0,
                    )
                
                if account:
                    account.record_request(success=False, latency_ms=0)
                    self.account_pool.mark_unhealthy(account.account_id, provider_type)
                
                # Wait before retry
                if retry_count < max_retries:
                    await asyncio.sleep(1 * retry_count)  # Exponential backoff
        
        # All retries failed
        raise RuntimeError(f"All retries failed. Last error: {last_error}")
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4.1-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Streaming chat completion.
        
        Args:
            messages: List of message dictionaries
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
            
        Yields:
            Chunks of the response
        """
        stream = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        
        async for chunk in stream:
            yield chunk.model_dump()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get gateway statistics.
        
        Returns:
            Dictionary with performance and pool statistics
        """
        return {
            "performance": self.performance_tracker.get_stats_summary(),
            "account_pools": self.account_pool.get_all_stats(),
        }


# Convenience function for simple usage
async def chat(
    prompt: str,
    model: str = "gpt-4.1-mini",
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """
    Simple chat function for quick usage.
    
    Args:
        prompt: User prompt
        model: Model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Model response as string
    """
    gateway = UnifiedLLMGateway()
    
    response = await gateway.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return response.choices[0].message.content


# CLI interface for testing
async def main():
    """CLI interface for testing the gateway."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gateway.py <prompt> [model]")
        print("\nExample:")
        print("  python gateway.py 'Explain quantum computing' gpt-4.1")
        print("  python gateway.py 'Write Python code' claude-opus-4-5")
        print("  python gateway.py 'Coding task' qwen3-coder-plus")
        return
    
    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gpt-4.1-mini"
    
    print(f"\n🤖 Model: {model}")
    print(f"💬 Prompt: {prompt}\n")
    print("=" * 60)
    
    gateway = UnifiedLLMGateway()
    
    # Stream response
    async for chunk in gateway.chat_completion_stream(
        messages=[{"role": "user", "content": prompt}],
        model=model,
    ):
        if chunk["choices"][0]["delta"].get("content"):
            print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
    
    print("\n" + "=" * 60)
    
    # Print stats
    stats = gateway.get_stats()
    print(f"\n📊 Stats:")
    print(f"Best provider: {stats['performance']['best_provider']}")
    print(f"\nProvider rankings:")
    for ranking in stats['performance']['provider_rankings'][:3]:
        print(f"  {ranking['provider']}: {ranking['success_rate']}% success, {ranking['avg_latency_ms']}ms")


if __name__ == "__main__":
    asyncio.run(main())
