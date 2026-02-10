"""
✅ QUALITY GATE
Enforce quality standards before proceeding

Based on V28's vibe_engine/quality_gate.py
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


class GateStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass
class GateCheck:
    """A quality gate check"""
    name: str
    status: GateStatus
    score: float
    message: str


class QualityGateAlgorithm(BaseAlgorithm):
    """
    ✅ Quality Gate
    
    Enforces quality standards:
    - Code quality checks
    - Test coverage gates
    - Performance thresholds
    - Security requirements
    
    From V28: vibe_engine/quality_gate.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="QualityGate",
            name="Quality Gate",
            level="operational",
            category="quality",
            version="1.0",
            description="Enforce quality standards",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("artifact", "object", True, "Artifact to check"),
                    IOField("gates", "array", False, "Gate configurations")
                ],
                outputs=[
                    IOField("passed", "boolean", True, "Overall pass/fail"),
                    IOField("checks", "array", True, "Individual check results")
                ]
            ),
            steps=["Load gates", "Run checks", "Aggregate results", "Determine verdict"],
            tags=["quality", "gate", "standards", "enforcement"]
        )
        
        self.default_gates = [
            {"name": "syntax", "threshold": 1.0, "weight": 3},
            {"name": "complexity", "threshold": 0.7, "weight": 2},
            {"name": "coverage", "threshold": 0.6, "weight": 2},
            {"name": "security", "threshold": 0.9, "weight": 3},
            {"name": "documentation", "threshold": 0.5, "weight": 1}
        ]
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        artifact = params.get("artifact", {})
        gates = params.get("gates", self.default_gates)
        
        if not artifact:
            return AlgorithmResult(status="error", error="No artifact provided")
        
        print(f"\n✅ Quality Gate")
        
        checks = []
        
        for gate in gates:
            check = self._run_check(gate, artifact)
            checks.append(check)
        
        # Determine overall result
        failed = [c for c in checks if c.status == GateStatus.FAIL]
        warned = [c for c in checks if c.status == GateStatus.WARN]
        
        overall_passed = len(failed) == 0
        
        print(f"   Result: {'PASS' if overall_passed else 'FAIL'} ({len(checks) - len(failed)}/{len(checks)})")
        
        return AlgorithmResult(
            status="success",
            data={
                "passed": overall_passed,
                "checks": [
                    {"name": c.name, "status": c.status.value, "score": c.score, "message": c.message}
                    for c in checks
                ],
                "failed_count": len(failed),
                "warning_count": len(warned)
            }
        )
    
    def _run_check(self, gate: Dict, artifact: Dict) -> GateCheck:
        name = gate.get("name", "unknown")
        threshold = gate.get("threshold", 0.7)
        
        # Simulate checks based on artifact
        score = self._simulate_check(name, artifact)
        
        if score >= threshold:
            status = GateStatus.PASS
            message = f"{name} check passed"
        elif score >= threshold * 0.8:
            status = GateStatus.WARN
            message = f"{name} check warning: {score:.0%} (threshold: {threshold:.0%})"
        else:
            status = GateStatus.FAIL
            message = f"{name} check failed: {score:.0%} (threshold: {threshold:.0%})"
        
        return GateCheck(name=name, status=status, score=score, message=message)
    
    def _simulate_check(self, check_name: str, artifact: Dict) -> float:
        # Simulate different checks
        content = artifact.get("content", "")
        
        if check_name == "syntax":
            try:
                if artifact.get("type") == "code":
                    compile(content, '<string>', 'exec')
                return 1.0
            except:
                return 0.0
        
        elif check_name == "complexity":
            # Simple heuristic
            lines = content.split('\n') if content else []
            return max(0.3, 1.0 - (len(lines) / 500))
        
        elif check_name == "coverage":
            has_tests = artifact.get("has_tests", False)
            return 0.8 if has_tests else 0.4
        
        elif check_name == "security":
            dangerous = ["eval(", "exec(", "__import__"]
            found = sum(1 for d in dangerous if d in content)
            return max(0, 1.0 - (found * 0.3))
        
        elif check_name == "documentation":
            has_docs = '"""' in content or "'''" in content or "#" in content
            return 0.8 if has_docs else 0.3
        
        return 0.5


def register(algorithm_manager):
    algo = QualityGateAlgorithm()
    algorithm_manager.register("QualityGate", algo)
    print("✅ QualityGate registered")


if __name__ == "__main__":
    algo = QualityGateAlgorithm()
    result = algo.execute({
        "artifact": {
            "type": "code",
            "content": '''def hello():
    """Say hello"""
    print("Hello, World!")
''',
            "has_tests": True
        }
    })
    print(f"Passed: {result.data['passed']}")
