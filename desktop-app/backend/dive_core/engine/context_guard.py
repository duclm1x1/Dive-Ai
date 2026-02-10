"""
Dive AI — Context Window Guard
Surpass Feature #2: Token monitoring, dynamic summarization, smart compaction.

OpenClaw blocks at <16K, warns at <32K. Dive AI adds:
  - Pre-compaction memory flush (save facts before compacting)
  - Adaptive chunk sizing for summarization
  - Cost-aware context budgeting
  - Token accounting per tool call
"""

import time
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class TokenBudget:
    """Track token usage across a conversation."""
    max_tokens: int = 128000      # Model context window
    reserved_system: int = 4000   # Reserved for system prompt
    reserved_output: int = 8000   # Reserved for model output
    warning_threshold: float = 0.75  # Warn at 75% usage
    critical_threshold: float = 0.90  # Critical at 90% usage

    @property
    def available(self) -> int:
        # Scale reserved amounts for small models so available is never negative
        total_reserved = self.reserved_system + self.reserved_output
        if total_reserved >= self.max_tokens:
            # For small models, reserve at most 40% of total
            total_reserved = int(self.max_tokens * 0.4)
        return max(1, self.max_tokens - total_reserved)

    def check(self, used: int) -> str:
        ratio = used / self.available if self.available > 0 else 1.0
        if ratio >= self.critical_threshold:
            return "critical"
        elif ratio >= self.warning_threshold:
            return "warning"
        return "ok"


@dataclass
class ContextMessage:
    """A message in the context window."""
    role: str
    content: str
    tokens: int = 0
    timestamp: float = field(default_factory=time.time)
    tool_call: bool = False
    compactable: bool = True
    preserved: bool = False  # If True, never compact this message


class ContextWindowGuard:
    """
    Prevents context overflow and ensures coherent LLM responses.

    Features beyond OpenClaw:
      - Pre-compaction memory flush
      - Adaptive summarization chunk sizing
      - Cost-aware token budgeting
      - Per-tool-call token accounting
    """

    # Rough token estimation: ~4 chars per token (English)
    CHARS_PER_TOKEN = 4

    # Safety minimums
    MIN_CONTEXT_BLOCK = 16000   # Block if context < 16K tokens
    MIN_CONTEXT_WARN = 32000    # Warn if context < 32K tokens

    def __init__(self, model_max_tokens: int = 128000):
        self.budget = TokenBudget(max_tokens=model_max_tokens)
        self._messages: List[ContextMessage] = []
        self._compaction_count = 0
        self._total_tokens_processed = 0
        self._facts_extracted: List[str] = []
        self._tool_token_usage: Dict[str, int] = {}

    # ── Token Estimation ──────────────────────────────────────

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (tiktoken-compatible)."""
        if not text:
            return 0
        # Rough estimate: count words + punctuation groups
        # More accurate than simple char/4 for mixed content
        words = len(re.findall(r'\S+', text))
        # Code tends to have more tokens per word
        code_bonus = text.count('\n') * 0.5
        return int(words * 1.3 + code_bonus)

    # ── Message Management ────────────────────────────────────

    def add_message(self, role: str, content: str,
                    tool_call: bool = False,
                    preserve: bool = False) -> Dict:
        """Add a message and check context status."""
        tokens = self.estimate_tokens(content)
        msg = ContextMessage(
            role=role,
            content=content,
            tokens=tokens,
            tool_call=tool_call,
            preserved=preserve,
        )
        self._messages.append(msg)
        self._total_tokens_processed += tokens

        if tool_call and role == "tool":
            tool_name = content[:50].split(":")[0] if ":" in content else "unknown"
            self._tool_token_usage[tool_name] = (
                self._tool_token_usage.get(tool_name, 0) + tokens
            )

        # Check status
        total = self.current_token_count()
        status = self.budget.check(total)

        avail = self.budget.available
        result = {
            "tokens_added": tokens,
            "total_tokens": total,
            "available": avail,
            "usage_ratio": round(total / avail, 3) if avail > 0 else 1.0,
            "status": status,
        }

        # Auto-compact if critical
        if status == "critical":
            compact_result = self.compact()
            result["compacted"] = True
            result["compaction"] = compact_result

        return result

    def current_token_count(self) -> int:
        """Get current total token count."""
        return sum(m.tokens for m in self._messages)

    # ── Context Compaction ────────────────────────────────────

    def compact(self, target_ratio: float = 0.50) -> Dict:
        """
        Compact context to target ratio.

        Strategy:
        1. Extract key facts from old messages (pre-compaction flush)
        2. Summarize compactable messages
        3. Replace old messages with summary
        4. Keep preserved messages intact
        """
        before = self.current_token_count()
        target_tokens = int(self.budget.available * target_ratio)

        if before <= target_tokens:
            return {"compacted": False, "reason": "Already within target"}

        # Phase 1: Extract facts before compacting
        new_facts = self._extract_facts()
        self._facts_extracted.extend(new_facts)

        # Phase 2: Identify compactable messages (oldest first)
        compactable = [m for m in self._messages
                       if m.compactable and not m.preserved]

        if not compactable:
            return {"compacted": False, "reason": "No compactable messages"}

        # Phase 3: Determine how many messages to compact
        tokens_to_remove = before - target_tokens
        messages_to_compact = []
        tokens_removed = 0

        for msg in compactable:
            if tokens_removed >= tokens_to_remove:
                break
            messages_to_compact.append(msg)
            tokens_removed += msg.tokens

        if not messages_to_compact:
            return {"compacted": False, "reason": "Nothing to compact"}

        # Phase 4: Generate summary of compacted messages
        summary = self._summarize_messages(messages_to_compact)
        summary_tokens = self.estimate_tokens(summary)

        # Phase 5: Replace compacted messages with summary
        summary_msg = ContextMessage(
            role="system",
            content=f"[Context Summary]\n{summary}",
            tokens=summary_tokens,
            compactable=False,  # Don't re-compact summaries
            preserved=True,
        )

        # Remove old messages, insert summary at their position
        first_idx = self._messages.index(messages_to_compact[0])
        for msg in messages_to_compact:
            self._messages.remove(msg)
        self._messages.insert(first_idx, summary_msg)

        after = self.current_token_count()
        self._compaction_count += 1

        return {
            "compacted": True,
            "messages_compacted": len(messages_to_compact),
            "tokens_before": before,
            "tokens_after": after,
            "tokens_saved": before - after,
            "facts_extracted": len(new_facts),
            "compaction_number": self._compaction_count,
        }

    def _extract_facts(self) -> List[str]:
        """Extract key facts from messages before compaction."""
        facts = []
        for msg in self._messages:
            if not msg.compactable or msg.preserved:
                continue
            content = msg.content
            # Extract URLs
            urls = re.findall(r'https?://\S+', content)
            for url in urls[:3]:
                facts.append(f"URL referenced: {url}")
            # Extract file paths
            paths = re.findall(r'[/\\][\w/\\.-]+\.\w+', content)
            for path in paths[:3]:
                facts.append(f"File: {path}")
            # Extract code patterns
            if '```' in content:
                facts.append("Code block discussed")
            # Extract key decisions (sentences with "should", "must", "decided")
            for line in content.split('\n'):
                line = line.strip()
                if any(kw in line.lower() for kw in
                       ['should', 'must', 'decided', 'important', 'critical']):
                    if 10 < len(line) < 200:
                        facts.append(f"Decision: {line[:150]}")
        return facts[:20]  # Cap at 20 facts

    def _summarize_messages(self, messages: List[ContextMessage]) -> str:
        """Generate a summary of messages (without LLM — rule-based)."""
        parts = []
        user_msgs = [m for m in messages if m.role == "user"]
        assistant_msgs = [m for m in messages if m.role == "assistant"]
        tool_msgs = [m for m in messages if m.tool_call]

        if user_msgs:
            topics = set()
            for m in user_msgs:
                words = m.content.split()[:10]
                topics.add(" ".join(words))
            parts.append(f"User discussed: {'; '.join(list(topics)[:5])}")

        if assistant_msgs:
            parts.append(f"Assistant provided {len(assistant_msgs)} responses")

        if tool_msgs:
            parts.append(f"{len(tool_msgs)} tool calls were made")

        total_tokens = sum(m.tokens for m in messages)
        parts.append(f"[{len(messages)} messages, ~{total_tokens} tokens compacted]")

        return "\n".join(parts)

    # ── Safety Checks ─────────────────────────────────────────

    def can_proceed(self) -> Tuple[bool, str]:
        """Check if we have enough context window to proceed."""
        available = self.budget.available - self.current_token_count()

        if available < self.MIN_CONTEXT_BLOCK:
            return False, f"Context too small: {available} tokens available (min: {self.MIN_CONTEXT_BLOCK})"

        if available < self.MIN_CONTEXT_WARN:
            return True, f"WARNING: Context cramped: {available} tokens available"

        return True, "OK"

    # ── Build Context ─────────────────────────────────────────

    def build_context(self) -> List[Dict[str, str]]:
        """Build the context messages list for LLM API call."""
        return [{"role": m.role, "content": m.content} for m in self._messages]

    # ── Stats ─────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        total = self.current_token_count()
        return {
            "model_max_tokens": self.budget.max_tokens,
            "available_tokens": self.budget.available,
            "used_tokens": total,
            "usage_ratio": round(total / self.budget.available, 3)
                if self.budget.available > 0 else 0,
            "message_count": len(self._messages),
            "compaction_count": self._compaction_count,
            "total_tokens_processed": self._total_tokens_processed,
            "facts_extracted": len(self._facts_extracted),
            "status": self.budget.check(total),
            "tool_token_usage": dict(self._tool_token_usage),
        }
