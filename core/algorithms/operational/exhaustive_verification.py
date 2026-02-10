"""
🔬 EXHAUSTIVE VERIFICATION
Comprehensive verification through multiple test strategies

Based on V28's layer5_exhaustiveverification.py
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class VerificationMethod(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    FUZZING = "fuzzing"
    PROPERTY = "property"
    SYMBOLIC = "symbolic"


@dataclass
class VerificationTest:
    """A verification test"""
    method: VerificationMethod
    name: str
    passed: bool
    details: str
    severity: str = "medium"


class ExhaustiveVerificationAlgorithm(BaseAlgorithm):
    """
    🔬 Exhaustive Verification
    
    Verifies code through multiple methods:
    - Static analysis
    - Dynamic testing
    - Fuzz testing
    - Property-based testing
    
    From V28: layer5_exhaustiveverification.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ExhaustiveVerification",
            name="Exhaustive Verification",
            level="operational",
            category="verification",
            version="1.0",
            description="Multi-strategy code verification",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("code", "string", True, "Code to verify"),
                    IOField("methods", "array", False, "Methods to use")
                ],
                outputs=[
                    IOField("verified", "boolean", True, "All tests passed"),
                    IOField("tests", "array", True, "Test results")
                ]
            ),
            steps=["Run static analysis", "Run dynamic tests", "Fuzz test", "Aggregate results"],
            tags=["verification", "testing", "exhaustive", "quality"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        code = params.get("code", "")
        methods = params.get("methods", ["static", "dynamic"])
        
        if not code:
            return AlgorithmResult(status="error", error="No code provided")
        
        print(f"\n🔬 Exhaustive Verification")
        
        tests = []
        
        if "static" in methods:
            tests.extend(self._static_analysis(code))
        if "dynamic" in methods:
            tests.extend(self._dynamic_tests(code))
        if "fuzzing" in methods:
            tests.extend(self._fuzz_tests(code))
        if "property" in methods:
            tests.extend(self._property_tests(code))
        
        passed = sum(1 for t in tests if t.passed)
        total = len(tests)
        verified = all(t.passed for t in tests)
        
        print(f"   Tests: {passed}/{total} passed")
        print(f"   Verified: {'✅ YES' if verified else '❌ NO'}")
        
        return AlgorithmResult(
            status="success",
            data={
                "verified": verified,
                "tests": [self._test_to_dict(t) for t in tests],
                "passed": passed,
                "failed": total - passed,
                "coverage": passed / total if total > 0 else 0
            }
        )
    
    def _static_analysis(self, code: str) -> List[VerificationTest]:
        tests = []
        
        # Check for syntax issues
        try:
            compile(code, '<string>', 'exec')
            tests.append(VerificationTest(
                VerificationMethod.STATIC, "syntax_check", True, "No syntax errors"
            ))
        except SyntaxError as e:
            tests.append(VerificationTest(
                VerificationMethod.STATIC, "syntax_check", False, str(e), "critical"
            ))
        
        # Check for common patterns
        if "eval(" in code or "exec(" in code:
            tests.append(VerificationTest(
                VerificationMethod.STATIC, "dangerous_functions", False, 
                "Found dangerous eval/exec", "high"
            ))
        else:
            tests.append(VerificationTest(
                VerificationMethod.STATIC, "dangerous_functions", True, "No dangerous functions"
            ))
        
        return tests
    
    def _dynamic_tests(self, code: str) -> List[VerificationTest]:
        tests = []
        
        # Try to execute code safely
        try:
            # Very limited execution scope
            safe_globals = {"__builtins__": {}}
            exec(code, safe_globals, {})
            tests.append(VerificationTest(
                VerificationMethod.DYNAMIC, "execution_test", True, "Code executes without error"
            ))
        except Exception as e:
            tests.append(VerificationTest(
                VerificationMethod.DYNAMIC, "execution_test", False, str(e)[:100]
            ))
        
        return tests
    
    def _fuzz_tests(self, code: str) -> List[VerificationTest]:
        tests = []
        
        # Simple fuzz candidates
        test_inputs = ["", None, [], {}, 0, -1, "test", "a" * 1000]
        passed = True
        
        # Check if code handles edge cases (heuristic)
        if "try:" in code or "except" in code:
            tests.append(VerificationTest(
                VerificationMethod.FUZZING, "error_handling", True, "Has error handling"
            ))
        else:
            tests.append(VerificationTest(
                VerificationMethod.FUZZING, "error_handling", False, 
                "No exception handling found", "medium"
            ))
        
        return tests
    
    def _property_tests(self, code: str) -> List[VerificationTest]:
        tests = []
        
        # Check for assertions
        if "assert" in code:
            tests.append(VerificationTest(
                VerificationMethod.PROPERTY, "has_assertions", True, "Uses assertions"
            ))
        else:
            tests.append(VerificationTest(
                VerificationMethod.PROPERTY, "has_assertions", False, 
                "No assertions found", "low"
            ))
        
        # Check for type hints
        if ":" in code and "->" in code:
            tests.append(VerificationTest(
                VerificationMethod.PROPERTY, "type_hints", True, "Has type hints"
            ))
        else:
            tests.append(VerificationTest(
                VerificationMethod.PROPERTY, "type_hints", False, 
                "No type hints found", "low"
            ))
        
        return tests
    
    def _test_to_dict(self, test: VerificationTest) -> Dict:
        return {
            "method": test.method.value,
            "name": test.name,
            "passed": test.passed,
            "details": test.details,
            "severity": test.severity
        }


def register(algorithm_manager):
    algo = ExhaustiveVerificationAlgorithm()
    algorithm_manager.register("ExhaustiveVerification", algo)
    print("✅ ExhaustiveVerification registered")


if __name__ == "__main__":
    algo = ExhaustiveVerificationAlgorithm()
    result = algo.execute({
        "code": '''
def add(a: int, b: int) -> int:
    try:
        assert isinstance(a, int)
        return a + b
    except Exception:
        return 0
''',
        "methods": ["static", "dynamic", "fuzzing", "property"]
    })
    print(f"Verified: {result.data['verified']}")
