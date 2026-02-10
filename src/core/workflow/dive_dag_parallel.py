#!/usr/bin/env python3
"""
Dive DAG Parallel Execution - V23 Component

Parallel execution engine for DAG workflows.
Executes independent nodes in parallel for maximum performance.
"""

import time
import concurrent.futures
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum


class NodeStatus(Enum):
    """Node execution status"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """A node in the DAG"""
    id: str
    task: Callable
    dependencies: List[str]
    metadata: Optional[Dict] = None


@dataclass
class NodeResult:
    """Result of node execution"""
    id: str
    status: NodeStatus
    result: Optional[any] = None
    error: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0


@dataclass
class DAGExecutionResult:
    """Complete DAG execution result"""
    success: bool
    node_results: Dict[str, NodeResult]
    total_time: float
    parallel_speedup: float
    nodes_executed: int
    nodes_failed: int


class DiveDAGParallel:
    """
    Parallel DAG execution engine.
    
    Features:
    - Automatic parallelization
    - Dependency resolution
    - Failure handling
    - Progress tracking
    - Performance metrics
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.stats = {
            'total_dags_executed': 0,
            'total_nodes_executed': 0,
            'total_parallel_time': 0.0,
            'total_sequential_time': 0.0
        }
    
    def execute_dag(
        self,
        nodes: List[DAGNode],
        stop_on_fail: bool = True
    ) -> DAGExecutionResult:
        """
        Execute DAG with automatic parallelization.
        
        Args:
            nodes: List of DAG nodes
            stop_on_fail: Whether to stop on first failure
            
        Returns:
            DAGExecutionResult with execution details
        """
        start_time = time.time()
        
        # Build dependency graph
        node_map = {node.id: node for node in nodes}
        results: Dict[str, NodeResult] = {}
        
        # Track node status
        status: Dict[str, NodeStatus] = {
            node.id: NodeStatus.PENDING for node in nodes
        }
        
        # Execute in waves (levels of parallelism)
        while True:
            # Find ready nodes (dependencies satisfied)
            ready_nodes = self._find_ready_nodes(nodes, status, results)
            
            if not ready_nodes:
                # Check if we're done
                if all(s in [NodeStatus.SUCCESS, NodeStatus.FAILED, NodeStatus.SKIPPED] 
                       for s in status.values()):
                    break
                else:
                    # Deadlock or circular dependency
                    for node_id, s in status.items():
                        if s == NodeStatus.PENDING:
                            results[node_id] = NodeResult(
                                id=node_id,
                                status=NodeStatus.FAILED,
                                error="Circular dependency or deadlock"
                            )
                            status[node_id] = NodeStatus.FAILED
                    break
            
            # Execute ready nodes in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all ready nodes
                futures = {}
                for node_id in ready_nodes:
                    node = node_map[node_id]
                    status[node_id] = NodeStatus.RUNNING
                    future = executor.submit(self._execute_node, node)
                    futures[future] = node_id
                
                # Wait for completion
                for future in concurrent.futures.as_completed(futures):
                    node_id = futures[future]
                    result = future.result()
                    results[node_id] = result
                    status[node_id] = result.status
                    
                    # Stop on fail if requested
                    if stop_on_fail and result.status == NodeStatus.FAILED:
                        # Cancel remaining and mark as skipped
                        for remaining_id, s in status.items():
                            if s in [NodeStatus.PENDING, NodeStatus.READY]:
                                results[remaining_id] = NodeResult(
                                    id=remaining_id,
                                    status=NodeStatus.SKIPPED,
                                    error="Skipped due to previous failure"
                                )
                                status[remaining_id] = NodeStatus.SKIPPED
                        break
        
        # Calculate metrics
        total_time = time.time() - start_time
        sequential_time = sum(r.duration for r in results.values())
        parallel_speedup = sequential_time / total_time if total_time > 0 else 1.0
        
        success = all(r.status == NodeStatus.SUCCESS for r in results.values())
        nodes_executed = len([r for r in results.values() if r.status == NodeStatus.SUCCESS])
        nodes_failed = len([r for r in results.values() if r.status == NodeStatus.FAILED])
        
        # Update stats
        self.stats['total_dags_executed'] += 1
        self.stats['total_nodes_executed'] += nodes_executed
        self.stats['total_parallel_time'] += total_time
        self.stats['total_sequential_time'] += sequential_time
        
        return DAGExecutionResult(
            success=success,
            node_results=results,
            total_time=total_time,
            parallel_speedup=parallel_speedup,
            nodes_executed=nodes_executed,
            nodes_failed=nodes_failed
        )
    
    def _find_ready_nodes(
        self,
        nodes: List[DAGNode],
        status: Dict[str, NodeStatus],
        results: Dict[str, NodeResult]
    ) -> List[str]:
        """Find nodes that are ready to execute"""
        ready = []
        
        for node in nodes:
            # Skip if not pending
            if status[node.id] != NodeStatus.PENDING:
                continue
            
            # Check if all dependencies succeeded
            deps_satisfied = all(
                dep_id in results and results[dep_id].status == NodeStatus.SUCCESS
                for dep_id in node.dependencies
            )
            
            if deps_satisfied:
                ready.append(node.id)
        
        return ready
    
    def _execute_node(self, node: DAGNode) -> NodeResult:
        """Execute a single node"""
        start_time = time.time()
        
        try:
            # Execute task
            result = node.task()
            
            return NodeResult(
                id=node.id,
                status=NodeStatus.SUCCESS,
                result=result,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time
            )
        except Exception as e:
            return NodeResult(
                id=node.id,
                status=NodeStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time
            )
    
    def visualize_dag(self, nodes: List[DAGNode]) -> str:
        """Generate ASCII visualization of DAG"""
        lines = ["DAG Visualization:", ""]
        
        # Group by level
        levels = self._compute_levels(nodes)
        max_level = max(levels.values()) if levels else 0
        
        for level in range(max_level + 1):
            level_nodes = [nid for nid, l in levels.items() if l == level]
            if level_nodes:
                lines.append(f"Level {level}: {', '.join(level_nodes)}")
        
        return "\n".join(lines)
    
    def _compute_levels(self, nodes: List[DAGNode]) -> Dict[str, int]:
        """Compute level of each node (for visualization)"""
        node_map = {node.id: node for node in nodes}
        levels = {}
        
        def compute_level(node_id: str) -> int:
            if node_id in levels:
                return levels[node_id]
            
            node = node_map[node_id]
            if not node.dependencies:
                levels[node_id] = 0
            else:
                levels[node_id] = 1 + max(
                    compute_level(dep_id) for dep_id in node.dependencies
                )
            
            return levels[node_id]
        
        for node in nodes:
            compute_level(node.id)
        
        return levels
    
    def get_stats(self) -> Dict:
        """Get execution statistics"""
        stats = self.stats.copy()
        if stats['total_parallel_time'] > 0:
            stats['average_speedup'] = \
                stats['total_sequential_time'] / stats['total_parallel_time']
        else:
            stats['average_speedup'] = 1.0
        return stats


def main():
    """Test DAG parallel execution"""
    print("=== Dive DAG Parallel Execution Test ===\n")
    
    engine = DiveDAGParallel(max_workers=4)
    
    # Define test DAG
    def task_a():
        time.sleep(0.1)
        return "A done"
    
    def task_b():
        time.sleep(0.1)
        return "B done"
    
    def task_c():
        time.sleep(0.1)
        return "C done"
    
    def task_d():
        time.sleep(0.1)
        return "D done"
    
    def task_e():
        time.sleep(0.1)
        return "E done"
    
    nodes = [
        DAGNode(id="A", task=task_a, dependencies=[]),
        DAGNode(id="B", task=task_b, dependencies=[]),
        DAGNode(id="C", task=task_c, dependencies=["A", "B"]),
        DAGNode(id="D", task=task_d, dependencies=["A"]),
        DAGNode(id="E", task=task_e, dependencies=["C", "D"])
    ]
    
    # Visualize
    print(engine.visualize_dag(nodes))
    print()
    
    # Execute
    print("Executing DAG...\n")
    result = engine.execute_dag(nodes)
    
    print(f"Success: {result.success}")
    print(f"Total time: {result.total_time:.2f}s")
    print(f"Parallel speedup: {result.parallel_speedup:.2f}x")
    print(f"Nodes executed: {result.nodes_executed}/{len(nodes)}")
    print()
    
    print("Node Results:")
    for node_id, node_result in result.node_results.items():
        print(f"  {node_id}: {node_result.status.value} ({node_result.duration:.3f}s)")
    
    print(f"\nEngine Stats: {engine.get_stats()}")


if __name__ == "__main__":
    main()
