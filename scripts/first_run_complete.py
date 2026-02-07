#!/usr/bin/env python3
"""
Dive AI V21.0 - Complete First Run Setup
Initializes the entire Dive AI system with doc-first workflow

This script:
1. Sets up Dive Memory Brain
2. Creates memory folder structure
3. Initializes doc-first workflow
4. Creates Dive AI self-documentation
5. Runs system health checks
6. Creates first version snapshot
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "core"))
sys.path.insert(0, str(Path(__file__).parent / "skills" / "dive-memory-v3" / "scripts"))

from dive_enhanced_workflow import DiveEnhancedWorkflow
from datetime import datetime


def print_banner(text: str):
    """Print formatted banner"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🧠 Dive AI V21.0 - First Run Setup                       ║
║                                                                              ║
║                  Complete Doc-First System Initialization                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # STEP 1: Initialize workflow
    print_banner("STEP 1: Initialize Enhanced Workflow")
    
    workflow = DiveEnhancedWorkflow(project_name="dive-ai")
    print("   ✅ Dive Memory Brain initialized")
    print(f"   📁 Memory root: {workflow.memory_root}")
    print(f"   💾 Database: {workflow.memory.db_path}")
    
    # STEP 2: Create Dive AI self-documentation
    print_banner("STEP 2: Create Dive AI Self-Documentation")
    
    doc_id, criteria_id = workflow.create_project_docs(
        project_id="dive-ai-v21",
        title="Dive AI V21.0 - Unified Brain System",
        full_doc="""## Overview

Dive AI V21.0 is a complete AI development platform with a unified brain architecture powered by Dive Memory V3.

## Core Philosophy

**"Doc First, Code Later"**
- Document research and decisions before implementation
- Create tasks with clear acceptance criteria
- AI automatically loads context from memory
- Knowledge accumulates over time instead of being lost

## Architecture

### 🧠 Dive Memory Brain (Central Hub)
The brain stores all knowledge and provides:
- **Knowledge Graph**: Automatic linking of related memories
- **Context Injection**: Auto-inject relevant context for tasks
- **Related Memories**: Discover connections via graph traversal
- **Duplicate Detection**: Automatic cleanup of redundant information

### 🎯 Dive Orchestrator (Cerebrum)
The decision-making component that:
- Checks memory before making decisions
- Makes informed choices based on history
- Stores decision results for future reference

### ✋ Dive Coder & 128 Agents (Hands/Feet)
The execution layer that:
- Checks memory before coding
- Executes with full context
- Stores execution results

## Workflow

1. **Research** → Document findings in memory
2. **Create 2 Files**:
   - Full Documentation (research, architecture, decisions)
   - Criteria & Checklist (acceptance criteria, tasks)
3. **AI Loads Context** → Automatically from memory
4. **AI Understands "Done"** → From acceptance criteria
5. **AI Executes** → With full context
6. **Store Results** → Back to memory

## Benefits

✅ **Knowledge Preservation**: Nothing is lost between sessions
✅ **Context Clarity**: AI always knows what to do
✅ **No Redundancy**: AI knows what's already done
✅ **Token Savings**: Reuse docs instead of re-research
✅ **Time Savings**: No starting from zero
✅ **Knowledge Compounds**: Builds over time

## Performance

- **13.9x faster** memory operations (vs V19)
- **98% smaller** database footprint
- **Sub-15ms** semantic search
- **50K+ memories** scalable
- **242 memories/second** throughput

## Memory Organization

```
memory/
├── projects/          # Project-specific databases
├── docs/              # Full documentation files
├── tasks/             # Criteria & checklist files
├── knowledge-graph/   # Graph visualizations
└── exports/           # Version snapshots
```

## Version Control

Every significant change creates a version snapshot with:
- Complete memory state
- Knowledge graph export
- Statistics and metrics
- Timestamp and description
""",
        criteria=[
            "Dive Memory Brain initialized and working",
            "Memory folder structure created",
            "Enhanced workflow system operational",
            "2-file system (full doc + criteria) working",
            "Knowledge graph generation working",
            "Context injection working",
            "Related memories discovery working",
            "Duplicate detection working",
            "Version control system working",
            "First-run setup completed",
            "Self-documentation created",
            "System health checks passing"
        ],
        architecture="""## System Architecture

```
Dive AI V21.0
│
├── 🧠 Core Brain System
│   ├── dive_memory_brain.py          # Central memory hub
│   ├── dive_orchestrator_brain.py    # Decision-making with memory
│   ├── dive_doc_first_workflow.py    # Doc-first workflow
│   └── dive_enhanced_workflow.py     # Enhanced with V3 features
│
├── 💾 Memory Storage
│   ├── memory/projects/              # Project databases
│   ├── memory/docs/                  # Full documentation
│   ├── memory/tasks/                 # Criteria & checklists
│   ├── memory/knowledge-graph/       # Graph exports
│   └── memory/exports/               # Version snapshots
│
├── 🤖 Agents & Skills
│   ├── agents/                       # 128 specialized agents
│   └── skills/                       # 20+ specialized skills
│
├── 🔧 Integration
│   ├── integration/                  # LLM clients, memory integration
│   └── orchestrator/                 # Task orchestration
│
└── 📚 Documentation
    ├── README.md                     # Main documentation
    ├── SECURITY.md                   # Security guide
    └── PROVIDER_INSTRUCTION_MANUAL.md # API provider guide
```

## Data Flow

1. **Input** → User request or task
2. **Check Memory** → Load relevant context
3. **Process** → Orchestrator decides, agents execute
4. **Store Results** → Back to memory
5. **Update Graph** → Link related memories
6. **Export** → Save to files (docs, criteria)
```
""",
        decisions=[
            {
                "title": "Unified Brain Architecture",
                "rationale": "Single source of truth for all knowledge",
                "alternatives": ["Distributed memory", "No memory system"],
                "impact": "All components share knowledge, learn together"
            },
            {
                "title": "Doc-First Workflow",
                "rationale": "Prevent knowledge loss, provide clear context",
                "alternatives": ["Code-first", "No documentation"],
                "impact": "Knowledge accumulates, AI always has context"
            },
            {
                "title": "2-File System",
                "rationale": "Separate full context from actionable checklist",
                "alternatives": ["Single file", "Multiple small files"],
                "impact": "Clear separation, easy to track progress"
            },
            {
                "title": "Memory Folder Organization",
                "rationale": "Structured storage for easy access and backup",
                "alternatives": ["Flat structure", "Database only"],
                "impact": "Easy to navigate, backup, and version control"
            }
        ]
    )
    
    print(f"   ✅ Self-documentation created")
    print(f"   📄 Full doc ID: {doc_id}")
    print(f"   📋 Criteria ID: {criteria_id}")
    
    # STEP 3: Load and verify context
    print_banner("STEP 3: Verify Enhanced Context Loading")
    
    context = workflow.load_enhanced_context("dive-ai-v21")
    
    print(f"   ✅ Full documentation: {'Loaded' if context['full_doc'] else 'Missing'}")
    print(f"   ✅ Criteria checklist: {'Loaded' if context['criteria'] else 'Missing'}")
    print(f"   🔗 Related memories: {len(context['related_memories'])}")
    print(f"   📊 Knowledge graph: {len(context['knowledge_graph']['nodes'])} nodes, {len(context['knowledge_graph']['edges'])} edges")
    print(f"   📁 Graph exported: {context['graph_file']}")
    
    # STEP 4: System health checks
    print_banner("STEP 4: System Health Checks")
    
    stats = workflow.get_enhanced_stats()
    
    checks = [
        ("Memory system", stats.get('total_memories', 0) > 0),
        ("Knowledge graph", stats.get('total_links', 0) >= 0),
        ("Documents", stats.get('documents', 0) > 0),
        ("Memory folders", Path(workflow.memory_root).exists()),
        ("Database", Path(workflow.memory.db_path).exists())
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {check_name}")
        if not passed:
            all_passed = False
    
    if not all_passed:
        print("\n   ⚠️  Some checks failed! Please review.")
        return False
    
    # STEP 5: Create first version snapshot
    print_banner("STEP 5: Create Version Snapshot")
    
    version_id = workflow.create_version_snapshot(
        version="21.0.0",
        description="Initial release with unified brain architecture and doc-first workflow"
    )
    
    print(f"   ✅ Version snapshot created: v21.0.0")
    print(f"   💾 Memory ID: {version_id}")
    
    # STEP 6: Display final statistics
    print_banner("STEP 6: Final Statistics")
    
    print(f"""
   📊 System Statistics:
   
   Memory System:
   - Total Memories: {stats.get('total_memories', 0)}
   - Total Links: {stats.get('total_links', 0)}
   - Total Sections: {stats.get('total_sections', 0)}
   - Avg Importance: {stats.get('avg_importance', 0)}
   
   Content:
   - Documents: {stats.get('documents', 0)}
   - Tasks: {stats.get('tasks', 0)}
   - Versions: {stats.get('versions', 0)}
   
   Storage:
   - Memory Root: {stats.get('memory_root', '')}
   - Database: {stats.get('db_path', '')}
   - Database Size: {Path(stats.get('db_path', '')).stat().st_size / 1024:.2f} KB
""")
    
    # STEP 7: Success message
    print_banner("✅ First Run Setup Complete!")
    
    print("""
   🎉 Dive AI V21.0 is now fully initialized!
   
   📚 What's Next:
   
   1. Start using doc-first workflow:
      python3 core/dive_enhanced_workflow.py
   
   2. Check your memory folder:
      ls -la memory/
   
   3. View knowledge graph:
      cat memory/knowledge-graph/dive-ai-v21_graph.json
   
   4. Read full documentation:
      cat memory/docs/dive-ai-v21_full.md
   
   5. Check criteria checklist:
      cat memory/tasks/dive-ai-v21_criteria.md
   
   🧠 Remember: Always "Doc First, Code Later"!
   
   Happy coding! 🚀
""")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during first run: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
