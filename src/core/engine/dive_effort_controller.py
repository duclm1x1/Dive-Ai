#!/usr/bin/env python3
"""
Dive Effort Controller - V22 Thinking Engine Component

Controls resource allocation based on task complexity.
Part of the Thinking Engine transformation (Week 2).
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

from core.dive_complexity_analyzer import ComplexityLevel


class ResourceType(Enum):
    """Types of resources to allocate"""
    CPU = "cpu"
    MEMORY = "memory"
    TOKENS = "tokens"
    TIME = "time"


@dataclass
class ResourceBudget:
    """Resource budget for a task"""
    cpu_cores: int
    memory_mb: int
    max_tokens: int
    max_time_seconds: float
    priority: str


class DiveEffortController:
    """
    Controls resource allocation based on task complexity.
    
    This ensures that simple tasks don't waste resources while
    complex tasks get the resources they need for deep reasoning.
    """
    
    def __init__(self, total_resources: Optional[Dict] = None):
        """
        Initialize effort controller.
        
        Args:
            total_resources: Total available resources
        """
        self.total_resources = total_resources or {
            'cpu_cores': 4,
            'memory_mb': 8192,
            'max_tokens': 100000,
            'max_time_seconds': 300
        }
        
        self.allocation_profiles = {
            ComplexityLevel.SIMPLE: {
                'cpu_ratio': 0.25,
                'memory_ratio': 0.25,
                'token_ratio': 0.1,
                'time_ratio': 0.05,
                'priority': 'low'
            },
            ComplexityLevel.MEDIUM: {
                'cpu_ratio': 0.5,
                'memory_ratio': 0.5,
                'token_ratio': 0.3,
                'time_ratio': 0.2,
                'priority': 'medium'
            },
            ComplexityLevel.COMPLEX: {
                'cpu_ratio': 0.75,
                'memory_ratio': 0.75,
                'token_ratio': 0.6,
                'time_ratio': 0.5,
                'priority': 'high'
            },
            ComplexityLevel.VERY_COMPLEX: {
                'cpu_ratio': 1.0,
                'memory_ratio': 1.0,
                'token_ratio': 1.0,
                'time_ratio': 1.0,
                'priority': 'critical'
            }
        }
        
        self.current_allocations = []
    
    def allocate(
        self,
        complexity_level: ComplexityLevel,
        task_id: Optional[str] = None
    ) -> ResourceBudget:
        """
        Allocate resources for a task based on complexity.
        
        Args:
            complexity_level: Task complexity level
            task_id: Optional task identifier
            
        Returns:
            ResourceBudget with allocated resources
        """
        
        profile = self.allocation_profiles[complexity_level]
        
        budget = ResourceBudget(
            cpu_cores=max(1, int(self.total_resources['cpu_cores'] * profile['cpu_ratio'])),
            memory_mb=int(self.total_resources['memory_mb'] * profile['memory_ratio']),
            max_tokens=int(self.total_resources['max_tokens'] * profile['token_ratio']),
            max_time_seconds=self.total_resources['max_time_seconds'] * profile['time_ratio'],
            priority=profile['priority']
        )
        
        # Record allocation
        self.current_allocations.append({
            'task_id': task_id,
            'complexity': complexity_level.value,
            'budget': budget
        })
        
        return budget
    
    def adjust_allocation(
        self,
        current_budget: ResourceBudget,
        progress: float,
        remaining_work: float
    ) -> ResourceBudget:
        """
        Dynamically adjust resource allocation based on progress.
        
        Args:
            current_budget: Current resource budget
            progress: Progress percentage (0-1)
            remaining_work: Estimated remaining work (0-1)
            
        Returns:
            Adjusted ResourceBudget
        """
        
        # If making good progress, maintain current allocation
        if progress > 0.5 and remaining_work < 0.5:
            return current_budget
        
        # If slow progress, increase allocation
        if progress < 0.3 and remaining_work > 0.7:
            return ResourceBudget(
                cpu_cores=min(self.total_resources['cpu_cores'], current_budget.cpu_cores + 1),
                memory_mb=int(current_budget.memory_mb * 1.2),
                max_tokens=int(current_budget.max_tokens * 1.2),
                max_time_seconds=current_budget.max_time_seconds * 1.5,
                priority='high'
            )
        
        # If almost done, can reduce allocation
        if progress > 0.8:
            return ResourceBudget(
                cpu_cores=max(1, current_budget.cpu_cores - 1),
                memory_mb=int(current_budget.memory_mb * 0.8),
                max_tokens=int(current_budget.max_tokens * 0.8),
                max_time_seconds=current_budget.max_time_seconds,
                priority='low'
            )
        
        return current_budget
    
    def release(self, task_id: Optional[str] = None):
        """Release resources for a completed task"""
        
        if task_id:
            self.current_allocations = [
                a for a in self.current_allocations
                if a['task_id'] != task_id
            ]
    
    def get_available_resources(self) -> Dict:
        """Get currently available resources"""
        
        # Calculate used resources
        used = {
            'cpu_cores': sum(a['budget'].cpu_cores for a in self.current_allocations),
            'memory_mb': sum(a['budget'].memory_mb for a in self.current_allocations),
            'max_tokens': sum(a['budget'].max_tokens for a in self.current_allocations)
        }
        
        # Calculate available
        available = {
            'cpu_cores': max(0, self.total_resources['cpu_cores'] - used['cpu_cores']),
            'memory_mb': max(0, self.total_resources['memory_mb'] - used['memory_mb']),
            'max_tokens': max(0, self.total_resources['max_tokens'] - used['max_tokens'])
        }
        
        return available
    
    def get_allocation_stats(self) -> Dict:
        """Get allocation statistics"""
        
        if not self.current_allocations:
            return {
                'active_tasks': 0,
                'total_cpu_used': 0,
                'total_memory_used': 0,
                'total_tokens_used': 0
            }
        
        return {
            'active_tasks': len(self.current_allocations),
            'total_cpu_used': sum(a['budget'].cpu_cores for a in self.current_allocations),
            'total_memory_used': sum(a['budget'].memory_mb for a in self.current_allocations),
            'total_tokens_used': sum(a['budget'].max_tokens for a in self.current_allocations),
            'by_complexity': {
                level.value: len([a for a in self.current_allocations if a['complexity'] == level.value])
                for level in ComplexityLevel
            }
        }


def main():
    """Test effort controller"""
    controller = DiveEffortController()
    
    print("=== Dive Effort Controller Test ===\n")
    
    # Test allocation for different complexity levels
    for level in ComplexityLevel:
        print(f"Complexity: {level.value}")
        budget = controller.allocate(level, f"task_{level.value}")
        print(f"CPU cores: {budget.cpu_cores}")
        print(f"Memory: {budget.memory_mb} MB")
        print(f"Max tokens: {budget.max_tokens}")
        print(f"Max time: {budget.max_time_seconds}s")
        print(f"Priority: {budget.priority}")
        print("-" * 80)
        print()
    
    # Show allocation stats
    print("\n=== Allocation Statistics ===")
    stats = controller.get_allocation_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Show available resources
    print("\n=== Available Resources ===")
    available = controller.get_available_resources()
    for key, value in available.items():
        print(f"{key}: {value}")
    
    # Test dynamic adjustment
    print("\n=== Dynamic Adjustment Test ===")
    budget = controller.allocate(ComplexityLevel.MEDIUM, "test_task")
    print(f"Initial budget: {budget.cpu_cores} cores, {budget.max_tokens} tokens")
    
    # Slow progress - should increase
    adjusted = controller.adjust_allocation(budget, progress=0.2, remaining_work=0.8)
    print(f"After slow progress: {adjusted.cpu_cores} cores, {adjusted.max_tokens} tokens")
    
    # Good progress - should maintain
    adjusted = controller.adjust_allocation(budget, progress=0.6, remaining_work=0.4)
    print(f"After good progress: {adjusted.cpu_cores} cores, {adjusted.max_tokens} tokens")
    
    # Almost done - should reduce
    adjusted = controller.adjust_allocation(budget, progress=0.9, remaining_work=0.1)
    print(f"After almost done: {adjusted.cpu_cores} cores, {adjusted.max_tokens} tokens")


if __name__ == "__main__":
    main()
