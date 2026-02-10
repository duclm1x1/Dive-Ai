"""
Dive AI V29.4 - LLM Connection System
Only V98 and AICoding with Claude Opus 4.6
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, AsyncIterator
from enum import Enum
import aiohttp
import asyncio
import time
import os


class TaskType(Enum):
    """Types of tasks for routing"""
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    VISION = "vision"
    AUTOMATION = "automation"


@dataclass
class LLMResponse:
    """Standard response from any LLM"""
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: float
    thinking: Optional[str] = None
    metadata: Dict[str, Any] = None


class BaseLLMClient(ABC):
    """Base class for all LLM connections"""
    
    def __init__(self, name: str, api_key: str, base_url: str, model: str):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.is_healthy = True
        self.request_count = 0
        self.error_count = 0
        self.last_used = 0
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Send chat request"""
        pass
    
    @abstractmethod
    async def stream(self, messages: List[Dict], **kwargs) -> AsyncIterator[str]:
        """Stream response"""
        pass
    
    async def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            response = await self.chat([{"role": "user", "content": "ping"}], max_tokens=10)
            self.is_healthy = True
            return True
        except Exception as e:
            self.is_healthy = False
            self.error_count += 1
            return False


# ============================================================
# V98 Claude 4.6 Opus Connection
# ============================================================

class V98Claude46Opus(BaseLLMClient):
    """V98 API - Claude 4.6 Opus Thinking"""
    
    PROVIDER = "v98"
    MODEL = "claude-sonnet-4-20250514"
    BASE_URL = "https://api.v98.chat/v1"
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("V98_API_KEY", "")
        super().__init__(
            name="v98_claude_4_6_opus",
            api_key=api_key,
            base_url=self.BASE_URL,
            model=self.MODEL
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Send chat to V98 Claude 4.6"""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 8192),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"V98 API error: {resp.status} - {error_text}")
                
                data = await resp.json()
                latency = (time.time() - start_time) * 1000
                
                self.request_count += 1
                self.last_used = time.time()
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=self.model,
                    provider=self.PROVIDER,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    latency_ms=latency,
                    thinking=data.get("thinking"),
                    metadata={"id": data.get("id")}
                )
    
    async def stream(self, messages: List[Dict], **kwargs) -> AsyncIterator[str]:
        """Stream response from V98"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 8192),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except:
                            pass


# ============================================================
# AICoding Claude 4.6 Opus Connection
# ============================================================

class AICodingClaude46Opus(BaseLLMClient):
    """AICoding API - Claude 4.6 Opus"""
    
    PROVIDER = "aicoding"
    MODEL = "claude-sonnet-4-20250514"
    BASE_URL = "https://api.aicoding.io/v1"
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("AICODING_API_KEY", "")
        super().__init__(
            name="aicoding_claude_4_6_opus",
            api_key=api_key,
            base_url=self.BASE_URL,
            model=self.MODEL
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Send chat to AICoding Claude 4.6"""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 8192),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"AICoding API error: {resp.status} - {error_text}")
                
                data = await resp.json()
                latency = (time.time() - start_time) * 1000
                
                self.request_count += 1
                self.last_used = time.time()
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=self.model,
                    provider=self.PROVIDER,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    latency_ms=latency,
                    metadata={"id": data.get("id")}
                )
    
    async def stream(self, messages: List[Dict], **kwargs) -> AsyncIterator[str]:
        """Stream response from AICoding"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 8192),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except:
                            pass


# ============================================================
# Connection Manager
# ============================================================

class LLMConnectionManager:
    """
    Manages V98 and AICoding connections with Claude 4.6
    - Primary: V98 Claude 4.6 Opus
    - Backup: AICoding Claude 4.6 Opus
    """
    
    def __init__(self, v98_key: str = None, aicoding_key: str = None):
        self.v98 = V98Claude46Opus(v98_key)
        self.aicoding = AICodingClaude46Opus(aicoding_key)
        
        # Failover chain: V98 -> AICoding
        self.primary = self.v98
        self.backup = self.aicoding
        
        self.stats = {
            "total_requests": 0,
            "v98_requests": 0,
            "aicoding_requests": 0,
            "failovers": 0,
            "errors": 0
        }
    
    async def chat(self, messages: List[Dict], 
                   prefer: str = "v98",
                   **kwargs) -> LLMResponse:
        """
        Send chat with automatic failover
        
        Args:
            messages: Chat messages
            prefer: "v98" or "aicoding"
        """
        self.stats["total_requests"] += 1
        
        # Select primary based on preference
        if prefer == "aicoding":
            primary, backup = self.aicoding, self.v98
        else:
            primary, backup = self.v98, self.aicoding
        
        # Try primary
        try:
            if primary.is_healthy:
                response = await primary.chat(messages, **kwargs)
                if prefer == "v98":
                    self.stats["v98_requests"] += 1
                else:
                    self.stats["aicoding_requests"] += 1
                return response
        except Exception as e:
            primary.is_healthy = False
            self.stats["failovers"] += 1
            print(f"⚠️ {primary.name} failed: {e}, trying backup...")
        
        # Try backup
        try:
            response = await backup.chat(messages, **kwargs)
            if backup.name == "v98_claude_4_6_opus":
                self.stats["v98_requests"] += 1
            else:
                self.stats["aicoding_requests"] += 1
            return response
        except Exception as e:
            self.stats["errors"] += 1
            raise Exception(f"All LLM connections failed: {e}")
    
    async def stream(self, messages: List[Dict], 
                     prefer: str = "v98",
                     **kwargs) -> AsyncIterator[str]:
        """Stream with automatic failover"""
        if prefer == "aicoding":
            primary, backup = self.aicoding, self.v98
        else:
            primary, backup = self.v98, self.aicoding
        
        try:
            if primary.is_healthy:
                async for chunk in primary.stream(messages, **kwargs):
                    yield chunk
                return
        except Exception as e:
            primary.is_healthy = False
            print(f"⚠️ {primary.name} stream failed, trying backup...")
        
        async for chunk in backup.stream(messages, **kwargs):
            yield chunk
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connections"""
        return {
            "v98": await self.v98.health_check(),
            "aicoding": await self.aicoding.health_check()
        }
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            **self.stats,
            "v98_healthy": self.v98.is_healthy,
            "aicoding_healthy": self.aicoding.is_healthy,
            "v98_request_count": self.v98.request_count,
            "aicoding_request_count": self.aicoding.request_count
        }


# ============================================================
# Utility Functions
# ============================================================

def create_manager(v98_key: str = None, aicoding_key: str = None) -> LLMConnectionManager:
    """Create a new LLM connection manager"""
    return LLMConnectionManager(v98_key, aicoding_key)


async def quick_chat(message: str, provider: str = "v98") -> str:
    """Quick chat helper"""
    manager = create_manager()
    response = await manager.chat(
        [{"role": "user", "content": message}],
        prefer=provider
    )
    return response.content


# ============================================================
# Test
# ============================================================

async def test_connections():
    """Test both connections"""
    manager = create_manager()
    
    print("🔍 Testing LLM connections...")
    
    # Health check
    health = await manager.health_check()
    print(f"   V98: {'✅' if health['v98'] else '❌'}")
    print(f"   AICoding: {'✅' if health['aicoding'] else '❌'}")
    
    # Test chat
    if any(health.values()):
        response = await manager.chat([
            {"role": "user", "content": "Say 'Hello from Dive AI V29.4!' in one line"}
        ])
        print(f"   Response: {response.content[:100]}...")
        print(f"   Provider: {response.provider}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
    
    print(f"\n📊 Stats: {manager.get_stats()}")


if __name__ == "__main__":
    asyncio.run(test_connections())
