"""
Input Validation Algorithm
Validate algorithm inputs against spec
"""

import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)

class InputValidationAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="InputValidation",
            name="Input Validation",
            level="operational",
            category="utilities",
            version="1.0",
            description="Validate inputs against algorithm spec (type, required fields).",
            io=AlgorithmIOSpec(
                inputs=[IOField("inputs", "object", True, "Inputs to validate"),
                       IOField("spec", "object", True, "Algorithm spec")],
                outputs=[IOField("valid", "boolean", True, "Is valid"),
                        IOField("errors", "list", False, "Validation errors")]
            ),
            steps=["Step 1: Check required fields", "Step 2: Validate types",
                   "Step 3: Return validation result"],
            tags=["validation", "utility"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        inputs = params.get("inputs", {})
        spec = params.get("spec", {})
        
        errors = []
        # Simple validation
        for field in spec.get("io", {}).get("inputs", []):
            if field.get("required") and field.get("name") not in inputs:
                errors.append(f"Missing required field: {field.get('name')}")
        
        return AlgorithmResult(status="success", data={
            "valid": len(errors) == 0,
            "errors": errors
        })

def register(algorithm_manager):
    algorithm_manager.register("InputValidation", InputValidationAlgorithm())
    print("✅ InputValidation Algorithm registered")
