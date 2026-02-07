"""
Unit tests for the communication protocol v2.0.

Tests cover:
- Message creation and serialization
- Protocol validation
- Message signing and verification
- Error reporting
- Handoff messaging
"""

import pytest
import json
from src.communication.protocol import (
    ProtocolVersion,
    MessageType,
    ErrorSeverity,
    MessageHeader,
    Message,
    ErrorReport,
    HandoffMessage,
    TaskMessage,
    ProtocolValidator,
    ProtocolConverter,
)


class TestProtocolVersion:
    """Tests for ProtocolVersion enum."""
    
    def test_protocol_versions(self):
        """Test protocol version values."""
        assert ProtocolVersion.V2_0.value == "2.0"
        assert ProtocolVersion.V2_1.value == "2.1"
    
    def test_protocol_version_string(self):
        """Test protocol version string representation."""
        assert str(ProtocolVersion.V2_0) == "2.0"
        assert str(ProtocolVersion.V2_1) == "2.1"


class TestMessageType:
    """Tests for MessageType enum."""
    
    def test_message_types(self):
        """Test message type values."""
        assert MessageType.TASK_REQUEST.value == "task_request"
        assert MessageType.TASK_RESPONSE.value == "task_response"
        assert MessageType.HANDOFF_REQUEST.value == "handoff_request"
        assert MessageType.ERROR_REPORT.value == "error_report"


class TestMessageHeader:
    """Tests for MessageHeader."""
    
    def test_message_header_creation(self):
        """Test creating a message header."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        assert header.protocol_version == "2.0"
        assert header.message_type == "task_request"
        assert header.sender_id == "orchestrator"
        assert header.receiver_id == "agent_001"
        assert header.message_id is not None
        assert header.timestamp is not None
    
    def test_message_header_invalid_version(self):
        """Test that invalid protocol version raises error."""
        with pytest.raises(ValueError):
            MessageHeader(
                protocol_version="1.0",
                message_type="task_request",
                sender_id="orchestrator",
                receiver_id="agent_001",
            )
    
    def test_message_header_to_dict(self):
        """Test converting header to dictionary."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        d = header.to_dict()
        
        assert d["protocol_version"] == "2.0"
        assert d["message_type"] == "task_request"
        assert d["sender_id"] == "orchestrator"
        assert d["receiver_id"] == "agent_001"


class TestMessage:
    """Tests for Message class."""
    
    def test_message_creation(self):
        """Test creating a message."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        payload = {"task_id": "task_001", "description": "Test task"}
        message = Message(header=header, payload=payload)
        
        assert message.header == header
        assert message.payload == payload
    
    def test_message_to_json(self):
        """Test converting message to JSON."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        payload = {"task_id": "task_001"}
        message = Message(header=header, payload=payload)
        
        json_str = message.to_json()
        data = json.loads(json_str)
        
        assert data["header"]["message_type"] == "task_request"
        assert data["payload"]["task_id"] == "task_001"
    
    def test_message_from_json(self):
        """Test creating message from JSON."""
        json_str = json.dumps({
            "header": {
                "protocol_version": "2.0",
                "message_id": "msg_001",
                "message_type": "task_request",
                "sender_id": "orchestrator",
                "receiver_id": "agent_001",
                "timestamp": "2024-01-31T12:00:00",
                "correlation_id": None,
                "signature": None,
            },
            "payload": {"task_id": "task_001"},
        })
        
        message = Message.from_json(json_str)
        
        assert message.header.message_type == "task_request"
        assert message.payload["task_id"] == "task_001"
    
    def test_message_signing(self):
        """Test message signing."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        payload = {"task_id": "task_001"}
        message = Message(header=header, payload=payload)
        
        secret_key = "super_secret_key"
        message.sign(secret_key)
        
        assert message.header.signature is not None
        assert len(message.header.signature) == 64  # SHA256 hex length
    
    def test_message_verify_signature(self):
        """Test message signature verification."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        payload = {"task_id": "task_001"}
        message = Message(header=header, payload=payload)
        
        secret_key = "super_secret_key"
        message.sign(secret_key)
        
        # Verify with correct key
        assert message.verify_signature(secret_key) is True
        
        # Verify with wrong key
        assert message.verify_signature("wrong_key") is False
    
    def test_message_signature_tampering_detection(self):
        """Test that tampering is detected."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        payload = {"task_id": "task_001"}
        message = Message(header=header, payload=payload)
        
        secret_key = "super_secret_key"
        message.sign(secret_key)
        
        # Tamper with payload
        message.payload["task_id"] = "task_002"
        
        # Verification should fail
        assert message.verify_signature(secret_key) is False


class TestErrorReport:
    """Tests for ErrorReport."""
    
    def test_error_report_creation(self):
        """Test creating an error report."""
        error = ErrorReport(
            error_type="execution_failure",
            message="Task execution failed",
            severity="error",
            context={"task_id": "task_001"},
        )
        
        assert error.error_type == "execution_failure"
        assert error.message == "Task execution failed"
        assert error.severity == "error"
        assert error.error_id is not None
    
    def test_error_report_invalid_severity(self):
        """Test that invalid severity raises error."""
        with pytest.raises(ValueError):
            ErrorReport(
                error_type="test",
                message="Test",
                severity="invalid_severity",
            )
    
    def test_error_report_to_message(self):
        """Test converting error report to message."""
        error = ErrorReport(
            error_type="execution_failure",
            message="Task execution failed",
            severity="error",
        )
        
        message = error.to_message("orchestrator", "agent_001")
        
        assert message.header.message_type == "error_report"
        assert message.header.sender_id == "orchestrator"
        assert message.payload["error_type"] == "execution_failure"
    
    def test_error_report_is_recoverable(self):
        """Test error recoverability check."""
        info_error = ErrorReport(
            error_type="test",
            message="Test",
            severity="info",
        )
        
        warning_error = ErrorReport(
            error_type="test",
            message="Test",
            severity="warning",
        )
        
        critical_error = ErrorReport(
            error_type="test",
            message="Test",
            severity="critical",
        )
        
        assert info_error.is_recoverable() is True
        assert warning_error.is_recoverable() is True
        assert critical_error.is_recoverable() is False


class TestHandoffMessage:
    """Tests for HandoffMessage."""
    
    def test_handoff_message_creation(self):
        """Test creating a handoff message."""
        handoff = HandoffMessage(
            handoff_id="handoff_001",
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type="specialization",
            reason="Need security expertise",
        )
        
        assert handoff.handoff_id == "handoff_001"
        assert handoff.from_agent_id == "agent_001"
        assert handoff.to_agent_specialization == "security_audit"
    
    def test_handoff_message_to_message(self):
        """Test converting handoff message to protocol message."""
        handoff = HandoffMessage(
            handoff_id="handoff_001",
            from_agent_id="agent_001",
            to_agent_specialization="security_audit",
            handoff_type="specialization",
            reason="Need security expertise",
        )
        
        message = handoff.to_message("agent_001", "orchestrator")
        
        assert message.header.message_type == "handoff_request"
        assert message.payload["handoff_id"] == "handoff_001"


class TestTaskMessage:
    """Tests for TaskMessage."""
    
    def test_task_message_creation(self):
        """Test creating a task message."""
        task = TaskMessage(
            task_id="task_001",
            description="Generate Python function",
            mode="autonomous",
            priority=8,
        )
        
        assert task.task_id == "task_001"
        assert task.description == "Generate Python function"
        assert task.mode == "autonomous"
        assert task.priority == 8
    
    def test_task_message_to_message(self):
        """Test converting task message to protocol message."""
        task = TaskMessage(
            task_id="task_001",
            description="Generate Python function",
        )
        
        message = task.to_message("orchestrator", "agent_001")
        
        assert message.header.message_type == "task_request"
        assert message.payload["task_id"] == "task_001"


class TestProtocolValidator:
    """Tests for ProtocolValidator."""
    
    def test_validate_valid_message(self):
        """Test validating a valid message."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        message = Message(header=header, payload={})
        
        is_valid, error = ProtocolValidator.validate_message(message)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_message_missing_sender(self):
        """Test validation fails when sender is missing."""
        header = MessageHeader(
            message_type="task_request",
            sender_id="",
            receiver_id="agent_001",
        )
        
        message = Message(header=header, payload={})
        
        is_valid, error = ProtocolValidator.validate_message(message)
        
        assert is_valid is False
        assert "sender" in error.lower()
    
    def test_validate_message_invalid_type(self):
        """Test validation fails with invalid message type."""
        header = MessageHeader(
            message_type="invalid_type",
            sender_id="orchestrator",
            receiver_id="agent_001",
        )
        
        message = Message(header=header, payload={})
        
        is_valid, error = ProtocolValidator.validate_message(message)
        
        assert is_valid is False
        assert "invalid" in error.lower()
    
    def test_validate_valid_error_report(self):
        """Test validating a valid error report."""
        error = ErrorReport(
            error_type="execution_failure",
            message="Task failed",
            severity="error",
        )
        
        is_valid, error_msg = ProtocolValidator.validate_error_report(error)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_error_report_missing_type(self):
        """Test validation fails when error type is missing."""
        error = ErrorReport(
            error_type="",
            message="Task failed",
            severity="error",
        )
        
        is_valid, error_msg = ProtocolValidator.validate_error_report(error)
        
        assert is_valid is False
        assert "error type" in error_msg.lower()


class TestProtocolConverter:
    """Tests for ProtocolConverter."""
    
    def test_error_to_message(self):
        """Test converting error to message."""
        message = ProtocolConverter.error_to_message(
            error_type="execution_failure",
            error_message="Task failed",
            severity="error",
            sender_id="orchestrator",
            receiver_id="agent_001",
            context={"task_id": "task_001"},
        )
        
        assert message.header.message_type == "error_report"
        assert message.payload["error_type"] == "execution_failure"
        assert message.payload["context"]["task_id"] == "task_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
