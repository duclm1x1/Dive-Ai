"""
🔌 ENHANCED V98 CONNECTION ALGORITHM
Comprehensive connection to V98Store API supporting all available models

Features:
- Auto-discovery of all 475+ available models
- OpenAI-compatible chat completions
- Model categorization (Claude, GPT, Gemini, etc.)
- Health checks and connection validation
- Token usage tracking
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


class V98ConnectionAlgorithm(BaseAlgorithm):
    """
    Enhanced V98 Connection Algorithm
    
    Provides comprehensive connection to V98Store API with:
    - All 475+ models support
    - OpenAI-compatible endpoints
    - Model categorization and filtering
    - Health monitoring
    """
    
    def __init__(self):
        """Initialize V98 Connection Algorithm"""
        
        self.spec = AlgorithmSpec(
            algorithm_id="V98Connection",
            name="V98 Store Connection (Enhanced)",
            level="operational",
            category="connection",
            version="2.0",
            description="Comprehensive V98Store API connection supporting all models, health checks, and OpenAI-compatible endpoints",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "Action: connect, list_models, chat, health"),
                    IOField("api_key", "string", False, "V98 API key (uses V98_API_KEY env if not provided)"),
                    IOField("model", "string", False, "Model to use (default: gpt-4o)"),
                    IOField("messages", "array", False, "Chat messages (for chat action)"),
                    IOField("temperature", "number", False, "Sampling temperature (default: 0.7)"),
                    IOField("max_tokens", "integer", False, "Max tokens (default: 2000)"),
                    IOField("filter_by", "string", False, "Filter models by name pattern")
                ],
                outputs=[
                    IOField("status", "string", True, "Connection status"),
                    IOField("models", "array", False, "Available models"),
                    IOField("response", "string", False, "API response"),
                    IOField("usage", "object", False, "Token usage stats")
                ]
            ),
            
            steps=[
                "1. Get API key from params or V98_API_KEY environment",
                "2. Validate API key format",
                "3. Create authenticated headers",
                "4. Execute requested action (connect/list/chat/health)",
                "5. Return results with metadata"
            ],
            
            tags=["connection", "api", "v98", "all-models", "openai-compatible"]
        )
        
        self.base_url = "https://v98store.com/v1"
        self.api_key = os.getenv("V98_API_KEY", "YOUR_V98_API_KEY_HERE")
        self.headers = None
        self.available_models = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute V98 connection action"""
        
        action = params.get("action", "connect")
        
        # Initialize connection
        api_key = params.get("api_key", self.api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"\n🔌 V98 Connection ({action})")
        
        if action == "connect":
            return self._connect()
        elif action == "list_models":
            return self._list_models(params.get("filter_by"))
        elif action == "chat":
            return self._chat(params)
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
            
            # Categorize models
            categories = self._categorize_models(self.available_models)
            
            print(f"   ✅ Connected! Found {len(self.available_models)} models")
            print(f"   📊 Categories: {list(categories.keys())}")
            
            return AlgorithmResult(
                status="success",
                data={
                    "connection_status": "connected",
                    "total_models": len(self.available_models),
                    "categories": categories,
                    "api_url": self.base_url
                },
                metadata={
                    "models_count": len(self.available_models),
                    "category_count": len(categories)
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Connection failed: {str(e)}"
            )
    
    def _list_models(self, filter_by: Optional[str] = None) -> AlgorithmResult:
        """List all available models with optional filtering"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("id", "") for model in data.get("data", [])]
            
            # Apply filter if provided
            if filter_by:
                models = [m for m in models if filter_by.lower() in m.lower()]
            
            print(f"   📋 Found {len(models)} models" + (f" matching '{filter_by}'" if filter_by else ""))
            if models:
                print(f"   Top 10: {models[:10]}")
            
            return AlgorithmResult(
                status="success",
                data={
                    "models": models,
                    "count": len(models),
                    "filter": filter_by
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(
                status="error",
                error=f"Failed to list models: {str(e)}"
            )
    
    def _chat(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Send chat completion request"""
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
                    "finish_reason": data.get("choices", [{}])[0].get("finish_reason", "")
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
    
    def _health_check(self) -> AlgorithmResult:
        """Check V98 API health"""
        try:
            # Test models endpoint as health check
            response = requests.get(
                f"{self.base_url}/models",
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
    
    def _categorize_models(self, models: List[str]) -> Dict[str, int]:
        """Categorize models by provider/type"""
        categories = {
            "claude": 0,
            "gpt": 0,
            "gemini": 0,
            "glm": 0,
            "o-series": 0,
            "codex": 0,
            "other": 0
        }
        
        for model in models:
            model_lower = model.lower()
            if "claude" in model_lower:
                categories["claude"] += 1
            elif "gpt" in model_lower:
                categories["gpt"] += 1
            elif "gemini" in model_lower:
                categories["gemini"] += 1
            elif "glm" in model_lower:
                categories["glm"] += 1
            elif model_lower.startswith("o"):
                categories["o-series"] += 1
            elif "codex" in model_lower:
                categories["codex"] += 1
            else:
                categories["other"] += 1
        
        return {k: v for k, v in categories.items() if v > 0}


def register(algorithm_manager):
    """Register V98 Connection Algorithm"""
    try:
        algo = V98ConnectionAlgorithm()
        algorithm_manager.register("V98Connection", algo)
        print("✅ V98Connection Algorithm registered (Enhanced)")
    except Exception as e:
        print(f"❌ Failed to register V98Connection: {e}")
