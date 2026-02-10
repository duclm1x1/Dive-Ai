"""
🧠 SELF-IMPROVING AGENTS
Learn from mistakes and optimize performance
"""

import os
import sys
import json
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class AgentPerformance:
    """Agent performance metrics"""
    agent_id: int
    role: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    avg_completion_time: float = 0.0
    avg_quality_score: float = 0.0
    improvement_rate: float = 0.0
    specializations: List[str] = field(default_factory=list)
    learned_patterns: List[str] = field(default_factory=list)


@dataclass
class LearningEvent:
    """Learning event from task execution"""
    event_id: str
    agent_id: int
    task_type: str
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    resolution: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion based on performance"""
    suggestion_id: str
    category: str  # prompt, model, temperature, retry_strategy
    current_value: Any
    suggested_value: Any
    expected_improvement: float
    confidence: float
    reason: str


class PerformanceAnalyzer:
    """
    📊 Analyzes agent performance and identifies patterns
    """
    
    def __init__(self):
        self.metrics: Dict[int, AgentPerformance] = {}
        self.events: List[LearningEvent] = []
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.success_patterns: Dict[str, List[str]] = defaultdict(list)
    
    def record_task_result(self, agent_id: int, role: str, task_type: str,
                          success: bool, completion_time: float,
                          quality_score: float = 1.0,
                          error: Optional[str] = None):
        """Record task execution result"""
        # Update agent metrics
        if agent_id not in self.metrics:
            self.metrics[agent_id] = AgentPerformance(agent_id=agent_id, role=role)
        
        metrics = self.metrics[agent_id]
        metrics.total_tasks += 1
        
        if success:
            metrics.successful_tasks += 1
            # Update success patterns
            self.success_patterns[task_type].append(role)
        else:
            metrics.failed_tasks += 1
            if error:
                self.error_patterns[error] += 1
        
        # Update averages
        n = metrics.total_tasks
        metrics.avg_completion_time = (
            (metrics.avg_completion_time * (n - 1) + completion_time) / n
        )
        metrics.avg_quality_score = (
            (metrics.avg_quality_score * (n - 1) + quality_score) / n
        )
        
        # Calculate improvement rate
        if metrics.total_tasks >= 10:
            recent_success = sum(1 for e in self.events[-10:]
                               if e.agent_id == agent_id and e.success)
            old_success = metrics.successful_tasks - recent_success
            old_total = metrics.total_tasks - 10
            if old_total > 0:
                old_rate = old_success / old_total
                new_rate = recent_success / 10
                metrics.improvement_rate = new_rate - old_rate
    
    def get_top_performers(self, role: str = None, limit: int = 10) -> List[AgentPerformance]:
        """Get top performing agents"""
        agents = list(self.metrics.values())
        
        if role:
            agents = [a for a in agents if a.role == role]
        
        # Sort by success rate and quality
        def score(a):
            if a.total_tasks == 0:
                return 0
            return (a.successful_tasks / a.total_tasks) * a.avg_quality_score
        
        agents.sort(key=score, reverse=True)
        return agents[:limit]
    
    def get_common_errors(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most common errors"""
        sorted_errors = sorted(self.error_patterns.items(), 
                              key=lambda x: x[1], reverse=True)
        return sorted_errors[:limit]
    
    def get_best_role_for_task(self, task_type: str) -> str:
        """Determine best role for task type based on history"""
        if task_type in self.success_patterns:
            roles = self.success_patterns[task_type]
            if roles:
                # Return most common successful role
                from collections import Counter
                return Counter(roles).most_common(1)[0][0]
        return "build"  # Default


class FeedbackLearner:
    """
    📚 Learning from feedback and mistakes
    """
    
    def __init__(self):
        self.lessons: Dict[str, List[str]] = defaultdict(list)
        self.retry_strategies: Dict[str, str] = {}
        self.prompt_improvements: Dict[str, str] = {}
    
    def learn_from_error(self, error_type: str, error_message: str,
                        context: Dict[str, Any]) -> LearningEvent:
        """Learn from error and suggest improvements"""
        event = LearningEvent(
            event_id=f"learn-{int(time.time())}",
            agent_id=context.get("agent_id", 0),
            task_type=context.get("task_type", "unknown"),
            success=False,
            error_type=error_type,
            error_message=error_message
        )
        
        # Analyze error and generate lessons
        lessons = []
        resolution = None
        
        if "timeout" in error_type.lower():
            lessons.append("Increase timeout for complex operations")
            lessons.append("Break down into smaller subtasks")
            resolution = "increase_timeout"
            self.retry_strategies[error_type] = "retry_with_higher_timeout"
        
        elif "rate_limit" in error_type.lower():
            lessons.append("Implement exponential backoff")
            lessons.append("Distribute load across time windows")
            resolution = "exponential_backoff"
            self.retry_strategies[error_type] = "wait_and_retry"
        
        elif "invalid_response" in error_type.lower():
            lessons.append("Improve prompt clarity")
            lessons.append("Add response format examples")
            resolution = "improve_prompt"
            self.prompt_improvements[context.get("task_type", "")] = "Add clearer formatting instructions"
        
        elif "context_length" in error_type.lower():
            lessons.append("Summarize context before sending")
            lessons.append("Use context compression")
            resolution = "compress_context"
        
        else:
            lessons.append(f"New error type encountered: {error_type}")
            lessons.append("Log for manual review")
            resolution = "manual_review"
        
        event.lessons_learned = lessons
        event.resolution = resolution
        
        # Store lessons
        for lesson in lessons:
            self.lessons[error_type].append(lesson)
        
        return event
    
    def learn_from_success(self, task_type: str, approach: str,
                          quality_score: float, context: Dict[str, Any]):
        """Learn from successful execution"""
        if quality_score >= 0.8:
            # High quality - remember this approach
            self.lessons[f"success_{task_type}"].append(
                f"Approach '{approach}' achieved {quality_score:.0%} quality"
            )
    
    def get_retry_strategy(self, error_type: str) -> Optional[str]:
        """Get learned retry strategy for error type"""
        return self.retry_strategies.get(error_type)
    
    def get_prompt_improvement(self, task_type: str) -> Optional[str]:
        """Get learned prompt improvement for task type"""
        return self.prompt_improvements.get(task_type)


class ParameterOptimizer:
    """
    ⚙️ Optimize model parameters based on performance
    """
    
    def __init__(self):
        self.parameter_history: Dict[str, List[Tuple[Any, float]]] = defaultdict(list)
        self.optimal_params: Dict[str, Any] = {}
    
    def record_parameter_performance(self, param_name: str, param_value: Any,
                                    performance_score: float):
        """Record parameter configuration and its performance"""
        self.parameter_history[param_name].append((param_value, performance_score))
        
        # Update optimal if this is better
        if param_name not in self.optimal_params:
            self.optimal_params[param_name] = (param_value, performance_score)
        elif performance_score > self.optimal_params[param_name][1]:
            self.optimal_params[param_name] = (param_value, performance_score)
    
    def suggest_parameters(self, param_name: str) -> OptimizationSuggestion:
        """Suggest optimal parameter value"""
        if param_name not in self.parameter_history:
            return None
        
        history = self.parameter_history[param_name]
        current = history[-1] if history else (None, 0)
        optimal = self.optimal_params.get(param_name, current)
        
        if optimal[0] == current[0]:
            return None
        
        return OptimizationSuggestion(
            suggestion_id=f"opt-{param_name}-{int(time.time())}",
            category="parameter",
            current_value=current[0],
            suggested_value=optimal[0],
            expected_improvement=optimal[1] - current[1],
            confidence=min(len(history) / 100, 0.95),  # Confidence increases with data
            reason=f"Parameter '{param_name}' performed better with value '{optimal[0]}'"
        )
    
    def optimize_temperature(self, task_type: str) -> float:
        """Suggest optimal temperature for task type"""
        history = self.parameter_history.get(f"temp_{task_type}", [])
        
        if len(history) < 5:
            # Default temperatures by task type
            defaults = {
                "coding": 0.2,
                "creative": 0.9,
                "analysis": 0.3,
                "documentation": 0.5,
                "default": 0.7
            }
            return defaults.get(task_type, defaults["default"])
        
        # Return best performing temperature
        return max(history, key=lambda x: x[1])[0]


class SelfImprovingAgent:
    """
    🧠 Self-Improving Agent System
    
    Combines learning from:
    - Performance metrics
    - Error analysis
    - Parameter optimization
    """
    
    def __init__(self):
        self.analyzer = PerformanceAnalyzer()
        self.learner = FeedbackLearner()
        self.optimizer = ParameterOptimizer()
        
        print("✅ SelfImprovingAgent initialized")
    
    def on_task_complete(self, agent_id: int, role: str, task_type: str,
                        completion_time: float, quality_score: float,
                        approach: str = None, params: Dict[str, Any] = None):
        """Called when task completes successfully"""
        # Record in analyzer
        self.analyzer.record_task_result(
            agent_id=agent_id,
            role=role,
            task_type=task_type,
            success=True,
            completion_time=completion_time,
            quality_score=quality_score
        )
        
        # Learn from success
        if approach:
            self.learner.learn_from_success(task_type, approach, quality_score, {
                "agent_id": agent_id,
                "role": role
            })
        
        # Record parameters
        if params:
            for param_name, param_value in params.items():
                self.optimizer.record_parameter_performance(
                    param_name, param_value, quality_score
                )
    
    def on_task_failed(self, agent_id: int, role: str, task_type: str,
                      error_type: str, error_message: str,
                      params: Dict[str, Any] = None) -> LearningEvent:
        """Called when task fails"""
        # Record in analyzer
        self.analyzer.record_task_result(
            agent_id=agent_id,
            role=role,
            task_type=task_type,
            success=False,
            completion_time=0,
            quality_score=0,
            error=error_type
        )
        
        # Learn from error
        event = self.learner.learn_from_error(error_type, error_message, {
            "agent_id": agent_id,
            "role": role,
            "task_type": task_type,
            "params": params
        })
        
        return event
    
    def get_recommendations(self, agent_id: int) -> Dict[str, Any]:
        """Get improvement recommendations for agent"""
        recommendations = {
            "agent_id": agent_id,
            "performance": None,
            "suggestions": [],
            "retry_strategies": {},
            "prompt_improvements": {}
        }
        
        # Get performance
        if agent_id in self.analyzer.metrics:
            metrics = self.analyzer.metrics[agent_id]
            recommendations["performance"] = {
                "total_tasks": metrics.total_tasks,
                "success_rate": metrics.successful_tasks / max(metrics.total_tasks, 1),
                "improvement_rate": metrics.improvement_rate,
                "avg_quality": metrics.avg_quality_score
            }
        
        # Get suggestions
        for param_name in ["temperature", "max_tokens", "retry_count"]:
            suggestion = self.optimizer.suggest_parameters(param_name)
            if suggestion:
                recommendations["suggestions"].append({
                    "parameter": param_name,
                    "current": suggestion.current_value,
                    "suggested": suggestion.suggested_value,
                    "improvement": f"+{suggestion.expected_improvement:.0%}"
                })
        
        # Get learned strategies
        recommendations["retry_strategies"] = dict(self.learner.retry_strategies)
        recommendations["prompt_improvements"] = dict(self.learner.prompt_improvements)
        
        return recommendations
    
    def get_best_agent_for_task(self, task_type: str, role: str = None) -> Optional[int]:
        """Get best agent ID for task based on learning"""
        top_performers = self.analyzer.get_top_performers(role=role, limit=5)
        
        if not top_performers:
            return None
        
        # Weight by recent improvement rate
        scored = []
        for agent in top_performers:
            if agent.total_tasks == 0:
                continue
            base_score = agent.successful_tasks / agent.total_tasks
            improvement_bonus = max(0, agent.improvement_rate * 0.2)
            scored.append((agent.agent_id, base_score + improvement_bonus))
        
        if not scored:
            return None
        
        # Return best or slight randomization for exploration
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 80% exploit best, 20% explore
        if random.random() < 0.8:
            return scored[0][0]
        else:
            return random.choice(scored[:3])[0] if len(scored) >= 3 else scored[0][0]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get learning summary"""
        total_agents = len(self.analyzer.metrics)
        total_tasks = sum(m.total_tasks for m in self.analyzer.metrics.values())
        avg_success = sum(
            m.successful_tasks / max(m.total_tasks, 1) 
            for m in self.analyzer.metrics.values()
        ) / max(total_agents, 1)
        
        return {
            "total_agents_tracked": total_agents,
            "total_tasks_analyzed": total_tasks,
            "average_success_rate": f"{avg_success:.0%}",
            "common_errors": self.analyzer.get_common_errors(5),
            "learned_strategies": len(self.learner.retry_strategies),
            "prompt_improvements": len(self.learner.prompt_improvements),
            "optimal_parameters": len(self.optimizer.optimal_params)
        }


# Global instance
_self_improver: Optional[SelfImprovingAgent] = None


def get_self_improver() -> SelfImprovingAgent:
    """Get or create global self-improver"""
    global _self_improver
    if _self_improver is None:
        _self_improver = SelfImprovingAgent()
    return _self_improver


if __name__ == "__main__":
    print("\n🧠 Self-Improving Agent Module\n")
    
    improver = get_self_improver()
    
    # Simulate some task executions
    for i in range(20):
        agent_id = random.randint(1, 10)
        success = random.random() > 0.3
        
        if success:
            improver.on_task_complete(
                agent_id=agent_id,
                role="build",
                task_type="coding",
                completion_time=random.uniform(1, 10),
                quality_score=random.uniform(0.7, 1.0),
                params={"temperature": random.choice([0.2, 0.5, 0.7])}
            )
        else:
            improver.on_task_failed(
                agent_id=agent_id,
                role="build",
                task_type="coding",
                error_type=random.choice(["timeout", "rate_limit", "invalid_response"]),
                error_message="Simulated error"
            )
    
    print("📊 Learning Summary:")
    summary = improver.get_summary()
    print(json.dumps(summary, indent=2, default=str))
    
    print("\n🎯 Best Agent for 'coding' task:")
    best = improver.get_best_agent_for_task("coding", "build")
    print(f"   Agent-{best}")
    
    print("\n💡 Recommendations for Agent-1:")
    recs = improver.get_recommendations(1)
    print(json.dumps(recs, indent=2, default=str))
