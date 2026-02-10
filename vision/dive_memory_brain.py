"""
Dive Memory Brain - Central Unified Memory System
The "brain" of Dive AI that all components connect to

Architecture:
    🧠 Dive Memory Brain (This file)
        ├── 🎯 Dive Orchestrator (checks memory before decisions)
        ├── ✋ Dive Coder (checks memory before coding, reports results)
        ├── 🤖 128 Agents (check memory before tasks, store learnings)
        └── 📊 All Components (always comeback to memory)

Philosophy:
    "Check memory before action, store results after action"
    Like a brain that checks past experiences before making decisions
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib

# Add skills path
skills_path = Path(__file__).parent.parent / "skills" / "dive-memory-v3" / "scripts"
sys.path.insert(0, str(skills_path))

from dive_memory import DiveMemory


class DiveMemoryBrain:
    """
    Central Brain of Dive AI
    All components must connect through this brain
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the brain"""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "data" / "dive_brain.db")
        
        self.memory = DiveMemory(db_path)
        self.memory.enable_context_injection()
        self.project_root = Path(__file__).parent.parent
        
        # Initialize brain
        self._init_brain()
    
    def _init_brain(self):
        """Initialize brain memory"""
        # Check if brain is already initialized
        results = self.memory.search("Dive Brain initialization", section="brain", top_k=1)
        
        if not results:
            self.memory.add(
                content="Dive Brain initialized - Central memory system for Dive AI",
                section="brain",
                tags=["initialization", "brain", "dive-ai"],
                importance=10,
                metadata={
                    "initialized_at": datetime.now().isoformat(),
                    "db_path": self.memory.db_path,
                    "project_root": str(self.project_root)
                }
            )
    
    # ============================================================================
    # CHECK MEMORY BEFORE ACTION
    # ============================================================================
    
    def check_before_file_modify(self, file_path: str) -> Dict[str, Any]:
        """
        Check memory before modifying a file
        Returns history of what was done to this file before
        """
        # Search for file history
        query = f"file:{file_path}"
        results = self.memory.search(
            query=query,
            section="file-changes",
            top_k=20
        )
        
        if not results:
            return {
                "has_history": False,
                "file_path": file_path,
                "message": f"No previous modifications found for {file_path}",
                "recommendation": "This is a new file or first modification",
                "history": []
            }
        
        # Build history
        history = []
        for r in results:
            history.append({
                "action": r.metadata.get("action", "unknown"),
                "description": r.metadata.get("description", ""),
                "timestamp": r.metadata.get("timestamp", ""),
                "result": r.metadata.get("result", ""),
                "file_hash": r.metadata.get("file_hash", ""),
                "score": r.score
            })
        
        # Get latest modification
        latest = history[0] if history else None
        
        # Generate recommendation
        recommendation = self._generate_file_recommendation(file_path, history)
        
        return {
            "has_history": True,
            "file_path": file_path,
            "message": f"Found {len(history)} previous modifications",
            "latest": latest,
            "history": history,
            "recommendation": recommendation
        }
    
    def check_before_feature_add(self, feature_name: str) -> Dict[str, Any]:
        """
        Check memory before adding a feature
        Returns if this feature was tried before and what happened
        """
        query = f"feature:{feature_name}"
        results = self.memory.search(
            query=query,
            section="features",
            top_k=10
        )
        
        if not results:
            return {
                "has_history": False,
                "feature_name": feature_name,
                "message": f"No previous attempts found for {feature_name}",
                "recommendation": "This is a new feature, proceed with implementation",
                "history": []
            }
        
        # Build history
        history = []
        for r in results:
            history.append({
                "status": r.metadata.get("status", "unknown"),
                "description": r.content,
                "timestamp": r.metadata.get("timestamp", ""),
                "result": r.metadata.get("result", ""),
                "files_affected": r.metadata.get("files_affected", []),
                "score": r.score
            })
        
        # Check if feature already exists
        existing = [h for h in history if h["status"] in ["added", "active", "completed"]]
        
        if existing:
            return {
                "has_history": True,
                "feature_name": feature_name,
                "message": f"⚠️  Feature already exists!",
                "existing": existing[0],
                "history": history,
                "recommendation": "Feature already implemented. Consider enhancing instead of re-adding."
            }
        
        # Check if feature was tried but failed
        failed = [h for h in history if h["status"] in ["failed", "removed"]]
        
        if failed:
            return {
                "has_history": True,
                "feature_name": feature_name,
                "message": f"⚠️  Feature was tried before but failed",
                "failed_attempts": failed,
                "history": history,
                "recommendation": f"Review why it failed before: {failed[0].get('result', 'Unknown reason')}"
            }
        
        return {
            "has_history": True,
            "feature_name": feature_name,
            "message": f"Found {len(history)} related entries",
            "history": history,
            "recommendation": "Review history before implementing"
        }
    
    def check_before_task_execute(self, task_description: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check memory before executing a task
        Returns similar past tasks and their results
        """
        results = self.memory.search(
            query=task_description,
            section="task-executions",
            top_k=10
        )
        
        if not results:
            return {
                "has_history": False,
                "task": task_description,
                "message": "No similar tasks found",
                "recommendation": "New task, proceed with execution",
                "similar_tasks": []
            }
        
        # Build similar tasks
        similar_tasks = []
        for r in results:
            similar_tasks.append({
                "task": r.metadata.get("task", ""),
                "status": r.metadata.get("status", "unknown"),
                "agent_id": r.metadata.get("agent_id", ""),
                "duration": r.metadata.get("duration", 0),
                "result": r.metadata.get("result", ""),
                "timestamp": r.metadata.get("timestamp", ""),
                "score": r.score
            })
        
        # Find successful similar tasks
        successful = [t for t in similar_tasks if t["status"] == "success"]
        
        # Find best agent for this task
        best_agent = None
        if agent_id is None and successful:
            # Count success by agent
            agent_success = {}
            for t in successful:
                aid = t["agent_id"]
                if aid:
                    agent_success[aid] = agent_success.get(aid, 0) + 1
            
            if agent_success:
                best_agent = max(agent_success.items(), key=lambda x: x[1])[0]
        
        recommendation = self._generate_task_recommendation(task_description, similar_tasks, best_agent)
        
        return {
            "has_history": True,
            "task": task_description,
            "message": f"Found {len(similar_tasks)} similar tasks",
            "similar_tasks": similar_tasks,
            "successful_tasks": successful,
            "best_agent": best_agent,
            "recommendation": recommendation
        }
    
    def check_before_deploy(self) -> Dict[str, Any]:
        """
        Check memory before deployment
        Returns issues from previous deployments
        """
        results = self.memory.search(
            query="deployment",
            section="deployments",
            top_k=20
        )
        
        if not results:
            return {
                "has_history": False,
                "message": "No previous deployments found",
                "recommendation": "First deployment, proceed with caution",
                "history": []
            }
        
        # Build deployment history
        history = []
        for r in results:
            history.append({
                "status": r.metadata.get("status", "unknown"),
                "version": r.metadata.get("version", ""),
                "timestamp": r.metadata.get("timestamp", ""),
                "issues": r.metadata.get("issues", []),
                "duration": r.metadata.get("duration", 0),
                "score": r.score
            })
        
        # Find recent failures
        recent_failures = [h for h in history[:5] if h["status"] == "failed"]
        
        # Collect all issues
        all_issues = []
        for h in history:
            all_issues.extend(h.get("issues", []))
        
        # Count issue frequency
        issue_freq = {}
        for issue in all_issues:
            issue_freq[issue] = issue_freq.get(issue, 0) + 1
        
        # Get common issues
        common_issues = sorted(issue_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        recommendation = self._generate_deploy_recommendation(history, recent_failures, common_issues)
        
        return {
            "has_history": True,
            "message": f"Found {len(history)} previous deployments",
            "history": history,
            "recent_failures": recent_failures,
            "common_issues": common_issues,
            "recommendation": recommendation
        }
    
    # ============================================================================
    # STORE RESULTS AFTER ACTION
    # ============================================================================
    
    def store_file_change(self, file_path: str, action: str, description: str,
                         result: str, details: Optional[Dict[str, Any]] = None):
        """Store file change after action"""
        # Calculate file hash
        full_path = self.project_root / file_path
        file_hash = None
        if full_path.exists():
            with open(full_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
        
        content = f"""File Change: {action}
File: {file_path}
Description: {description}
Result: {result}
Timestamp: {datetime.now().isoformat()}
File Hash: {file_hash}
"""
        
        if details:
            content += f"\nDetails:\n{json.dumps(details, indent=2)}"
        
        metadata = {
            "file_path": file_path,
            "action": action,
            "description": description,
            "result": result,
            "file_hash": file_hash,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            metadata.update(details)
        
        tags = ["file-change", action, Path(file_path).name]
        
        return self.memory.add(
            content=content,
            section="file-changes",
            tags=tags,
            importance=7,
            metadata=metadata
        )
    
    def store_feature_result(self, feature_name: str, status: str, description: str,
                            files_affected: List[str], result: str):
        """Store feature addition/removal result"""
        content = f"""Feature: {feature_name}
Status: {status}
Description: {description}
Result: {result}
Files Affected: {len(files_affected)}
Timestamp: {datetime.now().isoformat()}

Files:
{chr(10).join(f'  - {f}' for f in files_affected)}
"""
        
        metadata = {
            "feature_name": feature_name,
            "status": status,
            "description": description,
            "result": result,
            "files_affected": files_affected,
            "timestamp": datetime.now().isoformat()
        }
        
        tags = ["feature", status, feature_name.lower().replace(' ', '-')]
        
        return self.memory.add(
            content=content,
            section="features",
            tags=tags,
            importance=8,
            metadata=metadata
        )
    
    def store_task_result(self, task_description: str, agent_id: str, status: str,
                         duration: float, result: str, details: Optional[Dict[str, Any]] = None):
        """Store task execution result"""
        content = f"""Task: {task_description}
Agent: {agent_id}
Status: {status}
Duration: {duration:.2f}s
Result: {result}
Timestamp: {datetime.now().isoformat()}
"""
        
        if details:
            content += f"\nDetails:\n{json.dumps(details, indent=2)}"
        
        metadata = {
            "task": task_description,
            "agent_id": agent_id,
            "status": status,
            "duration": duration,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            metadata.update(details)
        
        tags = ["task-execution", status, agent_id]
        
        importance = 8 if status == "success" else 7
        
        return self.memory.add(
            content=content,
            section="task-executions",
            tags=tags,
            importance=importance,
            metadata=metadata
        )
    
    def store_deployment_result(self, version: str, status: str, duration: float,
                               issues: List[str], details: Optional[Dict[str, Any]] = None):
        """Store deployment result"""
        content = f"""Deployment: v{version}
Status: {status}
Duration: {duration:.2f}s
Issues: {len(issues)}
Timestamp: {datetime.now().isoformat()}

Issues:
{chr(10).join(f'  - {i}' for i in issues) if issues else '  None'}
"""
        
        if details:
            content += f"\nDetails:\n{json.dumps(details, indent=2)}"
        
        metadata = {
            "version": version,
            "status": status,
            "duration": duration,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            metadata.update(details)
        
        tags = ["deployment", status, f"v{version}"]
        
        importance = 9 if status == "success" else 8
        
        return self.memory.add(
            content=content,
            section="deployments",
            tags=tags,
            importance=importance,
            metadata=metadata
        )
    
    # ============================================================================
    # RECOMMENDATION GENERATION
    # ============================================================================
    
    def _generate_file_recommendation(self, file_path: str, history: List[Dict[str, Any]]) -> str:
        """Generate recommendation for file modification"""
        if not history:
            return "No history found. Proceed with modification."
        
        latest = history[0]
        
        # Check if last modification was recent
        try:
            last_time = datetime.fromisoformat(latest["timestamp"])
            time_diff = datetime.now() - last_time
            
            if time_diff.total_seconds() < 3600:  # Less than 1 hour
                return f"⚠️  File was modified {time_diff.total_seconds()/60:.0f} minutes ago. Review recent changes before modifying."
        except:
            pass
        
        # Check if there were issues
        if "error" in latest.get("result", "").lower() or "failed" in latest.get("result", "").lower():
            return f"⚠️  Last modification had issues: {latest['result']}. Be careful!"
        
        return f"File has {len(history)} previous modifications. Latest: {latest['action']} - {latest['description']}"
    
    def _generate_task_recommendation(self, task: str, similar_tasks: List[Dict[str, Any]], best_agent: Optional[str]) -> str:
        """Generate recommendation for task execution"""
        if not similar_tasks:
            return "No similar tasks found. Proceed with execution."
        
        successful = [t for t in similar_tasks if t["status"] == "success"]
        
        if successful:
            avg_duration = sum(t["duration"] for t in successful) / len(successful)
            
            recommendation = f"Found {len(successful)} successful similar tasks. "
            recommendation += f"Average duration: {avg_duration:.1f}s. "
            
            if best_agent:
                recommendation += f"Best agent: {best_agent}. "
            
            # Get common success pattern
            if successful[0].get("result"):
                recommendation += f"Typical approach: {successful[0]['result'][:100]}..."
            
            return recommendation
        
        failed = [t for t in similar_tasks if t["status"] == "failed"]
        if failed:
            return f"⚠️  {len(failed)} similar tasks failed before. Review failures: {failed[0].get('result', 'Unknown')[:100]}..."
        
        return f"Found {len(similar_tasks)} similar tasks with mixed results. Proceed with caution."
    
    def _generate_deploy_recommendation(self, history: List[Dict[str, Any]], 
                                       recent_failures: List[Dict[str, Any]],
                                       common_issues: List[Tuple[str, int]]) -> str:
        """Generate recommendation for deployment"""
        if not history:
            return "No deployment history. Proceed with caution."
        
        if recent_failures:
            return f"⚠️  {len(recent_failures)} recent deployments failed. Common issues: {', '.join(i[0] for i in common_issues[:3])}. Fix these before deploying!"
        
        success_rate = len([h for h in history if h["status"] == "success"]) / len(history) * 100
        
        recommendation = f"Deployment success rate: {success_rate:.1f}%. "
        
        if common_issues:
            recommendation += f"Watch out for: {', '.join(i[0] for i in common_issues[:3])}. "
        
        if success_rate > 80:
            recommendation += "Good track record, proceed with deployment."
        elif success_rate > 50:
            recommendation += "Moderate success rate, test thoroughly before deploying."
        else:
            recommendation += "⚠️  Low success rate, review and fix issues before deploying!"
        
        return recommendation
    
    # ============================================================================
    # BRAIN STATISTICS
    # ============================================================================
    
    def get_brain_stats(self) -> Dict[str, Any]:
        """Get brain statistics"""
        stats = self.memory.get_stats()
        
        # Add section-specific stats
        sections = ["file-changes", "features", "task-executions", "deployments", "brain"]
        section_stats = {}
        
        for section in sections:
            results = self.memory.search("", section=section, top_k=1000)
            section_stats[section] = len(results)
        
        return {
            **stats,
            "section_stats": section_stats,
            "db_path": self.memory.db_path,
            "project_root": str(self.project_root)
        }


# Singleton instance
_brain_instance = None

def get_brain() -> DiveMemoryBrain:
    """Get singleton brain instance"""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = DiveMemoryBrain()
    return _brain_instance


# Example usage
if __name__ == "__main__":
    brain = get_brain()
    
    print("🧠 Dive Memory Brain - Central Unified Memory System")
    print("=" * 80)
    print()
    
    # Example 1: Check before modifying a file
    print("Example 1: Check before modifying file")
    check = brain.check_before_file_modify("integration/dive_memory_brain.py")
    print(f"  Has history: {check['has_history']}")
    print(f"  Message: {check['message']}")
    print(f"  Recommendation: {check['recommendation']}")
    print()
    
    # Example 2: Store file change
    print("Example 2: Store file change")
    memory_id = brain.store_file_change(
        file_path="integration/dive_memory_brain.py",
        action="created",
        description="Created Dive Memory Brain - central unified memory system",
        result="Success - Brain system created"
    )
    print(f"  Stored: {memory_id}")
    print()
    
    # Example 3: Check before adding feature
    print("Example 3: Check before adding feature")
    check = brain.check_before_feature_add("Unified Memory Brain")
    print(f"  Has history: {check['has_history']}")
    print(f"  Message: {check['message']}")
    print(f"  Recommendation: {check['recommendation']}")
    print()
    
    # Example 4: Get brain stats
    print("Example 4: Brain statistics")
    stats = brain.get_brain_stats()
    print(f"  Total memories: {stats.get('total_memories', 0)}")
    print(f"  Sections: {stats.get('section_stats', {})}")
    print()
    
    print("✅ Brain is working!")
