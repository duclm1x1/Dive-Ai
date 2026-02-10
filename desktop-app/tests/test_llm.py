"""
LLM Tests - Test V98 connections and Claude models
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Add parent to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm.connections import (
    V98Client, V98ConnectionManager, get_manager,
    ALL_MODELS, CLAUDE_OPUS_46_THINKING, CLAUDE_SONNET_45
)
from backend.llm.router import ModelRouter, TaskType, route_prompt
from backend.llm.tokens import TokenTracker, record_usage


class TestV98Client:
    """Test V98 client"""
    
    def test_init_without_key(self):
        """Test client without API key"""
        with patch.dict(os.environ, {}, clear=True):
            client = V98Client()
            assert not client.is_available
    
    def test_init_with_key(self):
        """Test client with API key"""
        with patch.dict(os.environ, {"V98_API_KEY": "test_key"}):
            client = V98Client()
            assert client.is_available
    
    def test_chat_without_key(self):
        """Test chat fails without key"""
        with patch.dict(os.environ, {}, clear=True):
            client = V98Client()
            response = client.chat([{"role": "user", "content": "test"}])
            assert not response.success
            assert "API_KEY" in response.error


class TestModelRouter:
    """Test model routing"""
    
    def test_route_code_generation(self):
        """Test routing code generation task"""
        router = ModelRouter()
        decision = router.route("Write a Python function", task_type=TaskType.CODE_GENERATION)
        assert decision.model.id == "claude_opus_46_thinking"
    
    def test_route_fast_task(self):
        """Test routing fast task"""
        router = ModelRouter()
        decision = router.route("Quick hello", task_type=TaskType.FAST)
        assert decision.model.id == "claude_sonnet_45"
    
    def test_auto_route_thinking(self):
        """Test auto-routing to thinking model"""
        router = ModelRouter()
        decision = router.route("Think carefully about this complex architecture design")
        assert decision.model.supports_thinking
    
    def test_auto_route_simple(self):
        """Test auto-routing simple message"""
        router = ModelRouter()
        decision = router.route("hi")
        assert decision.model.id == "claude_sonnet_45"


class TestTokenTracker:
    """Test token tracking"""
    
    def test_record_usage(self):
        """Test recording token usage"""
        tracker = TokenTracker()
        usage = tracker.record("claude-opus-4-6-thinking", 100, 500)
        
        assert usage.input_tokens == 100
        assert usage.output_tokens == 500
        assert usage.total_tokens == 600
        assert usage.cost_usd > 0
    
    def test_get_stats(self):
        """Test getting stats"""
        tracker = TokenTracker()
        tracker.record("claude-opus-4-6-thinking", 100, 500)
        tracker.record("claude-sonnet-4-5", 50, 200)
        
        stats = tracker.get_usage()
        assert stats["requests"] == 2
        assert stats["total_tokens"] == 850
    
    def test_check_limits(self):
        """Test limit checking"""
        tracker = TokenTracker(hourly_limit=1000)
        tracker.record("test", 500, 500)
        
        limits = tracker.check_limits()
        assert limits["hourly_exceeded"]


class TestModels:
    """Test model configurations"""
    
    def test_all_models_count(self):
        """Test we have 5 models"""
        assert len(ALL_MODELS) == 5
    
    def test_primary_model(self):
        """Test primary model is Opus 4.6 Thinking"""
        assert CLAUDE_OPUS_46_THINKING.priority == 10
        assert CLAUDE_OPUS_46_THINKING.supports_thinking
    
    def test_model_priorities(self):
        """Test models are ordered by priority"""
        priorities = [m.priority for m in ALL_MODELS]
        assert priorities == sorted(priorities, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
