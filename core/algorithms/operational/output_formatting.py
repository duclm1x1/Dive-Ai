"""
Output Formatting Algorithm
Format algorithm outputs for CLI/API
"""

import os
import sys
import json
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)

class OutputFormattingAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="OutputFormatting",
            name="Output Formatting",
            level="operational",
            category="utilities",
            version="1.0",
            description="Format algorithm outputs (JSON, markdown, plain text).",
            io=AlgorithmIOSpec(
                inputs=[IOField("data", "object", True, "Data to format"),
                       IOField("format", "string", False, "json/markdown/plain")],
                outputs=[IOField("formatted", "string", True, "Formatted output")]
            ),
            steps=["Step 1: Detect format", "Step 2: Apply formatting", "Step 3: Return result"],
            tags=["formatting", "utility"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        data = params.get("data", {})
        fmt = params.get("format", "json")
        
        if fmt == "json":
            formatted = json.dumps(data, indent=2)
        elif fmt == "markdown":
            formatted = f"# Result\n\n```json\n{json.dumps(data, indent=2)}\n```"
        else:
            formatted = str(data)
        
        return AlgorithmResult(status="success", data={"formatted": formatted})

def register(algorithm_manager):
    algorithm_manager.register("OutputFormatting", OutputFormattingAlgorithm())
    print("✅ OutputFormatting Algorithm registered")
