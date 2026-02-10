"""
📋 TASK QUEUE SYSTEM
Priority queue with dependency graph (DAG) for task scheduling
"""

import os
import sys
import json
import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import heapq

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    READY = "ready"  # Dependencies satisfied
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Waiting for dependencies
    CANCELLED = "cancelled"


@dataclass(order=True)
class PriorityTask:
    """Task with priority for heap queue"""
    priority: int  # Lower = higher priority (inverted for max-heap behavior)
    created_at: float
    task_id: str = field(compare=False)
    description: str = field(compare=False)
    dependencies: List[str] = field(default_factory=list, compare=False)
    assigned_agents: List[int] = field(default_factory=list, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    result: Any = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    metadata: Dict = field(default_factory=dict, compare=False)


class DependencyGraph:
    """
    🔗 Directed Acyclic Graph for task dependencies
    Supports topological sorting and cycle detection
    """
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependencies
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependents
        self.lock = threading.Lock()
    
    def add_task(self, task_id: str, dependencies: List[str] = None):
        """Add task with dependencies"""
        with self.lock:
            if dependencies:
                for dep in dependencies:
                    self.graph[task_id].add(dep)
                    self.reverse_graph[dep].add(task_id)
            else:
                # Ensure task exists even without dependencies
                if task_id not in self.graph:
                    self.graph[task_id] = set()
    
    def remove_task(self, task_id: str):
        """Remove task from graph"""
        with self.lock:
            # Remove from dependencies
            if task_id in self.graph:
                del self.graph[task_id]
            
            # Remove from reverse graph
            if task_id in self.reverse_graph:
                for dependent in self.reverse_graph[task_id]:
                    self.graph[dependent].discard(task_id)
                del self.reverse_graph[task_id]
            
            # Clean up references
            for deps in self.graph.values():
                deps.discard(task_id)
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """Get task dependencies"""
        with self.lock:
            return self.graph.get(task_id, set()).copy()
    
    def get_dependents(self, task_id: str) -> Set[str]:
        """Get tasks that depend on this task"""
        with self.lock:
            return self.reverse_graph.get(task_id, set()).copy()
    
    def is_ready(self, task_id: str, completed_tasks: Set[str]) -> bool:
        """Check if task dependencies are satisfied"""
        with self.lock:
            deps = self.graph.get(task_id, set())
            return deps.issubset(completed_tasks)
    
    def has_cycle(self) -> bool:
        """Detect cycles using DFS"""
        with self.lock:
            visited = set()
            rec_stack = set()
            
            def dfs(node):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in self.graph.get(node, set()):
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            for node in self.graph:
                if node not in visited:
                    if dfs(node):
                        return True
            
            return False
    
    def topological_sort(self) -> List[str]:
        """Get topological order of tasks"""
        with self.lock:
            in_degree = defaultdict(int)
            
            # Calculate in-degrees
            for task_id, deps in self.graph.items():
                if task_id not in in_degree:
                    in_degree[task_id] = 0
                for dep in deps:
                    in_degree[task_id] += 1
            
            # Start with zero in-degree nodes
            queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
            result = []
            
            while queue:
                task_id = queue.pop(0)
                result.append(task_id)
                
                for dependent in self.reverse_graph.get(task_id, set()):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
            
            return result


class TaskQueue:
    """
    📋 Priority-based Task Queue with DAG Support
    """
    
    def __init__(self, max_parallel: int = 10):
        self.max_parallel = max_parallel
        self.heap: List[PriorityTask] = []
        self.tasks: Dict[str, PriorityTask] = {}
        self.dag = DependencyGraph()
        self.completed: Set[str] = set()
        self.running: Set[str] = set()
        self.lock = threading.Lock()
        self.task_counter = 0
        
        # Callbacks
        self.on_task_complete: Optional[Callable] = None
        self.on_task_failed: Optional[Callable] = None
        
        print("📋 TaskQueue initialized")
        print(f"   Max parallel: {max_parallel}")
    
    def add_task(self, description: str, priority: int = 3, 
                 dependencies: List[str] = None, metadata: Dict = None) -> str:
        """Add task to queue"""
        with self.lock:
            self.task_counter += 1
            task_id = f"task-{self.task_counter:06d}"
            
            # Invert priority for min-heap (higher priority = lower number)
            task = PriorityTask(
                priority=6 - priority,  # 5 becomes 1, 1 becomes 5
                created_at=time.time(),
                task_id=task_id,
                description=description,
                dependencies=dependencies or [],
                status=TaskStatus.PENDING,
                metadata=metadata or {}
            )
            
            self.tasks[task_id] = task
            self.dag.add_task(task_id, dependencies)
            
            # Check if ready immediately
            if self.dag.is_ready(task_id, self.completed):
                task.status = TaskStatus.READY
                heapq.heappush(self.heap, task)
            else:
                task.status = TaskStatus.BLOCKED
            
            return task_id
    
    def get_next_tasks(self, count: int = 1) -> List[PriorityTask]:
        """Get next tasks ready for execution"""
        with self.lock:
            # Check running limit
            available_slots = self.max_parallel - len(self.running)
            count = min(count, available_slots)
            
            if count <= 0:
                return []
            
            tasks = []
            temp = []
            
            while self.heap and len(tasks) < count:
                task = heapq.heappop(self.heap)
                
                if task.status != TaskStatus.READY:
                    continue
                
                if task.task_id in self.running:
                    temp.append(task)
                    continue
                
                task.status = TaskStatus.RUNNING
                self.running.add(task.task_id)
                tasks.append(task)
            
            # Put back tasks we couldn't use
            for t in temp:
                heapq.heappush(self.heap, t)
            
            return tasks
    
    def complete_task(self, task_id: str, result: Any = None):
        """Mark task as completed"""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = result
            
            self.running.discard(task_id)
            self.completed.add(task_id)
            
            # Check dependent tasks
            self._update_dependents(task_id)
            
            if self.on_task_complete:
                self.on_task_complete(task)
    
    def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            
            self.running.discard(task_id)
            
            if self.on_task_failed:
                self.on_task_failed(task)
    
    def cancel_task(self, task_id: str):
        """Cancel a task"""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.CANCELLED
            
            self.running.discard(task_id)
            self.dag.remove_task(task_id)
    
    def _update_dependents(self, completed_task_id: str):
        """Update status of dependent tasks"""
        dependents = self.dag.get_dependents(completed_task_id)
        
        for dep_id in dependents:
            if dep_id in self.tasks:
                task = self.tasks[dep_id]
                if task.status == TaskStatus.BLOCKED:
                    if self.dag.is_ready(dep_id, self.completed):
                        task.status = TaskStatus.READY
                        heapq.heappush(self.heap, task)
    
    def get_task(self, task_id: str) -> Optional[PriorityTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_pending_count(self) -> int:
        """Get count of pending tasks"""
        return sum(1 for t in self.tasks.values() if t.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.BLOCKED])
    
    def get_running_count(self) -> int:
        """Get count of running tasks"""
        return len(self.running)
    
    def get_completed_count(self) -> int:
        """Get count of completed tasks"""
        return len(self.completed)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            status_counts = defaultdict(int)
            for task in self.tasks.values():
                status_counts[task.status.value] += 1
            
            return {
                "total": len(self.tasks),
                "pending": status_counts.get("pending", 0) + status_counts.get("ready", 0),
                "running": len(self.running),
                "completed": len(self.completed),
                "failed": status_counts.get("failed", 0),
                "blocked": status_counts.get("blocked", 0),
                "status_breakdown": dict(status_counts)
            }
    
    def get_execution_order(self) -> List[str]:
        """Get optimal execution order based on dependencies"""
        return self.dag.topological_sort()
    
    def detect_deadlock(self) -> bool:
        """Check for deadlock (circular dependencies)"""
        return self.dag.has_cycle()


class ParallelExecutor:
    """
    ⚡ Parallel task executor with worker pool
    """
    
    def __init__(self, queue: TaskQueue, num_workers: int = 10):
        self.queue = queue
        self.num_workers = num_workers
        self.running = False
        self.workers: List[threading.Thread] = []
        self.executor_func: Optional[Callable] = None
    
    def set_executor(self, func: Callable[[PriorityTask], Any]):
        """Set the function to execute tasks"""
        self.executor_func = func
    
    def start(self):
        """Start executor"""
        if self.running:
            return
        
        self.running = True
        
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)
        
        print(f"⚡ ParallelExecutor started with {self.num_workers} workers")
    
    def stop(self):
        """Stop executor"""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=5)
        self.workers.clear()
        print("⏹️  ParallelExecutor stopped")
    
    def _worker_loop(self, worker_id: int):
        """Worker loop"""
        while self.running:
            tasks = self.queue.get_next_tasks(1)
            
            if not tasks:
                time.sleep(0.1)
                continue
            
            task = tasks[0]
            
            try:
                if self.executor_func:
                    result = self.executor_func(task)
                    self.queue.complete_task(task.task_id, result)
                else:
                    # Default: just mark complete
                    time.sleep(0.1)  # Simulate work
                    self.queue.complete_task(task.task_id)
            except Exception as e:
                self.queue.fail_task(task.task_id, str(e))


if __name__ == "__main__":
    # Test
    print("\n🧪 Testing Task Queue System...")
    
    queue = TaskQueue(max_parallel=5)
    
    # Add tasks with dependencies
    t1 = queue.add_task("Research requirements", priority=5)
    t2 = queue.add_task("Design architecture", priority=4, dependencies=[t1])
    t3 = queue.add_task("Implement backend", priority=3, dependencies=[t2])
    t4 = queue.add_task("Implement frontend", priority=3, dependencies=[t2])
    t5 = queue.add_task("Integration testing", priority=2, dependencies=[t3, t4])
    t6 = queue.add_task("Deploy", priority=1, dependencies=[t5])
    
    print(f"\n📋 Created {len(queue.tasks)} tasks with dependencies")
    print(f"   Execution order: {queue.get_execution_order()}")
    print(f"   Has cycle: {queue.detect_deadlock()}")
    
    # Simulate execution
    print(f"\n⚡ Simulating execution...")
    
    while queue.get_pending_count() > 0:
        tasks = queue.get_next_tasks(2)
        for task in tasks:
            print(f"   Running: {task.task_id} - {task.description}")
            queue.complete_task(task.task_id)
    
    stats = queue.get_stats()
    print(f"\n📊 Final stats: {json.dumps(stats, indent=2)}")
