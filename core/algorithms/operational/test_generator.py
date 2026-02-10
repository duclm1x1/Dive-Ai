"""
🧪 TEST GENERATOR
Generate tests from code specifications

Based on V28's vibe_engine/test_generator.py
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class TestCase:
    """A generated test case"""
    name: str
    description: str
    inputs: Dict
    expected: Any
    test_type: str


class TestGeneratorAlgorithm(BaseAlgorithm):
    """
    🧪 Test Generator
    
    Generates tests from code:
    - Unit test generation
    - Edge case detection
    - Assertion generation
    - Coverage optimization
    
    From V28: vibe_engine/test_generator.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="TestGenerator",
            name="Test Generator",
            level="operational",
            category="testing",
            version="1.0",
            description="Generate tests from code specifications",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("code", "string", False, "Code to test"),
                    IOField("function_name", "string", False, "Function to test"),
                    IOField("spec", "object", False, "Test specification")
                ],
                outputs=[
                    IOField("tests", "array", True, "Generated tests")
                ]
            ),
            steps=["Analyze code", "Identify test cases", "Generate assertions", "Format tests"],
            tags=["testing", "generation", "unit-tests"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        code = params.get("code", "")
        function_name = params.get("function_name", "")
        spec = params.get("spec", {})
        
        print(f"\n🧪 Test Generator")
        
        test_cases = []
        
        # Generate based on spec or code analysis
        if spec:
            test_cases = self._generate_from_spec(spec)
        elif code:
            test_cases = self._generate_from_code(code, function_name)
        else:
            test_cases = self._generate_sample()
        
        # Generate test code
        test_code = self._generate_test_code(test_cases, function_name or "my_function")
        
        print(f"   Generated: {len(test_cases)} test cases")
        
        return AlgorithmResult(
            status="success",
            data={
                "test_cases": [
                    {"name": t.name, "description": t.description, "type": t.test_type}
                    for t in test_cases
                ],
                "test_code": test_code,
                "count": len(test_cases)
            }
        )
    
    def _generate_from_spec(self, spec: Dict) -> List[TestCase]:
        test_cases = []
        
        # Normal cases
        for i, example in enumerate(spec.get("examples", [])):
            test_cases.append(TestCase(
                name=f"test_example_{i}",
                description=f"Test example {i+1}",
                inputs=example.get("input", {}),
                expected=example.get("expected"),
                test_type="normal"
            ))
        
        # Edge cases
        edge_cases = spec.get("edge_cases", [])
        for i, edge in enumerate(edge_cases):
            test_cases.append(TestCase(
                name=f"test_edge_case_{i}",
                description=edge.get("description", f"Edge case {i+1}"),
                inputs=edge.get("input", {}),
                expected=edge.get("expected"),
                test_type="edge"
            ))
        
        return test_cases
    
    def _generate_from_code(self, code: str, function_name: str) -> List[TestCase]:
        test_cases = []
        
        # Basic happy path
        test_cases.append(TestCase(
            name=f"test_{function_name}_basic",
            description="Test basic functionality",
            inputs={},
            expected=None,
            test_type="normal"
        ))
        
        # Null/empty input
        test_cases.append(TestCase(
            name=f"test_{function_name}_empty",
            description="Test with empty input",
            inputs={"input": None},
            expected=None,
            test_type="edge"
        ))
        
        # Error case
        test_cases.append(TestCase(
            name=f"test_{function_name}_error",
            description="Test error handling",
            inputs={"invalid": True},
            expected="error",
            test_type="error"
        ))
        
        return test_cases
    
    def _generate_sample(self) -> List[TestCase]:
        return [
            TestCase("test_sample", "Sample test", {}, None, "sample")
        ]
    
    def _generate_test_code(self, test_cases: List[TestCase], function_name: str) -> str:
        code = f'''import pytest

class Test{function_name.title().replace("_", "")}:
    """Tests for {function_name}"""
'''
        
        for tc in test_cases:
            code += f'''
    def {tc.name}(self):
        """{tc.description}"""
        # Arrange
        inputs = {tc.inputs}
        expected = {tc.expected}
        
        # Act
        result = {function_name}(**inputs)
        
        # Assert
        assert result == expected
'''
        
        return code


def register(algorithm_manager):
    algo = TestGeneratorAlgorithm()
    algorithm_manager.register("TestGenerator", algo)
    print("✅ TestGenerator registered")


if __name__ == "__main__":
    algo = TestGeneratorAlgorithm()
    result = algo.execute({
        "function_name": "calculate_total",
        "spec": {
            "examples": [
                {"input": {"items": [10, 20], "tax": 0.1}, "expected": 33}
            ],
            "edge_cases": [
                {"description": "Empty list", "input": {"items": [], "tax": 0}, "expected": 0}
            ]
        }
    })
    print(f"Generated: {result.data['count']} tests")
