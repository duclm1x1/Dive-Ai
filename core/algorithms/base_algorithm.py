"""
Base Algorithm Class for Dive AI V29.4
All algorithms must inherit from this base class
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AlgorithmResult:
    """Result returned by algorithm execution"""
    status: str  # "success", "error", "partial"
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IOField:
    """Input/Output field specification"""
    name: str
    type: str  # "string", "integer", "boolean", "list", "object", "any"
    required: bool
    description: str
    default: Any = None


@dataclass
class AlgorithmIOSpec:
    """Input/Output specification for an algorithm"""
    inputs: List[IOField] = field(default_factory=list)
    outputs: List[IOField] = field(default_factory=list)


@dataclass
class AlgorithmSpec:
    """Complete algorithm specification"""
    algorithm_id: str
    name: str
    level: str  # "operational", "composite"
    category: str  # "cli", "memory", "orchestration", etc.
    version: str
    description: str
    io: AlgorithmIOSpec
    steps: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    performance_target: Dict[str, Any] = field(default_factory=dict)


class BaseAlgorithm:
    """
    Base class for all Dive AI algorithms
    
    Algorithm = CODE + STEPS:
    - CODE: The actual implementation in execute()
    - STEPS: Documented in spec.steps
    
    Example:
        class MyAlgorithm(BaseAlgorithm):
            def __init__(self):
                self.spec = AlgorithmSpec(
                    algorithm_id="MyAlgorithm",
                    name="My Algorithm",
                    level="operational",
                    category="custom",
                    version="1.0",
                    description="What it does",
                    io=AlgorithmIOSpec(
                        inputs=[IOField("input", "string", True, "Input data")],
                        outputs=[IOField("output", "string", True, "Result")]
                    ),
                    steps=[
                        "Step 1: Parse input",
                        "Step 2: Process data",
                        "Step 3: Return result"
                    ],
                    tags=["custom"]
                )
            
            def execute(self, params: dict) -> AlgorithmResult:
                # Actual code implementation
                input_data = params.get("input")
                result = self._process(input_data)
                return AlgorithmResult(status="success", data={"output": result})
            
            def _process(self, data):
                # Helper method
                return data
    """
    
    def __init__(self):
        self.spec: AlgorithmSpec = None
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """
        Execute the algorithm
        
        Args:
            params: Input parameters matching spec.io.inputs
        
        Returns:
            AlgorithmResult with outputs matching spec.io.outputs
        """
        raise NotImplementedError("Algorithm must implement execute() method")
    
    def validate_inputs(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters
        
        Returns:
            (is_valid, error_message)
        """
        if not self.spec or not self.spec.io.inputs:
            return True, None
        
        for input_field in self.spec.io.inputs:
            if input_field.required and input_field.name not in params:
                return False, f"Missing required input: {input_field.name}"
        
        return True, None
    
    def get_info(self) -> Dict[str, Any]:
        """Get algorithm information"""
        if not self.spec:
            return {}
        
        return {
            "id": self.spec.algorithm_id,
            "name": self.spec.name,
            "level": self.spec.level,
            "category": self.spec.category,
            "version": self.spec.version,
            "description": self.spec.description,
            "inputs": [
                {
                    "name": inp.name,
                    "type": inp.type,
                    "required": inp.required,
                    "description": inp.description
                }
                for inp in self.spec.io.inputs
            ],
            "outputs": [
                {
                    "name": out.name,
                    "type": out.type,
                    "description": out.description
                }
                for out in self.spec.io.outputs
            ],
            "tags": self.spec.tags
        }
