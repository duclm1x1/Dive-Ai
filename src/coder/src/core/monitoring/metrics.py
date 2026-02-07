"""
Prometheus metrics for Dive Coder v16.

This module defines all metrics collected by the system for monitoring and observability.
Metrics are exported in Prometheus format.
"""

from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import Dict, Any


class CoreMetrics:
    """Core metrics for the Dive Coder v16 system."""
    
    # Task metrics
    tasks_total = Counter(
        'tasks_total',
        'Total number of tasks processed',
        ['task_type', 'mode', 'status']
    )
    
    tasks_active = Gauge(
        'tasks_active',
        'Number of currently active tasks'
    )
    
    task_completion_time = Histogram(
        'task_completion_seconds',
        'Task completion time in seconds',
        ['task_type', 'mode'],
        buckets=(0.1, 0.5, 1, 5, 10, 30, 60, 300, 600, 1800)
    )
    
    # Agent metrics
    agents_total = Gauge(
        'agents_total',
        'Total number of agents',
        ['specialization']
    )
    
    agents_active = Gauge(
        'agents_active',
        'Number of currently active agents',
        ['specialization']
    )
    
    agent_tasks_completed = Counter(
        'agent_tasks_completed_total',
        'Total tasks completed by agent',
        ['agent_id', 'specialization', 'status']
    )
    
    agent_execution_time = Histogram(
        'agent_execution_time_seconds',
        'Execution time per agent and skill',
        ['agent_id', 'skill'],
        buckets=(0.1, 0.5, 1, 5, 10, 30, 60, 300)
    )
    
    agent_success_rate = Gauge(
        'agent_success_rate',
        'Success rate for agent skill',
        ['agent_id', 'skill']
    )
    
    # Handoff metrics
    handoffs_total = Counter(
        'handoffs_total',
        'Total number of agent handoffs',
        ['handoff_type', 'status']
    )
    
    handoffs_active = Gauge(
        'handoffs_active',
        'Number of active handoff requests'
    )
    
    handoff_completion_time = Histogram(
        'handoff_completion_seconds',
        'Time to complete a handoff',
        ['handoff_type'],
        buckets=(0.1, 0.5, 1, 5, 10, 30, 60)
    )
    
    # Merge metrics
    merges_total = Counter(
        'merges_total',
        'Total merge operations',
        ['merge_type', 'status']
    )
    
    merge_conflicts_total = Counter(
        'merge_conflicts_total',
        'Total merge conflicts detected',
        ['conflict_type']
    )
    
    merge_conflict_rate = Gauge(
        'merge_conflict_rate',
        'Rate of merge conflicts per 100 merges'
    )
    
    merge_time = Histogram(
        'merge_time_seconds',
        'Time to complete a merge operation',
        ['merge_type'],
        buckets=(0.1, 0.5, 1, 5, 10, 30)
    )
    
    # Orchestrator metrics
    orchestrator_active = Gauge(
        'orchestrator_active',
        'Number of active orchestrator instances'
    )
    
    orchestrator_mode_switches = Counter(
        'orchestrator_mode_switches_total',
        'Total mode switches',
        ['from_mode', 'to_mode']
    )
    
    # Error metrics
    errors_total = Counter(
        'errors_total',
        'Total errors encountered',
        ['error_type', 'severity']
    )
    
    error_recovery_rate = Gauge(
        'error_recovery_rate',
        'Percentage of errors automatically recovered'
    )
    
    # System metrics
    system_uptime_seconds = Gauge(
        'system_uptime_seconds',
        'System uptime in seconds'
    )
    
    redis_queue_depth = Gauge(
        'redis_queue_depth',
        'Current depth of Redis task queue'
    )
    
    message_latency = Histogram(
        'message_latency_milliseconds',
        'Message latency between components',
        ['source', 'destination'],
        buckets=(1, 5, 10, 50, 100, 500, 1000)
    )


class MetricsCollector:
    """Utility class for collecting and managing metrics."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics = CoreMetrics()
    
    def record_task_start(self, task_type: str, mode: str) -> None:
        """Record the start of a task."""
        self.metrics.tasks_active.inc()
    
    def record_task_completion(
        self,
        task_type: str,
        mode: str,
        status: str,
        execution_time: float
    ) -> None:
        """Record the completion of a task."""
        self.metrics.tasks_total.labels(
            task_type=task_type,
            mode=mode,
            status=status
        ).inc()
        
        self.metrics.task_completion_time.labels(
            task_type=task_type,
            mode=mode
        ).observe(execution_time)
        
        self.metrics.tasks_active.dec()
    
    def record_agent_task_completion(
        self,
        agent_id: str,
        specialization: str,
        status: str
    ) -> None:
        """Record agent task completion."""
        self.metrics.agent_tasks_completed.labels(
            agent_id=agent_id,
            specialization=specialization,
            status=status
        ).inc()
    
    def record_agent_execution_time(
        self,
        agent_id: str,
        skill: str,
        execution_time: float
    ) -> None:
        """Record agent execution time for a skill."""
        self.metrics.agent_execution_time.labels(
            agent_id=agent_id,
            skill=skill
        ).observe(execution_time)
    
    def set_agent_success_rate(
        self,
        agent_id: str,
        skill: str,
        success_rate: float
    ) -> None:
        """Set agent success rate for a skill."""
        self.metrics.agent_success_rate.labels(
            agent_id=agent_id,
            skill=skill
        ).set(success_rate)
    
    def record_handoff(
        self,
        handoff_type: str,
        status: str,
        completion_time: float = None
    ) -> None:
        """Record a handoff operation."""
        self.metrics.handoffs_total.labels(
            handoff_type=handoff_type,
            status=status
        ).inc()
        
        if completion_time is not None:
            self.metrics.handoff_completion_time.labels(
                handoff_type=handoff_type
            ).observe(completion_time)
    
    def record_merge(
        self,
        merge_type: str,
        status: str,
        merge_time: float
    ) -> None:
        """Record a merge operation."""
        self.metrics.merges_total.labels(
            merge_type=merge_type,
            status=status
        ).inc()
        
        self.metrics.merge_time.labels(
            merge_type=merge_type
        ).observe(merge_time)
    
    def record_merge_conflict(self, conflict_type: str) -> None:
        """Record a merge conflict."""
        self.metrics.merge_conflicts_total.labels(
            conflict_type=conflict_type
        ).inc()
    
    def set_merge_conflict_rate(self, rate: float) -> None:
        """Set the merge conflict rate."""
        self.metrics.merge_conflict_rate.set(rate)
    
    def record_error(self, error_type: str, severity: str) -> None:
        """Record an error."""
        self.metrics.errors_total.labels(
            error_type=error_type,
            severity=severity
        ).inc()
    
    def set_error_recovery_rate(self, rate: float) -> None:
        """Set the error recovery rate."""
        self.metrics.error_recovery_rate.set(rate)
    
    def set_system_uptime(self, uptime_seconds: float) -> None:
        """Set system uptime."""
        self.metrics.system_uptime_seconds.set(uptime_seconds)
    
    def set_redis_queue_depth(self, depth: int) -> None:
        """Set Redis queue depth."""
        self.metrics.redis_queue_depth.set(depth)
    
    def record_message_latency(
        self,
        source: str,
        destination: str,
        latency_ms: float
    ) -> None:
        """Record message latency between components."""
        self.metrics.message_latency.labels(
            source=source,
            destination=destination
        ).observe(latency_ms)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            "tasks_active": self.metrics.tasks_active._value.get(),
            "agents_active": self.metrics.agents_active._metrics,
            "handoffs_active": self.metrics.handoffs_active._value.get(),
            "system_uptime_seconds": self.metrics.system_uptime_seconds._value.get(),
        }


# Global metrics collector instance
_collector = None


def get_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
