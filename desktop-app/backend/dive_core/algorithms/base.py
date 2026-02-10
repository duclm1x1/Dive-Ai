from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from ..specs import AlgorithmSpec, VerificationResult

@dataclass
class AlgorithmResult:
    status: str  # "success", "failure"
    data: Any
    meta: Dict[str, Any]
    cost: float = 0.0
    verification: Optional[VerificationResult] = None

class BaseAlgorithm(ABC):
    """
    Abstract Base Class for Dive V29 Algorithms.
    Implementation of an AlgorithmSpec.
    """
    def __init__(self):
        self.spec: Optional[AlgorithmSpec] = None
        self._name: Optional[str] = None

    @property
    def name(self) -> str:
        if self.spec:
            return self.spec.name
        if self._name:
            return self._name
        return self.__class__.__name__

    @name.setter
    def name(self, value: str):
        self._name = value

    @abstractmethod
    def execute(self, inputs: Dict[str, Any], context: Optional[Dict] = None) -> AlgorithmResult:
        """
        Executes the algorithm.
        Inputs must match self.spec.input_schema.
        """
        pass
    
    def verify_result(self, result: Any, context: Optional[Dict] = None) -> VerificationResult:
        """
        Runs the configured verifier on the result.
        """
        if self.spec and self.spec.verifier:
            verifier_instance = self.spec.verifier()
            return verifier_instance.verify(result, context)
        return VerificationResult(True, 1.0, "No verifier configured", {})

    def can_handle(self, task: str) -> float:
        """Legacy compatibility"""
        return 0.1
