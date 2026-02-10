#!/usr/bin/env python3
"""
Dive Strategy Selector - V22 Thinking Engine Component

Selects execution strategy based on complexity analysis.
Part of the Thinking Engine transformation.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from core.dive_complexity_analyzer import ComplexityLevel, ComplexityAnalysis


class ExecutionStrategy(Enum):
    """Execution strategies"""
    FAST_PATH = "fast_path"                    # Direct execution
    SLOW_PATH = "slow_path"                    # Deep reasoning
    ADAPTIVE_PATH = "adaptive_path"            # Mixed approach
    SLOW_PATH_ITERATIVE = "slow_path_iterative"  # Iterative reasoning


@dataclass
class StrategySelection:
    """Result of strategy selection"""
    strategy: ExecutionStrategy
    reasoning: str
    parameters: Dict[str, Any]
    fallback_strategy: Optional[ExecutionStrategy]


class DiveStrategySelector:
    """
    Selects execution strategy based on task complexity.
    
    This enables Dive AI to adapt its execution approach based on
    the task at hand - a key part of cognitive reasoning.
    """
    
    def __init__(self):
        self.strategy_configs = {
            ExecutionStrategy.FAST_PATH: {
                'max_thinking_time': 1.0,
                'max_steps': 3,
                'enable_reasoning_trace': False,
                'enable_artifacts': False,
                'resource_allocation': 'minimal'
            },
            ExecutionStrategy.SLOW_PATH: {
                'max_thinking_time': 60.0,
                'max_steps': 10,
                'enable_reasoning_trace': True,
                'enable_artifacts': True,
                'resource_allocation': 'high'
            },
            ExecutionStrategy.ADAPTIVE_PATH: {
                'max_thinking_time': 10.0,
                'max_steps': 5,
                'enable_reasoning_trace': True,
                'enable_artifacts': True,
                'resource_allocation': 'medium'
            },
            ExecutionStrategy.SLOW_PATH_ITERATIVE: {
                'max_thinking_time': 300.0,
                'max_steps': 20,
                'enable_reasoning_trace': True,
                'enable_artifacts': True,
                'resource_allocation': 'maximum',
                'enable_iteration': True,
                'max_iterations': 5
            }
        }
    
    def select(
        self,
        complexity_analysis: ComplexityAnalysis,
        constraints: Optional[Dict] = None
    ) -> StrategySelection:
        """
        Select execution strategy based on complexity analysis.
        
        Args:
            complexity_analysis: Result from complexity analyzer
            constraints: Optional constraints (time, resources, etc.)
            
        Returns:
            StrategySelection with strategy and parameters
        """
        constraints = constraints or {}
        
        # Get recommended strategy from complexity analysis
        recommended = complexity_analysis.recommended_strategy
        
        # Map to ExecutionStrategy enum
        strategy = self._map_to_strategy(recommended)
        
        # Apply constraints
        strategy = self._apply_constraints(strategy, constraints)
        
        # Get strategy parameters
        parameters = self._get_parameters(strategy, complexity_analysis)
        
        # Determine fallback strategy
        fallback = self._determine_fallback(strategy)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            strategy, complexity_analysis, constraints
        )
        
        return StrategySelection(
            strategy=strategy,
            reasoning=reasoning,
            parameters=parameters,
            fallback_strategy=fallback
        )
    
    def _map_to_strategy(self, recommended: str) -> ExecutionStrategy:
        """Map recommended strategy string to enum"""
        mapping = {
            'fast_path': ExecutionStrategy.FAST_PATH,
            'slow_path': ExecutionStrategy.SLOW_PATH,
            'adaptive_path': ExecutionStrategy.ADAPTIVE_PATH,
            'slow_path_iterative': ExecutionStrategy.SLOW_PATH_ITERATIVE
        }
        return mapping.get(recommended, ExecutionStrategy.ADAPTIVE_PATH)
    
    def _apply_constraints(
        self,
        strategy: ExecutionStrategy,
        constraints: Dict
    ) -> ExecutionStrategy:
        """Apply constraints to strategy selection"""
        
        # Time constraint
        if 'max_time' in constraints:
            max_time = constraints['max_time']
            config = self.strategy_configs[strategy]
            
            if config['max_thinking_time'] > max_time:
                # Downgrade to faster strategy
                if strategy == ExecutionStrategy.SLOW_PATH_ITERATIVE:
                    strategy = ExecutionStrategy.SLOW_PATH
                elif strategy == ExecutionStrategy.SLOW_PATH:
                    strategy = ExecutionStrategy.ADAPTIVE_PATH
                elif strategy == ExecutionStrategy.ADAPTIVE_PATH:
                    strategy = ExecutionStrategy.FAST_PATH
        
        # Resource constraint
        if 'max_resources' in constraints:
            max_resources = constraints['max_resources']
            if max_resources == 'low':
                # Force fast path
                strategy = ExecutionStrategy.FAST_PATH
        
        return strategy
    
    def _get_parameters(
        self,
        strategy: ExecutionStrategy,
        complexity_analysis: ComplexityAnalysis
    ) -> Dict[str, Any]:
        """Get strategy-specific parameters"""
        
        # Start with base config
        parameters = self.strategy_configs[strategy].copy()
        
        # Adjust based on complexity
        if complexity_analysis.level == ComplexityLevel.VERY_COMPLEX:
            parameters['max_steps'] = int(parameters['max_steps'] * 1.5)
            parameters['max_thinking_time'] *= 1.5
        
        # Add complexity info
        parameters['complexity_level'] = complexity_analysis.level.value
        parameters['complexity_score'] = complexity_analysis.score
        
        return parameters
    
    def _determine_fallback(
        self,
        strategy: ExecutionStrategy
    ) -> Optional[ExecutionStrategy]:
        """Determine fallback strategy if primary fails"""
        
        fallbacks = {
            ExecutionStrategy.SLOW_PATH_ITERATIVE: ExecutionStrategy.SLOW_PATH,
            ExecutionStrategy.SLOW_PATH: ExecutionStrategy.ADAPTIVE_PATH,
            ExecutionStrategy.ADAPTIVE_PATH: ExecutionStrategy.FAST_PATH,
            ExecutionStrategy.FAST_PATH: None
        }
        
        return fallbacks.get(strategy)
    
    def _generate_reasoning(
        self,
        strategy: ExecutionStrategy,
        complexity_analysis: ComplexityAnalysis,
        constraints: Dict
    ) -> str:
        """Generate human-readable reasoning for strategy selection"""
        
        reasoning = f"Selected strategy: {strategy.value}\n"
        reasoning += f"Based on complexity: {complexity_analysis.level.value} "
        reasoning += f"(score: {complexity_analysis.score:.1f})\n"
        
        if constraints:
            reasoning += f"Constraints applied: {', '.join(constraints.keys())}\n"
        
        config = self.strategy_configs[strategy]
        reasoning += f"Configuration:\n"
        reasoning += f"  - Max thinking time: {config['max_thinking_time']}s\n"
        reasoning += f"  - Max steps: {config['max_steps']}\n"
        reasoning += f"  - Reasoning trace: {config['enable_reasoning_trace']}\n"
        reasoning += f"  - Artifacts: {config['enable_artifacts']}\n"
        
        return reasoning.strip()


def main():
    """Test strategy selector"""
    from core.dive_complexity_analyzer import DiveComplexityAnalyzer
    
    analyzer = DiveComplexityAnalyzer()
    selector = DiveStrategySelector()
    
    # Test cases
    test_tasks = [
        ("Simple task", "List files"),
        ("Medium task", "Create a Python function"),
        ("Complex task", "Design and implement REST API"),
        ("Very complex task", "Refactor entire codebase with testing and deployment")
    ]
    
    print("=== Dive Strategy Selector Test ===\n")
    
    for name, task in test_tasks:
        print(f"{name}: {task}")
        
        # Analyze complexity
        analysis = analyzer.analyze(task)
        
        # Select strategy
        selection = selector.select(analysis)
        
        print(f"Strategy: {selection.strategy.value}")
        print(f"Fallback: {selection.fallback_strategy.value if selection.fallback_strategy else 'None'}")
        print(f"Reasoning:\n{selection.reasoning}")
        print("-" * 80)
        print()
    
    # Test with constraints
    print("\n=== Testing with Constraints ===\n")
    task = "Design and implement REST API"
    analysis = analyzer.analyze(task)
    
    print(f"Task: {task}")
    print(f"Complexity: {analysis.level.value}\n")
    
    # No constraints
    selection = selector.select(analysis)
    print(f"No constraints: {selection.strategy.value}")
    
    # Time constraint
    selection = selector.select(analysis, {'max_time': 5.0})
    print(f"Max time 5s: {selection.strategy.value}")
    
    # Resource constraint
    selection = selector.select(analysis, {'max_resources': 'low'})
    print(f"Low resources: {selection.strategy.value}")


if __name__ == "__main__":
    main()
