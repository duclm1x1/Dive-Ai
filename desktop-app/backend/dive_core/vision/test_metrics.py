"""
Unit tests for the metrics module.

Tests cover:
- Metrics collection
- Metrics recording
- Metrics retrieval
"""

import pytest
from unittest.mock import patch
from src.monitoring.metrics import CoreMetrics, MetricsCollector, get_collector


class TestMetricsCollector:
    """Tests for MetricsCollector."""
    
    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        
        assert collector.metrics is not None
        assert isinstance(collector.metrics, CoreMetrics)
    
    def test_record_task_start(self):
        """Test recording task start."""
        collector = MetricsCollector()
        
        # Record task start
        collector.record_task_start("code_generation", "autonomous")
        
        # Verify task is active
        assert collector.metrics.tasks_active._value.get() >= 1
    
    def test_record_task_completion(self):
        """Test recording task completion."""
        collector = MetricsCollector()
        
        # Reset gauge to 0 before test
        collector.metrics.tasks_active.set(0)
        
        collector.record_task_start("code_generation", "autonomous")
        initial_value = collector.metrics.tasks_active._value.get()
        
        collector.record_task_completion(
            "code_generation",
            "autonomous",
            "success",
            5.2
        )
        
        # Task should be decremented
        final_value = collector.metrics.tasks_active._value.get()
        assert final_value == initial_value - 1
    
    def test_record_agent_task_completion(self):
        """Test recording agent task completion."""
        collector = MetricsCollector()
        
        collector.record_agent_task_completion(
            "agent_001",
            "code_generation",
            "success"
        )
        
        # Verify metric was recorded
        assert collector.metrics.agent_tasks_completed is not None
    
    def test_record_agent_execution_time(self):
        """Test recording agent execution time."""
        collector = MetricsCollector()
        
        collector.record_agent_execution_time(
            "agent_001",
            "code_generation",
            3.5
        )
        
        assert collector.metrics.agent_execution_time is not None
    
    def test_set_agent_success_rate(self):
        """Test setting agent success rate."""
        collector = MetricsCollector()
        
        collector.set_agent_success_rate(
            "agent_001",
            "code_generation",
            0.95
        )
        
        assert collector.metrics.agent_success_rate is not None
    
    def test_record_handoff(self):
        """Test recording handoff."""
        collector = MetricsCollector()
        
        collector.record_handoff(
            "specialization",
            "accepted",
            1.5
        )
        
        assert collector.metrics.handoffs_total is not None
    
    def test_record_merge(self):
        """Test recording merge operation."""
        collector = MetricsCollector()
        
        collector.record_merge(
            "automatic",
            "success",
            0.8
        )
        
        assert collector.metrics.merges_total is not None
    
    def test_record_merge_conflict(self):
        """Test recording merge conflict."""
        collector = MetricsCollector()
        
        collector.record_merge_conflict("file_conflict")
        
        assert collector.metrics.merge_conflicts_total is not None
    
    def test_set_merge_conflict_rate(self):
        """Test setting merge conflict rate."""
        collector = MetricsCollector()
        
        collector.set_merge_conflict_rate(0.03)
        
        assert collector.metrics.merge_conflict_rate._value.get() == 0.03
    
    def test_record_error(self):
        """Test recording error."""
        collector = MetricsCollector()
        
        collector.record_error("execution_failure", "high")
        
        assert collector.metrics.errors_total is not None
    
    def test_set_error_recovery_rate(self):
        """Test setting error recovery rate."""
        collector = MetricsCollector()
        
        collector.set_error_recovery_rate(0.95)
        
        assert collector.metrics.error_recovery_rate._value.get() == 0.95
    
    def test_set_system_uptime(self):
        """Test setting system uptime."""
        collector = MetricsCollector()
        
        collector.set_system_uptime(3600.0)
        
        assert collector.metrics.system_uptime_seconds._value.get() == 3600.0
    
    def test_set_redis_queue_depth(self):
        """Test setting Redis queue depth."""
        collector = MetricsCollector()
        
        collector.set_redis_queue_depth(42)
        
        assert collector.metrics.redis_queue_depth._value.get() == 42
    
    def test_record_message_latency(self):
        """Test recording message latency."""
        collector = MetricsCollector()
        
        collector.record_message_latency(
            "orchestrator",
            "agent_001",
            5.2
        )
        
        assert collector.metrics.message_latency is not None
    
    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        collector = MetricsCollector()
        
        # Reset gauge to 0 before test
        collector.metrics.tasks_active.set(0)
        
        collector.record_task_start("code_generation", "autonomous")
        collector.set_system_uptime(3600.0)
        
        summary = collector.get_metrics_summary()
        
        assert "tasks_active" in summary
        assert "agents_active" in summary
        assert "handoffs_active" in summary
        assert "system_uptime_seconds" in summary
        assert summary["tasks_active"] >= 1
        assert summary["system_uptime_seconds"] == 3600.0


class TestGlobalCollector:
    """Tests for global collector instance."""
    
    def test_get_collector_singleton(self):
        """Test that get_collector returns singleton."""
        # Reset global collector for this test
        import src.monitoring.metrics as metrics_module
        original_collector = metrics_module._collector
        metrics_module._collector = None
        
        try:
            collector1 = get_collector()
            collector2 = get_collector()
            assert collector1 is collector2
        finally:
            metrics_module._collector = original_collector
    
    def test_global_collector_functionality(self):
        """Test that global collector works."""
        collector = get_collector()
        
        collector.record_task_start("test", "autonomous")
        
        assert collector.metrics.tasks_active._value.get() >= 1


class TestCoreMetrics:
    """Tests for CoreMetrics class."""
    
    def test_core_metrics_initialization(self):
        """Test that CoreMetrics initializes all counters and gauges."""
        metrics = CoreMetrics()
        
        assert metrics.tasks_total is not None
        assert metrics.tasks_active is not None
        assert metrics.agents_total is not None
        assert metrics.handoffs_total is not None
        assert metrics.merges_total is not None
        assert metrics.errors_total is not None
    
    def test_counter_metrics(self):
        """Test counter metrics."""
        metrics = CoreMetrics()
        
        # Increment counter
        metrics.tasks_total.labels(
            task_type="code_gen",
            mode="autonomous",
            status="success"
        ).inc()
        
        assert metrics.tasks_total is not None
    
    def test_gauge_metrics(self):
        """Test gauge metrics."""
        metrics = CoreMetrics()
        
        # Set gauge value
        metrics.tasks_active.set(5)
        assert metrics.tasks_active._value.get() == 5
        
        # Increment gauge
        metrics.tasks_active.inc()
        assert metrics.tasks_active._value.get() == 6
        
        # Decrement gauge
        metrics.tasks_active.dec()
        assert metrics.tasks_active._value.get() == 5
    
    def test_histogram_metrics(self):
        """Test histogram metrics."""
        metrics = CoreMetrics()
        
        # Record histogram value
        metrics.task_completion_time.labels(
            task_type="code_gen",
            mode="autonomous"
        ).observe(5.2)
        
        assert metrics.task_completion_time is not None


class TestMetricsIntegration:
    """Integration tests for metrics."""
    
    def test_full_task_lifecycle_metrics(self):
        """Test metrics for full task lifecycle."""
        collector = MetricsCollector()
        
        # Reset gauge to 0 before test
        collector.metrics.tasks_active.set(0)
        
        # Task starts
        collector.record_task_start("code_generation", "autonomous")
        initial_value = collector.metrics.tasks_active._value.get()
        assert initial_value == 1
        
        # Agent works on task
        collector.record_agent_execution_time("agent_001", "code_generation", 2.5)
        collector.record_agent_task_completion("agent_001", "code_generation", "success")
        
        # Task completes
        collector.record_task_completion(
            "code_generation",
            "autonomous",
            "success",
            2.5
        )
        final_value = collector.metrics.tasks_active._value.get()
        assert final_value == initial_value - 1
    
    def test_handoff_and_merge_metrics(self):
        """Test metrics for handoff and merge operations."""
        collector = MetricsCollector()
        
        # Handoff occurs
        collector.record_handoff("specialization", "accepted", 0.5)
        
        # Merge occurs
        collector.record_merge("automatic", "success", 0.3)
        
        # No conflicts
        collector.set_merge_conflict_rate(0.0)
        
        assert collector.metrics.handoffs_total is not None
        assert collector.metrics.merges_total is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
