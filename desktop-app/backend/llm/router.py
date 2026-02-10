"""
Model Router - Routes tasks to optimal Claude model

Based on task complexity and requirements:
- Complex reasoning → Opus Thinking
- Fast tasks → Sonnet
- High quality → Opus
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .connections import (
    V98Model, ALL_MODELS,
    CLAUDE_OPUS_46_THINKING,
    CLAUDE_SONNET_45,
    CLAUDE_SONNET_45_THINKING,
    CLAUDE_OPUS_45,
    CLAUDE_OPUS_45_THINKING
)


class TaskType(Enum):
    """Task type classification"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ANALYSIS = "analysis"
    CHAT = "chat"
    REASONING = "reasoning"
    FAST = "fast"
    CREATIVE = "creative"


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    model: V98Model
    reason: str
    confidence: float  # 0-1


class ModelRouter:
    """
    Routes tasks to optimal Claude model
    
    Decision matrix:
    - Code generation → Opus 4.6 Thinking
    - Code review → Sonnet 4.5
    - Complex analysis → Opus Thinking (4.6 or 4.5)
    - Fast/simple → Sonnet 4.5
    - Creative → Opus 4.5
    """
    
    # Keywords that suggest need for thinking models
    THINKING_KEYWORDS = [
        "think", "reason", "analyze", "complex", "debug",
        "architecture", "design", "optimize", "refactor",
        "explain why", "step by step", "carefully"
    ]
    
    # Keywords that suggest fast response needed
    FAST_KEYWORDS = [
        "quick", "simple", "short", "brief", "summarize",
        "ping", "test", "hello", "hi"
    ]
    
    # Keywords for code generation
    CODE_KEYWORDS = [
        "generate", "create", "write", "implement", "code",
        "function", "class", "module", "api", "endpoint"
    ]
    
    # Keywords for review
    REVIEW_KEYWORDS = [
        "review", "check", "fix", "bug", "error",
        "improve", "feedback", "comment"
    ]
    
    def __init__(self):
        self.decision_history: List[RoutingDecision] = []
    
    def route(self, 
              prompt: str,
              task_type: TaskType = None,
              prefer_thinking: bool = None,
              prefer_fast: bool = None) -> RoutingDecision:
        """
        Route prompt to optimal model
        
        Args:
            prompt: User prompt
            task_type: Override auto-detection
            prefer_thinking: Force thinking model
            prefer_fast: Force fast model
        """
        
        # Manual overrides
        if prefer_thinking:
            return self._decide(CLAUDE_OPUS_46_THINKING, "User prefers thinking", 1.0)
        
        if prefer_fast:
            return self._decide(CLAUDE_SONNET_45, "User prefers fast", 1.0)
        
        if task_type:
            return self._route_by_type(task_type)
        
        # Auto-detect from prompt
        return self._auto_route(prompt)
    
    def _decide(self, model: V98Model, reason: str, confidence: float) -> RoutingDecision:
        """Create and record decision"""
        decision = RoutingDecision(model=model, reason=reason, confidence=confidence)
        self.decision_history.append(decision)
        return decision
    
    def _route_by_type(self, task_type: TaskType) -> RoutingDecision:
        """Route by explicit task type"""
        
        routing_map = {
            TaskType.CODE_GENERATION: (CLAUDE_OPUS_46_THINKING, "Code gen needs reasoning"),
            TaskType.CODE_REVIEW: (CLAUDE_SONNET_45, "Reviews are fast"),
            TaskType.ANALYSIS: (CLAUDE_OPUS_46_THINKING, "Analysis needs thinking"),
            TaskType.CHAT: (CLAUDE_SONNET_45, "Chat should be fast"),
            TaskType.REASONING: (CLAUDE_OPUS_46_THINKING, "Explicit reasoning"),
            TaskType.FAST: (CLAUDE_SONNET_45, "Fast response needed"),
            TaskType.CREATIVE: (CLAUDE_OPUS_45, "Creative needs quality"),
        }
        
        model, reason = routing_map.get(task_type, (CLAUDE_SONNET_45, "Default"))
        return self._decide(model, reason, 0.9)
    
    def _auto_route(self, prompt: str) -> RoutingDecision:
        """Auto-detect task type from prompt"""
        
        prompt_lower = prompt.lower()
        
        # Check for thinking keywords
        thinking_score = sum(1 for kw in self.THINKING_KEYWORDS if kw in prompt_lower)
        
        # Check for fast keywords
        fast_score = sum(1 for kw in self.FAST_KEYWORDS if kw in prompt_lower)
        
        # Check for code keywords
        code_score = sum(1 for kw in self.CODE_KEYWORDS if kw in prompt_lower)
        
        # Check for review keywords
        review_score = sum(1 for kw in self.REVIEW_KEYWORDS if kw in prompt_lower)
        
        # Check prompt length
        is_long = len(prompt) > 1000
        is_short = len(prompt) < 100
        
        # Decision logic
        if thinking_score > 2 or (code_score > 1 and is_long):
            return self._decide(
                CLAUDE_OPUS_46_THINKING,
                f"High thinking score ({thinking_score})",
                0.8
            )
        
        if fast_score > 0 or is_short:
            return self._decide(
                CLAUDE_SONNET_45,
                f"Fast/simple request",
                0.85
            )
        
        if review_score > 0:
            return self._decide(
                CLAUDE_SONNET_45,
                "Review task detected",
                0.75
            )
        
        if code_score > 0:
            return self._decide(
                CLAUDE_OPUS_46_THINKING,
                "Code generation detected",
                0.7
            )
        
        # Default to balanced model
        return self._decide(
            CLAUDE_SONNET_45,
            "Default balanced choice",
            0.6
        )
    
    def get_stats(self) -> Dict:
        """Get routing statistics"""
        if not self.decision_history:
            return {"total": 0}
        
        model_counts = {}
        for d in self.decision_history:
            model_counts[d.model.name] = model_counts.get(d.model.name, 0) + 1
        
        return {
            "total": len(self.decision_history),
            "by_model": model_counts,
            "avg_confidence": sum(d.confidence for d in self.decision_history) / len(self.decision_history)
        }


# Singleton router
_router = None

def get_router() -> ModelRouter:
    """Get singleton router"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def route_prompt(prompt: str, **kwargs) -> V98Model:
    """Quick route helper"""
    router = get_router()
    decision = router.route(prompt, **kwargs)
    return decision.model
