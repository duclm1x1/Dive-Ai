#!/usr/bin/env python3
"""
Dive Orchestrator V22 - Integrated with Thinking Engine

This is the V22 orchestrator that integrates the Thinking Engine
transformation with the existing V21 search-driven architecture.

Architectural Evolution:
- V20: Simple orchestration
- V21: Search-driven orchestration (Advanced Search)
- V22: Cognitive orchestration (Thinking Engine)
"""

import sys
from typing import Dict, Optional, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.dive_thinking_engine import DiveThinkingEngine, ThinkingResult
from core.dive_complexity_analyzer import DiveComplexityAnalyzer
from core.dive_strategy_selector import DiveStrategySelector
from core.dive_dual_router import DiveDualRouter
from core.dive_effort_controller import DiveEffortController
from core.dive_reasoning_trace import DiveReasoningTrace
from core.dive_artifact_manager import DiveArtifactManager, ArtifactType


class DiveOrchestratorV22:
    """
    V22 Orchestrator with Thinking Engine integration.
    
    This orchestrator combines:
    - V21 Search Engine (fast context retrieval)
    - V22 Thinking Engine (cognitive reasoning)
    
    Result: Fast + Intelligent orchestration
    """
    
    def __init__(self):
        # V22 Thinking Engine components
        self.thinking_engine = DiveThinkingEngine()
        self.complexity_analyzer = DiveComplexityAnalyzer()
        self.strategy_selector = DiveStrategySelector()
        self.dual_router = DiveDualRouter()
        self.effort_controller = DiveEffortController()
        self.artifact_manager = DiveArtifactManager()
        
        # V21 Search Engine (would be initialized here if available)
        self.search_engine = None  # Placeholder
        
        # Statistics
        self.stats = {
            'tasks_processed': 0,
            'fast_path_count': 0,
            'slow_path_count': 0,
            'total_thinking_time': 0.0,
            'artifacts_created': 0
        }
    
    def orchestrate(
        self,
        task: str,
        context: Optional[Dict] = None,
        constraints: Optional[Dict] = None
    ) -> ThinkingResult:
        """
        Orchestrate task execution with cognitive reasoning.
        
        Args:
            task: Task description
            context: Optional context
            constraints: Optional constraints
            
        Returns:
            ThinkingResult with result, trace, and artifacts
        """
        
        # Update stats
        self.stats['tasks_processed'] += 1
        
        # Step 1: Use thinking engine to analyze and execute
        result = self.thinking_engine.think(
            task=task,
            context=context,
            constraints=constraints,
            executor=self._execute_task
        )
        
        # Step 2: Update routing stats
        if result.trace.strategy_selection.strategy.value.startswith('fast'):
            self.stats['fast_path_count'] += 1
        else:
            self.stats['slow_path_count'] += 1
        
        # Step 3: Update thinking time
        self.stats['total_thinking_time'] += result.trace.total_duration
        
        # Step 4: Update artifact count
        self.stats['artifacts_created'] += len(result.artifacts)
        
        return result
    
    def _execute_task(self, task: str, context: Optional[Dict]) -> Any:
        """
        Execute task (placeholder for actual execution).
        
        In real implementation, this would:
        1. Use search engine to retrieve context
        2. Call appropriate tools/APIs
        3. Generate code/documents
        4. Return results
        """
        # Placeholder implementation
        return f"Executed: {task}"
    
    def analyze_task(self, task: str) -> Dict:
        """
        Analyze task without executing.
        
        Returns:
            Analysis with complexity, strategy, routing, and resources
        """
        # Analyze complexity
        complexity = self.complexity_analyzer.analyze(task)
        
        # Select strategy
        strategy = self.strategy_selector.select(complexity)
        
        # Determine routing
        routing = self.dual_router.route(
            complexity.level,
            strategy.strategy,
            task
        )
        
        # Allocate resources
        resources = self.effort_controller.allocate(complexity.level)
        
        return {
            'complexity': {
                'level': complexity.level.value,
                'score': complexity.score,
                'estimated_time': complexity.estimated_time
            },
            'strategy': {
                'name': strategy.strategy.value,
                'parameters': strategy.parameters
            },
            'routing': {
                'path': routing.path,
                'reasoning': routing.reasoning
            },
            'resources': {
                'cpu_cores': resources.cpu_cores,
                'memory_mb': resources.memory_mb,
                'max_tokens': resources.max_tokens,
                'priority': resources.priority
            }
        }
    
    def get_stats(self) -> Dict:
        """Get orchestration statistics"""
        stats = self.stats.copy()
        
        if stats['tasks_processed'] > 0:
            stats['avg_thinking_time'] = (
                stats['total_thinking_time'] / stats['tasks_processed']
            )
            stats['fast_path_percentage'] = (
                stats['fast_path_count'] / stats['tasks_processed'] * 100
            )
        
        return stats


def main():
    """Test V22 orchestrator"""
    print("=== Dive Orchestrator V22 Test ===\n")
    
    orchestrator = DiveOrchestratorV22()
    
    # Test tasks
    test_tasks = [
        "List files in current directory",
        "Create a Python function to calculate fibonacci",
        "Design and implement a REST API with authentication",
        "Refactor the entire codebase, update tests, and deploy"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'='*80}")
        print(f"Task {i}: {task}")
        print('='*80)
        
        # Analyze task
        print("\n--- Analysis ---")
        analysis = orchestrator.analyze_task(task)
        print(f"Complexity: {analysis['complexity']['level']} (score: {analysis['complexity']['score']:.1f})")
        print(f"Strategy: {analysis['strategy']['name']}")
        print(f"Routing: {analysis['routing']['path']} path")
        print(f"Resources: {analysis['resources']['cpu_cores']} cores, {analysis['resources']['max_tokens']} tokens")
        
        # Execute task
        print("\n--- Execution ---")
        result = orchestrator.orchestrate(task)
        print(f"Success: {result.trace.success}")
        print(f"Duration: {result.trace.total_duration:.3f}s")
        print(f"Steps: {len(result.trace.steps)}")
        print(f"Artifacts: {len(result.artifacts)}")
        
        # Show reasoning trace
        print("\n--- Reasoning Trace ---")
        for step in result.trace.steps:
            print(f"  {step.step_id}. {step.description} - {step.result}")
    
    # Show overall stats
    print(f"\n\n{'='*80}")
    print("=== Overall Statistics ===")
    print('='*80)
    stats = orchestrator.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
