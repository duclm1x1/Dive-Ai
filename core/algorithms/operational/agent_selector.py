"""
Agent Selector Algorithm
Select optimal agents from pool of 128 for a task

Algorithm = CODE + STEPS
"""

import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class AgentSelectorAlgorithm(BaseAlgorithm):
    """
    Agent Selector - Choose optimal agents from 128-agent pool
    
    Analyzes task and selects best-fit agents based on capabilities
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AgentSelector",
            name="Agent Selector",
            level="operational",
            category="agent-coordination",
            version="1.0",
            description="Select optimal agents from pool of 128 specialized agents. Match task requirements to agent capabilities.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("task", "string", True, "Task description"),
                    IOField("task_type", "string", False, "Type: code/analysis/automation/etc"),
                    IOField("max_agents", "integer", False, "Max agents to return (default: 5)"),
                    IOField("required_capabilities", "list", False, "Must-have capabilities")
                ],
                outputs=[
                    IOField("selected_agents", "list", True, "Selected agent IDs and info"),
                    IOField("match_scores", "list", True, "Match scores per agent"),
                    IOField("total_capabilities", "integer", True, "Combined capabilities count")
                ]
            ),
            
            steps=[
                "Step 1: Parse task requirements",
                "Step 2: Extract required capabilities",
                "Step 3: Query agent pool (128 agents, 1968 capabilities)",
                "Step 4: Calculate match scores for each agent",
                "Step 5: Rank agents by score",
                "Step 6: Return top N agents"
            ],
            
            tags=["agents", "selection", "optimization"],
            performance_target={
                "accuracy": "90%+ optimal selection",
                "selection_time": "<500ms"
            }
        )
        
        # Load agent database (simplified for now)
        self.agents = self._load_agent_pool()
    
    def _load_agent_pool(self) -> Dict:
        """Load 128 agent definitions"""
        
        # Simplified agent pool - in production would load from agents/ directory
        agent_categories = {
            "coding": ["PythonExpert", "JavaScriptExpert", "GoExpert", "FullStackDev"],
            "data": ["DataAnalyst", "MLEngineer", "DatabaseExpert"],
            "automation": ["AutomationExpert", "TestingExpert", "DevOpsExpert"],
            "analysis": ["CodeReviewer", "SecurityAnalyst", "PerformanceAnalyst"],
            "design": ["Architect", "UIDesigner", "SystemDesigner"]
        }
        
        agents = {}
        agent_id = 1
        
        for category, agent_list in agent_categories.items():
            for agent_name in agent_list:
                agents[f"agent_{agent_id:03d}"] = {
                    "id": f"agent_{agent_id:03d}",
                    "name": agent_name,
                    "category": category,
                    "capabilities": self._get_agent_capabilities(agent_name),
                    "performance_score": 0.85 + (agent_id % 10) * 0.01  # Simulated
                }
                agent_id += 1
        
        return agents
    
    def _get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get capabilities for agent type"""
        
        capability_map = {
            "PythonExpert": ["python", "django", "flask", "fastapi", "testing"],
            "JavaScriptExpert": ["javascript", "node", "react", "vue", "typescript"],
            "DataAnalyst": ["pandas", "numpy", "sql", "visualization", "statistics"],
            "AutomationExpert": ["selenium", "pytest", "ci/cd", "scripting"],
            "CodeReviewer": ["code-review", "quality", "best-practices", "refactoring"]
        }
        
        return capability_map.get(agent_name, ["general"])
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute agent selection"""
        
        task = params.get("task", "")
        task_type = params.get("task_type", "")
        max_agents = params.get("max_agents", 5)
        required_capabilities = params.get("required_capabilities", [])
        
        print(f"\n🤖 Agent Selector: '{task[:60]}...'")
        print(f"   Max agents: {max_agents}")
        
        try:
            # Step 1-2: Extract capabilities from task
            task_capabilities = self._extract_capabilities(task, task_type)
            task_capabilities.extend(required_capabilities)
            
            print(f"   📋 Required capabilities: {len(task_capabilities)}")
            
            # Step 3-4: Score all agents
            agent_scores = []
            for agent_id, agent_info in self.agents.items():
                score = self._calculate_match_score(
                    agent_info["capabilities"],
                    task_capabilities
                )
                
                if score > 0:  # Only consider agents with positive match
                    agent_scores.append({
                        "agent_id": agent_id,
                        "agent_name": agent_info["name"],
                        "category": agent_info["category"],
                        "capabilities": agent_info["capabilities"],
                        "match_score": score
                    })
            
            # Step 5: Rank by score
            agent_scores.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Step 6: Select top N
            selected = agent_scores[:max_agents]
            total_caps = sum(len(a["capabilities"]) for a in selected)
            
            print(f"   ✅ Selected {len(selected)} agents (total {total_caps} capabilities)")
            
            return AlgorithmResult(
                status="success",
                data={
                    "selected_agents": selected,
                    "match_scores": [a["match_score"] for a in selected],
                    "total_capabilities": total_caps
                },
                metadata={
                    "task_capabilities": task_capabilities,
                    "agents_evaluated": len(agent_scores)
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Agent selection failed: {str(e)}")
    
    def _extract_capabilities(self, task: str, task_type: str) -> List[str]:
        """Extract required capabilities from task description"""
        
        capabilities = []
        task_lower = task.lower()
        
        # Language detection
        languages = ["python", "javascript", "java", "go", "typescript", "sql"]
        for lang in languages:
            if lang in task_lower:
                capabilities.append(lang)
        
        # Framework detection
        frameworks = ["django", "flask", "fastapi", "react", "vue", "node"]
        for fw in frameworks:
            if fw in task_lower:
                capabilities.append(fw)
        
        # Task type categorization
        if "test" in task_lower:
            capabilities.append("testing")
        if "automat" in task_lower:
            capabilities.append("automation")
        if "review" in task_lower:
            capabilities.append("code-review")
        if "data" in task_lower or "analys" in task_lower:
            capabilities.append("data-analysis")
        
        # Use task_type if provided
        if task_type:
            capabilities.append(task_type)
        
        return list(set(capabilities))
    
    def _calculate_match_score(self, agent_caps: List[str], required_caps: List[str]) -> float:
        """Calculate match score (0-1)"""
        
        if not required_caps:
            return 0.5  # Neutral score if no requirements
        
        matches = sum(1 for cap in required_caps if cap in agent_caps)
        
        score = matches / len(required_caps)
        
        return score


def register(algorithm_manager):
    """Register Agent Selector Algorithm"""
    try:
        algo = AgentSelectorAlgorithm()
        algorithm_manager.register("AgentSelector", algo)
        print("✅ Agent Selector Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register AgentSelector: {e}")
