#!/usr/bin/env python3
"""
Fully Functional V98API LLM Client
Real connection to V98API with Claude and GPT support
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

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

class V98APILLMClient:
    """Fully functional LLM client with real V98API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("V98API_KEY", "YOUR_V98_API_KEY_HERE")
        self.claude_base_url = "https://v98store.com"
        self.gpt_base_url = "https://v98store.com/v1"
        
        self.claude_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        self.gpt_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_with_claude(self, message: str, max_tokens: int = 1000) -> APIResponse:
        """Send message to Claude Sonnet 4.5"""
        try:
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.claude_base_url}/v1/messages",
                headers=self.claude_headers,
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": message}]
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return APIResponse(
                status="success",
                model="claude-sonnet-4-5-20250929",
                provider="v98api",
                content=result['content'][0]['text'],
                tokens_used={
                    "input": result['usage']['input_tokens'],
                    "output": result['usage']['output_tokens'],
                    "total": result['usage']['input_tokens'] + result['usage']['output_tokens']
                },
                latency_ms=latency_ms,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return APIResponse(
                status="error",
                model="claude-sonnet-4-5-20250929",
                provider="v98api",
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def chat_with_gpt(self, message: str, max_tokens: int = 1000) -> APIResponse:
        """Send message to GPT-4o"""
        try:
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.gpt_base_url}/chat/completions",
                headers=self.gpt_headers,
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": message}],
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return APIResponse(
                status="success",
                model="gpt-4o",
                provider="v98api",
                content=result['choices'][0]['message']['content'],
                tokens_used={
                    "prompt": result['usage']['prompt_tokens'],
                    "completion": result['usage']['completion_tokens'],
                    "total": result['usage']['total_tokens']
                },
                latency_ms=latency_ms,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return APIResponse(
                status="error",
                model="gpt-4o",
                provider="v98api",
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "claude_base_url": self.claude_base_url,
            "gpt_base_url": self.gpt_base_url,
            "api_key_set": bool(self.api_key),
            "providers": ["claude-sonnet-4-5-20250929", "gpt-4o"],
            "status": "ready"
        }

# Global instance
_llm_client = None

def get_v98api_client() -> V98APILLMClient:
    """Get or create the V98API LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = V98APILLMClient()
    return _llm_client

if __name__ == "__main__":
    client = get_v98api_client()
    
    print("\n" + "="*100)
    print("V98API LLM CLIENT - STATUS")
    print("="*100 + "\n")
    print(json.dumps(client.get_status(), indent=2))
    
    print("\n" + "="*100)
    print("TESTING CLAUDE SONNET 4.5")
    print("="*100 + "\n")
    response = client.chat_with_claude("Hello Claude! What is 2+2?")
    print(f"Status: {response.status}")
    print(f"Model: {response.model}")
    print(f"Content: {response.content}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Latency: {response.latency_ms:.2f}ms")
    
    print("\n" + "="*100)
    print("TESTING GPT-4o")
    print("="*100 + "\n")
    response = client.chat_with_gpt("Hello GPT! What is 2+2?")
    print(f"Status: {response.status}")
    print(f"Model: {response.model}")
    print(f"Content: {response.content}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Latency: {response.latency_ms:.2f}ms")
    
    print("\n" + "="*100 + "\n")
