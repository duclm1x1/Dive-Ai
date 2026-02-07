#!/usr/bin/env python3
"""
Dive Dual Router - V22 Thinking Engine Component

Routes tasks to fast or slow path based on complexity and strategy.
Part of the Thinking Engine transformation (Week 2).
"""

from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from core.dive_complexity_analyzer import ComplexityLevel
from core.dive_strategy_selector import ExecutionStrategy
from core.dive_thinking_engine import ThinkingResult, ThinkingTrace


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    path: str  # 'fast' or 'slow'
    reasoning: str
    estimated_time: float
    resource_allocation: str


class DiveDualRouter:
    """
    Routes tasks to appropriate execution path.
    
    The dual router is a key optimization that allows Dive AI to
    handle simple tasks quickly while dedicating resources to
    complex tasks that need deep reasoning.
    """
    
    def __init__(self):
        self.fast_path_threshold = ComplexityLevel.MEDIUM
        self.routing_stats = {
            'fast_path_count': 0,
            'slow_path_count': 0,
            'total_fast_time': 0.0,
            'total_slow_time': 0.0
        }
    
    def route(
        self,
        complexity_level: ComplexityLevel,
        strategy: ExecutionStrategy,
        task: str
    ) -> RoutingDecision:
        """
        Determine routing path based on complexity and strategy.
        
        Args:
            complexity_level: Task complexity level
            strategy: Selected execution strategy
            task: Task description
            
        Returns:
            RoutingDecision with path and reasoning
        """
        
        # Determine path
        if self._should_use_fast_path(complexity_level, strategy):
            path = 'fast'
            estimated_time = 0.5
            resource_allocation = 'minimal'
            reasoning = "Task is simple enough for fast path execution"
        else:
            path = 'slow'
            estimated_time = self._estimate_slow_path_time(complexity_level)
            resource_allocation = self._determine_resource_allocation(complexity_level)
            reasoning = "Task requires deep reasoning on slow path"
        
        return RoutingDecision(
            path=path,
            reasoning=reasoning,
            estimated_time=estimated_time,
            resource_allocation=resource_allocation
        )
    
    def _should_use_fast_path(
        self,
        complexity_level: ComplexityLevel,
        strategy: ExecutionStrategy
    ) -> bool:
        """Determine if task should use fast path"""
        
        # Fast path strategies always use fast path
        if strategy == ExecutionStrategy.FAST_PATH:
            return True
        
        # Simple tasks can use fast path even with other strategies
        if complexity_level == ComplexityLevel.SIMPLE:
            return True
        
        # All other cases use slow path
        return False
    
    def _estimate_slow_path_time(self, complexity_level: ComplexityLevel) -> float:
        """Estimate time for slow path execution"""
        
        time_estimates = {
            ComplexityLevel.SIMPLE: 1.0,
            ComplexityLevel.MEDIUM: 5.0,
            ComplexityLevel.COMPLEX: 30.0,
            ComplexityLevel.VERY_COMPLEX: 120.0
        }
        
        return time_estimates.get(complexity_level, 10.0)
    
    def _determine_resource_allocation(self, complexity_level: ComplexityLevel) -> str:
        """Determine resource allocation level"""
        
        allocations = {
            ComplexityLevel.SIMPLE: 'minimal',
            ComplexityLevel.MEDIUM: 'medium',
            ComplexityLevel.COMPLEX: 'high',
            ComplexityLevel.VERY_COMPLEX: 'maximum'
        }
        
        return allocations.get(complexity_level, 'medium')
    
    def record_execution(self, path: str, duration: float):
        """Record execution statistics"""
        
        if path == 'fast':
            self.routing_stats['fast_path_count'] += 1
            self.routing_stats['total_fast_time'] += duration
        else:
            self.routing_stats['slow_path_count'] += 1
            self.routing_stats['total_slow_time'] += duration
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        
        total_count = (
            self.routing_stats['fast_path_count'] +
            self.routing_stats['slow_path_count']
        )
        
        if total_count == 0:
            return self.routing_stats
        
        stats = self.routing_stats.copy()
        stats['fast_path_percentage'] = (
            self.routing_stats['fast_path_count'] / total_count * 100
        )
        stats['avg_fast_time'] = (
            self.routing_stats['total_fast_time'] / 
            max(1, self.routing_stats['fast_path_count'])
        )
        stats['avg_slow_time'] = (
            self.routing_stats['total_slow_time'] / 
            max(1, self.routing_stats['slow_path_count'])
        )
        
        return stats


def main():
    """Test dual router"""
    from core.dive_complexity_analyzer import DiveComplexityAnalyzer
    from core.dive_strategy_selector import DiveStrategySelector
    
    analyzer = DiveComplexityAnalyzer()
    selector = DiveStrategySelector()
    router = DiveDualRouter()
    
    # Test tasks
    test_tasks = [
        "List files",
        "Create a Python function",
        "Design REST API",
        "Refactor entire codebase"
    ]
    
    print("=== Dive Dual Router Test ===\n")
    
    for task in test_tasks:
        print(f"Task: {task}")
        
        # Analyze and select strategy
        analysis = analyzer.analyze(task)
        selection = selector.select(analysis)
        
        # Route
        decision = router.route(
            analysis.level,
            selection.strategy,
            task
        )
        
        print(f"Complexity: {analysis.level.value}")
        print(f"Strategy: {selection.strategy.value}")
        print(f"Path: {decision.path}")
        print(f"Estimated time: {decision.estimated_time}s")
        print(f"Resources: {decision.resource_allocation}")
        print(f"Reasoning: {decision.reasoning}")
        print("-" * 80)
        print()
    
    # Show stats
    print("\n=== Routing Statistics ===")
    stats = router.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
