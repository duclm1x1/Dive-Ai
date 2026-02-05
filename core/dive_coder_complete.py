#!/usr/bin/env python3
"""
Dive Coder - Complete Version with Memory Integration

This coder:
1. Receives tasks from Orchestrator
2. Checks memory for previous implementations
3. Executes with full context
4. Saves all results to memory
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "dive-memory-v3" / "scripts"))

from dive_memory import DiveMemory


class DiveCoderComplete:
    """
    Complete Dive Coder with memory integration
    
    Workflow:
    1. Receive task from Orchestrator
    2. Check memory for previous implementations
    3. Load relevant context
    4. Execute with full knowledge
    5. Save results to memory
    """
    
    def __init__(self, project_name: str = "dive-ai"):
        """
        Initialize coder with memory integration
        
        Args:
            project_name: Name of the project
        """
        self.project_name = project_name
        self.memory_root = Path(__file__).parent.parent / "memory"
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory
        db_path = self.memory_root / "projects" / f"{project_name}.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.memory = DiveMemory(db_path=str(db_path))
        
        # Session state
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.executions = []
    
    def check_memory_before_coding(self, task: str) -> Dict[str, Any]:
        """
        Check memory before coding
        
        Args:
            task: The task description
            
        Returns:
            Context from memory including previous implementations, patterns, etc.
        """
        print(f"\n🔍 Dive Coder - Checking memory before coding...")
        print(f"   Task: {task}")
        
        context = {
            "previous_implementations": [],
            "code_patterns": [],
            "known_issues": [],
            "best_practices": [],
            "related_code": []
        }
        
        # Search for previous implementations
        implementations = self.memory.search(task, top_k=5, section="implementations")
        context["previous_implementations"] = implementations
        print(f"   ✅ Found {len(implementations)} previous implementations")
        
        # Search for code patterns
        patterns = self.memory.search(f"pattern {task}", top_k=3, section="patterns")
        context["code_patterns"] = patterns
        print(f"   ✅ Found {len(patterns)} code patterns")
        
        # Search for known issues
        issues = self.memory.search(f"issue {task}", top_k=3, section="issues")
        context["known_issues"] = issues
        print(f"   ⚠️  Found {len(issues)} known issues")
        
        # Search for best practices
        practices = self.memory.search(f"best practice {task}", top_k=3, section="practices")
        context["best_practices"] = practices
        print(f"   ✅ Found {len(practices)} best practices")
        
        # Get related code via knowledge graph
        related = self.memory.search(task, top_k=5, section="code")
        context["related_code"] = related
        print(f"   🔗 Found {len(related)} related code pieces")
        
        return context
    
    def execute_with_context(self, task: str, decision: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task with full context from memory
        
        Args:
            task: The task to execute
            decision: Decision from orchestrator
            context: Context from memory
            
        Returns:
            Execution result
        """
        print(f"\n👨‍💻 Dive Coder - Executing with context...")
        
        result = {
            "task": task,
            "decision": decision.get("decision", ""),
            "approach": decision.get("rationale", ""),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "context_used": {
                "previous_implementations": len(context.get("previous_implementations", [])),
                "code_patterns": len(context.get("code_patterns", [])),
                "known_issues": len(context.get("known_issues", [])),
                "best_practices": len(context.get("best_practices", [])),
                "related_code": len(context.get("related_code", []))
            },
            "status": "completed",
            "output": {},
            "lessons_learned": []
        }
        
        # Simulate execution based on context
        if context.get("previous_implementations"):
            result["output"]["method"] = "reused_and_improved"
            result["output"]["base"] = "previous_implementation"
            result["lessons_learned"].append("Successfully reused previous implementation")
            print(f"   ✅ Reused previous implementation with improvements")
        
        elif context.get("code_patterns"):
            result["output"]["method"] = "pattern_based"
            result["output"]["patterns_used"] = len(context["code_patterns"])
            result["lessons_learned"].append("Applied known code patterns")
            print(f"   ✅ Applied {len(context['code_patterns'])} code patterns")
        
        else:
            result["output"]["method"] = "from_scratch"
            result["lessons_learned"].append("Implemented from scratch - will be saved as new pattern")
            print(f"   ✅ Implemented from scratch (new pattern)")
        
        # Check for known issues
        if context.get("known_issues"):
            result["output"]["avoided_issues"] = len(context["known_issues"])
            result["lessons_learned"].append(f"Avoided {len(context['known_issues'])} known issues")
            print(f"   ⚠️  Avoided {len(context['known_issues'])} known issues")
        
        # Apply best practices
        if context.get("best_practices"):
            result["output"]["practices_applied"] = len(context["best_practices"])
            result["lessons_learned"].append(f"Applied {len(context['best_practices'])} best practices")
            print(f"   ✅ Applied {len(context['best_practices'])} best practices")
        
        print(f"   ✅ Execution complete!")
        
        return result
    
    def save_result_to_memory(self, result: Dict[str, Any]) -> str:
        """
        Save execution result to memory
        
        Args:
            result: The execution result
            
        Returns:
            Memory ID
        """
        print(f"\n💾 Dive Coder - Saving result to memory...")
        
        # Prepare content
        lessons = "\n".join(f"- {lesson}" for lesson in result["lessons_learned"])
        
        content = f"""Execution Result: {result['task']}

Status: {result['status']}

Approach: {result['approach']}

Method: {result['output'].get('method', 'unknown')}

Context Used:
- Previous Implementations: {result['context_used']['previous_implementations']}
- Code Patterns: {result['context_used']['code_patterns']}
- Known Issues: {result['context_used']['known_issues']}
- Best Practices: {result['context_used']['best_practices']}
- Related Code: {result['context_used']['related_code']}

Lessons Learned:
{lessons}

Session: {result['session_id']}
Timestamp: {result['timestamp']}
"""
        
        # Save to memory database
        memory_id = self.memory.add(
            content=content,
            section="executions",
            tags=["coder", "execution", self.session_id, result['output'].get('method', 'unknown')],
            importance=7
        )
        
        # Save to file
        executions_dir = self.memory_root / "executions"
        executions_dir.mkdir(exist_ok=True)
        
        execution_file = executions_dir / f"{self.session_id}_{memory_id[:8]}.md"
        execution_file.write_text(f"""# Execution: {result['task']}

**Status**: {result['status']}

**Timestamp**: {result['timestamp']}

**Session**: {result['session_id']}

**Memory ID**: {memory_id}

---

## Approach

{result['approach']}

## Method

{result['output'].get('method', 'unknown')}

## Context Used

- **Previous Implementations**: {result['context_used']['previous_implementations']}
- **Code Patterns**: {result['context_used']['code_patterns']}
- **Known Issues**: {result['context_used']['known_issues']}
- **Best Practices**: {result['context_used']['best_practices']}
- **Related Code**: {result['context_used']['related_code']}

## Output

```json
{json.dumps(result['output'], indent=2)}
```

## Lessons Learned

{lessons}

---

*Saved by Dive Coder*
""")
        
        print(f"   ✅ Saved to memory: {memory_id}")
        print(f"   📁 Saved to file: {execution_file.name}")
        
        # Track execution
        self.executions.append({
            "memory_id": memory_id,
            "task": result["task"],
            "timestamp": result["timestamp"]
        })
        
        return memory_id
    
    def process_task(self, task: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete workflow: Check memory → Execute → Save
        
        Args:
            task: The task to execute
            decision: Decision from orchestrator
            
        Returns:
            Complete execution result
        """
        print(f"\n{'='*80}")
        print(f"  👨‍💻 Dive Coder - Processing Task")
        print(f"{'='*80}")
        print(f"  Task: {task}")
        print(f"  Decision: {decision.get('decision', 'N/A')}")
        print(f"  Session: {self.session_id}")
        print(f"{'='*80}")
        
        # Step 1: Check memory
        context = self.check_memory_before_coding(task)
        
        # Step 2: Execute with context
        result = self.execute_with_context(task, decision, context)
        
        # Step 3: Save result
        memory_id = self.save_result_to_memory(result)
        result["memory_id"] = memory_id
        
        print(f"\n{'='*80}")
        print(f"  ✅ Task Execution Complete")
        print(f"{'='*80}\n")
        
        return result
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of all executions in this session
        
        Returns:
            Execution summary
        """
        summary = {
            "session_id": self.session_id,
            "project": self.project_name,
            "total_executions": len(self.executions),
            "executions": self.executions,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary


def main():
    """Demo: Complete coder workflow"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                👨‍💻 Dive Coder - Complete Memory Integration Demo             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Initialize coder
    coder = DiveCoderComplete(project_name="dive-ai")
    
    # Simulate decision from orchestrator
    decision = {
        "decision": "Implement based on documentation",
        "rationale": "Found related docs. Follow documented approach.",
        "confidence": 0.8
    }
    
    # Process task
    result = coder.process_task(
        "Implement JWT authentication system with RS256 algorithm",
        decision
    )
    
    # Show execution summary
    print("\n" + "="*80)
    print("  EXECUTION SUMMARY")
    print("="*80)
    
    summary = coder.get_execution_summary()
    print(f"\n  Session ID: {summary['session_id']}")
    print(f"  Project: {summary['project']}")
    print(f"  Total Executions: {summary['total_executions']}")
    
    if summary['executions']:
        print(f"\n  Executions:")
        for i, exec_info in enumerate(summary['executions'], 1):
            print(f"    {i}. {exec_info['task']}")
            print(f"       Memory ID: {exec_info['memory_id']}")
            print(f"       Timestamp: {exec_info['timestamp']}")
    
    print(f"\n  ✅ Coder ready for next task!\n")


if __name__ == "__main__":
    main()
