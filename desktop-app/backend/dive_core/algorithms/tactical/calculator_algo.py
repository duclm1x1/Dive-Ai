import logging
from typing import Dict, Any, Optional
import math
from ..base import BaseAlgorithm, AlgorithmResult
from ...specs import AlgorithmSpec

logger = logging.getLogger(__name__)

class CalculatorAlgorithm(BaseAlgorithm):
    """
    Tactical algorithm for basic calculations.
    Demonstrates the V29 Algorithm Architecture.
    """
    
    OPERATIONS = {
        "add": lambda a, b: a + b,
        "sub": lambda a, b: a - b,
        "mul": lambda a, b: a * b,
        "div": lambda a, b: a / b
    }

    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            name="calculator",
            description="Basic arithmetic calculator algorithm",
            version="1.1.0",
            input_schema={
                "operation": "str (add, sub, mul, div)",
                "a": "float",
                "b": "float"
            },
            output_schema={
                "result": "float"
            },
            cost_per_call=0.0,
            tags=["tactical", "math"]
        )

    def execute(self, inputs: Dict[str, Any], context: Optional[Dict] = None) -> AlgorithmResult:
        """
        Execute calculation based on inputs.
        """
        try:
            op = inputs.get("operation", "add")
            
            # Input Validation
            if op not in self.OPERATIONS:
                 return AlgorithmResult(
                    status="failure",
                    data=None,
                    meta={"error": f"Unknown operation: {op}"}
                )

            try:
                a = float(inputs.get("a", 0))
                b = float(inputs.get("b", 0))
            except (ValueError, TypeError) as e:
                return AlgorithmResult(
                    status="failure",
                    data=None,
                    meta={"error": f"Invalid numeric input: {str(e)}"}
                )

            # Validate division by zero
            if op == "div" and b == 0:
                return AlgorithmResult(
                    status="failure",
                    data=None,
                    meta={"error": "Division by zero is not allowed"}
                )

            # Perform calculation
            result = self.OPERATIONS[op](a, b)

            # Check for invalid results (inf, nan)
            if not (result == result and abs(result) != float('inf')):  # NaN and Inf check
                return AlgorithmResult(
                    status="failure",
                    data=None,
                    meta={"error": "Calculation resulted in invalid value (overflow or NaN)"}
                )

            logger.info(f"Calculation successful: {a} {op} {b} = {result}")

            return AlgorithmResult(
                status="success",
                data={"result": result},
                meta={"operation": op, "a": a, "b": b}
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in calculator: {str(e)}", exc_info=True)
            return AlgorithmResult(
                status="failure",
                data=None,
                meta={"error": f"Unexpected error: {str(e)}"}
            )
