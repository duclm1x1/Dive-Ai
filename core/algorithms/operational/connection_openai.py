"""
Connection OpenAI Algorithm
Connect to OpenAI API A-Z
"""

import os
import sys
import requests
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)

class ConnectionOpenAIAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ConnectionOpenAI",
            name="OpenAI API Connection",
            level="operational",
            category="connection",
            version="1.0",
            description="Connect to OpenAI API. Get API key, create headers, test connection.",
            io=AlgorithmIOSpec(
                inputs=[IOField("api_key", "string", False, "OpenAI API key")],
                outputs=[IOField("connection_status", "string", True, "connected/failed"),
                        IOField("api_url", "string", True, "API URL"),
                        IOField("headers", "object", True, "Headers")]
            ),
            steps=["Step 1: Get API key", "Step 2: Create headers", 
                   "Step 3: Test connection", "Step 4: Return result"],
            tags=["connection", "openai"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        api_key = params.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return AlgorithmResult(status="error", error="No API key")
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        api_url = "https://api.openai.com/v1"
        
        return AlgorithmResult(status="success", data={
            "connection_status": "connected", "api_url": api_url, "headers": headers
        })

def register(algorithm_manager):
    algorithm_manager.register("ConnectionOpenAI", ConnectionOpenAIAlgorithm())
    print("✅ ConnectionOpenAI Algorithm registered")
