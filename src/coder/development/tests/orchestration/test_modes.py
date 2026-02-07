"""
Unit tests for the execution modes module.

Tests cover:
- ExecutionMode enum functionality
- ModeConfig creation and validation
- Mode transitions and configurations
"""

import pytest
from src.orchestration.modes import ExecutionMode, ModeConfig


class TestExecutionMode:
    """Tests for the ExecutionMode enum."""
    
    def test_execution_mode_values(self):
        """Test that ExecutionMode has the correct values."""
        assert ExecutionMode.AUTONOMOUS.value == "autonomous"
        assert ExecutionMode.DETERMINISTIC.value == "deterministic"
    
    def test_execution_mode_string_representation(self):
        """Test string representation of ExecutionMode."""
        assert str(ExecutionMode.AUTONOMOUS) == "autonomous"
        assert str(ExecutionMode.DETERMINISTIC) == "deterministic"
    
    def test_from_string_valid_modes(self):
        """Test creating ExecutionMode from valid string values."""
        assert ExecutionMode.from_string("autonomous") == ExecutionMode.AUTONOMOUS
        assert ExecutionMode.from_string("deterministic") == ExecutionMode.DETERMINISTIC
        assert ExecutionMode.from_string("AUTONOMOUS") == ExecutionMode.AUTONOMOUS
        assert ExecutionMode.from_string("DETERMINISTIC") == ExecutionMode.DETERMINISTIC
    
    def test_from_string_invalid_mode(self):
        """Test that invalid mode strings raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ExecutionMode.from_string("invalid_mode")
        
        assert "Invalid execution mode" in str(exc_info.value)
        assert "autonomous" in str(exc_info.value)
        assert "deterministic" in str(exc_info.value)
    
    def test_from_string_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            ExecutionMode.from_string("")


class TestModeConfig:
    """Tests for the ModeConfig class."""
    
    def test_autonomous_mode_config(self):
        """Test autonomous mode configuration."""
        config = ModeConfig.autonomous()
        
        assert config.mode == ExecutionMode.AUTONOMOUS
        assert config.allow_handoffs is True
        assert config.allow_agent_decisions is True
        assert config.strict_plan_adherence is False
        assert config.max_agent_autonomy_level == 10
    
    def test_deterministic_mode_config(self):
        """Test deterministic mode configuration."""
        config = ModeConfig.deterministic()
        
        assert config.mode == ExecutionMode.DETERMINISTIC
        assert config.allow_handoffs is False
        assert config.allow_agent_decisions is False
        assert config.strict_plan_adherence is True
        assert config.max_agent_autonomy_level == 0
    
    def test_custom_mode_config(self):
        """Test creating custom mode configurations."""
        config = ModeConfig(
            mode=ExecutionMode.AUTONOMOUS,
            allow_handoffs=False,
            allow_agent_decisions=True,
            strict_plan_adherence=False,
            max_agent_autonomy_level=5,
        )
        
        assert config.mode == ExecutionMode.AUTONOMOUS
        assert config.allow_handoffs is False
        assert config.allow_agent_decisions is True
        assert config.max_agent_autonomy_level == 5
    
    def test_mode_config_repr(self):
        """Test string representation of ModeConfig."""
        config = ModeConfig.autonomous()
        repr_str = repr(config)
        
        assert "ModeConfig" in repr_str
        assert "autonomous" in repr_str
        assert "allow_handoffs=True" in repr_str
    
    def test_mode_config_default_values(self):
        """Test default values in ModeConfig."""
        config = ModeConfig(mode=ExecutionMode.AUTONOMOUS)
        
        assert config.allow_handoffs is True
        assert config.allow_agent_decisions is True
        assert config.strict_plan_adherence is False
        assert config.max_agent_autonomy_level == 10


class TestModeTransitions:
    """Tests for mode transitions and behavior."""
    
    def test_mode_independence(self):
        """Test that mode configurations are independent."""
        autonomous = ModeConfig.autonomous()
        deterministic = ModeConfig.deterministic()
        
        # Verify they have different configurations
        assert autonomous.allow_handoffs != deterministic.allow_handoffs
        assert autonomous.allow_agent_decisions != deterministic.allow_agent_decisions
        assert autonomous.max_agent_autonomy_level != deterministic.max_agent_autonomy_level
    
    def test_mode_config_immutability_concern(self):
        """Test that mode configs can be created independently."""
        config1 = ModeConfig.autonomous()
        config2 = ModeConfig.autonomous()
        
        # They should be separate instances
        assert config1 is not config2
        # But have the same values
        assert config1.mode == config2.mode
        assert config1.allow_handoffs == config2.allow_handoffs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
