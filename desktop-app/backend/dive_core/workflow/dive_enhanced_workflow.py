"""
Dive Enhanced Workflow System
Full utilization of Dive Memory V3 capabilities

Features:
    ✅ Knowledge Graph visualization
    ✅ Context Injection for tasks
    ✅ Related Memories discovery
    ✅ Duplicate Detection & Cleanup
    ✅ 2-File System (Full Doc + Criteria)
    ✅ Memory Folder Organization
    ✅ Version Control Integration
    ✅ First-Run Setup

Architecture:
    memory/
    ├── projects/          # Project-specific memories
    ├── docs/              # Full documentation files
    ├── tasks/             # Task criteria files
    ├── knowledge-graph/   # Graph exports
    └── exports/           # Exported memories
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "dive-memory-v3" / "scripts"))

from dive_memory import DiveMemory


class DiveEnhancedWorkflow:
    """
    Enhanced Workflow with Full Dive Memory V3 Capabilities
    """
    
    def __init__(self, project_name: Optional[str] = None):
        """Initialize enhanced workflow"""
        self.project_root = Path(__file__).parent.parent
        self.memory_root = self.project_root / "memory"
        
        # Initialize memory with project-specific database
        if project_name:
            db_path = str(self.memory_root / "projects" / f"{project_name}.db")
        else:
            db_path = str(self.project_root / "data" / "dive_brain.db")
        
        self.memory = DiveMemory(db_path)
        self.memory.enable_context_injection()
        self.project_name = project_name or "default"
        
        # Ensure folders exist
        self._ensure_folders()
    
    def _ensure_folders(self):
        """Ensure memory folder structure exists"""
        folders = ["projects", "docs", "tasks", "knowledge-graph", "exports"]
        for folder in folders:
            (self.memory_root / folder).mkdir(parents=True, exist_ok=True)
    
    # ============================================================================
    # 2-FILE SYSTEM: Full Doc + Criteria
    # ============================================================================
    
    def create_project_docs(self, project_id: str, title: str,
                           full_doc: str, criteria: List[str],
                           architecture: Optional[str] = None,
                           decisions: Optional[List[Dict[str, str]]] = None) -> Tuple[str, str]:
        """
        Create 2 files for project:
        1. Full Documentation (research, architecture, decisions)
        2. Criteria & Checklist (acceptance criteria, tasks)
        
        Returns:
            (doc_memory_id, criteria_memory_id)
        """
        print(f"\n📚 Creating project documentation: {project_id}")
        
        # FILE 1: Full Documentation
        full_doc_content = f"""# {title} - Full Documentation

**Project ID**: {project_id}
**Created**: {datetime.now().isoformat()}
**Type**: Full Documentation

---

## Research & Context

{full_doc}

"""
        
        if architecture:
            full_doc_content += f"""## Architecture

{architecture}

"""
        
        if decisions:
            full_doc_content += """## Decisions

"""
            for i, decision in enumerate(decisions, 1):
                full_doc_content += f"""### Decision {i}: {decision.get('title', '')}

**Rationale**: {decision.get('rationale', '')}

**Alternatives Considered**:
{chr(10).join(f'- {alt}' for alt in decision.get('alternatives', []))}

**Impact**: {decision.get('impact', '')}

---

"""
        
        # Store full doc in memory
        doc_memory_id = self.memory.add(
            content=full_doc_content,
            section="documents",
            subsection="full-docs",
            tags=["project", project_id, "full-doc"],
            importance=10,
            metadata={
                "project_id": project_id,
                "title": title,
                "doc_type": "full",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Save to file
        doc_file = self.memory_root / "docs" / f"{project_id}_full.md"
        with open(doc_file, 'w') as f:
            f.write(full_doc_content)
        
        print(f"   ✅ Full doc: {doc_file}")
        
        # FILE 2: Criteria & Checklist
        criteria_content = f"""# {title} - Criteria & Checklist

**Project ID**: {project_id}
**Created**: {datetime.now().isoformat()}
**Type**: Criteria & Checklist

---

## Acceptance Criteria

{chr(10).join(f'{i+1}. [ ] {criterion}' for i, criterion in enumerate(criteria))}

## Status

- **Total Criteria**: {len(criteria)}
- **Completed**: 0
- **Remaining**: {len(criteria)}
- **Progress**: 0%

## Reference

Full documentation: @doc/{project_id}_full

---

**Instructions for AI**:
1. Read full documentation using @doc/{project_id}_full
2. Check each criterion as you complete it
3. Update progress percentage
4. Store results back to memory
"""
        
        # Store criteria in memory
        criteria_memory_id = self.memory.add(
            content=criteria_content,
            section="documents",
            subsection="criteria",
            tags=["project", project_id, "criteria"],
            importance=9,
            metadata={
                "project_id": project_id,
                "title": title,
                "doc_type": "criteria",
                "total_criteria": len(criteria),
                "completed": 0,
                "progress": 0,
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Save to file
        criteria_file = self.memory_root / "tasks" / f"{project_id}_criteria.md"
        with open(criteria_file, 'w') as f:
            f.write(criteria_content)
        
        print(f"   ✅ Criteria: {criteria_file}")
        print(f"   📊 Total criteria: {len(criteria)}")
        
        return (doc_memory_id, criteria_memory_id)
    
    # ============================================================================
    # ENHANCED CONTEXT LOADING (with Knowledge Graph & Related Memories)
    # ============================================================================
    
    def load_enhanced_context(self, project_id: str) -> Dict[str, Any]:
        """
        Load complete enhanced context with:
        - Full documentation
        - Criteria checklist
        - Related memories (via knowledge graph)
        - Auto-injected context
        """
        print(f"\n🧠 Loading enhanced context for: {project_id}")
        
        # Load full doc
        full_doc_results = self.memory.search(
            query=f"project:{project_id} full-doc",
            section="documents",
            tags=["full-doc"],
            top_k=1
        )
        
        full_doc = full_doc_results[0] if full_doc_results else None
        
        # Load criteria
        criteria_results = self.memory.search(
            query=f"project:{project_id} criteria",
            section="documents",
            tags=["criteria"],
            top_k=1
        )
        
        criteria = criteria_results[0] if criteria_results else None
        
        # Get related memories via knowledge graph
        related_memories = []
        if full_doc:
            print(f"   🔗 Finding related memories...")
            related = self.memory.get_related(full_doc.id, max_depth=2)
            related_memories = related
            print(f"      Found {len(related)} related memories")
        
        # Get context injection
        print(f"   💉 Injecting relevant context...")
        injected_context = self.memory.get_context_for_task(
            task=f"project {project_id}",
            max_memories=10
        )
        
        # Build knowledge graph
        print(f"   📊 Building knowledge graph...")
        graph = self.memory.get_graph(section="documents")
        
        # Export graph
        graph_file = self.memory_root / "knowledge-graph" / f"{project_id}_graph.json"
        with open(graph_file, 'w') as f:
            json.dump(graph, f, indent=2)
        print(f"      Graph exported: {graph_file}")
        
        print(f"   ✅ Enhanced context loaded")
        
        return {
            "project_id": project_id,
            "full_doc": full_doc,
            "criteria": criteria,
            "related_memories": related_memories,
            "injected_context": injected_context,
            "knowledge_graph": graph,
            "graph_file": str(graph_file)
        }
    
    # ============================================================================
    # DUPLICATE DETECTION & CLEANUP
    # ============================================================================
    
    def cleanup_duplicates(self, threshold: float = 0.95) -> Dict[str, Any]:
        """
        Find and merge duplicate memories
        """
        print(f"\n🧹 Cleaning up duplicates (threshold: {threshold})...")
        
        # Find duplicates
        duplicates = self.memory.find_duplicates(threshold=threshold)
        
        print(f"   Found {len(duplicates)} duplicate pairs")
        
        if duplicates:
            # Merge duplicates
            self.memory.merge_duplicates(duplicates, strategy="keep_newer")
            print(f"   ✅ Merged {len(duplicates)} duplicates")
        
        return {
            "duplicates_found": len(duplicates),
            "duplicates_merged": len(duplicates)
        }
    
    # ============================================================================
    # VERSION CONTROL
    # ============================================================================
    
    def create_version_snapshot(self, version: str, description: str) -> str:
        """
        Create version snapshot of current memory state
        """
        print(f"\n📸 Creating version snapshot: v{version}")
        
        # Get all memories
        stats = self.memory.get_stats()
        
        # Export memories
        export_file = self.memory_root / "exports" / f"v{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Get graph
        graph = self.memory.get_graph()
        
        snapshot = {
            "version": version,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "graph": graph
        }
        
        with open(export_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        # Store version in memory
        version_memory_id = self.memory.add(
            content=f"""# Version Snapshot: v{version}

**Description**: {description}
**Timestamp**: {datetime.now().isoformat()}
**Export File**: {export_file.name}

## Statistics

- Total Memories: {stats.get('total_memories', 0)}
- Total Links: {stats.get('total_links', 0)}
- Total Sections: {stats.get('total_sections', 0)}
- Avg Importance: {stats.get('avg_importance', 0)}
""",
            section="versions",
            tags=["version", f"v{version}"],
            importance=10,
            metadata={
                "version": version,
                "description": description,
                "export_file": str(export_file),
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        print(f"   ✅ Snapshot created: {export_file}")
        print(f"   📊 Memories: {stats.get('total_memories', 0)}")
        print(f"   🔗 Links: {stats.get('total_links', 0)}")
        
        return version_memory_id
    
    # ============================================================================
    # STATISTICS & REPORTING
    # ============================================================================
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics"""
        stats = self.memory.get_stats()
        
        # Get sections
        sections = self.memory.get_sections()
        
        # Count by type
        docs_count = len(self.memory.search("", section="documents", top_k=1000))
        tasks_count = len(self.memory.search("", section="tasks", top_k=1000))
        versions_count = len(self.memory.search("", section="versions", top_k=1000))
        
        return {
            **stats,
            "sections": sections,
            "documents": docs_count,
            "tasks": tasks_count,
            "versions": versions_count,
            "memory_root": str(self.memory_root),
            "db_path": self.memory.db_path
        }


# Example usage
if __name__ == "__main__":
    print("🚀 Dive Enhanced Workflow System")
    print("="*80)
    
    # Initialize workflow
    workflow = DiveEnhancedWorkflow(project_name="dive-ai-v21")
    
    # STEP 1: Create project with 2 files
    print("\n" + "="*80)
    print("STEP 1: Create Project Documentation (2 Files)")
    print("="*80)
    
    doc_id, criteria_id = workflow.create_project_docs(
        project_id="dive-ai-v21-unified-brain",
        title="Dive AI V21 - Unified Brain Architecture",
        full_doc="""## Research

### Problem
Dive AI needs a unified memory system where all components (Orchestrator, Coder, Agents) connect to a central brain.

### Solution
Implement Dive Memory Brain as the central hub with:
- Check memory before action
- Store results after action
- Knowledge graph for relationships
- Context injection for tasks

### Benefits
- Knowledge accumulates over time
- No redundant work
- AI learns from past experiences
- Token savings through context reuse
""",
        criteria=[
            "Dive Memory Brain implemented as central hub",
            "All components check memory before actions",
            "All components store results after actions",
            "Knowledge graph visualization working",
            "Context injection integrated",
            "Related memories discovery working",
            "2-file system (full doc + criteria) implemented",
            "Memory folder structure organized",
            "Version control system working"
        ],
        architecture="""## Architecture

```
Dive AI V21 - Unified Brain
├── 🧠 Dive Memory Brain (Central Hub)
│   ├── Knowledge Graph
│   ├── Context Injection
│   ├── Related Memories
│   └── Duplicate Detection
│
├── 🎯 Dive Orchestrator (Cerebrum)
│   ├── Check memory before decisions
│   ├── Make informed decisions
│   └── Store decision results
│
└── ✋ Dive Coder & Agents (Hands/Feet)
    ├── Check memory before coding
    ├── Execute with context
    └── Store execution results
```
""",
        decisions=[
            {
                "title": "Use Dive Memory V3 as central brain",
                "rationale": "13.9x faster, knowledge graph, context injection",
                "alternatives": ["Build custom memory", "Use external database"],
                "impact": "Maximum performance with built-in intelligence"
            },
            {
                "title": "Implement 2-file system",
                "rationale": "Separate full context from checklist for clarity",
                "alternatives": ["Single file", "Multiple small files"],
                "impact": "Clear separation of documentation and tasks"
            }
        ]
    )
    
    # STEP 2: Load enhanced context
    print("\n" + "="*80)
    print("STEP 2: Load Enhanced Context")
    print("="*80)
    
    context = workflow.load_enhanced_context("dive-ai-v21-unified-brain")
    
    print(f"\n📊 Context Summary:")
    print(f"   Full Doc: {'✅' if context['full_doc'] else '❌'}")
    print(f"   Criteria: {'✅' if context['criteria'] else '❌'}")
    print(f"   Related Memories: {len(context['related_memories'])}")
    print(f"   Knowledge Graph: {len(context['knowledge_graph']['nodes'])} nodes, {len(context['knowledge_graph']['edges'])} edges")
    
    # STEP 3: Cleanup duplicates
    print("\n" + "="*80)
    print("STEP 3: Cleanup Duplicates")
    print("="*80)
    
    cleanup_result = workflow.cleanup_duplicates(threshold=0.95)
    
    # STEP 4: Create version snapshot
    print("\n" + "="*80)
    print("STEP 4: Create Version Snapshot")
    print("="*80)
    
    version_id = workflow.create_version_snapshot(
        version="21.0",
        description="Unified Brain Architecture with full Dive Memory V3 integration"
    )
    
    # STEP 5: Get statistics
    print("\n" + "="*80)
    print("STEP 5: Enhanced Statistics")
    print("="*80)
    
    stats = workflow.get_enhanced_stats()
    print(f"\n📊 Enhanced Stats:")
    print(f"   Total Memories: {stats.get('total_memories', 0)}")
    print(f"   Total Links: {stats.get('total_links', 0)}")
    print(f"   Documents: {stats.get('documents', 0)}")
    print(f"   Tasks: {stats.get('tasks', 0)}")
    print(f"   Versions: {stats.get('versions', 0)}")
    print(f"   Memory Root: {stats.get('memory_root', '')}")
    
    print("\n" + "="*80)
    print("✅ Enhanced Workflow is working!")
    print("="*80)
