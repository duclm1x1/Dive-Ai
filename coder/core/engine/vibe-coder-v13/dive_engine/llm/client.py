"""
Dive Engine V2 - Real LLM Client
=================================

This module provides real LLM integration with multiple API providers:
- V98API (OpenAI, Claude, Gemini compatible)
- AICoding API (OpenAI compatible)

Features:
- Automatic provider selection and fallback
- Streaming support
- Token counting and budget tracking
- Rate limiting and retry logic
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union

try:
    from openai import AsyncOpenAI, OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Install with: pip install openai")


# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================

class Provider(Enum):
    """LLM API providers."""
    V98API = "v98api"
    AICODING = "aicoding"
    OPENAI = "openai"


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: Provider
    base_url: str
    api_key: str
    models: Dict[str, str]  # tier -> model_name
    enabled: bool = True
    priority: int = 0  # Higher priority = preferred
    max_retries: int = 3
    timeout: int = 120


# =============================================================================
# MODEL REGISTRY
# =============================================================================

class ModelRegistry:
    """
    Registry of available models with comprehensive model information.
    Supports all latest models including GPT-5.2 Pro, Claude 4.5, Codex, etc.
    """
    
    # Comprehensive model catalog
    MODELS = {
        # GPT-5 Series
        "gpt-5.2-pro": {"tier": "premium", "capabilities": ["reasoning", "thinking", "coding"]},
        "gpt-5.2": {"tier": "advanced", "capabilities": ["reasoning", "thinking"]},
        
        # GPT-4 Series
        "gpt-4.1": {"tier": "standard", "capabilities": ["general", "coding"]},
        "gpt-4.1-mini": {"tier": "fast", "capabilities": ["general", "fast"]},
        "gpt-4.1-nano": {"tier": "fast", "capabilities": ["general", "fast", "cheap"]},
        
        # Claude 4.5 Series
        "claude-opus-4.5": {"tier": "premium", "capabilities": ["reasoning", "thinking", "extended_thinking"]},
        "claude-sonnet-4.5": {"tier": "advanced", "capabilities": ["reasoning", "coding"]},
        "claude-3-opus": {"tier": "advanced", "capabilities": ["reasoning"]},
        "claude-3-sonnet": {"tier": "standard", "capabilities": ["general"]},
        
        # Gemini Series
        "gemini-2.5-flash": {"tier": "fast", "capabilities": ["general", "multimodal"]},
        "gemini-2.0-flash": {"tier": "fast", "capabilities": ["general"]},
        
        # Codex Series
        "codex-plus": {"tier": "advanced", "capabilities": ["coding", "specialized"]},
        "codex": {"tier": "standard", "capabilities": ["coding"]},
        
        # O-Series (Reasoning Models)
        "o1": {"tier": "premium", "capabilities": ["reasoning", "thinking"]},
        "o1-mini": {"tier": "advanced", "capabilities": ["reasoning", "thinking"]},
        "o3-mini": {"tier": "advanced", "capabilities": ["reasoning", "thinking", "advanced"]},
    }
    
    @classmethod
    def get_model_for_tier(cls, tier: str) -> str:
        """Get best model for a tier."""
        tier_mapping = {
            "tier_fast": "gpt-4.1-mini",
            "tier_think": "gpt-4.1",
            "tier_monitor": "gpt-4.1-mini",
            "tier_code": "codex",
            "tier_reasoning": "gpt-5.2",
            "tier_extended_thinking": "claude-opus-4.5",
        }
        return tier_mapping.get(tier, "gpt-4.1")
    
    @classmethod
    def list_models(cls, capability: Optional[str] = None) -> List[str]:
        """List available models, optionally filtered by capability."""
        if not capability:
            return list(cls.MODELS.keys())
        
        return [
            model_id for model_id, info in cls.MODELS.items()
            if capability in info["capabilities"]
        ]
    
    @classmethod
    def get_model_info(cls, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        return cls.MODELS.get(model_id)


# Default provider configurations
DEFAULT_PROVIDERS = [
    ProviderConfig(
        name=Provider.V98API,
        base_url="https://v98store.com/v1",
        api_key=os.getenv("V98API_KEY", "sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y"),
        models={
            "tier_fast": "gpt-4.1-mini",
            "tier_think": "gpt-4.1",
            "tier_monitor": "gpt-4.1-mini",
            "tier_code": "codex",
            "tier_reasoning": "gpt-5.2",
            "tier_extended_thinking": "claude-opus-4.5",
            "claude_opus": "claude-opus-4.5",
            "claude_sonnet": "claude-sonnet-4.5",
            "gemini": "gemini-2.5-flash",
            "codex": "codex-plus",
            "o1": "o1",
            "o3": "o3-mini",
        },
        priority=10,
    ),
    ProviderConfig(
        name=Provider.AICODING,
        base_url="https://aicoding.io.vn/v1",
        api_key=os.getenv("AICODING_API_KEY", "sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk"),
        models={
            "tier_fast": "gpt-4.1-mini",
            "tier_think": "gpt-4.1",
            "tier_monitor": "gpt-4.1-mini",
            "tier_code": "codex",
        },
        priority=5,
    ),
]


# =============================================================================
# LLM CLIENT
# =============================================================================

@dataclass
class LLMRequest:
    """A request to the LLM."""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    tier: str = "tier_think"
    max_tokens: int = 8000
    temperature: float = 0.7
    stream: bool = False
    thinking_budget: Optional[int] = None  # For reasoning models


@dataclass
class LLMResponse:
    """A response from the LLM."""
    content: str
    model: str
    provider: Provider
    usage: Dict[str, int] = field(default_factory=dict)
    thinking_content: Optional[str] = None
    latency_ms: int = 0
    finish_reason: str = "stop"


class LLMClient:
    """
    Real LLM client with multi-provider support.
    
    This client:
    - Automatically selects provider based on availability and priority
    - Handles fallback when primary provider fails
    - Tracks token usage and costs
    - Supports streaming responses
    """
    
    def __init__(
        self,
        providers: Optional[List[ProviderConfig]] = None,
        default_tier: str = "tier_think",
    ):
        """
        Initialize LLM client.
        
        Args:
            providers: List of provider configurations
            default_tier: Default model tier to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package required. Install with: pip install openai")
        
        self.providers = providers or DEFAULT_PROVIDERS
        self.default_tier = default_tier
        
        # Sort providers by priority (highest first)
        self.providers = sorted(self.providers, key=lambda p: p.priority, reverse=True)
        
        # Initialize OpenAI clients for each provider
        self.clients: Dict[Provider, OpenAI] = {}
        self.async_clients: Dict[Provider, AsyncOpenAI] = {}
        
        for provider in self.providers:
            if provider.enabled:
                self.clients[provider.name] = OpenAI(
                    base_url=provider.base_url,
                    api_key=provider.api_key,
                    timeout=provider.timeout,
                )
                self.async_clients[provider.name] = AsyncOpenAI(
                    base_url=provider.base_url,
                    api_key=provider.api_key,
                    timeout=provider.timeout,
                )
        
        # Model registry
        self.registry = ModelRegistry()
        
        # Usage tracking
        self.total_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0
    
    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        tier: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Synchronous LLM call.
        
        Args:
            prompt: User prompt
            system: System prompt
            tier: Model tier to use
            **kwargs: Additional arguments
            
        Returns:
            Response content
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        request = LLMRequest(
            messages=messages,
            tier=tier or self.default_tier,
            **kwargs
        )
        
        response = self._call_with_fallback(request)
        return response.content
    
    async def call_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        tier: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Asynchronous LLM call.
        
        Args:
            prompt: User prompt
            system: System prompt
            tier: Model tier to use
            **kwargs: Additional arguments
            
        Returns:
            Response content
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        request = LLMRequest(
            messages=messages,
            tier=tier or self.default_tier,
            **kwargs
        )
        
        response = await self._call_async_with_fallback(request)
        return response.content
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        tier: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream LLM response.
        
        Args:
            prompt: User prompt
            system: System prompt
            tier: Model tier to use
            **kwargs: Additional arguments
            
        Yields:
            Response chunks
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        request = LLMRequest(
            messages=messages,
            tier=tier or self.default_tier,
            stream=True,
            **kwargs
        )
        
        async for chunk in self._stream_with_fallback(request):
            yield chunk
    
    def _call_with_fallback(self, request: LLMRequest) -> LLMResponse:
        """Call LLM with automatic fallback."""
        last_error = None
        
        for provider in self.providers:
            if not provider.enabled:
                continue
            
            try:
                return self._call_provider(provider, request)
            except Exception as e:
                last_error = e
                print(f"Provider {provider.name.value} failed: {e}, trying next...")
                continue
        
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    async def _call_async_with_fallback(self, request: LLMRequest) -> LLMResponse:
        """Call LLM asynchronously with automatic fallback."""
        last_error = None
        
        for provider in self.providers:
            if not provider.enabled:
                continue
            
            try:
                return await self._call_provider_async(provider, request)
            except Exception as e:
                last_error = e
                print(f"Provider {provider.name.value} failed: {e}, trying next...")
                continue
        
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    async def _stream_with_fallback(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream LLM with automatic fallback."""
        last_error = None
        
        for provider in self.providers:
            if not provider.enabled:
                continue
            
            try:
                async for chunk in self._stream_provider(provider, request):
                    yield chunk
                return
            except Exception as e:
                last_error = e
                print(f"Provider {provider.name.value} failed: {e}, trying next...")
                continue
        
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    def _call_provider(self, provider: ProviderConfig, request: LLMRequest) -> LLMResponse:
        """Call a specific provider."""
        client = self.clients[provider.name]
        
        # Select model
        model = request.model or provider.models.get(request.tier, provider.models["tier_think"])
        
        # Make API call
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model,
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract response
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        
        # Update tracking
        self.total_tokens += usage["total_tokens"]
        self.call_count += 1
        
        return LLMResponse(
            content=content,
            model=model,
            provider=provider.name,
            usage=usage,
            latency_ms=latency_ms,
            finish_reason=response.choices[0].finish_reason,
        )
    
    async def _call_provider_async(
        self,
        provider: ProviderConfig,
        request: LLMRequest
    ) -> LLMResponse:
        """Call a specific provider asynchronously."""
        client = self.async_clients[provider.name]
        
        # Select model
        model = request.model or provider.models.get(request.tier, provider.models["tier_think"])
        
        # Make API call
        start_time = time.time()
        
        response = await client.chat.completions.create(
            model=model,
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract response
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        
        # Update tracking
        self.total_tokens += usage["total_tokens"]
        self.call_count += 1
        
        return LLMResponse(
            content=content,
            model=model,
            provider=provider.name,
            usage=usage,
            latency_ms=latency_ms,
            finish_reason=response.choices[0].finish_reason,
        )
    
    async def _stream_provider(
        self,
        provider: ProviderConfig,
        request: LLMRequest
    ) -> AsyncIterator[str]:
        """Stream from a specific provider."""
        client = self.async_clients[provider.name]
        
        # Select model
        model = request.model or provider.models.get(request.tier, provider.models["tier_think"])
        
        # Make streaming API call
        stream = await client.chat.completions.create(
            model=model,
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def list_models(self, capability: Optional[str] = None) -> List[str]:
        """List available models."""
        return self.registry.list_models(capability)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        return self.registry.get_model_info(model_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "call_count": self.call_count,
            "providers": [p.name.value for p in self.providers if p.enabled],
            "available_models": len(self.registry.MODELS),
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_llm_client(
    v98api_key: Optional[str] = None,
    aicoding_key: Optional[str] = None,
) -> LLMClient:
    """
    Create LLM client with custom API keys.
    
    Args:
        v98api_key: V98API key (uses default if None)
        aicoding_key: AICoding API key (uses default if None)
        
    Returns:
        Configured LLMClient
    """
    providers = []
    
    # V98API
    if v98api_key or DEFAULT_PROVIDERS[0].api_key:
        providers.append(ProviderConfig(
            name=Provider.V98API,
            base_url="https://v98store.com/v1",
            api_key=v98api_key or DEFAULT_PROVIDERS[0].api_key,
            models=DEFAULT_PROVIDERS[0].models,
            priority=10,
        ))
    
    # AICoding
    if aicoding_key or DEFAULT_PROVIDERS[1].api_key:
        providers.append(ProviderConfig(
            name=Provider.AICODING,
            base_url="https://aicoding.io.vn/v1",
            api_key=aicoding_key or DEFAULT_PROVIDERS[1].api_key,
            models=DEFAULT_PROVIDERS[1].models,
            priority=5,
        ))
    
    return LLMClient(providers=providers)


# =============================================================================
# CONVENIENCE WRAPPER
# =============================================================================

class SimpleLLMCaller:
    """Simple callable wrapper for LLMClient."""
    
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or create_llm_client()
    
    def __call__(self, prompt: str, system: str = "") -> str:
        """Call LLM with prompt and system message."""
        return self.client.call(prompt, system)
