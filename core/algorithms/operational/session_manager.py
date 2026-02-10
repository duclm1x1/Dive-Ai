"""
📋 SESSION MANAGER
Manage conversation sessions and context

Based on V28's core_engine/session_manager.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class Message:
    """A message in a session"""
    role: str  # user, assistant, system
    content: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class Session:
    """A conversation session"""
    id: str
    messages: List[Message] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
    created_at: float = 0.0
    last_active: float = 0.0


class SessionManagerAlgorithm(BaseAlgorithm):
    """
    📋 Session Manager
    
    Manages conversation sessions:
    - Session lifecycle
    - Message history
    - Context preservation
    - Multi-session support
    
    From V28: core_engine/session_manager.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="SessionManager",
            name="Session Manager",
            level="operational",
            category="context",
            version="1.0",
            description="Manage conversation sessions",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "create/add/get/close"),
                    IOField("session_id", "string", False, "Session ID"),
                    IOField("message", "object", False, "Message to add")
                ],
                outputs=[
                    IOField("result", "object", True, "Session result")
                ]
            ),
            steps=["Manage lifecycle", "Store messages", "Track context", "Handle cleanup"],
            tags=["session", "context", "conversation"]
        )
        
        self.sessions: Dict[str, Session] = {}
        self.active_session: Optional[str] = None
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "get")
        
        print(f"\n📋 Session Manager")
        
        if action == "create":
            return self._create_session(params.get("session_id"))
        elif action == "add":
            return self._add_message(params.get("session_id", ""), params.get("message", {}))
        elif action == "get":
            return self._get_session(params.get("session_id", ""))
        elif action == "close":
            return self._close_session(params.get("session_id", ""))
        elif action == "list":
            return self._list_sessions()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _create_session(self, session_id: Optional[str]) -> AlgorithmResult:
        now = time.time()
        session = Session(
            id=session_id or f"session_{len(self.sessions)}_{int(now)}",
            created_at=now,
            last_active=now
        )
        
        self.sessions[session.id] = session
        self.active_session = session.id
        
        print(f"   Created: {session.id}")
        
        return AlgorithmResult(
            status="success",
            data={"session_id": session.id, "total_sessions": len(self.sessions)}
        )
    
    def _add_message(self, session_id: str, message_data: Dict) -> AlgorithmResult:
        session_id = session_id or self.active_session
        
        if not session_id or session_id not in self.sessions:
            return AlgorithmResult(status="error", error="Session not found")
        
        session = self.sessions[session_id]
        message = Message(
            role=message_data.get("role", "user"),
            content=message_data.get("content", ""),
            timestamp=time.time(),
            metadata=message_data.get("metadata", {})
        )
        
        session.messages.append(message)
        session.last_active = time.time()
        
        return AlgorithmResult(
            status="success",
            data={
                "session_id": session_id,
                "message_count": len(session.messages)
            }
        )
    
    def _get_session(self, session_id: str) -> AlgorithmResult:
        session_id = session_id or self.active_session
        
        if not session_id or session_id not in self.sessions:
            return AlgorithmResult(status="error", error="Session not found")
        
        session = self.sessions[session_id]
        
        return AlgorithmResult(
            status="success",
            data={
                "session_id": session.id,
                "message_count": len(session.messages),
                "messages": [
                    {"role": m.role, "content": m.content[:100], "timestamp": m.timestamp}
                    for m in session.messages[-20:]  # Last 20 messages
                ],
                "context": session.context,
                "created_at": session.created_at,
                "last_active": session.last_active
            }
        )
    
    def _close_session(self, session_id: str) -> AlgorithmResult:
        session_id = session_id or self.active_session
        
        if not session_id or session_id not in self.sessions:
            return AlgorithmResult(status="error", error="Session not found")
        
        session = self.sessions.pop(session_id)
        
        if self.active_session == session_id:
            self.active_session = next(iter(self.sessions), None)
        
        return AlgorithmResult(
            status="success",
            data={
                "closed": session_id,
                "message_count": len(session.messages),
                "remaining_sessions": len(self.sessions)
            }
        )
    
    def _list_sessions(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "sessions": [
                    {
                        "id": s.id,
                        "message_count": len(s.messages),
                        "last_active": s.last_active
                    }
                    for s in sorted(self.sessions.values(), key=lambda x: -x.last_active)
                ],
                "active_session": self.active_session,
                "total": len(self.sessions)
            }
        )


def register(algorithm_manager):
    algo = SessionManagerAlgorithm()
    algorithm_manager.register("SessionManager", algo)
    print("✅ SessionManager registered")


if __name__ == "__main__":
    algo = SessionManagerAlgorithm()
    algo.execute({"action": "create"})
    algo.execute({"action": "add", "message": {"role": "user", "content": "Hello!"}})
    algo.execute({"action": "add", "message": {"role": "assistant", "content": "Hi there!"}})
    result = algo.execute({"action": "get"})
    print(f"Messages: {result.data['message_count']}")
