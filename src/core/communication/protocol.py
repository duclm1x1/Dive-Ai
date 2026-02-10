"""
Communication Protocol v2.0 for Dive Coder v16.

This module defines the communication protocol between components:
- Message versioning and compatibility
- Message signing and validation
- Error reporting format
- Handoff message format
- Request/Response patterns
"""

import json
import hashlib
import hmac
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


class ProtocolVersion(Enum):
    """Protocol versions."""
    V2_0 = "2.0"
    V2_1 = "2.1"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class MessageType(Enum):
    """Types of messages in the protocol."""
    
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HANDOFF_REQUEST = "handoff_request"
    HANDOFF_RESPONSE = "handoff_response"
    ERROR_REPORT = "error_report"
    STATUS_UPDATE = "status_update"
    HEARTBEAT = "heartbeat"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class ErrorSeverity(Enum):
    """Error severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class MessageHeader:
    """Header for all protocol messages."""
    
    protocol_version: str = "2.0"
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None
    signature: Optional[str] = None
    
    def __post_init__(self):
        """Validate header."""
        if self.protocol_version not in ["2.0", "2.1"]:
            raise ValueError(f"Unsupported protocol version: {self.protocol_version}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Message:
    """Base message class for protocol v2.0."""
    
    header: MessageHeader
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert message to JSON."""
        return json.dumps({
            "header": self.header.to_dict(),
            "payload": self.payload,
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON."""
        data = json.loads(json_str)
        header = MessageHeader(**data["header"])
        return cls(header=header, payload=data["payload"])
    
    def sign(self, secret_key: str) -> None:
        """
        Sign the message with a secret key.
        
        Args:
            secret_key: Secret key for signing
        """
        # Create signature from header and payload
        message_content = json.dumps({
            "header": {k: v for k, v in self.header.to_dict().items() if k != "signature"},
            "payload": self.payload,
        }, sort_keys=True)
        
        signature = hmac.new(
            secret_key.encode(),
            message_content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.header.signature = signature
    
    def verify_signature(self, secret_key: str) -> bool:
        """
        Verify message signature.
        
        Args:
            secret_key: Secret key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.header.signature:
            return False
        
        # Recreate signature
        message_content = json.dumps({
            "header": {k: v for k, v in self.header.to_dict().items() if k != "signature"},
            "payload": self.payload,
        }, sort_keys=True)
        
        expected_signature = hmac.new(
            secret_key.encode(),
            message_content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(self.header.signature, expected_signature)


@dataclass
class ErrorReport:
    """Error report message."""
    
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_type: str = ""
    severity: str = "error"
    message: str = ""
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_action: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate error report."""
        if self.severity not in ["info", "warning", "error", "critical"]:
            raise ValueError(f"Invalid severity: {self.severity}")
    
    def to_message(self, sender_id: str, receiver_id: str) -> Message:
        """Convert to a protocol message."""
        header = MessageHeader(
            message_type=str(MessageType.ERROR_REPORT),
            sender_id=sender_id,
            receiver_id=receiver_id,
        )
        
        return Message(
            header=header,
            payload=asdict(self),
        )
    
    def is_recoverable(self) -> bool:
        """Check if error is recoverable."""
        return self.severity in ["info", "warning"]


@dataclass
class HandoffMessage:
    """Handoff message in protocol format."""
    
    handoff_id: str
    from_agent_id: str
    to_agent_specialization: str
    handoff_type: str
    reason: str
    task_context: Dict[str, Any] = field(default_factory=dict)
    partial_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_message(self, sender_id: str, receiver_id: str) -> Message:
        """Convert to a protocol message."""
        header = MessageHeader(
            message_type=str(MessageType.HANDOFF_REQUEST),
            sender_id=sender_id,
            receiver_id=receiver_id,
        )
        
        return Message(
            header=header,
            payload=asdict(self),
        )


@dataclass
class TaskMessage:
    """Task request message in protocol format."""
    
    task_id: str
    description: str
    mode: str = "autonomous"
    priority: int = 5
    max_agents: int = 4
    timeout_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_message(self, sender_id: str, receiver_id: str) -> Message:
        """Convert to a protocol message."""
        header = MessageHeader(
            message_type=str(MessageType.TASK_REQUEST),
            sender_id=sender_id,
            receiver_id=receiver_id,
        )
        
        return Message(
            header=header,
            payload=asdict(self),
        )


class ProtocolValidator:
    """Validates protocol compliance."""
    
    @staticmethod
    def validate_message(message: Message) -> tuple[bool, Optional[str]]:
        """
        Validate a message for protocol compliance.
        
        Args:
            message: Message to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required header fields
        if not message.header.protocol_version:
            return False, "Missing protocol version"
        
        if not message.header.message_id:
            return False, "Missing message ID"
        
        if not message.header.message_type:
            return False, "Missing message type"
        
        if not message.header.sender_id:
            return False, "Missing sender ID"
        
        if not message.header.receiver_id:
            return False, "Missing receiver ID"
        
        # Check message type is valid
        valid_types = [str(t) for t in MessageType]
        if message.header.message_type not in valid_types:
            return False, f"Invalid message type: {message.header.message_type}"
        
        return True, None
    
    @staticmethod
    def validate_error_report(error: ErrorReport) -> tuple[bool, Optional[str]]:
        """
        Validate an error report.
        
        Args:
            error: Error report to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not error.error_type:
            return False, "Missing error type"
        
        if not error.message:
            return False, "Missing error message"
        
        valid_severities = [str(s) for s in ErrorSeverity]
        if error.severity not in valid_severities:
            return False, f"Invalid severity: {error.severity}"
        
        return True, None


class ProtocolConverter:
    """Converts between internal and protocol formats."""
    
    @staticmethod
    def task_spec_to_message(task_spec: Any, sender_id: str, receiver_id: str) -> Message:
        """Convert TaskSpec to protocol message."""
        task_msg = TaskMessage(
            task_id=task_spec.task_id,
            description=task_spec.description,
            mode=str(task_spec.mode),
            priority=task_spec.priority,
            max_agents=task_spec.max_agents,
            timeout_seconds=task_spec.timeout_seconds,
            metadata=task_spec.metadata,
        )
        
        return task_msg.to_message(sender_id, receiver_id)
    
    @staticmethod
    def handoff_request_to_message(
        handoff_request: Any,
        sender_id: str,
        receiver_id: str
    ) -> Message:
        """Convert HandoffRequest to protocol message."""
        handoff_msg = HandoffMessage(
            handoff_id=handoff_request.handoff_id,
            from_agent_id=handoff_request.from_agent_id,
            to_agent_specialization=handoff_request.to_agent_specialization,
            handoff_type=str(handoff_request.handoff_type),
            reason=handoff_request.reason,
            task_context=handoff_request.task_context,
            partial_results=handoff_request.partial_results,
        )
        
        return handoff_msg.to_message(sender_id, receiver_id)
    
    @staticmethod
    def error_to_message(
        error_type: str,
        error_message: str,
        severity: str,
        sender_id: str,
        receiver_id: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
    ) -> Message:
        """Create error report message."""
        error = ErrorReport(
            error_type=error_type,
            message=error_message,
            severity=severity,
            context=context or {},
            stack_trace=stack_trace,
        )
        
        return error.to_message(sender_id, receiver_id)
