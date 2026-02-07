"""
Unit tests for the agent handoff mechanism.

Tests cover:
- HandoffRequest creation and validation
- HandoffManager functionality
- Handoff lifecycle management
- Agent specialization tracking
"""

import pytest
from datetime import datetime
from src.agents.handoff import (
    HandoffRequest,
    HandoffType,
    HandoffStatus,
    HandoffManager,
)


class TestHandoffType:
    """Tests for HandoffType enum."""
    
    def test_handoff_type_values(self):
        """Test that HandoffType has correct values."""
        assert HandoffType.SPECIALIZATION.value == "specialization"
        assert HandoffType.COMPLEXITY.value == "complexity"
        assert HandoffType.RESOURCE.value == "resource"
        assert HandoffType.ESCALATION.value == "escalation"
    
    def test_handoff_type_string_representation(self):
        """Test string representation of HandoffType."""
        assert str(HandoffType.SPECIALIZATION) == "specialization"
        assert str(HandoffType.COMPLEXITY) == "complexity"


class TestHandoffStatus:
    """Tests for HandoffStatus enum."""
    
    def test_handoff_status_values(self):
        """Test that HandoffStatus has correct values."""
        assert HandoffStatus.PENDING.value == "pending"
        assert HandoffStatus.ACCEPTED.value == "accepted"
        assert HandoffStatus.REJECTED.value == "rejected"
        assert HandoffStatus.COMPLETED.value == "completed"
        assert HandoffStatus.FAILED.value == "failed"


class TestHandoffRequest:
    """Tests for HandoffRequest data class."""
    
    def test_handoff_request_creation(self):
        """Test creating a HandoffRequest."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Task requires security expertise",
            task_context={"task_id": "task_001"},
        )
        
        assert request.from_agent_id == "agent_001"
        assert request.to_agent_specialization == "security_audit"
        assert request.handoff_type == HandoffType.SPECIALIZATION
        assert request.reason == "Task requires security expertise"
        assert request.status == HandoffStatus.PENDING
        assert request.handoff_id is not None
    
    def test_handoff_request_with_partial_results(self):
        """Test HandoffRequest with partial results."""
        partial = {"code_analyzed": 150, "issues_found": 3}
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.COMPLEXITY,
            reason="Task too complex",
            partial_results=partial,
        )
        
        assert request.partial_results == partial
    
    def test_handoff_request_string_type_conversion(self):
        """Test that string handoff types are converted."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="test",
            handoff_type="specialization",
            reason="Test",
        )
        
        assert request.handoff_type == HandoffType.SPECIALIZATION
        assert isinstance(request.handoff_type, HandoffType)
    
    def test_handoff_request_invalid_type(self):
        """Test that invalid handoff type raises error."""
        with pytest.raises(ValueError):
            HandoffRequest(
                from_agent_id="agent_001",
                to_agent_specialization="test",
                handoff_type="invalid_type",
                reason="Test",
            )
    
    def test_handoff_request_accept(self):
        """Test accepting a handoff request."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
        )
        
        assert request.status == HandoffStatus.PENDING
        assert request.accepted_at is None
        
        request.accept("agent_002")
        
        assert request.status == HandoffStatus.ACCEPTED
        assert request.assigned_to_agent_id == "agent_002"
        assert request.accepted_at is not None
    
    def test_handoff_request_reject(self):
        """Test rejecting a handoff request."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
        )
        
        request.reject("No suitable agent available")
        
        assert request.status == HandoffStatus.REJECTED
        assert request.error_message == "No suitable agent available"
    
    def test_handoff_request_complete(self):
        """Test completing a handoff request."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
        )
        
        request.accept("agent_002")
        request.complete()
        
        assert request.status == HandoffStatus.COMPLETED
    
    def test_handoff_request_fail(self):
        """Test failing a handoff request."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
        )
        
        request.fail("Agent crashed during execution")
        
        assert request.status == HandoffStatus.FAILED
        assert request.error_message == "Agent crashed during execution"
    
    def test_handoff_request_status_checks(self):
        """Test status checking methods."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="test",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
        )
        
        assert request.is_pending() is True
        assert request.is_accepted() is False
        assert request.is_completed() is False
        
        request.accept("agent_002")
        assert request.is_pending() is False
        assert request.is_accepted() is True
        
        request.complete()
        assert request.is_completed() is True
    
    def test_handoff_request_to_dict(self):
        """Test converting HandoffRequest to dictionary."""
        request = HandoffRequest(
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test reason",
        )
        
        request.accept("agent_002")
        
        d = request.to_dict()
        
        assert d["from_agent_id"] == "agent_001"
        assert d["to_agent_specialization"] == "security_audit"
        assert d["handoff_type"] == "specialization"
        assert d["status"] == "accepted"
        assert d["assigned_to_agent_id"] == "agent_002"
        assert d["reason"] == "Test reason"


class TestHandoffManager:
    """Tests for HandoffManager."""
    
    def test_handoff_manager_initialization(self):
        """Test HandoffManager initialization."""
        manager = HandoffManager()
        
        assert len(manager.pending_handoffs) == 0
        assert len(manager.completed_handoffs) == 0
        assert len(manager.agent_specializations) == 0
    
    def test_register_agent(self):
        """Test registering agents with specializations."""
        manager = HandoffManager()
        
        manager.register_agent("agent_001", ["code_generation", "refactoring"])
        manager.register_agent("agent_002", ["security_audit", "testing"])
        
        assert "agent_001" in manager.agent_specializations
        assert "agent_002" in manager.agent_specializations
        assert manager.agent_specializations["agent_001"] == ["code_generation", "refactoring"]
    
    def test_create_handoff_request(self):
        """Test creating a handoff request through the manager."""
        manager = HandoffManager()
        
        request = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Need security expertise",
            task_context={"task_id": "task_001"},
            partial_results={"analyzed": 100},
        )
        
        assert request.handoff_id in manager.pending_handoffs
        assert request.status == HandoffStatus.PENDING
    
    def test_find_suitable_agent(self):
        """Test finding an agent with required specialization."""
        manager = HandoffManager()
        manager.register_agent("agent_001", ["code_generation"])
        manager.register_agent("agent_002", ["security_audit", "testing"])
        manager.register_agent("agent_003", ["documentation"])
        
        # Find agent with security_audit
        agent = manager.find_suitable_agent("security_audit")
        assert agent == "agent_002"
        
        # Find agent with code_generation
        agent = manager.find_suitable_agent("code_generation")
        assert agent == "agent_001"
        
        # Find agent with non-existent specialization
        agent = manager.find_suitable_agent("non_existent")
        assert agent is None
    
    def test_accept_handoff(self):
        """Test accepting a handoff request."""
        manager = HandoffManager()
        
        request = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
            task_context={},
            partial_results={},
        )
        
        handoff_id = request.handoff_id
        result = manager.accept_handoff(handoff_id, "agent_002")
        
        assert result is True
        assert manager.pending_handoffs[handoff_id].status == HandoffStatus.ACCEPTED
        assert manager.pending_handoffs[handoff_id].assigned_to_agent_id == "agent_002"
    
    def test_accept_nonexistent_handoff(self):
        """Test accepting a non-existent handoff."""
        manager = HandoffManager()
        
        result = manager.accept_handoff("nonexistent_id", "agent_002")
        
        assert result is False
    
    def test_reject_handoff(self):
        """Test rejecting a handoff request."""
        manager = HandoffManager()
        
        request = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
            task_context={},
            partial_results={},
        )
        
        handoff_id = request.handoff_id
        result = manager.reject_handoff(handoff_id, "No suitable agent")
        
        assert result is True
        assert handoff_id not in manager.pending_handoffs
        assert len(manager.completed_handoffs) == 1
        assert manager.completed_handoffs[0].status == HandoffStatus.REJECTED
    
    def test_complete_handoff(self):
        """Test completing a handoff request."""
        manager = HandoffManager()
        
        request = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
            task_context={},
            partial_results={},
        )
        
        handoff_id = request.handoff_id
        manager.accept_handoff(handoff_id, "agent_002")
        result = manager.complete_handoff(handoff_id)
        
        assert result is True
        assert handoff_id not in manager.pending_handoffs
        assert len(manager.completed_handoffs) == 1
        assert manager.completed_handoffs[0].status == HandoffStatus.COMPLETED
    
    def test_get_pending_handoffs(self):
        """Test getting all pending handoffs."""
        manager = HandoffManager()
        
        req1 = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test 1",
            task_context={},
            partial_results={},
        )
        
        req2 = manager.create_handoff_request(
            from_agent_id="agent_002",
            to_specialization="testing",
            handoff_type=HandoffType.COMPLEXITY,
            reason="Test 2",
            task_context={},
            partial_results={},
        )
        
        pending = manager.get_pending_handoffs()
        
        assert len(pending) == 2
        assert req1 in pending
        assert req2 in pending
    
    def test_get_handoff_status(self):
        """Test getting handoff status."""
        manager = HandoffManager()
        
        request = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
            task_context={},
            partial_results={},
        )
        
        handoff_id = request.handoff_id
        
        # Check pending status
        status = manager.get_handoff_status(handoff_id)
        assert status == HandoffStatus.PENDING
        
        # Accept and check status
        manager.accept_handoff(handoff_id, "agent_002")
        status = manager.get_handoff_status(handoff_id)
        assert status == HandoffStatus.ACCEPTED
        
        # Complete and check status
        manager.complete_handoff(handoff_id)
        status = manager.get_handoff_status(handoff_id)
        assert status == HandoffStatus.COMPLETED
    
    def test_get_stats(self):
        """Test getting handoff statistics."""
        manager = HandoffManager()
        manager.register_agent("agent_001", ["code_generation"])
        manager.register_agent("agent_002", ["security_audit"])
        
        # Create and complete some handoffs
        req1 = manager.create_handoff_request(
            from_agent_id="agent_001",
            to_specialization="security_audit",
            handoff_type=HandoffType.SPECIALIZATION,
            reason="Test",
            task_context={},
            partial_results={},
        )
        
        req2 = manager.create_handoff_request(
            from_agent_id="agent_002",
            to_specialization="testing",
            handoff_type=HandoffType.COMPLEXITY,
            reason="Test",
            task_context={},
            partial_results={},
        )
        
        manager.complete_handoff(req1.handoff_id)
        
        stats = manager.get_stats()
        
        assert stats["pending_handoffs"] == 1
        assert stats["completed_handoffs"] == 1
        assert stats["registered_agents"] == 2
        assert "specialization" in stats["completed_by_type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
