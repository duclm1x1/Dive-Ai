#!/usr/bin/env python3
"""
Unified LLM Client - Supporting Both V98API and AICoding
Equal providers with automatic failover and parallel execution
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from anthropic import Anthropic
except ImportError:
    os.system("pip3 install anthropic")
    from anthropic import Anthropic

class Provider(Enum):
    """LLM Providers"""
    V98API = "v98api"
    AICODING = "aicoding"

@dataclass
class APIResponse:
    """API Response wrapper"""
    status: str
    model: str
    provider: str
    content: Optional[str] = None
    tokens_used: Optional[Dict[str, int]] = None
    latency_ms: float = 0.0
    error: Optional[str] = None
    timestamp: str = ""

class UnifiedLLMClient:
    """Unified LLM Client supporting both V98API and AICoding"""
    
    def __init__(self):
        # V98API Configuration
        self.v98api_key = os.getenv("V98API_KEY", "sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y")
        self.v98api_base_url = "https://v98store.com"
        
        # AICoding Configuration
        self.aicoding_key = os.getenv("AICODING_API_KEY", "sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk")
        self.aicoding_base_url = "https://aicoding.io.vn"
        
        # Initialize both clients
        self.v98api_client = Anthropic(
            api_key=self.v98api_key,
            base_url=self.v98api_base_url
        )
        
        self.aicoding_client = Anthropic(
            api_key=self.aicoding_key,
            base_url=self.aicoding_base_url
        )
        
        self.provider_stats = {
            Provider.V98API: {"requests": 0, "successes": 0, "failures": 0, "avg_latency": 0},
            Provider.AICODING: {"requests": 0, "successes": 0, "failures": 0, "avg_latency": 0}
        }
    
    def chat_with_claude_sonnet(self, message: str, max_tokens: int = 1000, 
                                provider: Optional[Provider] = None) -> APIResponse:
        """Send message to Claude Sonnet 4.5 (Orchestrator)"""
        
        # If no provider specified, use both in parallel and return the faster one
        if provider is None:
            responses = []
            for prov in [Provider.V98API, Provider.AICODING]:
                try:
                    resp = self._send_sonnet_message(message, max_tokens, prov)
                    responses.append(resp)
                except:
                    pass
            
            if responses:
                # Return the fastest response
                return min(responses, key=lambda x: x.latency_ms)
            else:
                return APIResponse(
                    status="error",
                    model="claude-sonnet-4-5-20250929",
                    provider="all",
                    error="All providers failed",
                    timestamp=datetime.now().isoformat()
                )
        else:
            return self._send_sonnet_message(message, max_tokens, provider)
    
    def _send_sonnet_message(self, message: str, max_tokens: int, 
                            provider: Provider) -> APIResponse:
        """Internal method to send message to Sonnet"""
        try:
            start_time = datetime.now()
            
            client = self.v98api_client if provider == Provider.V98API else self.aicoding_client
            
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": message}]
            )
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update stats
            self.provider_stats[provider]["requests"] += 1
            self.provider_stats[provider]["successes"] += 1
            self.provider_stats[provider]["avg_latency"] = (
                (self.provider_stats[provider]["avg_latency"] * 
                 (self.provider_stats[provider]["successes"] - 1) + latency_ms) /
                self.provider_stats[provider]["successes"]
            )
            
            return APIResponse(
                status="success",
                model="claude-sonnet-4-5-20250929",
                provider=provider.value,
                content=response.content[0].text,
                tokens_used={
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                },
                latency_ms=latency_ms,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            self.provider_stats[provider]["requests"] += 1
            self.provider_stats[provider]["failures"] += 1
            
            return APIResponse(
                status="error",
                model="claude-sonnet-4-5-20250929",
                provider=provider.value,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def chat_with_claude_opus(self, message: str, max_tokens: int = 1000,
                             provider: Optional[Provider] = None) -> APIResponse:
        """Send message to Claude Opus 4.5 (Agents)"""
        
        if provider is None:
            responses = []
            for prov in [Provider.V98API, Provider.AICODING]:
                try:
                    resp = self._send_opus_message(message, max_tokens, prov)
                    responses.append(resp)
                except:
                    pass
            
            if responses:
                return min(responses, key=lambda x: x.latency_ms)
            else:
                return APIResponse(
                    status="error",
                    model="claude-opus-4-5-20251101",
                    provider="all",
                    error="All providers failed",
                    timestamp=datetime.now().isoformat()
                )
        else:
            return self._send_opus_message(message, max_tokens, provider)
    
    def _send_opus_message(self, message: str, max_tokens: int,
                          provider: Provider) -> APIResponse:
        """Internal method to send message to Opus"""
        try:
            start_time = datetime.now()
            
            client = self.v98api_client if provider == Provider.V98API else self.aicoding_client
            
            response = client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": message}]
            )
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update stats
            self.provider_stats[provider]["requests"] += 1
            self.provider_stats[provider]["successes"] += 1
            self.provider_stats[provider]["avg_latency"] = (
                (self.provider_stats[provider]["avg_latency"] * 
                 (self.provider_stats[provider]["successes"] - 1) + latency_ms) /
                self.provider_stats[provider]["successes"]
            )
            
            return APIResponse(
                status="success",
                model="claude-opus-4-5-20251101",
                provider=provider.value,
                content=response.content[0].text,
                tokens_used={
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                },
                latency_ms=latency_ms,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            self.provider_stats[provider]["requests"] += 1
            self.provider_stats[provider]["failures"] += 1
            
            return APIResponse(
                status="error",
                model="claude-opus-4-5-20251101",
                provider=provider.value,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "providers": {
                "v98api": {
                    "base_url": self.v98api_base_url,
                    "status": "ready"
                },
                "aicoding": {
                    "base_url": self.aicoding_base_url,
                    "status": "ready"
                }
            },
            "models": {
                "orchestrator": "claude-sonnet-4-5-20250929",
                "agents": "claude-opus-4-5-20251101"
            },
            "provider_stats": {
                "v98api": self.provider_stats[Provider.V98API],
                "aicoding": self.provider_stats[Provider.AICODING]
            },
            "status": "ready"
        }

# Global instance
_llm_client = None

def get_unified_client() -> UnifiedLLMClient:
    """Get or create the unified LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = UnifiedLLMClient()
    return _llm_client

if __name__ == "__main__":
    import json
    
    client = get_unified_client()
    
    print("\n" + "="*100)
    print("UNIFIED LLM CLIENT - STATUS")
    print("="*100 + "\n")
    print(json.dumps(client.get_status(), indent=2))
    
    print("\n" + "="*100)
    print("TESTING CLAUDE SONNET 4.5 (Orchestrator) - PARALLEL BOTH PROVIDERS")
    print("="*100 + "\n")
    response = client.chat_with_claude_sonnet("Hello! What is 2+2?")
    print(f"Status: {response.status}")
    print(f"Model: {response.model}")
    print(f"Provider Used: {response.provider}")
    print(f"Content: {response.content}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Latency: {response.latency_ms:.2f}ms")
    
    print("\n" + "="*100)
    print("TESTING CLAUDE OPUS 4.5 (Agents) - PARALLEL BOTH PROVIDERS")
    print("="*100 + "\n")
    response = client.chat_with_claude_opus("Hello! What is 2+2?")
    print(f"Status: {response.status}")
    print(f"Model: {response.model}")
    print(f"Provider Used: {response.provider}")
    print(f"Content: {response.content}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Latency: {response.latency_ms:.2f}ms")
    
    print("\n" + "="*100 + "\n")
