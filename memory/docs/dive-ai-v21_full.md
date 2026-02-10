# Dive AI V21.0 - Unified Brain System - Full Documentation

**Project ID**: dive-ai-v21
**Created**: 2026-02-05T18:22:02.084092
**Type**: Full Documentation

---

## Research & Context

## Overview

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


## Architecture

## System Architecture

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


## Decisions

### Decision 1: Unified Brain Architecture

**Rationale**: Single source of truth for all knowledge

**Alternatives Considered**:
- Distributed memory
- No memory system

**Impact**: All components share knowledge, learn together

---

### Decision 2: Doc-First Workflow

**Rationale**: Prevent knowledge loss, provide clear context

**Alternatives Considered**:
- Code-first
- No documentation

**Impact**: Knowledge accumulates, AI always has context

---

### Decision 3: 2-File System

**Rationale**: Separate full context from actionable checklist

**Alternatives Considered**:
- Single file
- Multiple small files

**Impact**: Clear separation, easy to track progress

---

### Decision 4: Memory Folder Organization

**Rationale**: Structured storage for easy access and backup

**Alternatives Considered**:
- Flat structure
- Database only

**Impact**: Easy to navigate, backup, and version control

---

