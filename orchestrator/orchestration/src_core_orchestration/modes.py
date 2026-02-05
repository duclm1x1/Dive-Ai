"""
Execution modes for the Dive Coder v16 Orchestrator.

This module defines the two execution modes supported by the system:
- AUTONOMOUS: Agents have full agency to make decisions and adapt
- DETERMINISTIC: Orchestrator maintains strict control over execution flow
"""

from enum import Enum
from typing import Optional


class ExecutionMode(Enum):
    """Enumeration of supported execution modes."""
    
    AUTONOMOUS = "autonomous"
    DETERMINISTIC = "deterministic"
    
    def __str__(self) -> str:
        """Return the string representation of the mode."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "ExecutionMode":
        """
        Create an ExecutionMode from a string value.
        
        Args:
            value: String representation of the mode
            
        Returns:
            ExecutionMode instance
            
        Raises:
            ValueError: If the value is not a valid mode
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_modes = ", ".join([m.value for m in cls])
            raise ValueError(
                f"Invalid execution mode '{value}'. Must be one of: {valid_modes}"
            )


class ModeConfig:
    """Configuration for execution mode behavior."""
    
    def __init__(
        self,
        mode: ExecutionMode,
        allow_handoffs: bool = True,
        allow_agent_decisions: bool = True,
        strict_plan_adherence: bool = False,
        max_agent_autonomy_level: int = 10,
    ):
        """
        Initialize mode configuration.
        
        Args:
            mode: The execution mode
            allow_handoffs: Whether agents can request handoffs
            allow_agent_decisions: Whether agents can make independent decisions
            strict_plan_adherence: Whether to strictly follow the execution plan
            max_agent_autonomy_level: Maximum autonomy level (0-10) for agents
        """
        self.mode = mode
        self.allow_handoffs = allow_handoffs
        self.allow_agent_decisions = allow_agent_decisions
        self.strict_plan_adherence = strict_plan_adherence
        self.max_agent_autonomy_level = max_agent_autonomy_level
    
    @classmethod
    def autonomous(cls) -> "ModeConfig":
        """Create a configuration for autonomous mode."""
        return cls(
            mode=ExecutionMode.AUTONOMOUS,
            allow_handoffs=True,
            allow_agent_decisions=True,
            strict_plan_adherence=False,
            max_agent_autonomy_level=10,
        )
    
    @classmethod
    def deterministic(cls) -> "ModeConfig":
        """Create a configuration for deterministic mode."""
        return cls(
            mode=ExecutionMode.DETERMINISTIC,
            allow_handoffs=False,
            allow_agent_decisions=False,
            strict_plan_adherence=True,
            max_agent_autonomy_level=0,
        )
    
    def __repr__(self) -> str:
        """Return string representation of the configuration."""
        return (
            f"ModeConfig(mode={self.mode.value}, "
            f"allow_handoffs={self.allow_handoffs}, "
            f"allow_agent_decisions={self.allow_agent_decisions}, "
            f"strict_plan_adherence={self.strict_plan_adherence}, "
            f"max_autonomy={self.max_agent_autonomy_level})"
        )
