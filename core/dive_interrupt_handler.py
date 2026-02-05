#!/usr/bin/env python3
"""
Dive Interrupt Handler - Adaptive Execution System

Inspired by Manus AI's ability to:
- Quick read user input during execution
- Analyze intent immediately
- Merge into current task or queue
- Resume with updated context

Architecture:
1. Interrupt Detection - Monitor for user input during execution
2. Quick Analyzer - Fast intent analysis (< 100ms)
3. Priority Assessment - Urgent vs Normal vs Low
4. Context Merger - Merge into current plan or queue
5. Resume System - Continue with updated context

Author: Dive AI Team
Version: V21.2 - Adaptive Execution
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class InterruptPriority(Enum):
    """Priority levels for interrupts"""
    URGENT = "urgent"  # Stop immediately, handle now
    HIGH = "high"  # Finish current step, then handle
    NORMAL = "normal"  # Merge into current plan
    LOW = "low"  # Queue for later


class InterruptAction(Enum):
    """Actions to take on interrupt"""
    MERGE = "merge"  # Merge into current task
    PAUSE_AND_HANDLE = "pause_and_handle"  # Pause, handle, resume
    QUEUE = "queue"  # Queue for later
    IGNORE = "ignore"  # Not relevant, ignore


@dataclass
class Interrupt:
    """User interrupt during execution"""
    message: str
    timestamp: datetime
    priority: InterruptPriority
    action: InterruptAction
    intent: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class QuickAnalyzer:
    """
    Quick intent analyzer for interrupts
    
    Must be FAST (< 100ms) to not block execution
    """
    
    def analyze(self, message: str, current_context: Dict[str, Any]) -> Interrupt:
        """
        Quick analysis of interrupt message
        
        Returns:
            Interrupt with priority and action
        """
        message_lower = message.lower()
        
        # Detect priority
        priority = self._detect_priority(message_lower)
        
        # Detect intent
        intent = self._detect_intent(message_lower, current_context)
        
        # Decide action
        action = self._decide_action(priority, intent, current_context)
        
        return Interrupt(
            message=message,
            timestamp=datetime.now(),
            priority=priority,
            action=action,
            intent=intent,
            context=current_context
        )
    
    def _detect_priority(self, message: str) -> InterruptPriority:
        """Detect priority from message"""
        
        # Urgent keywords
        urgent_keywords = ["stop", "wait", "cancel", "abort", "urgent", "immediately"]
        if any(kw in message for kw in urgent_keywords):
            return InterruptPriority.URGENT
        
        # High priority keywords
        high_keywords = ["important", "critical", "must", "need to", "should"]
        if any(kw in message for kw in high_keywords):
            return InterruptPriority.HIGH
        
        # Modification keywords (normal - merge into current)
        modify_keywords = ["instead", "change", "update", "modify", "use", "add"]
        if any(kw in message for kw in modify_keywords):
            return InterruptPriority.NORMAL
        
        # Default to low
        return InterruptPriority.LOW
    
    def _detect_intent(self, message: str, context: Dict[str, Any]) -> str:
        """Detect intent of interrupt"""
        
        if "stop" in message or "cancel" in message:
            return "cancel_current_task"
        elif "wait" in message or "pause" in message:
            return "pause_current_task"
        elif "instead" in message or "change" in message:
            return "modify_current_task"
        elif "add" in message or "also" in message:
            return "extend_current_task"
        elif "?" in message:
            return "ask_question"
        else:
            return "new_request"
    
    def _decide_action(self, priority: InterruptPriority, intent: str, context: Dict[str, Any]) -> InterruptAction:
        """Decide what action to take"""
        
        if priority == InterruptPriority.URGENT:
            return InterruptAction.PAUSE_AND_HANDLE
        
        if intent in ["modify_current_task", "extend_current_task"]:
            return InterruptAction.MERGE
        
        if intent == "cancel_current_task":
            return InterruptAction.PAUSE_AND_HANDLE
        
        if intent == "ask_question":
            return InterruptAction.PAUSE_AND_HANDLE
        
        if priority == InterruptPriority.NORMAL:
            return InterruptAction.MERGE
        
        return InterruptAction.QUEUE


class ContextMerger:
    """
    Merges interrupt into current execution context
    """
    
    def merge(self, interrupt: Interrupt, current_plan: Any) -> Any:
        """
        Merge interrupt into current plan
        
        Args:
            interrupt: The interrupt to merge
            current_plan: Current execution plan
            
        Returns:
            Updated plan with interrupt merged
        """
        
        if interrupt.action == InterruptAction.MERGE:
            return self._merge_into_plan(interrupt, current_plan)
        elif interrupt.action == InterruptAction.PAUSE_AND_HANDLE:
            return self._pause_and_handle(interrupt, current_plan)
        elif interrupt.action == InterruptAction.QUEUE:
            return self._queue_for_later(interrupt, current_plan)
        else:
            return current_plan
    
    def _merge_into_plan(self, interrupt: Interrupt, plan: Any) -> Any:
        """Merge interrupt into current plan"""
        
        if interrupt.intent == "modify_current_task":
            # Modify current step
            if hasattr(plan, 'steps') and plan.steps:
                current_step = next((s for s in plan.steps if s.status == "in_progress"), None)
                if current_step:
                    # Update step description with modification
                    current_step.description += f" (Modified: {interrupt.message})"
        
        elif interrupt.intent == "extend_current_task":
            # Add new step
            if hasattr(plan, 'steps'):
                new_step_id = len(plan.steps) + 1
                from dive_smart_orchestrator import Step
                new_step = Step(
                    id=new_step_id,
                    description=interrupt.message,
                    status="pending"
                )
                plan.steps.append(new_step)
        
        return plan
    
    def _pause_and_handle(self, interrupt: Interrupt, plan: Any) -> Any:
        """Pause current plan and handle interrupt"""
        
        if hasattr(plan, 'status'):
            plan.status = "paused"
        
        # Mark current step as paused
        if hasattr(plan, 'steps'):
            for step in plan.steps:
                if step.status == "in_progress":
                    step.status = "paused"
        
        return plan
    
    def _queue_for_later(self, interrupt: Interrupt, plan: Any) -> Any:
        """Queue interrupt for later"""
        
        # Add to plan's queue
        if not hasattr(plan, 'queued_interrupts'):
            plan.queued_interrupts = []
        
        plan.queued_interrupts.append(interrupt)
        
        return plan


class InterruptHandler:
    """
    Main interrupt handler
    
    Monitors for user input during execution and handles adaptively
    """
    
    def __init__(self):
        self.quick_analyzer = QuickAnalyzer()
        self.context_merger = ContextMerger()
        self.interrupt_queue: List[Interrupt] = []
        self.current_plan: Optional[Any] = None
        self.is_executing = False
        self.interrupt_callback: Optional[Callable] = None
    
    def set_current_plan(self, plan: Any):
        """Set current execution plan"""
        self.current_plan = plan
    
    def set_interrupt_callback(self, callback: Callable):
        """Set callback for when interrupt is detected"""
        self.interrupt_callback = callback
    
    def start_execution(self):
        """Mark execution as started"""
        self.is_executing = True
    
    def stop_execution(self):
        """Mark execution as stopped"""
        self.is_executing = False
    
    def handle_user_input(self, message: str) -> Interrupt:
        """
        Handle user input during execution
        
        Flow:
        1. Quick analyze (< 100ms)
        2. Determine priority and action
        3. Merge into plan or pause
        4. Return interrupt for logging
        
        Args:
            message: User message
            
        Returns:
            Interrupt object
        """
        
        print(f"\n⚡ INTERRUPT DETECTED: {message[:50]}...")
        
        # Quick analysis
        context = self._get_current_context()
        interrupt = self.quick_analyzer.analyze(message, context)
        
        print(f"   Priority: {interrupt.priority.value}")
        print(f"   Intent: {interrupt.intent}")
        print(f"   Action: {interrupt.action.value}")
        
        # Handle based on action
        if interrupt.action == InterruptAction.MERGE:
            print("   🔀 Merging into current plan...")
            self.current_plan = self.context_merger.merge(interrupt, self.current_plan)
            print("   ✅ Merged successfully!")
        
        elif interrupt.action == InterruptAction.PAUSE_AND_HANDLE:
            print("   ⏸️ Pausing execution...")
            self.current_plan = self.context_merger.merge(interrupt, self.current_plan)
            self.is_executing = False
            print("   ⏸️ Paused. Handling interrupt...")
            
            # Notify callback
            if self.interrupt_callback:
                self.interrupt_callback(interrupt)
        
        elif interrupt.action == InterruptAction.QUEUE:
            print("   📋 Queuing for later...")
            self.interrupt_queue.append(interrupt)
        
        else:
            print("   ❌ Ignoring (not relevant)")
        
        return interrupt
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current execution context"""
        context = {
            "is_executing": self.is_executing,
            "has_plan": self.current_plan is not None
        }
        
        if self.current_plan:
            if hasattr(self.current_plan, 'steps'):
                context["total_steps"] = len(self.current_plan.steps)
                context["completed_steps"] = sum(1 for s in self.current_plan.steps if s.status == "done")
                context["current_step"] = next((s for s in self.current_plan.steps if s.status == "in_progress"), None)
        
        return context
    
    def resume_execution(self):
        """Resume paused execution"""
        if self.current_plan and hasattr(self.current_plan, 'status'):
            self.current_plan.status = "in_progress"
        
        # Resume paused steps
        if self.current_plan and hasattr(self.current_plan, 'steps'):
            for step in self.current_plan.steps:
                if step.status == "paused":
                    step.status = "in_progress"
        
        self.is_executing = True
        print("   ▶️ Resuming execution...")
    
    def get_queued_interrupts(self) -> List[Interrupt]:
        """Get queued interrupts"""
        return self.interrupt_queue.copy()
    
    def clear_queue(self):
        """Clear interrupt queue"""
        self.interrupt_queue.clear()


# Test function
def test_interrupt_handler():
    """Test interrupt handler"""
    print("🧪 Testing Interrupt Handler\n")
    
    handler = InterruptHandler()
    
    # Create mock plan
    from dive_smart_orchestrator import Plan, Step
    plan = Plan(
        steps=[
            Step(id=1, description="Install Dive AI", status="done"),
            Step(id=2, description="Configure LLM", status="in_progress"),
            Step(id=3, description="Test setup", status="pending")
        ],
        parallel_groups=[]
    )
    
    handler.set_current_plan(plan)
    handler.start_execution()
    
    # Test 1: Normal modification (merge)
    print("="*60)
    print("TEST 1: Modification (should merge)")
    print("="*60)
    interrupt1 = handler.handle_user_input("Use Python 3.11 instead")
    assert interrupt1.action == InterruptAction.MERGE
    print("✅ Test 1 passed!\n")
    
    # Test 2: Urgent stop (pause and handle)
    print("="*60)
    print("TEST 2: Urgent stop (should pause)")
    print("="*60)
    interrupt2 = handler.handle_user_input("Wait, stop! I need to change something")
    assert interrupt2.action == InterruptAction.PAUSE_AND_HANDLE
    assert not handler.is_executing
    print("✅ Test 2 passed!\n")
    
    # Test 3: Resume
    print("="*60)
    print("TEST 3: Resume execution")
    print("="*60)
    handler.resume_execution()
    assert handler.is_executing
    print("✅ Test 3 passed!\n")
    
    # Test 4: Extension (merge)
    print("="*60)
    print("TEST 4: Extension (should merge)")
    print("="*60)
    interrupt4 = handler.handle_user_input("Also add stress testing")
    assert interrupt4.action == InterruptAction.MERGE
    print("✅ Test 4 passed!\n")
    
    print("✅ All interrupt handler tests passed!")


if __name__ == "__main__":
    test_interrupt_handler()
