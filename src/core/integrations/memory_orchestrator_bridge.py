#!/usr/bin/env python3
"""
Memory ↔ Orchestrator Integration Bridge
Connects Memory System with Orchestrator for intelligent task planning
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskPlan:
    """Task plan with memory context"""
    task_id: str
    description: str
    steps: List[Dict[str, Any]]
    memory_context: Dict[str, Any]
    priority: int
    estimated_tokens: int


class MemoryOrchestratorBridge:
    """
    Bridges Memory System and Orchestrator
    Uses memory to inform task planning and execution
    """
    
    def __init__(self, memory_system, orchestrator):
        """
        Initialize bridge
        
        Args:
            memory_system: MemorySystem instance
            orchestrator: Orchestrator instance
        """
        self.memory = memory_system
        self.orchestrator = orchestrator
        self.task_plans = {}
        self.execution_history = []
    
    async def plan_task_with_memory(
        self,
        task: str,
        project_id: str
    ) -> TaskPlan:
        """
        Plan task using memory context
        
        Args:
            task: Task description
            project_id: Project identifier
        
        Returns:
            Task plan with memory context
        """
        # Retrieve relevant memory
        memory_context = await self._get_task_memory(project_id, task)
        
        # Use orchestrator to plan task
        plan = await self.orchestrator.plan_task(
            task,
            context=memory_context
        )
        
        # Store plan in memory
        task_plan = TaskPlan(
            task_id=plan.get('id', 'unknown'),
            description=task,
            steps=plan.get('steps', []),
            memory_context=memory_context,
            priority=plan.get('priority', 5),
            estimated_tokens=plan.get('estimated_tokens', 0)
        )
        
        self.task_plans[task_plan.task_id] = task_plan
        
        # Store in memory
        await self.memory.store_episodic(
            project_id,
            description=f"Task planned: {task}",
            metadata={'task_id': task_plan.task_id, 'steps': len(task_plan.steps)}
        )
        
        return task_plan
    
    async def execute_task_with_memory(
        self,
        task_id: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Execute task with memory tracking
        
        Args:
            task_id: Task identifier
            project_id: Project identifier
        
        Returns:
            Execution result
        """
        task_plan = self.task_plans.get(task_id)
        if not task_plan:
            return {'status': 'error', 'message': 'Task not found'}
        
        # Execute with orchestrator
        result = await self.orchestrator.execute_task(
            task_plan.steps,
            context=task_plan.memory_context
        )
        
        # Store execution in memory
        execution_record = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'status': result.get('status'),
            'duration': result.get('duration'),
            'tokens_used': result.get('tokens_used', 0),
            'success': result.get('success', False)
        }
        
        await self.memory.store_episodic(
            project_id,
            description=f"Task executed: {task_plan.description}",
            metadata=execution_record
        )
        
        self.execution_history.append(execution_record)
        
        return result
    
    async def _get_task_memory(
        self,
        project_id: str,
        task: str
    ) -> Dict[str, Any]:
        """Get memory context for task planning"""
        try:
            # Get similar past tasks
            past_tasks = await self.memory.recall_semantic(
                project_id,
                query=task,
                limit=3
            )
            
            # Get relevant procedures
            procedures = await self.memory.recall_procedural(
                project_id,
                query=task,
                limit=5
            )
            
            # Get recent context
            recent = await self.memory.recall_episodic(
                project_id,
                limit=5
            )
            
            return {
                'past_tasks': past_tasks,
                'procedures': procedures,
                'recent_context': recent,
                'project_id': project_id
            }
        except Exception as e:
            print(f"⚠️ Failed to get task memory: {e}")
            return {}
    
    async def learn_from_execution(
        self,
        task_id: str,
        project_id: str,
        feedback: str
    ):
        """Learn from task execution and store in memory"""
        try:
            task_plan = self.task_plans.get(task_id)
            if not task_plan:
                return
            
            # Store as semantic memory (knowledge)
            await self.memory.store_semantic(
                project_id,
                fact=f"Task '{task_plan.description}' - {feedback}",
                metadata={
                    'task_id': task_id,
                    'steps': task_plan.steps,
                    'feedback': feedback
                }
            )
            
            print(f"✅ Learned from task {task_id}")
        except Exception as e:
            print(f"❌ Failed to learn from execution: {e}")
    
    async def get_task_recommendations(
        self,
        project_id: str,
        current_task: str
    ) -> List[Dict[str, Any]]:
        """Get recommended tasks based on memory"""
        try:
            # Get similar completed tasks
            similar_tasks = await self.memory.recall_semantic(
                project_id,
                query=current_task,
                limit=5
            )
            
            return similar_tasks
        except Exception as e:
            print(f"⚠️ Failed to get recommendations: {e}")
            return []
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]
    
    async def optimize_task_plan(
        self,
        task_id: str,
        project_id: str
    ) -> TaskPlan:
        """Optimize task plan based on execution history"""
        try:
            task_plan = self.task_plans.get(task_id)
            if not task_plan:
                return None
            
            # Get execution history for this task type
            history = [
                e for e in self.execution_history
                if e.get('task_id') == task_id
            ]
            
            if not history:
                return task_plan
            
            # Calculate average metrics
            avg_duration = sum(h.get('duration', 0) for h in history) / len(history)
            avg_tokens = sum(h.get('tokens_used', 0) for h in history) / len(history)
            success_rate = sum(1 for h in history if h.get('success')) / len(history)
            
            # Store optimization in memory
            await self.memory.store_semantic(
                project_id,
                fact=f"Task optimization: {task_plan.description} - Success rate: {success_rate:.1%}",
                metadata={
                    'avg_duration': avg_duration,
                    'avg_tokens': avg_tokens,
                    'success_rate': success_rate
                }
            )
            
            return task_plan
        except Exception as e:
            print(f"⚠️ Failed to optimize plan: {e}")
            return None


# Integration helper
async def integrate_memory_orchestrator(
    memory_system,
    orchestrator
) -> MemoryOrchestratorBridge:
    """Create and initialize Memory-Orchestrator bridge"""
    bridge = MemoryOrchestratorBridge(memory_system, orchestrator)
    print("✅ Memory ↔ Orchestrator bridge initialized")
    return bridge


# Example usage
if __name__ == "__main__":
    print("Memory ↔ Orchestrator Integration Bridge")
    print("This module connects Memory and Orchestrator systems")
