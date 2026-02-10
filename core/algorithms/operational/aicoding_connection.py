"""
🔌 AICODING CONNECTION ALGORITHM
Comprehensive connection to AICoding.io.vn API

Features:
- OpenAI-compatible chat completions
- Anthropic native messages endpoint  
- Model listing and discovery
- Health monitoring
- Dual format support (OpenAI + Anthropic)
"""

import os
import sys
import requests
from typing import Dict, Any, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class AICodingConnectionAlgorithm(BaseAlgorithm):
    """
    AICoding Connection Algorithm
    
    Provides comprehensive connection to AICoding.io.vn API with:
    - OpenAI-compatible endpoints
    - Anthropic native format
    - Health checks
    - Model discovery
    """
    
    def __init__(self):
        """Initialize AICoding Connection Algorithm"""
        
        self.spec = AlgorithmSpec(
            algorithm_id="AICodingConnection",
            name="AICoding.io.vn Connection",
            level="operational",
            category="connection",
            version="1.0",
            description="Connect to AICoding.io.vn API with OpenAI and Anthropic format support",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "Action: connect, list_models, chat, messages, health"),
                    IOField("api_key", "string", False, "API key (uses AICODING_API_KEY env if not provided)"),
                    IOField("model", "string", False, "Model to use (default: gpt-4o)"),
                    IOField("messages", "array", False, "Messages array"),
                    IOField("temperature", "number", False, "Sampling temperature (default: 0.7)"),
                    IOField("max_tokens", "integer", False, "Max tokens (default: 2000)"),
                    IOField("format", "string", False, "Format: openai or anthropic (default: openai)")
                ],
                outputs=[
                    IOField("status", "string", True, "Connection status"),
                    IOField("models", "array", False, "Available models"),
                    IOField("response", "string", False, "API response"),
                    IOField("usage", "object", False, "Token usage stats")
                ]
            ),
            
            steps=[
                "1. Get API key from params or AICODING_API_KEY environment",
                "2. Validate API key format",
                "3. Create authenticated headers",
                "4. Execute requested action",
                "5. Return results with metadata"
            ],
            
            tags=["connection", "api", "aicoding", "openai", "anthropic"]
        )
        
        self.base_url = "https://aicoding.io.vn/v1"
        self.api_key = os.getenv("AICODING_API_KEY", "YOUR_AICODING_API_KEY_HERECJCk")
        self.headers = None
        self.available_models = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute AICoding connection action"""
        
        action = params.get("action", "connect")
        
        # Initialize connection
        api_key = params.get("api_key", self.api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"  # For Anthropic endpoints
        }
        
        print(f"\n🔌 AICoding Connection ({action})")
        
        if action == "connect":
            return self._connect()
        elif action == "list_models":
            return self._list_models()
        elif action == "chat":
            return self._chat_openai(params)
        elif action == "messages":
            return self._messages_anthropic(params)
        elif action == "health":
            return self._health_check()
        else:
            return AlgorithmResult(
                status="error",
                error=f"Unknown action: {action}"
            )
    
    def _connect(self) -> AlgorithmResult:
        """Test connection and load models"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.available_models = [
                model.get("id", "") for model in data.get("data", [])
            ]
            
            print(f"   ✅ Connected! Found {len(self.available_models)} models")
            print(f"   📋 Sample models: {self.available_models[:5]}")
            
            return AlgorithmResult(
                status="success",
                data={
                    "connection_status": "connected",
                    "total_models": len(self.available_models),
                    "api_url": self.base_url,
                    "endpoints": {
                        "health": "/health",
                        "models": "/v1/models",
                        "chat": "/v1/chat/completions",
                        "messages": "/v1/messages"
                    }
                },
                metadata={
                    "models_count": len(self.available_models)
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Connection failed: {str(e)}"
            )
    
    def _list_models(self) -> AlgorithmResult:
        """List all available models"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("id", "") for model in data.get("data", [])]
            
            print(f"   📋 Found {len(models)} models")
            if models:
                print(f"   Sample: {models[:10]}")
            
            return AlgorithmResult(
                status="success",
                data={
                    "models": models,
                    "count": len(models)
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Failed to list models: {str(e)}"
            )
    
    def _chat_openai(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Send OpenAI-format chat completion request"""
        messages = params.get("messages", [])
        model = params.get("model", "gpt-4o")
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 2000)
        
        if not messages:
            return AlgorithmResult(
                status="error",
                error="No messages provided"
            )
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            
            print(f"   ✅ Response received ({usage.get('total_tokens', 0)} tokens)")
            
            return AlgorithmResult(
                status="success",
                data={
                    "response": content,
                    "model": data.get("model", model),
                    "usage": usage,
                    "finish_reason": data.get("choices", [{}])[0].get("finish_reason", ""),
                    "format": "openai"
                },
                metadata={
                    "tokens_used": usage.get("total_tokens", 0)
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Chat request failed: {str(e)}"
            )
    
    def _messages_anthropic(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Send Anthropic-format messages request"""
        messages = params.get("messages", [])
        model = params.get("model", "claude-opus-4-6")
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 2000)
        
        if not messages:
            return AlgorithmResult(
                status="error",
                error="No messages provided"
            )
        
        try:
            # Anthropic native format
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "")
            usage = data.get("usage", {})
            
            print(f"   ✅ Response received ({usage.get('input_tokens', 0) + usage.get('output_tokens', 0)} tokens)")
            
            return AlgorithmResult(
                status="success",
                data={
                    "response": content,
                    "model": data.get("model", model),
                    "usage": {
                        "prompt_tokens": usage.get("input_tokens", 0),
                        "completion_tokens": usage.get("output_tokens", 0),
                        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                    },
                    "stop_reason": data.get("stop_reason", ""),
                    "format": "anthropic"
                },
                metadata={
                    "tokens_used": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Messages request failed: {str(e)}"
            )
    
    def _health_check(self) -> AlgorithmResult:
        """Check AICoding API health"""
        try:
            response = requests.get(
                f"{self.base_url.replace('/v1', '')}/health",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"   ✅ API is healthy")
                return AlgorithmResult(
                    status="success",
                    data={
                        "health": "healthy",
                        "status_code": 200,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                )
            else:
                return AlgorithmResult(
                    status="degraded",
                    data={
                        "health": "degraded",
                        "status_code": response.status_code
                    }
                )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Health check failed: {str(e)}"
            )


def register(algorithm_manager):
    """Register AICoding Connection Algorithm"""
    try:
        algo = AICodingConnectionAlgorithm()
        algorithm_manager.register("AICodingConnection", algo)
        print("✅ AICodingConnection Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register AICodingConnection: {e}")
