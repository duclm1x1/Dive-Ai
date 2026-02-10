"""
Dive AI V20 + Dive-Memory v3 Integration
Automatic context injection and learning from execution
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add skills path
skills_path = Path(__file__).parent.parent / "skills" / "dive-memory-v3" / "scripts"
sys.path.insert(0, str(skills_path))

from dive_memory import DiveMemory


class DiveAIMemoryIntegration:
    """Integration between Dive AI and Dive-Memory v3"""
    
    def __init__(self, memory_db_path: Optional[str] = None):
        """Initialize integration"""
        self.memory = DiveMemory(memory_db_path)
        self.memory.enable_context_injection()
    
    def inject_context(self, task: str, max_memories: int = 5) -> str:
        """Inject relevant context for a task"""
        context = self.memory.get_context_for_task(task, max_memories=max_memories)
        return context
    
    def store_execution_result(self, task: str, result: Dict[str, Any],
                               section: str = "executions",
                               importance: int = 7):
        """Store task execution results"""
        content = f"Task: {task}\n"
        content += f"Status: {result.get('status', 'unknown')}\n"
        
        if result.get('summary'):
            content += f"Summary: {result['summary']}\n"
        
        if result.get('solution'):
            content += f"Solution: {result['solution']}\n"
        
        metadata = {
            "cost": result.get('cost', 0),
            "duration": result.get('duration', 0),
            "model": result.get('model'),
            "agent_id": result.get('agent_id'),
            "success": result.get('status') == 'success'
        }
        
        tags = ["execution"]
        if result.get('status') == 'success':
            tags.append("success")
        else:
            tags.append("failed")
        
        # Add task type tags
        if "auth" in task.lower():
            tags.append("authentication")
        if "api" in task.lower():
            tags.append("api")
        if "database" in task.lower() or "db" in task.lower():
            tags.append("database")
        
        memory_id = self.memory.add(
            content=content,
            section=section,
            tags=tags,
            importance=importance,
            metadata=metadata
        )
        
        return memory_id
    
    def store_solution(self, problem: str, solution: str,
                      section: str = "solutions",
                      tags: Optional[List[str]] = None,
                      importance: int = 8):
        """Store successful solution"""
        content = f"Problem: {problem}\n\nSolution: {solution}"
        
        memory_id = self.memory.add(
            content=content,
            section=section,
            tags=tags or [],
            importance=importance
        )
        
        return memory_id
    
    def store_decision(self, decision: str, rationale: str,
                      section: str = "decisions",
                      tags: Optional[List[str]] = None,
                      importance: int = 8):
        """Store architectural decision"""
        content = f"Decision: {decision}\n\nRationale: {rationale}"
        
        memory_id = self.memory.add(
            content=content,
            section=section,
            tags=tags or ["architecture"],
            importance=importance,
            metadata={"rationale": rationale}
        )
        
        return memory_id
    
    def store_agent_capability(self, agent_id: str, capability: str,
                               performance_score: float,
                               section: str = "capabilities"):
        """Store agent capability performance"""
        content = f"Agent {agent_id} excels at: {capability}\n"
        content += f"Performance score: {performance_score:.2f}"
        
        memory_id = self.memory.add(
            content=content,
            section=section,
            tags=[f"agent-{agent_id}", capability],
            importance=int(performance_score * 10),
            metadata={
                "agent_id": agent_id,
                "capability": capability,
                "performance_score": performance_score
            }
        )
        
        return memory_id
    
    def find_best_agent_for_task(self, task: str) -> Optional[str]:
        """Find best agent for a task based on past performance"""
        results = self.memory.search(
            query=task,
            section="capabilities",
            top_k=5
        )
        
        if not results:
            return None
        
        # Return agent with highest performance
        best_agent = None
        best_score = 0.0
        
        for result in results:
            agent_id = result.metadata.get("agent_id")
            performance = result.metadata.get("performance_score", 0)
            
            if performance > best_score:
                best_score = performance
                best_agent = agent_id
        
        return best_agent
    
    def get_similar_past_tasks(self, task: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find similar past tasks"""
        results = self.memory.search(
            query=task,
            section="executions",
            top_k=top_k
        )
        
        return [
            {
                "content": r.content,
                "score": r.score,
                "success": r.metadata.get("success", False),
                "cost": r.metadata.get("cost", 0),
                "duration": r.metadata.get("duration", 0)
            }
            for r in results
        ]
    
    def learn_from_feedback(self, task: str, feedback: str,
                           rating: int, section: str = "feedback"):
        """Store user feedback for learning"""
        content = f"Task: {task}\n\nFeedback: {feedback}\n\nRating: {rating}/10"
        
        memory_id = self.memory.add(
            content=content,
            section=section,
            tags=["feedback", "learning"],
            importance=rating,
            metadata={
                "task": task,
                "feedback": feedback,
                "rating": rating
            }
        )
        
        return memory_id
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return self.memory.get_stats()
    
    def cleanup_old_memories(self, min_importance: int = 3,
                            max_age_days: int = 90,
                            min_access_count: int = 2):
        """Cleanup old low-value memories"""
        # This would implement pruning logic
        # For now, just return stats
        return self.get_memory_stats()


# Example usage
if __name__ == "__main__":
    # Initialize integration
    integration = DiveAIMemoryIntegration()
    
    # Example: Store execution result
    result = {
        "status": "success",
        "summary": "Built authentication system with JWT",
        "solution": "Implemented JWT with refresh tokens",
        "cost": 0.05,
        "duration": 120,
        "model": "claude-opus-4-5",
        "agent_id": "agent-42"
    }
    
    memory_id = integration.store_execution_result(
        task="Build authentication system",
        result=result
    )
    print(f"Stored execution: {memory_id}")
    
    # Example: Inject context for new task
    context = integration.inject_context("Implement user authentication")
    print(f"\nContext:\n{context}")
    
    # Example: Find best agent
    best_agent = integration.find_best_agent_for_task("Build React component")
    print(f"\nBest agent: {best_agent}")
    
    # Example: Get stats
    stats = integration.get_memory_stats()
    print(f"\nMemory stats: {stats}")
