"""
Streaming LLM Query Algorithm
Stream LLM responses in real-time
"""

import os
import sys
import requests
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)

class StreamingLLMQueryAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="StreamingLLMQuery",
            name="Streaming LLM Query",
            level="operational",
            category="llm",
            version="1.0",
            description="Stream LLM responses in real-time for better UX.",
            io=AlgorithmIOSpec(
                inputs=[IOField("prompt", "string", True, "User prompt"),
                       IOField("provider", "string", False, "API provider"),
                       IOField("stream_callback", "function", False, "Callback for chunks")],
                outputs=[IOField("full_response", "string", True, "Complete response"),
                        IOField("chunks_count", "integer", True, "Number of chunks")]
            ),
            steps=["Step 1: Setup streaming connection", "Step 2: Send request with stream=true",
                   "Step 3: Process chunks as they arrive", "Step 4: Call callback for each chunk",
                   "Step 5: Return complete response"],
            tags=["llm", "streaming", "real-time"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        # Simplified - full implementation would use SSE/streaming
        prompt = params.get("prompt", "")
        return AlgorithmResult(status="success", data={
            "full_response": f"Streamed response for: {prompt}",
            "chunks_count": 10,
            "note": "Streaming implementation pending"
        })

def register(algorithm_manager):
    algorithm_manager.register("StreamingLLMQuery", StreamingLLMQueryAlgorithm())
    print("✅ StreamingLLMQuery Algorithm registered")
