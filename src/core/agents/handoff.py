"""
Agent handoff mechanism for Dive Coder v16.

This module provides the infrastructure for agents to request handoffs to other agents
when they encounter tasks outside their specialization or capability.

Handoff Types:
- SPECIALIZATION: Task requires a specialist agent
- COMPLEXITY: Task exceeds agent capability
- RESOURCE: Agent lacks required resources
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


class HandoffType(Enum):
    """Types of handoff requests."""
    
    SPECIALIZATION = "specialization"  # Task requires specialist expertise
    COMPLEXITY = "complexity"  # Task exceeds capability level
    RESOURCE = "resource"  # Missing required resources
    ESCALATION = "escalation"  # Needs higher-level handling
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class HandoffStatus(Enum):
    """Status of a handoff request."""
    
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class HandoffRequest:
    """
    Request for an agent to hand off a task to another agent.
    
    Attributes:
        handoff_id: Unique identifier for this handoff
        from_agent_id: ID of the agent requesting handoff
        to_agent_specialization: Specialization required in target agent
        handoff_type: Type of handoff (specialization, complexity, etc.)
        reason: Human-readable reason for the handoff
        task_context: Context about the current task
        partial_results: Any partial results from the current agent
        requested_at: Timestamp of handoff request
        accepted_at: Timestamp when handoff was accepted (if applicable)
        status: Current status of the handoff
    """
    
    from_agent_id: str
    to_agent_specialization: str
    handoff_type: HandoffType
    reason: str
    task_context: Dict[str, Any] = field(default_factory=dict)
    partial_results: Dict[str, Any] = field(default_factory=dict)
    handoff_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requested_at: datetime = field(default_factory=datetime.now)
    accepted_at: Optional[datetime] = None
    status: HandoffStatus = field(default=HandoffStatus.PENDING)
    assigned_to_agent_id: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate handoff request."""
        if not isinstance(self.handoff_type, HandoffType):
            if isinstance(self.handoff_type, str):
                self.handoff_type = HandoffType(self.handoff_type)
            else:
                raise ValueError(f"Invalid handoff type: {self.handoff_type}")
    
    def accept(self, assigned_to_agent_id: str) -> None:
        """
        Mark the handoff as accepted.
        
        Args:
            assigned_to_agent_id: ID of the agent accepting the handoff
        """
        self.status = HandoffStatus.ACCEPTED
        self.accepted_at = datetime.now()
        self.assigned_to_agent_id = assigned_to_agent_id
    
    def reject(self, reason: str) -> None:
        """
        Reject the handoff request.
        
        Args:
            reason: Reason for rejection
        """
        self.status = HandoffStatus.REJECTED
        self.error_message = reason
    
    def complete(self) -> None:
        """Mark the handoff as completed."""
        self.status = HandoffStatus.COMPLETED
    
    def fail(self, error_message: str) -> None:
        """
        Mark the handoff as failed.
        
        Args:
            error_message: Description of the failure
        """
        self.status = HandoffStatus.FAILED
        self.error_message = error_message
    
    def is_pending(self) -> bool:
        """Check if handoff is pending."""
        return self.status == HandoffStatus.PENDING
    
    def is_accepted(self) -> bool:
        """Check if handoff is accepted."""
        return self.status == HandoffStatus.ACCEPTED
    
    def is_completed(self) -> bool:
        """Check if handoff is completed."""
        return self.status == HandoffStatus.COMPLETED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "handoff_id": self.handoff_id,
            "from_agent_id": self.from_agent_id,
            "to_agent_specialization": self.to_agent_specialization,
            "handoff_type": str(self.handoff_type),
            "reason": self.reason,
            "status": str(self.status),
            "assigned_to_agent_id": self.assigned_to_agent_id,
            "requested_at": self.requested_at.isoformat(),
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
        }


class HandoffManager:
    """
    Manages handoff requests and routing.
    
    Responsibilities:
    - Track pending handoff requests
    - Find suitable agents for handoffs
    - Manage handoff lifecycle
    """
    
    def __init__(self):
        """Initialize the handoff manager."""
        self.pending_handoffs: Dict[str, HandoffRequest] = {}
        self.completed_handoffs: list[HandoffRequest] = []
        self.agent_specializations: Dict[str, list[str]] = {}
    
    def register_agent(self, agent_id: str, specializations: list[str]) -> None:
        """
        Register an agent with its specializations.
        
        Args:
            agent_id: ID of the agent
            specializations: List of specializations (skills) the agent has
        """
        self.agent_specializations[agent_id] = specializations
    
    def create_handoff_request(
        self,
        from_agent_id: str,
        to_specialization: str,
        handoff_type: HandoffType,
        reason: str,
        task_context: Dict[str, Any],
        partial_results: Dict[str, Any],
    ) -> HandoffRequest:
        """
        Create a new handoff request.
        
        Args:
            from_agent_id: ID of agent requesting handoff
            to_specialization: Required specialization
            handoff_type: Type of handoff
            reason: Reason for handoff
            task_context: Current task context
            partial_results: Partial results from current agent
            
        Returns:
            HandoffRequest instance
        """
        handoff = HandoffRequest(
            from_agent_id=from_agent_id,
            to_agent_specialization=to_specialization,
            handoff_type=handoff_type,
            reason=reason,
            task_context=task_context,
            partial_results=partial_results,
        )
        
        self.pending_handoffs[handoff.handoff_id] = handoff
        return handoff
    
    def find_suitable_agent(self, specialization: str) -> Optional[str]:
        """
        Find an agent with the required specialization.
        
        Args:
            specialization: Required specialization
            
        Returns:
            Agent ID if found, None otherwise
        """
        for agent_id, specs in self.agent_specializations.items():
            if specialization in specs:
                return agent_id
        return None
    
    def accept_handoff(self, handoff_id: str, assigned_to_agent_id: str) -> bool:
        """
        Accept a handoff request.
        
        Args:
            handoff_id: ID of the handoff request
            assigned_to_agent_id: ID of agent accepting the handoff
            
        Returns:
            True if accepted, False if not found
        """
        if handoff_id not in self.pending_handoffs:
            return False
        
        handoff = self.pending_handoffs[handoff_id]
        handoff.accept(assigned_to_agent_id)
        return True
    
    def reject_handoff(self, handoff_id: str, reason: str) -> bool:
        """
        Reject a handoff request.
        
        Args:
            handoff_id: ID of the handoff request
            reason: Reason for rejection
            
        Returns:
            True if rejected, False if not found
        """
        if handoff_id not in self.pending_handoffs:
            return False
        
        handoff = self.pending_handoffs[handoff_id]
        handoff.reject(reason)
        self.completed_handoffs.append(handoff)
        del self.pending_handoffs[handoff_id]
        return True
    
    def complete_handoff(self, handoff_id: str) -> bool:
        """
        Mark a handoff as completed.
        
        Args:
            handoff_id: ID of the handoff request
            
        Returns:
            True if completed, False if not found
        """
        if handoff_id not in self.pending_handoffs:
            return False
        
        handoff = self.pending_handoffs[handoff_id]
        handoff.complete()
        self.completed_handoffs.append(handoff)
        del self.pending_handoffs[handoff_id]
        return True
    
    def get_pending_handoffs(self) -> list[HandoffRequest]:
        """Get all pending handoff requests."""
        return list(self.pending_handoffs.values())
    
    def get_handoff_status(self, handoff_id: str) -> Optional[HandoffStatus]:
        """
        Get the status of a handoff request.
        
        Args:
            handoff_id: ID of the handoff request
            
        Returns:
            HandoffStatus if found, None otherwise
        """
        if handoff_id in self.pending_handoffs:
            return self.pending_handoffs[handoff_id].status
        
        for handoff in self.completed_handoffs:
            if handoff.handoff_id == handoff_id:
                return handoff.status
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about handoffs."""
        total_completed = len(self.completed_handoffs)
        completed_by_type = {}
        for handoff in self.completed_handoffs:
            htype = str(handoff.handoff_type)
            completed_by_type[htype] = completed_by_type.get(htype, 0) + 1
        
        return {
            "pending_handoffs": len(self.pending_handoffs),
            "completed_handoffs": total_completed,
            "registered_agents": len(self.agent_specializations),
            "completed_by_type": completed_by_type,
        }
