from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable, List

@dataclass
class VerificationResult:
    success: bool
    score: float
    message: str
    details: Dict[str, Any]

@dataclass
class AlgorithmSpec:
    name: str
    description: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    verifier: Optional[Callable] = None
    cost_per_call: float = 0.0
    tags: List[str] = None
