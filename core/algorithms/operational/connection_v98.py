"""
ConnectionV98 Algorithm
Handles A-Z connection to v98store.com API

Algorithm = CODE + STEPS:
- CODE: Full implementation of V98 API connection
- STEPS: Documented in spec.steps
"""

import os
import sys
import requests
from typing import Dict, Any

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class ConnectionV98Algorithm(BaseAlgorithm):
    """
    V98 API Connection Algorithm
    
    Complete A-Z implementation for connecting to v98store.com API
    """
    
    def __init__(self):
        """Initialize ConnectionV98 Algorithm"""
        
        self.spec = AlgorithmSpec(
            algorithm_id="ConnectionV98",
            name="V98 API Connection",
            level="operational",
            category="connection",
            version="1.0",
            description="Connect to v98store.com API (A-Z). Get API key from environment, create headers, test connection, and return authenticated session.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField(
                        name="api_key",
                        type="string",
                        required=False,
                        description="V98 API key (optional, will use V98_API_KEY env var if not provided)"
                    ),
                    IOField(
                        name="model",
                        type="string",
                        required=False,
                        description="Model to use (default: claude-opus-4-6-thinking)"
                    ),
                    IOField(
                        name="test_connection",
                        type="boolean",
                        required=False,
                        description="Test connection after setup (default: true)"
                    )
                ],
                outputs=[
                    IOField(
                        name="connection_status",
                        type="string",
                        required=True,
                        description="Connection status (connected/failed)"
                    ),
                    IOField(
                        name="api_url",
                        type="string",
                        required=True,
                        description="V98 API base URL"
                    ),
                    IOField(
                        name="headers",
                        type="object",
                        required=True,
                        description="Request headers with authorization"
                    ),
                    IOField(
                        name="available_models",
                        type="list",
                        required=False,
                        description="List of available models"
                    )
                ]
            ),
            
            steps=[
                "Step 1: Get API key from params or V98_API_KEY environment variable",
                "Step 2: Validate API key format (not empty)",
                "Step 3: Create request headers with Authorization bearer token",
                "Step 4: Set V98 API base URL (https://api.v98store.com/v1)",
                "Step 5: If test_connection=true, make test request to /models endpoint",
                "Step 6: Return connection status, URL, headers, and available models"
            ],
            
            tags=["connection", "api", "v98", "authentication"]
        )
        
        # V98 configuration
        self.api_url = "https://api.v98store.com/v1"
        self.default_model = "claude-opus-4-6-thinking"
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """
        Execute V98 connection A-Z
        
        Implements all steps documented in spec.steps
        """
        
        print(f"🔌 Connecting to V98 API...")
        
        try:
            # Step 1: Get API key
            api_key = params.get("api_key") or os.getenv("V98_API_KEY")
            if not api_key:
                return AlgorithmResult(
                    status="error",
                    error="No API key provided. Set V98_API_KEY environment variable or pass api_key parameter."
                )
            
            # Step 2: Validate API key
            if len(api_key.strip()) == 0:
                return AlgorithmResult(
                    status="error",
                    error="API key is empty"
                )
            
            # Step 3: Create headers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Step 4: Set API URL
            api_url = self.api_url
            
            # Step 5: Test connection (if requested)
            test_connection = params.get("test_connection", True)
            available_models = []
            
            if test_connection:
                try:
                    response = requests.get(
                        f"{api_url}/models",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [
                            model.get("id", "unknown")
                            for model in models_data.get("data", [])
                        ]
                        print(f"   ✅ Connected! Found {len(available_models)} models")
                    else:
                        return AlgorithmResult(
                            status="error",
                            error=f"Connection test failed: HTTP {response.status_code}"
                        )
                
                except requests.exceptions.RequestException as e:
                    return AlgorithmResult(
                        status="error",
                        error=f"Connection test failed: {str(e)}"
                    )
            
            # Step 6: Return success result
            return AlgorithmResult(
                status="success",
                data={
                    "connection_status": "connected",
                    "api_url": api_url,
                    "headers": headers,
                    "available_models": available_models,
                    "model": params.get("model", self.default_model)
                },
                metadata={
                    "test_performed": test_connection,
                    "models_count": len(available_models)
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Unexpected error: {str(e)}"
            )


# Registration function
def register(algorithm_manager):
    """Register ConnectionV98 Algorithm"""
    try:
        algo = ConnectionV98Algorithm()
        algorithm_manager.register("ConnectionV98", algo)
        print("✅ ConnectionV98 Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register ConnectionV98: {e}")
