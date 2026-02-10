"""
LLM Query Algorithm
Send query to LLM and get response

Algorithm = CODE + STEPS
"""

import os
import sys
import requests
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class LLMQueryAlgorithm(BaseAlgorithm):
    """
    LLM Query Algorithm
    
    Send query to LLM (V98/AICoding/OpenAI) and get response
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="LLMQuery",
            name="LLM Query",
            level="operational",
            category="llm",
            version="1.0",
            description="Send query to LLM and get response. Supports V98, AICoding, OpenAI.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("prompt", "string", True, "User prompt/question"),
                    IOField("provider", "string", False, "API provider (v98/aicoding/openai, default: v98)"),
                    IOField("model", "string", False, "Model name"),
                    IOField("connection", "object", False, "Pre-established connection"),
                    IOField("max_tokens", "integer", False, "Max response tokens (default: 4096)"),
                    IOField("temperature", "float", False, "Temperature 0-2 (default: 0.7)")
                ],
                outputs=[
                    IOField("response", "string", True, "LLM response"),
                    IOField("tokens", "integer", True, "Tokens used"),
                    IOField("model_used", "string", True, "Actual model used"),
                    IOField("cost_estimate", "float", False, "Estimated cost USD")
                ]
            ),
            
            steps=[
                "Step 1: Get/validate connection (use existing or create new)",
                "Step 2: Format prompt for LLM",
                "Step 3: Prepare request payload (messages, model, params)",
                "Step 4: Send POST request to /chat/completions",
                "Step 5: Parse response (extract text, tokens)",
                "Step 6: Calculate cost estimate",
                "Step 7: Return response + metadata"
            ],
            
            tags=["llm", "query", "chat", "api"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute LLM query"""
        
        prompt = params.get("prompt", "")
        provider = params.get("provider", "v98")
        model = params.get("model")
        max_tokens = params.get("max_tokens", 4096)
        temperature = params.get("temperature", 0.7)
        
        print(f"\n💬 LLM Query: '{prompt[:60]}...'")
        print(f"   Provider: {provider}")
        
        try:
            # Step 1: Get connection
            connection = params.get("connection")
            if not connection:
                # Create new connection based on provider
                connection = self._create_connection(provider, model)
            
            api_url = connection["api_url"]
            headers = connection["headers"]
            model_name = model or connection.get("model", "claude-opus-4-6-thinking")
            
            # Step 2-3: Format prompt and prepare payload
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Step 4: Send request
            response = requests.post(
                f"{api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                return AlgorithmResult(
                    status="error",
                    error=f"LLM API error: HTTP {response.status_code}"
                )
            
            # Step 5: Parse response
            data = response.json()
            llm_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            # Step 6: Calculate cost (rough estimate)
            cost = self._estimate_cost(provider, model_name, tokens_used)
            
            # Step 7: Return
            return AlgorithmResult(
                status="success",
                data={
                    "response": llm_response,
                    "tokens": tokens_used,
                    "model_used": model_name,
                    "cost_estimate": cost
                },
                metadata={
                    "provider": provider,
                    "prompt_length": len(prompt)
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"LLM query failed: {str(e)}"
            )
    
    def _create_connection(self, provider: str, model: str = None) -> Dict[str, Any]:
        """Create connection based on provider"""
        
        if provider == "v98":
            api_key = os.getenv("V98_API_KEY")
            return {
                "api_url": "https://api.v98store.com/v1",
                "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                "model": model or "claude-opus-4-6-thinking"
            }
        elif provider == "aicoding":
            api_key = os.getenv("AICODING_API_KEY")
            return {
                "api_url": "https://api.aicoding.com/v1",
                "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                "model": model or "claude-opus-4-6"
            }
        else:  # openai
            api_key = os.getenv("OPENAI_API_KEY")
            return {
                "api_url": "https://api.openai.com/v1",
                "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                "model": model or "gpt-4"
            }
    
    def _estimate_cost(self, provider: str, model: str, tokens: int) -> float:
        """Estimate cost based on provider/model/tokens"""
        
        # Very rough estimates (per 1M tokens)
        cost_per_1m = {
            "v98": 15.0,  # Claude Opus
            "aicoding": 15.0,
            "openai": 30.0  # GPT-4
        }
        
        base_cost = cost_per_1m.get(provider, 15.0)
        return (tokens / 1_000_000) * base_cost


def register(algorithm_manager):
    """Register LLM Query Algorithm"""
    try:
        algo = LLMQueryAlgorithm()
        algorithm_manager.register("LLMQuery", algo)
        print("✅ LLM Query Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register LLMQuery: {e}")
