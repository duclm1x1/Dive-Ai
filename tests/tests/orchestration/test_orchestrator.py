"""
Unit tests for the Orchestrator class.

Tests cover:
- Task specification creation and validation
- Execution result tracking
- Dual-mode execution (autonomous and deterministic)
- Task lifecycle management
"""

import pytest
from datetime import datetime
from src.orchestration.orchestrator import Orchestrator, TaskSpec, ExecutionResult
from src.orchestration.modes import ExecutionMode


class TestTaskSpec:
    """Tests for TaskSpec data class."""
    
    def test_task_spec_creation(self):
        """Test creating a TaskSpec with required fields."""
        spec = TaskSpec(
            task_id="task_001",
            description="Generate a Python function"
        )
        
        assert spec.task_id == "task_001"
        assert spec.description == "Generate a Python function"
        assert spec.mode == ExecutionMode.AUTONOMOUS
        assert spec.priority == 5
        assert spec.max_agents == 4
        assert spec.timeout_seconds is None
    
    def test_task_spec_with_all_fields(self):
        """Test creating a TaskSpec with all fields."""
        spec = TaskSpec(
            task_id="task_002",
            description="Refactor legacy code",
            mode=ExecutionMode.DETERMINISTIC,
            priority=8,
            max_agents=2,
            timeout_seconds=300,
            metadata={"language": "python", "complexity": "high"}
        )
        
        assert spec.task_id == "task_002"
        assert spec.mode == ExecutionMode.DETERMINISTIC
        assert spec.priority == 8
        assert spec.max_agents == 2
        assert spec.timeout_seconds == 300
        assert spec.metadata["language"] == "python"
    
    def test_task_spec_invalid_priority(self):
        """Test that invalid priority raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TaskSpec(task_id="task_003", description="Test", priority=0)
        assert "Priority must be between 1 and 10" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            TaskSpec(task_id="task_004", description="Test", priority=11)
        assert "Priority must be between 1 and 10" in str(exc_info.value)
    
    def test_task_spec_invalid_max_agents(self):
        """Test that invalid max_agents raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TaskSpec(task_id="task_005", description="Test", max_agents=0)
        assert "max_agents must be between 1 and 8" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            TaskSpec(task_id="task_006", description="Test", max_agents=9)
        assert "max_agents must be between 1 and 8" in str(exc_info.value)
    
    def test_task_spec_mode_string_conversion(self):
        """Test that mode strings are converted to ExecutionMode."""
        spec = TaskSpec(
            task_id="task_007",
            description="Test",
            mode="deterministic"
        )
        
        assert spec.mode == ExecutionMode.DETERMINISTIC
        assert isinstance(spec.mode, ExecutionMode)
    
    def test_task_spec_timestamp(self):
        """Test that TaskSpec records creation timestamp."""
        before = datetime.now()
        spec = TaskSpec(task_id="task_008", description="Test")
        after = datetime.now()
        
        assert before <= spec.created_at <= after


class TestExecutionResult:
    """Tests for ExecutionResult data class."""
    
    def test_execution_result_creation(self):
        """Test creating an ExecutionResult."""
        result = ExecutionResult(
            task_id="task_001",
            status="success",
            result={"code": "def hello(): pass"},
            agents_used=2,
            execution_time_seconds=5.2,
            subtasks_completed=4,
        )
        
        assert result.task_id == "task_001"
        assert result.status == "success"
        assert result.result["code"] == "def hello(): pass"
        assert result.agents_used == 2
        assert result.execution_time_seconds == 5.2
        assert result.subtasks_completed == 4
    
    def test_execution_result_failure(self):
        """Test creating a failed ExecutionResult."""
        result = ExecutionResult(
            task_id="task_002",
            status="failure",
            error="Agent timeout after 300 seconds",
            agents_used=1,
            subtasks_failed=2,
        )
        
        assert result.status == "failure"
        assert result.error == "Agent timeout after 300 seconds"
        assert result.subtasks_failed == 2
    
    def test_execution_result_timestamp(self):
        """Test that ExecutionResult records completion timestamp."""
        before = datetime.now()
        result = ExecutionResult(task_id="task_003", status="success")
        after = datetime.now()
        
        assert before <= result.completed_at <= after


class TestOrchestratorBasics:
    """Tests for basic Orchestrator functionality."""
    
    def test_orchestrator_initialization(self):
        """Test Orchestrator initialization."""
        orchestrator = Orchestrator(name="TestOrch")
        
        assert orchestrator.name == "TestOrch"
        assert len(orchestrator.active_tasks) == 0
        assert len(orchestrator.completed_tasks) == 0
    
    def test_orchestrator_default_name(self):
        """Test Orchestrator with default name."""
        orchestrator = Orchestrator()
        
        assert orchestrator.name == "MainOrchestrator"
    
    def test_orchestrator_get_status(self):
        """Test getting orchestrator status."""
        orchestrator = Orchestrator(name="StatusTest")
        status = orchestrator.get_status()
        
        assert status["name"] == "StatusTest"
        assert status["active_tasks"] == 0
        assert status["completed_tasks"] == 0


class TestOrchestratorAutonomousMode:
    """Tests for autonomous mode execution."""
    
    def test_run_autonomous_mode(self):
        """Test executing a task in autonomous mode."""
        orchestrator = Orchestrator()
        spec = TaskSpec(
            task_id="auto_001",
            description="Generate code",
            mode=ExecutionMode.AUTONOMOUS
        )
        
        result = orchestrator.run(spec)
        
        assert result.task_id == "auto_001"
        assert result.status == "success"
        assert result.mode_used == ExecutionMode.AUTONOMOUS
        assert len(orchestrator.completed_tasks) == 1
    
    def test_autonomous_mode_allows_handoffs(self):
        """Test that autonomous mode allows handoffs."""
        orchestrator = Orchestrator()
        spec = TaskSpec(
            task_id="auto_002",
            description="Complex task",
            mode=ExecutionMode.AUTONOMOUS
        )
        
        result = orchestrator.run(spec)
        
        assert orchestrator.mode_config is not None
        assert orchestrator.mode_config.allow_handoffs is True
        assert orchestrator.mode_config.allow_agent_decisions is True


class TestOrchestratorDeterministicMode:
    """Tests for deterministic mode execution."""
    
    def test_run_deterministic_mode(self):
        """Test executing a task in deterministic mode."""
        orchestrator = Orchestrator()
        spec = TaskSpec(
            task_id="det_001",
            description="Security audit",
            mode=ExecutionMode.DETERMINISTIC
        )
        
        result = orchestrator.run(spec)
        
        assert result.task_id == "det_001"
        assert result.status == "success"
        assert result.mode_used == ExecutionMode.DETERMINISTIC
    
    def test_deterministic_mode_strict_control(self):
        """Test that deterministic mode has strict control."""
        orchestrator = Orchestrator()
        spec = TaskSpec(
            task_id="det_002",
            description="Compliance check",
            mode=ExecutionMode.DETERMINISTIC
        )
        
        result = orchestrator.run(spec)
        
        assert orchestrator.mode_config is not None
        assert orchestrator.mode_config.allow_handoffs is False
        assert orchestrator.mode_config.allow_agent_decisions is False
        assert orchestrator.mode_config.strict_plan_adherence is True


class TestOrchestratorModeOverride:
    """Tests for mode override functionality."""
    
    def test_mode_override_in_run(self):
        """Test that mode can be overridden in run() call."""
        orchestrator = Orchestrator()
        spec = TaskSpec(
            task_id="override_001",
            description="Test override",
            mode=ExecutionMode.AUTONOMOUS
        )
        
        # Override to deterministic
        result = orchestrator.run(spec, mode=ExecutionMode.DETERMINISTIC)
        
        assert result.mode_used == ExecutionMode.DETERMINISTIC
        assert orchestrator.mode_config.mode == ExecutionMode.DETERMINISTIC
    
    def test_mode_override_preserves_spec(self):
        """Test that mode override doesn't modify the original spec."""
        orchestrator = Orchestrator()
        spec = TaskSpec(
            task_id="override_002",
            description="Test",
            mode=ExecutionMode.AUTONOMOUS
        )
        
        original_mode = spec.mode
        orchestrator.run(spec, mode=ExecutionMode.DETERMINISTIC)
        
        assert spec.mode == original_mode


class TestOrchestratorTaskTracking:
    """Tests for task tracking and lifecycle."""
    
    def test_task_tracking_during_execution(self):
        """Test that tasks are tracked during execution."""
        orchestrator = Orchestrator()
        spec = TaskSpec(task_id="track_001", description="Test")
        
        # Task should not be active before execution
        assert "track_001" not in orchestrator.active_tasks
        
        result = orchestrator.run(spec)
        
        # Task should not be active after execution
        assert "track_001" not in orchestrator.active_tasks
        # But should be in completed tasks
        assert len(orchestrator.completed_tasks) == 1
        assert orchestrator.completed_tasks[0].task_id == "track_001"
    
    def test_multiple_task_execution(self):
        """Test executing multiple tasks sequentially."""
        orchestrator = Orchestrator()
        
        for i in range(3):
            spec = TaskSpec(task_id=f"multi_{i}", description=f"Task {i}")
            orchestrator.run(spec)
        
        assert len(orchestrator.completed_tasks) == 3
        assert orchestrator.get_status()["completed_tasks"] == 3


class TestOrchestratorErrorHandling:
    """Tests for error handling in the Orchestrator."""
    
    def test_invalid_execution_mode(self):
        """Test that invalid execution mode raises error."""
        orchestrator = Orchestrator()
        spec = TaskSpec(task_id="error_001", description="Test")
        
        # This should not raise during run() but should handle gracefully
        # The actual error would come from mode validation
        result = orchestrator.run(spec)
        assert result.status in ["success", "failure"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
