"""
Dive Orchestrator with Brain Connection
The "Cerebrum" that makes decisions by checking the brain first

Philosophy:
    "Always check brain memory before making any decision"
    
Flow:
    1. Receive task
    2. Check brain for similar tasks
    3. Make informed decision based on history
    4. Execute decision
    5. Store result back to brain
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add core path
sys.path.insert(0, str(Path(__file__).parent))

from dive_memory_brain import get_brain


class DiveOrchestratorBrain:
    """
    Dive Orchestrator with Brain Connection
    Always checks memory before making decisions
    """
    
    def __init__(self):
        self.brain = get_brain()
        self.name = "Dive Orchestrator"
    
    def decide_task_assignment(self, task_description: str, available_agents: List[str]) -> Dict[str, Any]:
        """
        Decide which agent should handle the task
        Always checks brain first for similar tasks
        """
        print(f"\n🎯 {self.name}: Deciding task assignment...")
        print(f"   Task: {task_description}")
        print(f"   Available agents: {len(available_agents)}")
        
        # STEP 1: Check brain for similar tasks
        print(f"\n🧠 Checking brain for similar tasks...")
        check_result = self.brain.check_before_task_execute(task_description)
        
        if check_result["has_history"]:
            print(f"   ✅ Found {len(check_result['similar_tasks'])} similar tasks")
            print(f"   💡 Recommendation: {check_result['recommendation']}")
            
            # Use brain's recommendation for best agent
            if check_result.get("best_agent"):
                selected_agent = check_result["best_agent"]
                print(f"   🎯 Brain recommends: {selected_agent}")
            else:
                # Fallback to first available agent
                selected_agent = available_agents[0] if available_agents else None
                print(f"   🎯 No recommendation, using: {selected_agent}")
        else:
            print(f"   ℹ️  No history found, this is a new type of task")
            selected_agent = available_agents[0] if available_agents else None
            print(f"   🎯 Assigning to: {selected_agent}")
        
        return {
            "selected_agent": selected_agent,
            "check_result": check_result,
            "decision_time": time.time()
        }
    
    def decide_feature_implementation(self, feature_name: str, feature_description: str) -> Dict[str, Any]:
        """
        Decide whether to implement a feature
        Always checks brain first to see if feature exists or was tried before
        """
        print(f"\n🎯 {self.name}: Deciding feature implementation...")
        print(f"   Feature: {feature_name}")
        
        # STEP 1: Check brain for feature history
        print(f"\n🧠 Checking brain for feature history...")
        check_result = self.brain.check_before_feature_add(feature_name)
        
        should_implement = True
        reason = ""
        
        if check_result["has_history"]:
            print(f"   ⚠️  Feature has history!")
            print(f"   💡 Recommendation: {check_result['recommendation']}")
            
            # Check if feature already exists
            if "already exists" in check_result["recommendation"].lower():
                should_implement = False
                reason = "Feature already exists"
                print(f"   ❌ Decision: Do NOT implement (already exists)")
            
            # Check if feature failed before
            elif "failed before" in check_result["recommendation"].lower():
                should_implement = False
                reason = "Feature failed in previous attempts"
                print(f"   ❌ Decision: Do NOT implement (failed before)")
            else:
                should_implement = True
                reason = "Feature has history but can be implemented"
                print(f"   ✅ Decision: Implement (with caution)")
        else:
            print(f"   ℹ️  No history found, this is a new feature")
            should_implement = True
            reason = "New feature"
            print(f"   ✅ Decision: Implement")
        
        return {
            "should_implement": should_implement,
            "reason": reason,
            "check_result": check_result,
            "decision_time": time.time()
        }
    
    def decide_deployment(self, version: str) -> Dict[str, Any]:
        """
        Decide whether to proceed with deployment
        Always checks brain for previous deployment issues
        """
        print(f"\n🎯 {self.name}: Deciding deployment...")
        print(f"   Version: {version}")
        
        # STEP 1: Check brain for deployment history
        print(f"\n🧠 Checking brain for deployment history...")
        check_result = self.brain.check_before_deploy()
        
        should_deploy = True
        warnings = []
        
        if check_result["has_history"]:
            print(f"   ✅ Found {len(check_result['history'])} previous deployments")
            print(f"   💡 Recommendation: {check_result['recommendation']}")
            
            # Check for recent failures
            if check_result.get("recent_failures"):
                should_deploy = False
                warnings.append(f"{len(check_result['recent_failures'])} recent deployments failed")
                print(f"   ⚠️  Recent failures detected!")
            
            # Check for common issues
            if check_result.get("common_issues"):
                common_issues = [issue[0] for issue in check_result["common_issues"][:3]]
                warnings.extend(common_issues)
                print(f"   ⚠️  Common issues: {', '.join(common_issues)}")
            
            if should_deploy:
                print(f"   ✅ Decision: Proceed with deployment")
            else:
                print(f"   ❌ Decision: Do NOT deploy (fix issues first)")
        else:
            print(f"   ℹ️  No deployment history found")
            should_deploy = True
            warnings.append("First deployment - proceed with caution")
            print(f"   ✅ Decision: Proceed (first deployment)")
        
        return {
            "should_deploy": should_deploy,
            "warnings": warnings,
            "check_result": check_result,
            "decision_time": time.time()
        }
    
    def execute_task_with_memory(self, task_description: str, agent_id: str) -> Dict[str, Any]:
        """
        Execute a task and store result in brain
        Complete flow: check -> decide -> execute -> store
        """
        print(f"\n{'='*80}")
        print(f"🎯 {self.name}: Executing task with memory")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        # STEP 1: Check brain
        check_result = self.brain.check_before_task_execute(task_description, agent_id)
        
        # STEP 2: Make decision based on brain
        if check_result["has_history"] and check_result.get("successful_tasks"):
            print(f"\n💡 Learning from {len(check_result['successful_tasks'])} successful similar tasks")
        
        # STEP 3: Execute (simulated)
        print(f"\n⚙️  Executing task with agent {agent_id}...")
        time.sleep(0.1)  # Simulate execution
        
        # STEP 4: Store result in brain
        duration = time.time() - start_time
        result = f"Task completed successfully using approach from brain memory"
        
        print(f"\n💾 Storing result in brain...")
        memory_id = self.brain.store_task_result(
            task_description=task_description,
            agent_id=agent_id,
            status="success",
            duration=duration,
            result=result,
            details={
                "had_history": check_result["has_history"],
                "similar_tasks_count": len(check_result.get("similar_tasks", []))
            }
        )
        
        print(f"   ✅ Stored in brain: {memory_id}")
        print(f"\n✅ Task completed in {duration:.2f}s")
        
        return {
            "status": "success",
            "duration": duration,
            "result": result,
            "memory_id": memory_id,
            "check_result": check_result
        }


# Example usage
if __name__ == "__main__":
    print("🧠 Dive Orchestrator with Brain Connection")
    print("="*80)
    
    orchestrator = DiveOrchestratorBrain()
    
    # Example 1: Decide task assignment
    print("\n" + "="*80)
    print("Example 1: Task Assignment Decision")
    print("="*80)
    
    decision = orchestrator.decide_task_assignment(
        task_description="Build authentication system with JWT",
        available_agents=["agent-001", "agent-042", "agent-099"]
    )
    print(f"\n📊 Decision: {decision['selected_agent']}")
    
    # Example 2: Decide feature implementation
    print("\n" + "="*80)
    print("Example 2: Feature Implementation Decision")
    print("="*80)
    
    decision = orchestrator.decide_feature_implementation(
        feature_name="JWT Authentication",
        feature_description="Add JWT-based authentication system"
    )
    print(f"\n📊 Decision: {'Implement' if decision['should_implement'] else 'Do NOT implement'}")
    print(f"   Reason: {decision['reason']}")
    
    # Example 3: Execute task with memory
    print("\n" + "="*80)
    print("Example 3: Execute Task with Memory")
    print("="*80)
    
    result = orchestrator.execute_task_with_memory(
        task_description="Implement user login endpoint",
        agent_id="agent-042"
    )
    print(f"\n📊 Result: {result['status']}")
    
    # Example 4: Execute same task again (should use memory)
    print("\n" + "="*80)
    print("Example 4: Execute Same Task Again (with memory)")
    print("="*80)
    
    result = orchestrator.execute_task_with_memory(
        task_description="Implement user login endpoint",
        agent_id="agent-042"
    )
    print(f"\n📊 Result: {result['status']}")
    print(f"   Had history: {result['check_result']['has_history']}")
    
    print("\n" + "="*80)
    print("✅ Orchestrator with Brain is working!")
    print("="*80)
