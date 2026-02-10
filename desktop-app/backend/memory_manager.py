"""
Dive AI — Memory Manager
Two-tier memory system for conversation context.

Short-term: recent messages in current conversation (last 20)
Long-term: persistent facts about user, preferences, summaries
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class MemoryManager:
    """Manages conversation context and long-term memory."""

    MAX_SHORT_TERM = 20  # Messages to include in LLM context
    SUMMARIZE_EVERY = 15  # Summarize after this many new messages

    def __init__(self, storage=None):
        """
        Args:
            storage: LocalStorage instance for persistence
        """
        self.storage = storage
        self._current_conv_id: Optional[str] = None
        self._short_term: List[Dict] = []  # Recent messages
        self._long_term: Dict = {}  # Persistent facts
        self._message_count_since_summary = 0

        # Load long-term memory from storage
        if storage:
            self._long_term = storage.get_memory("context")
            if not self._long_term:
                self._long_term = {
                    "user_facts": [],
                    "preferences": {},
                    "key_topics": [],
                    "created_at": datetime.now().isoformat(),
                }
                storage.save_memory("context", self._long_term)

        print(f"🧠 Memory initialized: {len(self._long_term.get('user_facts', []))} facts")

    def set_conversation(self, conv_id: str):
        """Switch to a conversation and load its messages."""
        self._current_conv_id = conv_id
        self._message_count_since_summary = 0

        if self.storage:
            messages = self.storage.get_messages(conv_id, limit=self.MAX_SHORT_TERM)
            self._short_term = messages
        else:
            self._short_term = []

    def add_message(self, role: str, content: str, thinking: str = None,
                    model: str = None, latency_ms: float = None,
                    actions: List[Dict] = None, tokens: int = 0):
        """Add message to short-term memory."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if thinking:
            msg["thinking"] = thinking
        if model:
            msg["model"] = model

        self._short_term.append(msg)

        # Trim to max size
        if len(self._short_term) > self.MAX_SHORT_TERM:
            self._short_term = self._short_term[-self.MAX_SHORT_TERM:]

        self._message_count_since_summary += 1

    def build_context_messages(self, current_message: str) -> List[Dict]:
        """
        Build the messages array to send to LLM.
        Includes long-term memory + recent conversation history + current message.
        """
        messages = []

        # 1. Long-term memory as system context
        memory_context = self._format_long_term_memory()
        if memory_context:
            messages.append({
                "role": "system",
                "content": memory_context,
            })

        # 2. Recent conversation history
        for msg in self._short_term:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        # 3. Current user message
        messages.append({
            "role": "user",
            "content": current_message,
        })

        return messages

    def _format_long_term_memory(self) -> str:
        """Format long-term memory for inclusion in system prompt."""
        parts = []

        facts = self._long_term.get("user_facts", [])
        if facts:
            parts.append("USER CONTEXT (from previous conversations):")
            for fact in facts[-10:]:  # Last 10 facts
                parts.append(f"  - {fact}")

        prefs = self._long_term.get("preferences", {})
        if prefs:
            parts.append("\nUSER PREFERENCES:")
            for k, v in prefs.items():
                parts.append(f"  - {k}: {v}")

        topics = self._long_term.get("key_topics", [])
        if topics:
            parts.append(f"\nRECENT TOPICS: {', '.join(topics[-5:])}")

        return "\n".join(parts) if parts else ""

    def extract_facts(self, message: str, response: str):
        """
        Extract key facts from a conversation turn.
        Simple heuristic-based extraction (no LLM dependency).
        """
        # Extract user preferences
        pref_keywords = {
            "language": ["vietnamese", "english", "tiếng việt"],
            "coding_language": ["python", "javascript", "typescript", "rust", "go"],
            "os": ["windows", "mac", "linux"],
        }

        msg_lower = message.lower()
        for pref_key, keywords in pref_keywords.items():
            for kw in keywords:
                if kw in msg_lower:
                    self._long_term.setdefault("preferences", {})[pref_key] = kw
                    break

        # Extract project mentions
        if any(word in msg_lower for word in ["project", "app", "repo", "repository"]):
            # Keep track of mentioned projects
            topics = self._long_term.setdefault("key_topics", [])
            topic = message[:50].strip()
            if topic not in topics:
                topics.append(topic)
                if len(topics) > 20:
                    topics.pop(0)

        # Save updated memory
        if self.storage:
            self._long_term["updated_at"] = datetime.now().isoformat()
            self.storage.save_memory("context", self._long_term)

    def add_fact(self, fact: str):
        """Manually add a fact to long-term memory."""
        facts = self._long_term.setdefault("user_facts", [])
        if fact not in facts:
            facts.append(fact)
            if len(facts) > 50:
                facts.pop(0)
        if self.storage:
            self.storage.save_memory("context", self._long_term)

    def get_status(self) -> Dict:
        """Get memory status for API/UI."""
        return {
            "initialized": True,
            "current_conversation": self._current_conv_id,
            "short_term_messages": len(self._short_term),
            "max_short_term": self.MAX_SHORT_TERM,
            "long_term_facts": len(self._long_term.get("user_facts", [])),
            "long_term_topics": len(self._long_term.get("key_topics", [])),
            "preferences": self._long_term.get("preferences", {}),
        }

    def clear_long_term(self):
        """Clear long-term memory."""
        self._long_term = {
            "user_facts": [],
            "preferences": {},
            "key_topics": [],
            "created_at": datetime.now().isoformat(),
        }
        if self.storage:
            self.storage.save_memory("context", self._long_term)
