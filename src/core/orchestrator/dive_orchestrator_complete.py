#!/usr/bin/env python3
"""
Dive Orchestrator - Complete Version with Auto-Load and Memory Integration

This orchestrator:
1. Auto-loads memory on startup
2. Checks memory before every decision
3. Saves every decision to memory
4. Maintains continuous workflow loop
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


class DiveOrchestratorComplete:
    """
    Complete Dive Orchestrator with auto-loading and memory integration
    
    Workflow:
    1. Startup → Auto-load all memory
    2. Receive task → Check memory for context
    3. Make decision → Save to memory
    4. Delegate to coder → Monitor execution
    5. Receive results → Save to memory
    """
    
    def __init__(self, project_name: str = "dive-ai", auto_load: bool = True):
        """
        Initialize orchestrator with auto-loading
        
        Args:
            project_name: Name of the project
            auto_load: Whether to auto-load memory on startup
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
        self.loaded_context = {}
        
        # Auto-load on startup
        if auto_load:
            self._auto_load_memory()
    
    def _auto_load_memory(self):
        """
        Auto-load all memory files on startup
        
        This ensures the orchestrator has full context from previous sessions
        """
        print(f"\n🧠 Dive Orchestrator - Auto-Loading Memory...")
        print(f"   📁 Memory root: {self.memory_root}")
        
        # Load all documentation files
        docs_dir = self.memory_root / "docs"
        if docs_dir.exists():
            docs = list(docs_dir.glob("*.md"))
            print(f"   📄 Found {len(docs)} documentation files")
            
            for doc_file in docs:
                content = doc_file.read_text()
                self.loaded_context[f"doc:{doc_file.stem}"] = content
        
        # Load all task files
        tasks_dir = self.memory_root / "tasks"
        if tasks_dir.exists():
            tasks = list(tasks_dir.glob("*.md"))
            print(f"   📋 Found {len(tasks)} task files")
            
            for task_file in tasks:
                content = task_file.read_text()
                self.loaded_context[f"task:{task_file.stem}"] = content
        
        # Load all knowledge graphs
        graph_dir = self.memory_root / "knowledge-graph"
        if graph_dir.exists():
            graphs = list(graph_dir.glob("*.json"))
            print(f"   🔗 Found {len(graphs)} knowledge graphs")
            
            for graph_file in graphs:
                content = json.loads(graph_file.read_text())
                self.loaded_context[f"graph:{graph_file.stem}"] = content
        
        # Load all version exports
        exports_dir = self.memory_root / "exports"
        if exports_dir.exists():
            exports = list(exports_dir.glob("*.json"))
            print(f"   📸 Found {len(exports)} version snapshots")
            
            # Load latest export for quick context
            if exports:
                latest_export = max(exports, key=lambda p: p.stat().st_mtime)
                content = json.loads(latest_export.read_text())
                self.loaded_context["latest_version"] = content
                print(f"   ✅ Loaded latest version: {latest_export.stem}")
        
        # Query memory database for recent activities
        recent_memories = self.memory.search("", top_k=10, section="")
        print(f"   💾 Found {len(recent_memories)} recent memories in database")
        
        print(f"   ✅ Auto-load complete!")
        print(f"   📊 Total context loaded: {len(self.loaded_context)} items\n")
        
        return self.loaded_context
    
    def check_memory_before_decision(self, task: str) -> Dict[str, Any]:
        """
        Check memory before making a decision
        
        Args:
            task: The task description
            
        Returns:
            Context from memory including similar decisions, related docs, etc.
        """
        print(f"\n🔍 Checking memory before decision...")
        print(f"   Task: {task}")
        
        context = {
            "similar_decisions": [],
            "related_docs": [],
            "previous_attempts": [],
            "recommendations": []
        }
        
        # Search for similar decisions
        similar = self.memory.search(task, top_k=5, section="decisions")
        context["similar_decisions"] = similar
        print(f"   ✅ Found {len(similar)} similar decisions")
        
        # Search for related documentation
        related = self.memory.search(task, top_k=5, section="documentation")
        context["related_docs"] = related
        print(f"   ✅ Found {len(related)} related docs")
        
        # Search for previous attempts
        attempts = self.memory.search(task, top_k=3, section="executions")
        context["previous_attempts"] = attempts
        print(f"   ✅ Found {len(attempts)} previous attempts")
        
        # Get context injection
        injected_context = self.memory.get_context_for_task(task, max_memories=5)
        if injected_context:
            context["injected_context"] = injected_context
            print(f"   💉 Injected {len(injected_context)} chars of context")
        
        return context
    
    def make_decision(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a decision based on task and context from memory
        
        Args:
            task: The task description
            context: Context from memory
            
        Returns:
            Decision with rationale
        """
        print(f"\n🎯 Making decision...")
        
        # Analyze context
        has_similar = len(context.get("similar_decisions", [])) > 0
        has_docs = len(context.get("related_docs", [])) > 0
        has_attempts = len(context.get("previous_attempts", [])) > 0
        
        decision = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "context_used": {
                "similar_decisions": has_similar,
                "related_docs": has_docs,
                "previous_attempts": has_attempts
            },
            "decision": "",
            "rationale": "",
            "confidence": 0.0
        }
        
        # Make decision based on context
        if has_attempts:
            decision["decision"] = "Reuse previous approach with improvements"
            decision["rationale"] = f"Found {len(context['previous_attempts'])} previous attempts. Can learn from them."
            decision["confidence"] = 0.9
        elif has_docs:
            decision["decision"] = "Implement based on documentation"
            decision["rationale"] = f"Found {len(context['related_docs'])} related docs. Follow documented approach."
            decision["confidence"] = 0.8
        elif has_similar:
            decision["decision"] = "Adapt similar decision"
            decision["rationale"] = f"Found {len(context['similar_decisions'])} similar decisions. Adapt approach."
            decision["confidence"] = 0.7
        else:
            decision["decision"] = "Research and implement from scratch"
            decision["rationale"] = "No previous context found. Need fresh research."
            decision["confidence"] = 0.5
        
        print(f"   ✅ Decision: {decision['decision']}")
        print(f"   📝 Rationale: {decision['rationale']}")
        print(f"   📊 Confidence: {decision['confidence']}")
        
        return decision
    
    def save_decision_to_memory(self, decision: Dict[str, Any]) -> str:
        """
        Save decision to memory
        
        Args:
            decision: The decision to save
            
        Returns:
            Memory ID
        """
        print(f"\n💾 Saving decision to memory...")
        
        # Save to memory database
        memory_id = self.memory.add(
            content=f"""Decision: {decision['decision']}

Task: {decision['task']}

Rationale: {decision['rationale']}

Confidence: {decision['confidence']}

Context Used:
- Similar Decisions: {decision['context_used']['similar_decisions']}
- Related Docs: {decision['context_used']['related_docs']}
- Previous Attempts: {decision['context_used']['previous_attempts']}

Session: {decision['session_id']}
Timestamp: {decision['timestamp']}
""",
            section="decisions",
            tags=["orchestrator", "decision", self.session_id],
            importance=8
        )
        
        # Save to file
        decisions_dir = self.memory_root / "decisions"
        decisions_dir.mkdir(exist_ok=True)
        
        decision_file = decisions_dir / f"{self.session_id}_{memory_id[:8]}.md"
        decision_file.write_text(f"""# Decision: {decision['decision']}

**Task**: {decision['task']}

**Timestamp**: {decision['timestamp']}

**Session**: {decision['session_id']}

**Memory ID**: {memory_id}

---

## Rationale

{decision['rationale']}

## Confidence

{decision['confidence']} / 1.0

## Context Used

- **Similar Decisions**: {'Yes' if decision['context_used']['similar_decisions'] else 'No'}
- **Related Docs**: {'Yes' if decision['context_used']['related_docs'] else 'No'}
- **Previous Attempts**: {'Yes' if decision['context_used']['previous_attempts'] else 'No'}

---

*Saved by Dive Orchestrator*
""")
        
        print(f"   ✅ Saved to memory: {memory_id}")
        print(f"   📁 Saved to file: {decision_file.name}")
        
        return memory_id
    
    def delegate_to_coder(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate task to Dive Coder
        
        Args:
            decision: The decision to execute
            
        Returns:
            Execution plan
        """
        print(f"\n👨‍💻 Delegating to Dive Coder...")
        
        execution_plan = {
            "decision_id": decision.get("memory_id", ""),
            "task": decision["task"],
            "approach": decision["decision"],
            "status": "delegated",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   ✅ Task delegated to Dive Coder")
        print(f"   📋 Approach: {execution_plan['approach']}")
        
        return execution_plan
    
    def process_task(self, task: str) -> Dict[str, Any]:
        """
        Complete workflow: Check memory → Decide → Save → Delegate
        
        Args:
            task: The task to process
            
        Returns:
            Complete workflow result
        """
        print(f"\n{'='*80}")
        print(f"  🧠 Dive Orchestrator - Processing Task")
        print(f"{'='*80}")
        print(f"  Task: {task}")
        print(f"  Session: {self.session_id}")
        print(f"{'='*80}")
        
        # Step 1: Check memory
        context = self.check_memory_before_decision(task)
        
        # Step 2: Make decision
        decision = self.make_decision(task, context)
        
        # Step 3: Save decision
        memory_id = self.save_decision_to_memory(decision)
        decision["memory_id"] = memory_id
        
        # Step 4: Delegate to coder
        execution_plan = self.delegate_to_coder(decision)
        
        result = {
            "task": task,
            "context": context,
            "decision": decision,
            "execution_plan": execution_plan,
            "session_id": self.session_id
        }
        
        print(f"\n{'='*80}")
        print(f"  ✅ Task Processing Complete")
        print(f"{'='*80}\n")
        
        return result
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session
        
        Returns:
            Session summary with all decisions and context
        """
        summary = {
            "session_id": self.session_id,
            "project": self.project_name,
            "loaded_context_items": len(self.loaded_context),
            "memory_root": str(self.memory_root),
            "timestamp": datetime.now().isoformat()
        }
        
        # Get session statistics
        stats = self.memory.get_stats()
        summary["memory_stats"] = stats
        
        return summary


def main():
    """Demo: Complete orchestrator workflow"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              🧠 Dive Orchestrator - Complete Auto-Load Demo                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Initialize orchestrator (auto-loads memory)
    orchestrator = DiveOrchestratorComplete(project_name="dive-ai", auto_load=True)
    
    # Process a task
    result = orchestrator.process_task(
        "Implement JWT authentication system with RS256 algorithm"
    )
    
    # Show session summary
    print("\n" + "="*80)
    print("  SESSION SUMMARY")
    print("="*80)
    
    summary = orchestrator.get_session_summary()
    print(f"\n  Session ID: {summary['session_id']}")
    print(f"  Project: {summary['project']}")
    print(f"  Loaded Context: {summary['loaded_context_items']} items")
    print(f"  Memory Stats:")
    print(f"    - Total Memories: {summary['memory_stats'].get('total_memories', 0)}")
    print(f"    - Total Links: {summary['memory_stats'].get('total_links', 0)}")
    print(f"\n  ✅ Orchestrator ready for next task!\n")


if __name__ == "__main__":
    main()
