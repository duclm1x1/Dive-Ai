#!/usr/bin/env python3
"""
Dive Distributed Execution - V23.1 Component

Advanced parallel strategies and distributed execution for Dive AI.
Supports work stealing, adaptive scheduling, and load balancing.
"""

import time
import concurrent.futures
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from queue import Queue, Empty
import threading


class SchedulingStrategy(Enum):
    """Parallel execution strategies"""
    STATIC = "static"  # Fixed assignment
    DYNAMIC = "dynamic"  # Work stealing
    ADAPTIVE = "adaptive"  # Adaptive based on load
    DISTRIBUTED = "distributed"  # Multi-machine


@dataclass
class Task:
    """A task to execute"""
    id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 0
    estimated_duration: float = 1.0


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    success: bool
    result: Optional[any] = None
    error: Optional[str] = None
    duration: float = 0.0
    worker_id: int = 0


class WorkStealingExecutor:
    """
    Work stealing executor for load balancing.
    
    Workers steal tasks from each other when idle.
    """
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.queues = [Queue() for _ in range(num_workers)]
        self.results: List[TaskResult] = []
        self.stats = {
            'tasks_executed': 0,
            'tasks_stolen': 0,
            'total_time': 0.0
        }
    
    def execute(self, tasks: List[Task]) -> List[TaskResult]:
        """Execute tasks with work stealing"""
        start_time = time.time()
        
        # Distribute tasks initially
        for i, task in enumerate(tasks):
            self.queues[i % self.num_workers].put(task)
        
        # Start workers
        results_lock = threading.Lock()
        
        def worker(worker_id: int):
            while True:
                # Try to get task from own queue
                task = None
                try:
                    task = self.queues[worker_id].get(timeout=0.01)
                except Empty:
                    # Try to steal from other workers
                    for other_id in range(self.num_workers):
                        if other_id != worker_id:
                            try:
                                task = self.queues[other_id].get(timeout=0.01)
                                with results_lock:
                                    self.stats['tasks_stolen'] += 1
                                break
                            except Empty:
                                continue
                
                if task is None:
                    # Check if all queues are empty
                    if all(q.empty() for q in self.queues):
                        break
                    continue
                
                # Execute task
                task_start = time.time()
                try:
                    kwargs = task.kwargs or {}
                    result = task.func(*task.args, **kwargs)
                    task_result = TaskResult(
                        task_id=task.id,
                        success=True,
                        result=result,
                        duration=time.time() - task_start,
                        worker_id=worker_id
                    )
                except Exception as e:
                    task_result = TaskResult(
                        task_id=task.id,
                        success=False,
                        error=str(e),
                        duration=time.time() - task_start,
                        worker_id=worker_id
                    )
                
                with results_lock:
                    self.results.append(task_result)
                    self.stats['tasks_executed'] += 1
        
        # Run workers
        threads = []
        for i in range(self.num_workers):
            t = threading.Thread(target=worker, args=(i,))
            t.start()
            threads.append(t)
        
        # Wait for completion
        for t in threads:
            t.join()
        
        self.stats['total_time'] = time.time() - start_time
        
        return self.results


class AdaptiveScheduler:
    """
    Adaptive scheduler that adjusts based on system load.
    
    Monitors worker performance and adjusts task assignment.
    """
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.worker_loads = [0.0] * num_workers
        self.worker_speeds = [1.0] * num_workers  # Relative speed
        self.stats = {
            'tasks_executed': 0,
            'load_adjustments': 0,
            'total_time': 0.0
        }
    
    def execute(self, tasks: List[Task]) -> List[TaskResult]:
        """Execute tasks with adaptive scheduling"""
        start_time = time.time()
        
        # Sort tasks by priority and estimated duration
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (-t.priority, -t.estimated_duration)
        )
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {}
            
            for task in sorted_tasks:
                # Find worker with lowest load
                worker_id = self._select_worker()
                
                # Submit task
                future = executor.submit(self._execute_task, task, worker_id)
                futures[future] = (task, worker_id)
                
                # Update load
                self.worker_loads[worker_id] += task.estimated_duration
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                task, worker_id = futures[future]
                result = future.result()
                results.append(result)
                
                # Update worker speed based on actual vs estimated
                actual_duration = result.duration
                estimated_duration = task.estimated_duration
                if estimated_duration > 0:
                    speed_factor = estimated_duration / actual_duration
                    self.worker_speeds[worker_id] = \
                        0.9 * self.worker_speeds[worker_id] + 0.1 * speed_factor
                    self.stats['load_adjustments'] += 1
                
                # Update load
                self.worker_loads[worker_id] -= task.estimated_duration
                self.stats['tasks_executed'] += 1
        
        self.stats['total_time'] = time.time() - start_time
        
        return results
    
    def _select_worker(self) -> int:
        """Select worker with lowest adjusted load"""
        adjusted_loads = [
            load / speed
            for load, speed in zip(self.worker_loads, self.worker_speeds)
        ]
        return adjusted_loads.index(min(adjusted_loads))
    
    def _execute_task(self, task: Task, worker_id: int) -> TaskResult:
        """Execute a single task"""
        start_time = time.time()
        
        try:
            kwargs = task.kwargs or {}
            result = task.func(*task.args, **kwargs)
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                duration=time.time() - start_time,
                worker_id=worker_id
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                duration=time.time() - start_time,
                worker_id=worker_id
            )


class DiveDistributedExecution:
    """
    Main distributed execution system.
    
    Supports multiple strategies and can switch dynamically.
    """
    
    def __init__(
        self,
        strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE,
        num_workers: int = 4
    ):
        self.strategy = strategy
        self.num_workers = num_workers
        self.stats = {
            'total_executions': 0,
            'by_strategy': {s.value: 0 for s in SchedulingStrategy}
        }
    
    def execute(
        self,
        tasks: List[Task],
        strategy: Optional[SchedulingStrategy] = None
    ) -> List[TaskResult]:
        """
        Execute tasks using specified strategy.
        
        Args:
            tasks: List of tasks to execute
            strategy: Override default strategy
            
        Returns:
            List of TaskResults
        """
        exec_strategy = strategy or self.strategy
        
        if exec_strategy == SchedulingStrategy.STATIC:
            results = self._execute_static(tasks)
        elif exec_strategy == SchedulingStrategy.DYNAMIC:
            results = self._execute_work_stealing(tasks)
        elif exec_strategy == SchedulingStrategy.ADAPTIVE:
            results = self._execute_adaptive(tasks)
        elif exec_strategy == SchedulingStrategy.DISTRIBUTED:
            results = self._execute_distributed(tasks)
        else:
            raise ValueError(f"Unknown strategy: {exec_strategy}")
        
        self.stats['total_executions'] += 1
        self.stats['by_strategy'][exec_strategy.value] += 1
        
        return results
    
    def _execute_static(self, tasks: List[Task]) -> List[TaskResult]:
        """Static assignment - simple ThreadPoolExecutor"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(self._run_task, task): task
                for task in tasks
            }
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return results
    
    def _execute_work_stealing(self, tasks: List[Task]) -> List[TaskResult]:
        """Work stealing execution"""
        executor = WorkStealingExecutor(num_workers=self.num_workers)
        return executor.execute(tasks)
    
    def _execute_adaptive(self, tasks: List[Task]) -> List[TaskResult]:
        """Adaptive scheduling"""
        scheduler = AdaptiveScheduler(num_workers=self.num_workers)
        return scheduler.execute(tasks)
    
    def _execute_distributed(self, tasks: List[Task]) -> List[TaskResult]:
        """Distributed execution (simulated)"""
        # In real implementation, would distribute across machines
        # For now, use adaptive scheduling
        return self._execute_adaptive(tasks)
    
    def _run_task(self, task: Task) -> TaskResult:
        """Run a single task"""
        start_time = time.time()
        
        try:
            kwargs = task.kwargs or {}
            result = task.func(*task.args, **kwargs)
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                duration=time.time() - start_time
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                duration=time.time() - start_time
            )
    
    def get_stats(self) -> Dict:
        """Get execution statistics"""
        return self.stats.copy()


def main():
    """Test distributed execution"""
    print("=== Dive Distributed Execution Test ===\n")
    
    # Create test tasks
    def test_task(duration: float, task_id: str):
        time.sleep(duration)
        return f"{task_id} completed"
    
    tasks = [
        Task(id=f"task_{i}", func=test_task, args=(0.1, f"task_{i}"), estimated_duration=0.1)
        for i in range(20)
    ]
    
    # Test each strategy
    for strategy in [SchedulingStrategy.STATIC, SchedulingStrategy.DYNAMIC, SchedulingStrategy.ADAPTIVE]:
        print(f"\nTesting {strategy.value} strategy:")
        
        executor = DiveDistributedExecution(strategy=strategy, num_workers=4)
        start_time = time.time()
        results = executor.execute(tasks)
        total_time = time.time() - start_time
        
        successful = len([r for r in results if r.success])
        print(f"  Tasks: {len(tasks)}")
        print(f"  Successful: {successful}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Speedup: {sum(t.estimated_duration for t in tasks) / total_time:.2f}x")
        
        if strategy == SchedulingStrategy.DYNAMIC:
            # Show work stealing stats
            print(f"  Work stealing: Available")


if __name__ == "__main__":
    main()
