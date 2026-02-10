"""
Dive AI V29.4 - Task Router
Routes tasks to appropriate LLM connection based on task type
Uses Claude 4.6 Opus via V98 (primary) and AICoding (backup)
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

from .connection_manager import (
    LLMConnectionManager, 
    LLMResponse, 
    TaskType,
    create_manager
)


@dataclass
class Task:
    """A task to be processed by LLM"""
    id: str
    type: TaskType
    prompt: str
    context: Optional[str] = None
    priority: int = 5  # 1-10, higher = more important
    max_tokens: int = 8192
    temperature: float = 0.7
    prefer_provider: str = "v98"


@dataclass
class TaskResult:
    """Result of a processed task"""
    task_id: str
    success: bool
    response: Optional[LLMResponse] = None
    error: Optional[str] = None


class TaskRouter:
    """
    Routes tasks to V98 or AICoding based on:
    - Task type
    - Priority
    - Connection health
    - Load balancing
    """
    
    def __init__(self, v98_key: str = None, aicoding_key: str = None):
        self.manager = LLMConnectionManager(v98_key, aicoding_key)
        
        # Task queues by priority
        self.high_priority_queue: List[Task] = []
        self.normal_queue: List[Task] = []
        
        # Processing stats
        self.processed = 0
        self.failed = 0
    
    def _build_messages(self, task: Task) -> List[Dict]:
        """Build messages for LLM"""
        messages = []
        
        # Add system prompt based on task type
        system_prompts = {
            TaskType.CHAT: "You are Dive AI, a helpful AI assistant.",
            TaskType.CODE: "You are an expert programmer. Write clean, efficient code.",
            TaskType.REASONING: "You are a logical reasoning expert. Think step by step.",
            TaskType.VISION: "You are a vision expert. Analyze images carefully.",
            TaskType.AUTOMATION: "You are a desktop automation expert. Provide precise actions."
        }
        
        messages.append({
            "role": "system",
            "content": system_prompts.get(task.type, system_prompts[TaskType.CHAT])
        })
        
        # Add context if provided
        if task.context:
            messages.append({
                "role": "user",
                "content": f"Context:\n{task.context}"
            })
            messages.append({
                "role": "assistant",
                "content": "I understand the context. Please continue."
            })
        
        # Add main prompt
        messages.append({
            "role": "user",
            "content": task.prompt
        })
        
        return messages
    
    def _select_provider(self, task: Task) -> str:
        """Select best provider for task"""
        # If user specified preference, use it
        if task.prefer_provider:
            return task.prefer_provider
        
        # For high priority, use V98 (usually more reliable)
        if task.priority >= 8:
            return "v98"
        
        # Load balance based on stats
        stats = self.manager.get_stats()
        v98_load = stats["v98_requests"]
        aicoding_load = stats["aicoding_requests"]
        
        # Prefer less loaded provider
        if v98_load < aicoding_load and self.manager.v98.is_healthy:
            return "v98"
        elif self.manager.aicoding.is_healthy:
            return "aicoding"
        
        return "v98"  # Default
    
    async def process(self, task: Task) -> TaskResult:
        """Process a single task"""
        try:
            messages = self._build_messages(task)
            provider = self._select_provider(task)
            
            response = await self.manager.chat(
                messages,
                prefer=provider,
                max_tokens=task.max_tokens,
                temperature=task.temperature
            )
            
            self.processed += 1
            return TaskResult(
                task_id=task.id,
                success=True,
                response=response
            )
            
        except Exception as e:
            self.failed += 1
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
    
    async def process_batch(self, tasks: List[Task], 
                           concurrency: int = 3) -> List[TaskResult]:
        """Process multiple tasks concurrently"""
        # Sort by priority (highest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        results = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await self.process(task)
        
        tasks_coros = [process_with_semaphore(t) for t in sorted_tasks]
        results = await asyncio.gather(*tasks_coros)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get router statistics"""
        return {
            "processed": self.processed,
            "failed": self.failed,
            "success_rate": self.processed / max(1, self.processed + self.failed),
            **self.manager.get_stats()
        }


# ============================================================
# Convenience Functions
# ============================================================

async def route_chat(prompt: str, context: str = None) -> str:
    """Quick chat routing"""
    router = TaskRouter()
    task = Task(
        id="quick_chat",
        type=TaskType.CHAT,
        prompt=prompt,
        context=context
    )
    result = await router.process(task)
    return result.response.content if result.success else f"Error: {result.error}"


async def route_code(prompt: str, context: str = None) -> str:
    """Quick code routing"""
    router = TaskRouter()
    task = Task(
        id="quick_code",
        type=TaskType.CODE,
        prompt=prompt,
        context=context,
        temperature=0.3  # Lower for code
    )
    result = await router.process(task)
    return result.response.content if result.success else f"Error: {result.error}"


async def route_reasoning(prompt: str, context: str = None) -> str:
    """Quick reasoning routing"""
    router = TaskRouter()
    task = Task(
        id="quick_reasoning",
        type=TaskType.REASONING,
        prompt=prompt,
        context=context,
        max_tokens=16000,  # More for reasoning
        temperature=0.5
    )
    result = await router.process(task)
    return result.response.content if result.success else f"Error: {result.error}"


# ============================================================
# Test
# ============================================================

async def test_router():
    """Test the task router"""
    router = TaskRouter()
    
    print("🔀 Testing Task Router...")
    
    # Create test tasks
    tasks = [
        Task(id="1", type=TaskType.CHAT, prompt="Hello!", priority=5),
        Task(id="2", type=TaskType.CODE, prompt="Write a hello world in Python", priority=8),
        Task(id="3", type=TaskType.REASONING, prompt="What is 2+2? Explain.", priority=3),
    ]
    
    # Process batch
    results = await router.process_batch(tasks)
    
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"   {status} Task {result.task_id}: {result.response.content[:50] if result.success else result.error}...")
    
    print(f"\n📊 Stats: {router.get_stats()}")


if __name__ == "__main__":
    asyncio.run(test_router())
