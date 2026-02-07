#!/usr/bin/env python3
"""
Dive Complexity Analyzer - V22 Thinking Engine Component

Analyzes task complexity to determine execution strategy.
Part of the Thinking Engine transformation.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class ComplexityLevel(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"          # Direct execution, < 1s
    MEDIUM = "medium"          # Multi-step planning, < 10s
    COMPLEX = "complex"        # Iterative reasoning, > 10s
    VERY_COMPLEX = "very_complex"  # Deep reasoning, > 60s


@dataclass
class ComplexityAnalysis:
    """Result of complexity analysis"""
    level: ComplexityLevel
    score: float  # 0-100
    factors: Dict[str, float]
    reasoning: str
    estimated_time: float  # seconds
    recommended_strategy: str


class DiveComplexityAnalyzer:
    """
    Analyzes task complexity to guide execution strategy.
    
    This is a key component of the Thinking Engine transformation,
    enabling Dive AI to be self-aware of task complexity.
    """
    
    def __init__(self):
        self.complexity_thresholds = {
            ComplexityLevel.SIMPLE: (0, 25),
            ComplexityLevel.MEDIUM: (25, 50),
            ComplexityLevel.COMPLEX: (50, 75),
            ComplexityLevel.VERY_COMPLEX: (75, 100)
        }
        
    def analyze(self, task: str, context: Optional[Dict] = None) -> ComplexityAnalysis:
        """
        Analyze task complexity.
        
        Args:
            task: Task description
            context: Optional context (history, dependencies, etc.)
            
        Returns:
            ComplexityAnalysis with level, score, and recommendations
        """
        context = context or {}
        
        # Calculate complexity factors
        factors = self._calculate_factors(task, context)
        
        # Calculate overall score
        score = self._calculate_score(factors)
        
        # Determine complexity level
        level = self._determine_level(score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(factors, level)
        
        # Estimate time
        estimated_time = self._estimate_time(level, factors)
        
        # Recommend strategy
        recommended_strategy = self._recommend_strategy(level, factors)
        
        return ComplexityAnalysis(
            level=level,
            score=score,
            factors=factors,
            reasoning=reasoning,
            estimated_time=estimated_time,
            recommended_strategy=recommended_strategy
        )
    
    def _calculate_factors(self, task: str, context: Dict) -> Dict[str, float]:
        """Calculate individual complexity factors"""
        factors = {}
        
        # Factor 1: Task length (0-20 points)
        task_length = len(task)
        factors['task_length'] = min(20, task_length / 50)
        
        # Factor 2: Number of steps (0-20 points)
        step_keywords = ['first', 'then', 'next', 'after', 'finally', 'step']
        step_count = sum(1 for kw in step_keywords if kw in task.lower())
        factors['step_count'] = min(20, step_count * 5)
        
        # Factor 3: Technical complexity (0-20 points)
        tech_keywords = [
            'algorithm', 'optimize', 'refactor', 'architecture',
            'design', 'implement', 'integrate', 'analyze'
        ]
        tech_count = sum(1 for kw in tech_keywords if kw in task.lower())
        factors['technical_complexity'] = min(20, tech_count * 4)
        
        # Factor 4: Multiple domains (0-15 points)
        domains = ['code', 'database', 'api', 'ui', 'test', 'deploy', 'document']
        domain_count = sum(1 for d in domains if d in task.lower())
        factors['domain_count'] = min(15, domain_count * 3)
        
        # Factor 5: Dependencies (0-15 points)
        dependency_keywords = ['depend', 'require', 'need', 'must', 'should']
        dep_count = sum(1 for kw in dependency_keywords if kw in task.lower())
        factors['dependencies'] = min(15, dep_count * 3)
        
        # Factor 6: Uncertainty (0-10 points)
        uncertainty_keywords = ['maybe', 'possibly', 'might', 'could', 'unclear', 'unknown']
        uncertainty_count = sum(1 for kw in uncertainty_keywords if kw in task.lower())
        factors['uncertainty'] = min(10, uncertainty_count * 5)
        
        # Factor 7: Context complexity (0-10 points from context)
        if context:
            context_size = len(str(context))
            factors['context_complexity'] = min(10, context_size / 500)
        else:
            factors['context_complexity'] = 0
        
        return factors
    
    def _calculate_score(self, factors: Dict[str, float]) -> float:
        """Calculate overall complexity score (0-100)"""
        return sum(factors.values())
    
    def _determine_level(self, score: float) -> ComplexityLevel:
        """Determine complexity level from score"""
        for level, (min_score, max_score) in self.complexity_thresholds.items():
            if min_score <= score < max_score:
                return level
        return ComplexityLevel.VERY_COMPLEX
    
    def _generate_reasoning(self, factors: Dict[str, float], level: ComplexityLevel) -> str:
        """Generate human-readable reasoning"""
        top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:3]
        
        reasoning = f"Task complexity: {level.value}\n"
        reasoning += "Key factors:\n"
        for factor, score in top_factors:
            if score > 0:
                reasoning += f"  - {factor.replace('_', ' ').title()}: {score:.1f} points\n"
        
        return reasoning.strip()
    
    def _estimate_time(self, level: ComplexityLevel, factors: Dict[str, float]) -> float:
        """Estimate execution time in seconds"""
        base_times = {
            ComplexityLevel.SIMPLE: 0.5,
            ComplexityLevel.MEDIUM: 5.0,
            ComplexityLevel.COMPLEX: 30.0,
            ComplexityLevel.VERY_COMPLEX: 120.0
        }
        
        base_time = base_times[level]
        
        # Adjust based on specific factors
        if factors.get('dependencies', 0) > 10:
            base_time *= 1.5
        if factors.get('uncertainty', 0) > 5:
            base_time *= 1.3
        
        return base_time
    
    def _recommend_strategy(self, level: ComplexityLevel, factors: Dict[str, float]) -> str:
        """Recommend execution strategy"""
        if level == ComplexityLevel.SIMPLE:
            return "fast_path"
        elif level == ComplexityLevel.MEDIUM:
            if factors.get('uncertainty', 0) > 5:
                return "adaptive_path"
            return "fast_path"
        elif level == ComplexityLevel.COMPLEX:
            return "slow_path"
        else:  # VERY_COMPLEX
            return "slow_path_iterative"


def main():
    """Test complexity analyzer"""
    analyzer = DiveComplexityAnalyzer()
    
    # Test cases
    test_tasks = [
        "List files in current directory",
        "Create a Python function to calculate fibonacci numbers",
        "Design and implement a complete REST API with authentication, database integration, and comprehensive testing",
        "Refactor the codebase to improve performance, then update documentation, and finally deploy to production"
    ]
    
    print("=== Dive Complexity Analyzer Test ===\n")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"Task {i}: {task}")
        analysis = analyzer.analyze(task)
        print(f"Level: {analysis.level.value}")
        print(f"Score: {analysis.score:.1f}")
        print(f"Strategy: {analysis.recommended_strategy}")
        print(f"Estimated time: {analysis.estimated_time:.1f}s")
        print(f"Reasoning:\n{analysis.reasoning}")
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()
