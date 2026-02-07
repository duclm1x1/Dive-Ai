"""
Dive Engine V2 - Streaming Thinking Engine
===========================================

This module implements streaming thinking blocks with interleaved tool support,
based on Claude Opus 4.5's Extended Thinking mechanism.

Key Features:
- Real-time streaming of thinking blocks
- Interleaved tool calls during reasoning
- Thinking block preservation across turns
- Progressive refinement with tool feedback

Based on:
- Claude Opus 4.5 Extended Thinking
- Interleaved thinking with tool use
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple

from dive_engine.core.models import (
    CognitivePhase,
    ThinkingBlock,
    ThinkingPhase,
    ThinkingStrategy,
    utcnow_iso,
)


# =============================================================================
# STREAMING EVENTS
# =============================================================================

class StreamEventType(Enum):
    """Types of streaming events."""
    THINKING_START = "thinking_start"
    THINKING_CHUNK = "thinking_chunk"
    THINKING_END = "thinking_end"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    PHASE_START = "phase_start"
    PHASE_END = "phase_end"
    ERROR = "error"


@dataclass
class StreamEvent:
    """A streaming event."""
    type: StreamEventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=utcnow_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# =============================================================================
# TOOL CALL
# =============================================================================

@dataclass
class ToolCall:
    """A tool call request."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: f"call_{id(object())}")
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "call_id": self.call_id,
            "result": self.result,
            "error": self.error,
        }


# =============================================================================
# STREAMING THINKING ENGINE
# =============================================================================

class StreamingThinkingEngine:
    """
    Streaming thinking engine with interleaved tool support.
    
    This engine:
    - Streams thinking blocks in real-time
    - Detects tool call requests in thinking
    - Executes tools and feeds results back
    - Continues reasoning with tool results
    - Preserves thinking blocks across turns
    """
    
    def __init__(
        self,
        llm_client: Any,
        tool_executor: Optional[Callable[[ToolCall], Any]] = None,
        max_tool_iterations: int = 5,
    ):
        """
        Initialize streaming thinking engine.
        
        Args:
            llm_client: LLM client with streaming support
            tool_executor: Function to execute tool calls
            max_tool_iterations: Max tool call iterations
        """
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_tool_iterations = max_tool_iterations
        
        # Thinking state
        self.thinking_blocks: List[ThinkingBlock] = []
        self.current_phase: Optional[CognitivePhase] = None
        self.tool_call_count = 0
    
    async def stream_thinking(
        self,
        prompt: str,
        system: str,
        phase: CognitivePhase,
        strategy: ThinkingStrategy,
        budget_tokens: int = 10000,
    ) -> AsyncIterator[StreamEvent]:
        """
        Stream thinking for a cognitive phase.
        
        Args:
            prompt: User prompt
            system: System prompt
            phase: Current cognitive phase
            strategy: Thinking strategy
            budget_tokens: Token budget for thinking
            
        Yields:
            StreamEvent objects
        """
        self.current_phase = phase
        
        # Emit phase start
        yield StreamEvent(
            type=StreamEventType.PHASE_START,
            data={"phase": phase.value, "strategy": strategy.value}
        )
        
        # Check if interleaved thinking is enabled
        interleaved = strategy in {
            ThinkingStrategy.INTERLEAVED,
            ThinkingStrategy.EXTENDED_THINKING,
        }
        
        if interleaved:
            # Interleaved thinking with tool calls
            async for event in self._stream_interleaved(
                prompt, system, phase, budget_tokens
            ):
                yield event
        else:
            # Standard thinking without tools
            async for event in self._stream_standard(
                prompt, system, phase, budget_tokens
            ):
                yield event
        
        # Emit phase end
        yield StreamEvent(
            type=StreamEventType.PHASE_END,
            data={"phase": phase.value, "blocks_generated": len(self.thinking_blocks)}
        )
    
    async def _stream_standard(
        self,
        prompt: str,
        system: str,
        phase: CognitivePhase,
        budget_tokens: int,
    ) -> AsyncIterator[StreamEvent]:
        """Stream standard thinking without tools."""
        # Emit thinking start
        yield StreamEvent(
            type=StreamEventType.THINKING_START,
            data={"phase": phase.value}
        )
        
        # Stream from LLM
        thinking_content = ""
        
        try:
            async for chunk in self.llm_client.stream(
                prompt=prompt,
                system=system,
                max_tokens=budget_tokens,
            ):
                thinking_content += chunk
                
                # Emit chunk
                yield StreamEvent(
                    type=StreamEventType.THINKING_CHUNK,
                    data={"chunk": chunk, "phase": phase.value}
                )
        
        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": str(e), "phase": phase.value}
            )
            return
        
        # Create thinking block
        block = ThinkingBlock(
            block_id=f"{phase.value}-{len(self.thinking_blocks)}",
            phase=phase,
            content=thinking_content,
            signature=f"sig_{hash(thinking_content) % 10000}",
        )
        self.thinking_blocks.append(block)
        
        # Emit thinking end
        yield StreamEvent(
            type=StreamEventType.THINKING_END,
            data={
                "phase": phase.value,
                "block_id": block.block_id,
                "content_length": len(thinking_content),
            }
        )
    
    async def _stream_interleaved(
        self,
        prompt: str,
        system: str,
        phase: CognitivePhase,
        budget_tokens: int,
    ) -> AsyncIterator[StreamEvent]:
        """Stream interleaved thinking with tool calls."""
        iteration = 0
        conversation_history = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        
        while iteration < self.max_tool_iterations:
            iteration += 1
            
            # Emit thinking start
            yield StreamEvent(
                type=StreamEventType.THINKING_START,
                data={"phase": phase.value, "iteration": iteration}
            )
            
            # Stream from LLM
            thinking_content = ""
            
            try:
                async for chunk in self.llm_client.stream(
                    prompt=conversation_history[-1]["content"],
                    system=system,
                    max_tokens=budget_tokens // self.max_tool_iterations,
                ):
                    thinking_content += chunk
                    
                    # Emit chunk
                    yield StreamEvent(
                        type=StreamEventType.THINKING_CHUNK,
                        data={"chunk": chunk, "phase": phase.value, "iteration": iteration}
                    )
            
            except Exception as e:
                yield StreamEvent(
                    type=StreamEventType.ERROR,
                    data={"error": str(e), "phase": phase.value}
                )
                break
            
            # Create thinking block
            block = ThinkingBlock(
                block_id=f"{phase.value}-{len(self.thinking_blocks)}-iter{iteration}",
                phase=phase,
                content=thinking_content,
                signature=f"sig_{hash(thinking_content) % 10000}",
            )
            self.thinking_blocks.append(block)
            
            # Emit thinking end
            yield StreamEvent(
                type=StreamEventType.THINKING_END,
                data={
                    "phase": phase.value,
                    "block_id": block.block_id,
                    "iteration": iteration,
                }
            )
            
            # Check for tool calls
            tool_calls = self._extract_tool_calls(thinking_content)
            
            if not tool_calls:
                # No more tool calls, done
                break
            
            # Execute tool calls
            for tool_call in tool_calls:
                # Emit tool call start
                yield StreamEvent(
                    type=StreamEventType.TOOL_CALL_START,
                    data={
                        "tool_name": tool_call.tool_name,
                        "call_id": tool_call.call_id,
                        "arguments": tool_call.arguments,
                    }
                )
                
                # Execute tool
                if self.tool_executor:
                    try:
                        tool_call.result = await self._execute_tool_async(tool_call)
                    except Exception as e:
                        tool_call.error = str(e)
                else:
                    tool_call.result = f"Mock result for {tool_call.tool_name}"
                
                self.tool_call_count += 1
                
                # Emit tool call end
                yield StreamEvent(
                    type=StreamEventType.TOOL_CALL_END,
                    data={
                        "tool_name": tool_call.tool_name,
                        "call_id": tool_call.call_id,
                        "result": str(tool_call.result)[:500],
                        "error": tool_call.error,
                    }
                )
            
            # Add tool results to conversation
            tool_results_text = self._format_tool_results(tool_calls)
            conversation_history.append({
                "role": "assistant",
                "content": thinking_content,
            })
            conversation_history.append({
                "role": "user",
                "content": f"Tool results:\n{tool_results_text}\n\nContinue reasoning with these results.",
            })
    
    def _extract_tool_calls(self, thinking_content: str) -> List[ToolCall]:
        """
        Extract tool call requests from thinking content.
        
        Looks for patterns like:
        - <tool>tool_name(arg1="value1", arg2="value2")</tool>
        - [TOOL: tool_name, args: {...}]
        """
        tool_calls = []
        
        # Pattern 1: <tool>name(args)</tool>
        pattern1 = r'<tool>(\w+)\((.*?)\)</tool>'
        for match in re.finditer(pattern1, thinking_content):
            tool_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments
            arguments = self._parse_tool_args(args_str)
            
            tool_calls.append(ToolCall(
                tool_name=tool_name,
                arguments=arguments,
            ))
        
        # Pattern 2: [TOOL: name, args: {...}]
        pattern2 = r'\[TOOL:\s*(\w+),\s*args:\s*(\{.*?\})\]'
        for match in re.finditer(pattern2, thinking_content):
            tool_name = match.group(1)
            args_json = match.group(2)
            
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError:
                arguments = {}
            
            tool_calls.append(ToolCall(
                tool_name=tool_name,
                arguments=arguments,
            ))
        
        return tool_calls
    
    def _parse_tool_args(self, args_str: str) -> Dict[str, Any]:
        """Parse tool arguments from string."""
        arguments = {}
        
        # Simple key="value" parsing
        pattern = r'(\w+)="([^"]*)"'
        for match in re.finditer(pattern, args_str):
            key = match.group(1)
            value = match.group(2)
            arguments[key] = value
        
        return arguments
    
    async def _execute_tool_async(self, tool_call: ToolCall) -> Any:
        """Execute tool call asynchronously."""
        if asyncio.iscoroutinefunction(self.tool_executor):
            return await self.tool_executor(tool_call)
        else:
            return self.tool_executor(tool_call)
    
    def _format_tool_results(self, tool_calls: List[ToolCall]) -> str:
        """Format tool results for feedback."""
        lines = []
        for call in tool_calls:
            if call.error:
                lines.append(f"- {call.tool_name}: ERROR - {call.error}")
            else:
                result_str = str(call.result)[:200]
                lines.append(f"- {call.tool_name}: {result_str}")
        return "\n".join(lines)
    
    def get_thinking_blocks(self) -> List[ThinkingBlock]:
        """Get all thinking blocks generated."""
        return self.thinking_blocks
    
    def get_phase_summary(self) -> ThinkingPhase:
        """Get summary of current phase."""
        if not self.current_phase:
            raise ValueError("No active phase")
        
        phase_state = ThinkingPhase(
            phase=self.current_phase,
            run_id="streaming",
        )
        phase_state.blocks = self.thinking_blocks
        phase_state.tool_calls = [
            {"name": "tool_call", "count": self.tool_call_count}
        ]
        phase_state.status = "completed"
        
        return phase_state


# =============================================================================
# THINKING BLOCK PRESERVER
# =============================================================================

class ThinkingBlockPreserver:
    """
    Preserves thinking blocks across conversation turns.
    
    Based on Claude's thinking block preservation feature.
    """
    
    def __init__(self, max_blocks: int = 10):
        """
        Initialize preserver.
        
        Args:
            max_blocks: Max blocks to preserve
        """
        self.max_blocks = max_blocks
        self.preserved_blocks: List[ThinkingBlock] = []
    
    def preserve(self, blocks: List[ThinkingBlock]):
        """Preserve thinking blocks."""
        self.preserved_blocks.extend(blocks)
        
        # Keep only recent blocks
        if len(self.preserved_blocks) > self.max_blocks:
            self.preserved_blocks = self.preserved_blocks[-self.max_blocks:]
    
    def get_context(self) -> str:
        """Get preserved context as text."""
        if not self.preserved_blocks:
            return ""
        
        lines = ["Previous thinking context:"]
        for block in self.preserved_blocks:
            lines.append(f"\n[{block.phase.value}]")
            lines.append(block.content[:500])
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear preserved blocks."""
        self.preserved_blocks = []


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_streaming_engine(
    llm_client: Any,
    tool_executor: Optional[Callable] = None,
) -> StreamingThinkingEngine:
    """
    Create streaming thinking engine.
    
    Args:
        llm_client: LLM client with streaming support
        tool_executor: Optional tool executor
        
    Returns:
        StreamingThinkingEngine
    """
    return StreamingThinkingEngine(
        llm_client=llm_client,
        tool_executor=tool_executor,
    )
