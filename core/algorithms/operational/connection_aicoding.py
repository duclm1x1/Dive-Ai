"""
ConnectionAICoding Algorithm
Connect to aicoding.com API A-Z

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


class ConnectionAICodingAlgorithm(BaseAlgorithm):
    """
    AICoding API Connection Algorithm
    
    Complete A-Z implementation for connecting to aicoding.com API
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ConnectionAICoding",
            name="AICoding API Connection",
            level="operational",
            category="connection",
            version="1.0",
            description="Connect to aicoding.com API A-Z. Get API key, create headers, test connection, return session.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("api_key", "string", False, "AICoding API key (uses AICODING_API_KEY env if not provided)"),
                    IOField("model", "string", False, "Model to use (default: claude-opus-4-6)"),
                    IOField("test_connection", "boolean", False, "Test connection (default: true)")
                ],
                outputs=[
                    IOField("connection_status", "string", True, "connected/failed"),
                    IOField("api_url", "string", True, "AICoding API URL"),
                    IOField("headers", "object", True, "Request headers"),
                    IOField("available_models", "list", False, "Available models")
                ]
            ),
            
            steps=[
                "Step 1: Get API key from params or AICODING_API_KEY env",
                "Step 2: Validate API key format",
                "Step 3: Create request headers with Authorization",
                "Step 4: Set AICoding API URL",
                "Step 5: Test connection if requested",
                "Step 6: Return connection status + details"
            ],
            
            tags=["connection", "api", "aicoding", "authentication"]
        )
        
        self.api_url = "https://api.aicoding.com/v1"
        self.default_model = "claude-opus-4-6"
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute AICoding connection A-Z"""
        
        print(f"🔌 Connecting to AICoding API...")
        
        try:
            # Step 1: Get API key
            api_key = params.get("api_key") or os.getenv("AICODING_API_KEY")
            if not api_key:
                return AlgorithmResult(
                    status="error",
                    error="No API key. Set AICODING_API_KEY env or pass api_key parameter."
                )
            
            # Step 2: Validate
            if len(api_key.strip()) == 0:
                return AlgorithmResult(status="error", error="API key is empty")
            
            # Step 3: Create headers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Step 4: Set URL
            api_url = self.api_url
            
            # Step 5: Test connection
            available_models = []
            if params.get("test_connection", True):
                try:
                    response = requests.get(f"{api_url}/models", headers=headers, timeout=10)
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [m.get("id", "unknown") for m in models_data.get("data", [])]
                        print(f"   ✅ Connected! Found {len(available_models)} models")
                    else:
                        return AlgorithmResult(status="error", error=f"Test failed: HTTP {response.status_code}")
                except requests.exceptions.RequestException as e:
                    return AlgorithmResult(status="error", error=f"Test failed: {str(e)}")
            
            # Step 6: Return success
            return AlgorithmResult(
                status="success",
                data={
                    "connection_status": "connected",
                    "api_url": api_url,
                    "headers": headers,
                    "available_models": available_models,
                    "model": params.get("model", self.default_model)
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Unexpected: {str(e)}")


def register(algorithm_manager):
    """Register ConnectionAICoding Algorithm"""
    try:
        algo = ConnectionAICodingAlgorithm()
        algorithm_manager.register("ConnectionAICoding", algo)
        print("✅ ConnectionAICoding Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register ConnectionAICoding: {e}")
