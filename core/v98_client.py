"""
Simple V98 API Client for Direct LLM Queries

Provides a straightforward interface to V98 API without complex dependencies.
"""

import os
import requests
from typing import Dict, Any, List, Optional


class V98Client:
    """Direct V98 API Client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://v98store.com/v1"
    ):
        """
        Initialize V98 Client
        
        Args:
            api_key: V98 API key (uses V98_API_KEY env var if not provided)
            base_url: V98 API base URL
        """
        self.api_key = api_key or os.getenv(
            "V98_API_KEY",
            "YOUR_V98_API_KEY_HERE"
        )
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            API response dict
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models
        
        Returns:
            List of model IDs
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return [model.get("id", "") for model in data.get("data", [])]
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            return []


# Simple test function
def test_v98_connection():
    """Test V98 API connection"""
    print("=" * 70)
    print("Testing V98 API Connection")
    print("=" * 70)
    
    client = V98Client()
    
    # Test 1: Get available models
    print("\n[1] Fetching available models...")
    models = client.get_available_models()
    if models:
        print(f"    ✅ Found {len(models)} models")
        print(f"    Top 5: {models[:5]}")
    else:
        print("    ❌ No models found or connection failed")
    
    # Test 2: Simple chat completion
    print("\n[2] Testing chat completion...")
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, Dive AI!' and nothing else."}
        ],
        model="gpt-4o",
        temperature=0.3,
        max_tokens=50
    )
    
    if "error" in response:
        print(f"    ❌ Error: {response['error']}")
        if response.get("status_code"):
            print(f"    Status Code: {response['status_code']}")
    else:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"    ✅ Response: {content}")
        print(f"    Model: {response.get('model', 'unknown')}")
        print(f"    Tokens: {response.get('usage', {}).get('total_tokens', 0)}")
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    test_v98_connection()
