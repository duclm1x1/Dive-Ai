#!/usr/bin/env python3
"""
Dive Thinking Engine - V22 Core Transformation

The Thinking Engine transforms Dive AI from reactive to cognitive.
This is the main component that orchestrates complexity analysis,
strategy selection, and adaptive execution.

This is an architectural transformation similar to how Advanced Search
transformed data access in V21.
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from core.dive_complexity_analyzer import (
    DiveComplexityAnalyzer,
    ComplexityAnalysis,
    ComplexityLevel
)
from core.dive_strategy_selector import (
    DiveStrategySelector,
    StrategySelection,
    ExecutionStrategy
)


@dataclass
class ThinkingStep:
    """A single step in the reasoning trace"""
    step_id: int
    timestamp: datetime
    description: str
    action: str
    result: Optional[Any] = None
    duration: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class ThinkingTrace:
    """Complete reasoning trace for a task"""
    task: str
    complexity_analysis: ComplexityAnalysis
    strategy_selection: StrategySelection
    steps: List[ThinkingStep] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    success: bool = False
    error: Optional[str] = None


@dataclass
class ThinkingResult:
    """Result of thinking engine execution"""
    result: Any
    trace: ThinkingTrace
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DiveThinkingEngine:
    """
    Cognitive reasoning engine for Dive AI V22.
    
    This transforms Dive AI from reactive orchestrator to cognitive
    reasoning system. It analyzes task complexity, selects appropriate
    execution strategy, and maintains full reasoning trace.
    
    Architectural Transformation:
    - Before (V21): task → execute → result
    - After (V22): task → analyze → strategize → execute with trace → result + artifacts
    """
    
    def __init__(self):
        self.complexity_analyzer = DiveComplexityAnalyzer()
        self.strategy_selector = DiveStrategySelector()
        self.execution_strategies = self._init_strategies()
        
    def _init_strategies(self) -> Dict[ExecutionStrategy, Callable]:
        """Initialize execution strategy handlers"""
        return {
            ExecutionStrategy.FAST_PATH: self._execute_fast_path,
            ExecutionStrategy.SLOW_PATH: self._execute_slow_path,
            ExecutionStrategy.ADAPTIVE_PATH: self._execute_adaptive_path,
            ExecutionStrategy.SLOW_PATH_ITERATIVE: self._execute_slow_path_iterative
        }
    
    def think(
        self,
        task: str,
        context: Optional[Dict] = None,
        constraints: Optional[Dict] = None,
        executor: Optional[Callable] = None
    ) -> ThinkingResult:
        """
        Main thinking method - analyzes, strategizes, and executes.
        
        Args:
            task: Task description
            context: Optional context (history, dependencies, etc.)
            constraints: Optional constraints (time, resources, etc.)
            executor: Optional custom executor function
            
        Returns:
            ThinkingResult with result, trace, and artifacts
        """
        
        # Step 1: Analyze complexity
        complexity_analysis = self.complexity_analyzer.analyze(task, context)
        
        # Step 2: Select strategy
        strategy_selection = self.strategy_selector.select(
            complexity_analysis, constraints
        )
        
        # Step 3: Create thinking trace
        trace = ThinkingTrace(
            task=task,
            complexity_analysis=complexity_analysis,
            strategy_selection=strategy_selection
        )
        
        # Step 4: Execute with selected strategy
        try:
            result, artifacts = self._execute_strategy(
                task=task,
                strategy_selection=strategy_selection,
                trace=trace,
                context=context,
                executor=executor
            )
            
            trace.success = True
            trace.end_time = datetime.now()
            trace.total_duration = (trace.end_time - trace.start_time).total_seconds()
            
            return ThinkingResult(
                result=result,
                trace=trace,
                artifacts=artifacts,
                metadata={
                    'complexity_level': complexity_analysis.level.value,
                    'strategy_used': strategy_selection.strategy.value,
                    'total_duration': trace.total_duration
                }
            )
            
        except Exception as e:
            trace.success = False
            trace.error = str(e)
            trace.end_time = datetime.now()
            trace.total_duration = (trace.end_time - trace.start_time).total_seconds()
            
            # Try fallback strategy if available
            if strategy_selection.fallback_strategy:
                return self._try_fallback(
                    task, context, constraints, executor,
                    strategy_selection.fallback_strategy, trace
                )
            
            raise
    
    def _execute_strategy(
        self,
        task: str,
        strategy_selection: StrategySelection,
        trace: ThinkingTrace,
        context: Optional[Dict],
        executor: Optional[Callable]
    ) -> tuple[Any, Dict]:
        """Execute task with selected strategy"""
        
        strategy = strategy_selection.strategy
        handler = self.execution_strategies[strategy]
        
        return handler(
            task=task,
            parameters=strategy_selection.parameters,
            trace=trace,
            context=context,
            executor=executor
        )
    
    def _execute_fast_path(
        self,
        task: str,
        parameters: Dict,
        trace: ThinkingTrace,
        context: Optional[Dict],
        executor: Optional[Callable]
    ) -> tuple[Any, Dict]:
        """Fast path: Direct execution, minimal overhead"""
        
        step = self._add_step(trace, "Execute fast path", "direct_execution")
        
        start = time.time()
        
        if executor:
            result = executor(task, context)
        else:
            result = f"Fast path execution: {task}"
        
        step.duration = time.time() - start
        step.result = "Success"
        
        artifacts = {}
        
        return result, artifacts
    
    def _execute_slow_path(
        self,
        task: str,
        parameters: Dict,
        trace: ThinkingTrace,
        context: Optional[Dict],
        executor: Optional[Callable]
    ) -> tuple[Any, Dict]:
        """Slow path: Deep reasoning with full trace"""
        
        # Step 1: Break down task
        step1 = self._add_step(trace, "Break down task", "task_decomposition")
        subtasks = self._decompose_task(task)
        step1.result = f"{len(subtasks)} subtasks"
        
        # Step 2: Plan execution
        step2 = self._add_step(trace, "Plan execution", "planning")
        plan = self._create_plan(subtasks)
        step2.result = "Execution plan created"
        
        # Step 3: Execute with reasoning
        step3 = self._add_step(trace, "Execute with reasoning", "execution")
        
        if executor:
            result = executor(task, context)
        else:
            result = f"Slow path execution: {task}"
        
        step3.result = "Success"
        
        # Step 4: Generate artifacts
        artifacts = self._generate_artifacts(task, result, trace)
        
        return result, artifacts
    
    def _execute_adaptive_path(
        self,
        task: str,
        parameters: Dict,
        trace: ThinkingTrace,
        context: Optional[Dict],
        executor: Optional[Callable]
    ) -> tuple[Any, Dict]:
        """Adaptive path: Mixed approach based on progress"""
        
        # Start with fast path
        step1 = self._add_step(trace, "Try fast path", "adaptive_fast")
        
        if executor:
            result = executor(task, context)
        else:
            result = f"Adaptive execution: {task}"
        
        step1.result = "Success"
        
        # Generate artifacts if needed
        artifacts = {}
        if parameters.get('enable_artifacts'):
            artifacts = self._generate_artifacts(task, result, trace)
        
        return result, artifacts
    
    def _execute_slow_path_iterative(
        self,
        task: str,
        parameters: Dict,
        trace: ThinkingTrace,
        context: Optional[Dict],
        executor: Optional[Callable]
    ) -> tuple[Any, Dict]:
        """Slow path iterative: Multiple iterations with refinement"""
        
        max_iterations = parameters.get('max_iterations', 5)
        
        result = None
        for i in range(max_iterations):
            step = self._add_step(
                trace,
                f"Iteration {i+1}/{max_iterations}",
                "iterative_execution"
            )
            
            if executor:
                result = executor(task, context)
            else:
                result = f"Iterative execution {i+1}: {task}"
            
            step.result = f"Iteration {i+1} complete"
            
            # Check if we should continue
            if self._should_stop_iteration(result, i, max_iterations):
                break
        
        # Generate comprehensive artifacts
        artifacts = self._generate_artifacts(task, result, trace)
        
        return result, artifacts
    
    def _add_step(
        self,
        trace: ThinkingTrace,
        description: str,
        action: str
    ) -> ThinkingStep:
        """Add a step to the reasoning trace"""
        
        step = ThinkingStep(
            step_id=len(trace.steps) + 1,
            timestamp=datetime.now(),
            description=description,
            action=action
        )
        
        trace.steps.append(step)
        return step
    
    def _decompose_task(self, task: str) -> List[str]:
        """Decompose task into subtasks"""
        # Simple decomposition for now
        return [task]
    
    def _create_plan(self, subtasks: List[str]) -> Dict:
        """Create execution plan"""
        return {
            'subtasks': subtasks,
            'order': 'sequential'
        }
    
    def _generate_artifacts(
        self,
        task: str,
        result: Any,
        trace: ThinkingTrace
    ) -> Dict[str, Any]:
        """Generate structured artifacts"""
        
        return {
            'task': task,
            'result': result,
            'reasoning_trace': {
                'steps': len(trace.steps),
                'duration': sum(s.duration for s in trace.steps),
                'complexity': trace.complexity_analysis.level.value
            }
        }
    
    def _should_stop_iteration(
        self,
        result: Any,
        iteration: int,
        max_iterations: int
    ) -> bool:
        """Determine if we should stop iterating"""
        # Simple check for now
        return iteration >= max_iterations - 1
    
    def _try_fallback(
        self,
        task: str,
        context: Optional[Dict],
        constraints: Optional[Dict],
        executor: Optional[Callable],
        fallback_strategy: ExecutionStrategy,
        original_trace: ThinkingTrace
    ) -> ThinkingResult:
        """Try fallback strategy if primary fails"""
        
        # Create new trace for fallback
        trace = ThinkingTrace(
            task=task,
            complexity_analysis=original_trace.complexity_analysis,
            strategy_selection=StrategySelection(
                strategy=fallback_strategy,
                reasoning="Fallback after primary strategy failed",
                parameters={},
                fallback_strategy=None
            )
        )
        
        # Execute fallback
        result, artifacts = self._execute_strategy(
            task=task,
            strategy_selection=trace.strategy_selection,
            trace=trace,
            context=context,
            executor=executor
        )
        
        trace.success = True
        trace.end_time = datetime.now()
        trace.total_duration = (trace.end_time - trace.start_time).total_seconds()
        
        return ThinkingResult(
            result=result,
            trace=trace,
            artifacts=artifacts,
            metadata={
                'fallback_used': True,
                'original_strategy': original_trace.strategy_selection.strategy.value,
                'fallback_strategy': fallback_strategy.value
            }
        )


def main():
    """Test thinking engine"""
    engine = DiveThinkingEngine()
    
    # Test tasks with different complexity levels
    test_tasks = [
        "List files",
        "Create a Python function",
        "Design and implement REST API",
        "Refactor entire codebase with testing"
    ]
    
    print("=== Dive Thinking Engine Test ===\n")
    
    for task in test_tasks:
        print(f"Task: {task}")
        
        # Think about the task
        result = engine.think(task)
        
        print(f"Complexity: {result.trace.complexity_analysis.level.value}")
        print(f"Strategy: {result.trace.strategy_selection.strategy.value}")
        print(f"Steps: {len(result.trace.steps)}")
        print(f"Duration: {result.trace.total_duration:.3f}s")
        print(f"Success: {result.trace.success}")
        
        print("\nReasoning trace:")
        for step in result.trace.steps:
            print(f"  {step.step_id}. {step.description} - {step.result}")
        
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()
