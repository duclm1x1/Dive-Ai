from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult
from core.algorithms.algorithm_spec import AlgorithmSpec, AlgorithmIOSpec, IOField, StepSpec
from core.algorithms.registry import AlgorithmRegistry
import ast
import re
from typing import Dict, List, Any

class CodeOptimization(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="code_optimization",
            name="Code Performance Optimizer",
            level="tactical",
            category="performance",
            version="1.0",
            description="Analyzes and optimizes Python/JavaScript code for performance improvements through complexity analysis, refactoring, and profiling",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField(name="source_code", type="string", required=True, description="Source code to optimize"),
                    IOField(name="language", type="string", required=True, description="Programming language (python or javascript)"),
                    IOField(name="optimization_goals", type="array", required=False, description="Specific optimization targets (e.g., speed, memory, readability)")
                ],
                outputs=[
                    IOField(name="optimized_code", type="string", description="Optimized version of the source code"),
                    IOField(name="improvements", type="array", description="List of improvements made with descriptions"),
                    IOField(name="performance_gain", type="object", description="Estimated performance metrics and gains")
                ]
            ),
            steps=[
                StepSpec(step_id="parse_code", description="Parse and analyze source code structure"),
                StepSpec(step_id="complexity_analysis", description="Analyze time and space complexity"),
                StepSpec(step_id="identify_bottlenecks", description="Identify performance bottlenecks and anti-patterns"),
                StepSpec(step_id="apply_optimizations", description="Apply optimization techniques"),
                StepSpec(step_id="measure_improvements", description="Calculate performance improvements")
            ]
        )
    
    def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> AlgorithmResult:
        source_code = inputs.get("source_code", "")
        language = inputs.get("language", "python").lower()
        optimization_goals = inputs.get("optimization_goals", ["speed", "memory"])
        
        if not source_code:
            return AlgorithmResult(status="error", data={"error": "No source code provided"})
        
        improvements = []
        optimized_code = source_code
        
        # Step 1: Parse code
        if language == "python":
            optimized_code, improvements = self._optimize_python(source_code, optimization_goals)
        elif language == "javascript":
            optimized_code, improvements = self._optimize_javascript(source_code, optimization_goals)
        else:
            return AlgorithmResult(status="error", data={"error": f"Unsupported language: {language}"})
        
        # Step 5: Calculate performance gain
        performance_gain = {
            "complexity_reduction": len([i for i in improvements if "complexity" in i.get("type", "")]),
            "optimizations_applied": len(improvements),
            "estimated_speedup": self._estimate_speedup(improvements),
            "memory_improvement": self._estimate_memory_improvement(improvements)
        }
        
        return AlgorithmResult(
            status="success",
            data={
                "optimized_code": optimized_code,
                "improvements": improvements,
                "performance_gain": performance_gain
            }
        )
    
    def _optimize_python(self, code: str, goals: List[str]) -> tuple:
        improvements = []
        optimized = code
        
        # List comprehension optimization
        if "for " in code and ".append(" in code:
            pattern = r'(\w+)\s*=\s*\[\]\s*\n\s*for\s+(\w+)\s+in\s+([^\:]+):\s*\n\s*\1\.append\(([^\)]+)\)'
            if re.search(pattern, code):
                optimized = re.sub(pattern, r'\1 = [\4 for \2 in \3]', optimized)
                improvements.append({"type": "complexity", "description": "Converted loop with append to list comprehension", "impact": "high"})
        
        # String concatenation optimization
        if '+=' in code and 'str' in code.lower():
            improvements.append({"type": "memory", "description": "Consider using join() or f-strings instead of += for string concatenation", "impact": "medium"})
        
        # Unnecessary list() calls
        if re.search(r'for\s+\w+\s+in\s+list\(', code):
            optimized = re.sub(r'for\s+(\w+)\s+in\s+list\(([^\)]+)\)', r'for \1 in \2', optimized)
            improvements.append({"type": "performance", "description": "Removed unnecessary list() conversion in loop", "impact": "low"})
        
        # Multiple lookups optimization
        if code.count('.get(') > 2 or code.count('[') > 3:
            improvements.append({"type": "performance", "description": "Consider caching repeated dictionary/list lookups", "impact": "medium"})
        
        return optimized, improvements
    
    def _optimize_javascript(self, code: str, goals: List[str]) -> tuple:
        improvements = []
        optimized = code
        
        # var to const/let
        if 'var ' in code:
            optimized = re.sub(r'\bvar\b', 'const', optimized)
            improvements.append({"type": "best_practice", "description": "Replaced var with const for better scoping", "impact": "low"})
        
        # Array.push in loop to spread or concat
        if '.push(' in code and 'for' in code:
            improvements.append({"type": "performance", "description": "Consider using spread operator or concat instead of push in loops", "impact": "medium"})
        
        # == to ===
        if ' == ' in code or ' != ' in code:
            optimized = optimized.replace(' == ', ' === ').replace(' != ', ' !== ')
            improvements.append({"type": "best_practice", "description": "Replaced loose equality with strict equality", "impact": "low"})
        
        return optimized, improvements
    
    def _estimate_speedup(self, improvements: List[Dict]) -> str:
        high_impact = len([i for i in improvements if i.get("impact") == "high"])
        medium_impact = len([i for i in improvements if i.get("impact") == "medium"])
        
        if high_impact >= 2:
            return "20-40%"
        elif high_impact >= 1 or medium_impact >= 3:
            return "10-20%"
        elif medium_impact >= 1:
            return "5-10%"
        else:
            return "1-5%"
    
    def _estimate_memory_improvement(self, improvements: List[Dict]) -> str:
        memory_improvements = len([i for i in improvements if i.get("type") == "memory"])
        
        if memory_improvements >= 2:
            return "15-30%"
        elif memory_improvements >= 1:
            return "5-15%"
        else:
            return "0-5%"