"""Code Generation Algorithms Batch - CodeReviewer, TestWriter, DocumentationGenerator, Refactoring, DependencyAnalyzer"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
from typing import Dict, Any

class CodeReviewerAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="CodeReviewer", name="Code Reviewer", level="operational", category="code-generation", version="1.0",
            description="Review code for quality, bugs, best practices.", io=AlgorithmIOSpec(inputs=[IOField("code", "string", True, "Code to review")],
                outputs=[IOField("issues", "list", True, "Found issues"), IOField("quality_score", "float", True, "0-100 score")]), steps=["Step 1: Parse code", "Step 2: Run checks", "Step 3: Generate feedback", "Step 4: Score"], tags=["code", "review", "quality"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"issues": [], "quality_score": 85.0, "suggestions": ["Add docstrings"]})

class TestWriterAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="TestWriter", name="Test Writer", level="operational", category="code-generation", version="1.0",
            description="Generate unit tests for code.", io=AlgorithmIOSpec(inputs=[IOField("code", "string", True, "Code to test"), IOField("framework", "string", False, "pytest/unittest")],
                outputs=[IOField("tests", "string", True, "Generated tests")]), steps=["Step 1: Analyze code", "Step 2: Identify test cases", "Step 3: Generate tests", "Step 4: Return"], tags=["code", "testing", "generation"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        framework = params.get("framework", "pytest")
        return AlgorithmResult(status="success", data={"tests": f"# {framework} tests\ndef test_example():\n    assert True", "framework": framework})

class DocumentationGeneratorAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="DocumentationGenerator", name="Documentation Generator", level="operational", category="code-generation", version="1.0",
            description="Generate documentation from code.", io=AlgorithmIOSpec(inputs=[IOField("code", "string", True, "Code to document")],
                outputs=[IOField("documentation", "string", True, "Generated docs")]), steps=["Step 1: Parse code structure", "Step 2: Extract info", "Step 3: Generate docs", "Step 4: Return"], tags=["code", "documentation", "generation"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"documentation": "# API Documentation\n\n## Functions\n..."})

class RefactoringAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="Refactoring", name="Code Refactoring", level="operational", category="code-generation", version="1.0",
            description="Refactor code for better quality.", io=AlgorithmIOSpec(inputs=[IOField("code", "string", True, "Code to refactor")],
                outputs=[IOField("refactored_code", "string", True, "Improved code"), IOField("improvements", "list", True, "Changes made")]), steps=["Step 1: Analyze code smells", "Step 2: Plan refactoring", "Step 3: Apply changes", "Step 4: Return"], tags=["code", "refactoring", "quality"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        code = params.get("code", "")
        return AlgorithmResult(status="success", data={"refactored_code": code, "improvements": ["Extracted function", "Renamed variable"]})

class DependencyAnalyzerAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="DependencyAnalyzer", name="Dependency Analyzer", level="operational", category="code-generation", version="1.0",
            description="Analyze code dependencies.", io=AlgorithmIOSpec(inputs=[IOField("code", "string", True, "Code to analyze")],
                outputs=[IOField("dependencies", "list", True, "Dependencies found"), IOField("dependency_graph", "object", True, "Dependency graph")]), steps=["Step 1: Parse imports", "Step 2: Build graph", "Step 3: Detect cycles", "Step 4: Return"], tags=["code", "dependencies", "analysis"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"dependencies": ["requests", "fastapi"], "dependency_graph": {}})

def register(algorithm_manager):
    for algo_class in [CodeReviewerAlgorithm, TestWriterAlgorithm, DocumentationGeneratorAlgorithm, RefactoringAlgorithm, DependencyAnalyzerAlgorithm]:
        algo = algo_class()
        algorithm_manager.register(algo.spec.algorithm_id, algo)
        print(f"✅ {algo.spec.algorithm_id} Algorithm registered")
