# Dive Search Engine - Design Document

## 🎯 Vision

Transform Advanced Search from a skill into **Dive Search Engine** - a core component that powers the entire Dive AI system through unified search across all data sources.

---

## 🔥 Why Dive Search Engine?

### Current State (Advanced Search as Skill)
❌ Limited to file searching
❌ Isolated from Memory system
❌ Not integrated with Update tracking
❌ Manual invocation required
❌ No orchestrator integration

### Future State (Dive Search Engine)
✅ **Unified search** across files, memory, updates, dependencies
✅ **Deeply integrated** with all Dive AI components
✅ **Automatic indexing** on changes
✅ **Search-driven** task routing in Orchestrator
✅ **Real-time** notifications and updates
✅ **Semantic search** with AI understanding

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DIVE SEARCH ENGINE                           │
│                    (Core Component)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   UNIFIED INDEX                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │  Files   │  │  Memory  │  │ Updates  │  │   Deps   │ │  │
│  │  │  Index   │  │  Index   │  │  Index   │  │  Graph   │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  SEARCH PROCESSOR                         │  │
│  │  • Query Parser                                          │  │
│  │  • Semantic Understanding (AI-powered)                   │  │
│  │  • Multi-source Search                                   │  │
│  │  • Result Ranking & Fusion                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  SEARCH INTERFACE                         │  │
│  │  • CLI: dive-search query "..."                          │  │
│  │  • API: search_engine.search(...)                        │  │
│  │  • Orchestrator Integration                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │ Memory │    │ Update │    │ Depend │    │Orchest │
    │ System │    │ System │    │ Tracker│    │ rator  │
    └────────┘    └────────┘    └────────┘    └────────┘
```

---

## 📦 Core Components

### 1. **Unified Index**

Indexes data from multiple sources:

#### a) **File Index**
- **Content:** Python files, shell scripts, configs, docs
- **Metadata:** Imports, classes, functions, exports
- **Structure:** AST-based for Python, text-based for others
- **Update:** Auto-reindex on file changes

#### b) **Memory Index**
- **Content:** FULL.md, CRITERIA.md, CHANGELOG.md files
- **Metadata:** Project names, versions, features
- **Structure:** Markdown sections, code blocks
- **Update:** Auto-reindex on memory updates

#### c) **Update Index**
- **Content:** Change log, impact analyses, update plans
- **Metadata:** Change types, categories, breaking changes
- **Structure:** JSON records with relationships
- **Update:** Real-time indexing on changes

#### d) **Dependency Graph**
- **Content:** File relationships, imports, dependencies
- **Metadata:** Node types, edge types, versions
- **Structure:** Graph database format
- **Update:** Auto-rebuild on code changes

### 2. **Search Processor**

#### Query Parser
```python
# Natural language queries
"find all files that import dive_memory"
"show breaking changes in v21.0"
"what features were added to orchestrator?"

# Structured queries
{
    "type": "file",
    "imports": "dive_memory",
    "modified_after": "2026-02-01"
}
```

#### Semantic Understanding (AI-Powered)
- Understands intent: "files affected by memory change" → search files + dependencies + updates
- Expands queries: "orchestrator" → ["dive_smart_orchestrator.py", "orchestrator logic", "task routing"]
- Suggests related: "Show related files" when viewing search results

#### Multi-Source Search
- Searches across all indexes simultaneously
- Merges results intelligently
- Ranks by relevance

#### Result Ranking & Fusion
- **Relevance Score:** Based on query match
- **Recency Score:** Newer changes ranked higher
- **Impact Score:** Breaking changes ranked higher
- **Relationship Score:** Related files grouped together

### 3. **Search Interface**

#### CLI Tool
```bash
# Basic search
dive-search "AuthService"

# Search in specific source
dive-search --source memory "knowledge graph"
dive-search --source files "class DiveMemory"
dive-search --source updates "breaking changes"

# Advanced queries
dive-search --imports "dive_memory" --modified-after "2026-02-01"
dive-search --breaking-changes --version "21.0"

# Search and act
dive-search "files using old memory API" --auto-fix
```

#### Python API
```python
from core.dive_search_engine import DiveSearchEngine

engine = DiveSearchEngine()

# Simple search
results = engine.search("dive_memory")

# Advanced search
results = engine.search(
    query="memory system",
    sources=["files", "memory", "updates"],
    filters={
        "modified_after": "2026-02-01",
        "breaking": True
    }
)

# Search with action
results = engine.search_and_analyze(
    query="files affected by orchestrator change",
    auto_fix=True
)
```

#### Orchestrator Integration
```python
# In Dive Smart Orchestrator
def analyze_task(self, task):
    # Use search to find relevant context
    context = self.search_engine.search(
        query=task.description,
        sources=["memory", "files"],
        limit=10
    )
    
    # Use context to route task
    if context.has_breaking_changes():
        return self.route_to_update_handler(task, context)
    
    return self.route_to_coder(task, context)
```

---

## 🔍 Search Capabilities

### 1. **File Search**
```python
# Find files by content
engine.search("class DiveMemory")

# Find files by structure
engine.search(imports="dive_memory_3file_complete")

# Find files by metadata
engine.search(modified_after="2026-02-01", author="dive-ai")
```

### 2. **Memory Search**
```python
# Search in memory docs
engine.search("knowledge graph feature", source="memory")

# Search by project
engine.search(project="dive-ai-v21", source="memory")

# Search criteria
engine.search("execution guidelines", source="memory", file_type="criteria")
```

### 3. **Update Search**
```python
# Find breaking changes
engine.search(breaking=True, source="updates")

# Find changes by category
engine.search(category="FEATURE", source="updates")

# Find related changes
engine.search(related_to="dive_memory_3file_complete.py", source="updates")
```

### 4. **Dependency Search**
```python
# Find dependents
engine.search(dependents_of="core/dive_memory.py")

# Find dependencies
engine.search(dependencies_of="dive_ai_complete_system.py")

# Find circular dependencies
engine.search(circular_dependencies=True)
```

### 5. **Cross-Source Search**
```python
# Search across all sources
results = engine.search("memory system refactor")

# Results include:
# - Files: dive_memory_3file_complete.py
# - Memory: DIVE_AI_V21_FULL.md (mentions memory refactor)
# - Updates: Change #42 (memory system refactor)
# - Dependencies: 15 files depend on dive_memory
```

---

## 🚀 Integration Points

### 1. **Dive Memory Integration**

```python
class DiveMemory3FileComplete:
    def __init__(self):
        self.search_engine = DiveSearchEngine()
    
    def load_project(self, project):
        # After loading, index in search engine
        content = self._load_files(project)
        self.search_engine.index_memory(project, content)
        return content
    
    def search_memory(self, query):
        # Use search engine for memory search
        return self.search_engine.search(
            query=query,
            source="memory"
        )
```

### 2. **Dive Update Integration**

```python
class DiveUpdateSystem:
    def __init__(self):
        self.search_engine = DiveSearchEngine()
    
    def analyze_impact(self, changed_files):
        # Use search to find related files
        related = self.search_engine.search(
            related_to=changed_files,
            sources=["files", "dependencies"]
        )
        
        # Analyze impact
        return self._analyze(changed_files, related)
    
    def track_change(self, change):
        # Index change in search engine
        self.search_engine.index_change(change)
```

### 3. **Dive Orchestrator Integration**

```python
class DiveSmartOrchestrator:
    def __init__(self):
        self.search_engine = DiveSearchEngine()
    
    def analyze_task(self, task):
        # Search for relevant context
        context = self.search_engine.search(
            query=task.description,
            sources=["memory", "files", "updates"],
            semantic=True  # AI-powered understanding
        )
        
        # Use context for routing
        return self._route_with_context(task, context)
    
    def find_related_tasks(self, current_task):
        # Search for similar past tasks
        return self.search_engine.search(
            query=current_task.description,
            source="memory",
            file_type="changelog",
            semantic=True
        )
```

### 4. **Dive Coder Integration**

```python
class DiveSmartCoder:
    def __init__(self):
        self.search_engine = DiveSearchEngine()
    
    def find_relevant_code(self, task):
        # Search for relevant code examples
        return self.search_engine.search(
            query=task.description,
            source="files",
            file_type="python",
            semantic=True
        )
    
    def check_breaking_changes(self, file):
        # Search for breaking changes affecting this file
        return self.search_engine.search(
            related_to=file,
            source="updates",
            breaking=True
        )
```

---

## 💡 Advanced Features

### 1. **Semantic Search (AI-Powered)**

```python
# Natural language query
results = engine.search(
    "Show me all files that were affected by the memory system refactor",
    semantic=True
)

# AI understands:
# - "memory system refactor" → search updates for memory changes
# - "files affected" → search dependencies
# - Combines results intelligently
```

### 2. **Search-Driven Task Routing**

```python
# Orchestrator uses search to route tasks
task = "Fix bug in orchestrator"

# Search finds:
# - orchestrator files
# - recent changes to orchestrator
# - breaking changes in dependencies
# - related bug fixes in memory

# Routes to appropriate handler based on search results
```

### 3. **Auto-Fix with Search**

```bash
# Find and fix outdated imports
dive-search "files using old memory API" --auto-fix

# Search finds:
# - Files importing old API
# - Update plan with new API
# - Applies fixes automatically
```

### 4. **Real-Time Notifications**

```python
# Search engine monitors changes
engine.watch(
    query="breaking changes in core",
    callback=lambda result: notify_ai(result)
)

# When breaking change detected:
# - AI receives notification
# - Search finds affected files
# - Auto-generates update plan
```

---

## 📊 Index Structure

### Unified Index Schema

```json
{
  "files": {
    "core/dive_memory_3file_complete.py": {
      "type": "python",
      "imports": ["os", "pathlib", "datetime"],
      "classes": ["DiveMemory3FileComplete"],
      "functions": ["load_project", "save_project"],
      "version": "21.0",
      "last_modified": "2026-02-05T10:30:00",
      "dependents": ["dive_smart_orchestrator.py", "dive_smart_coder.py"],
      "content_hash": "abc123..."
    }
  },
  "memory": {
    "DIVE_AI_V21_FULL.md": {
      "project": "dive-ai-v21",
      "type": "full",
      "sections": ["Overview", "Features", "Architecture"],
      "features": ["3-file memory", "knowledge graph"],
      "version": "21.0",
      "last_updated": "2026-02-05T10:30:00"
    }
  },
  "updates": {
    "change_42": {
      "type": "MODIFIED",
      "category": "REFACTOR",
      "file": "core/dive_memory_3file_complete.py",
      "description": "Refactored to 3-file structure",
      "breaking": true,
      "related_files": ["orchestrator.py", "coder.py"],
      "timestamp": "2026-02-05T10:30:00"
    }
  },
  "dependencies": {
    "nodes": [...],
    "edges": [...]
  }
}
```

---

## 🎯 Use Cases

### Use Case 1: Find Files Affected by Change

```python
# Developer changes dive_memory.py
changed_file = "core/dive_memory_3file_complete.py"

# Search finds all affected files
results = engine.search(
    related_to=changed_file,
    sources=["dependencies", "updates"]
)

# Results:
# - 15 files import dive_memory
# - 3 breaking changes in history
# - 5 files need updates
```

### Use Case 2: Search-Driven Task Routing

```python
# Task: "Add knowledge graph feature"
task = Task("Add knowledge graph feature")

# Orchestrator searches for context
context = engine.search(
    query=task.description,
    sources=["memory", "files"],
    semantic=True
)

# Context includes:
# - Memory: Previous knowledge graph discussions
# - Files: Related graph implementations
# - Updates: Recent graph-related changes

# Routes to appropriate handler with full context
```

### Use Case 3: Find Breaking Changes

```bash
# Before deploying v21.0
dive-search --breaking-changes --version "21.0"

# Results:
# 🔴 3 Breaking Changes Found:
#    1. dive_memory API changed (affects 15 files)
#    2. orchestrator routing changed (affects 5 files)
#    3. config format changed (affects 2 files)
#
# 💡 Recommendation: Run auto-fix before deployment
```

### Use Case 4: Memory Search for Context

```python
# AI needs context about "memory system"
context = engine.search(
    query="memory system architecture",
    source="memory",
    semantic=True
)

# Results include:
# - FULL.md: Complete memory system docs
# - CRITERIA.md: Memory usage guidelines
# - CHANGELOG.md: Memory evolution history
```

---

## 🚀 Implementation Plan

### Phase 1: Core Engine
1. Implement unified index structure
2. Create file indexer (AST-based for Python)
3. Create memory indexer (Markdown parser)
4. Create update indexer (JSON parser)
5. Implement basic search functionality

### Phase 2: Advanced Search
1. Add semantic search (AI-powered)
2. Implement result ranking & fusion
3. Add query parser for natural language
4. Implement filters and facets

### Phase 3: Integration
1. Integrate with Dive Memory
2. Integrate with Dive Update
3. Integrate with Dependency Tracker
4. Integrate with Orchestrator

### Phase 4: CLI & API
1. Create CLI tool (dive-search)
2. Create Python API
3. Add auto-fix capabilities
4. Add real-time monitoring

### Phase 5: Optimization
1. Add caching layer
2. Optimize indexing performance
3. Add incremental indexing
4. Add distributed search (future)

---

## 📈 Success Metrics

- **Search Speed:** < 100ms for most queries
- **Index Size:** < 50MB for typical project
- **Accuracy:** 95%+ relevant results in top 10
- **Coverage:** 100% of files, memory, updates indexed
- **Integration:** Used by all major Dive AI components

---

## 🔮 Future Enhancements

1. **Vector Search:** Semantic embeddings for better understanding
2. **Graph Search:** Traverse dependency graph in search
3. **Time Travel:** Search historical states
4. **Distributed Search:** Scale across multiple projects
5. **Visual Search:** Search by code structure/patterns
6. **Voice Search:** Natural language voice queries

---

## 📝 Summary

**Dive Search Engine** transforms Advanced Search from a skill into a core component that:

✅ **Unifies** search across files, memory, updates, dependencies
✅ **Powers** Orchestrator with search-driven task routing
✅ **Enables** real-time notifications and auto-fixes
✅ **Provides** semantic understanding with AI
✅ **Integrates** deeply with all Dive AI components

**Result:** Dive AI becomes much more powerful, faster, and better with unified search capabilities!

---

**Status:** Design Complete - Ready for Implementation
**Version:** 1.0
**Date:** February 5, 2026
