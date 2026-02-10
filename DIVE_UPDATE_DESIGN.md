# Dive Update System - Design Document

## 🎯 Problem Statement

**Current Issue:**
When Dive AI fixes a problem or breaks through to a new version, it only updates the specific file being worked on. Related files that depend on the changed code still use old code, causing inconsistencies.

**Example:**
- Update `first_run_complete.py` to V21.0
- But `install.sh` still calls old V20.4 code
- Result: System inconsistency

**Need:**
A system that automatically detects, analyzes, and suggests updates for all related files when making changes.

---

## 🏗️ System Architecture

### **Dive Update System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    DIVE UPDATE SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Dependency      │───▶│  Impact          │              │
│  │  Tracker         │    │  Analyzer        │              │
│  └──────────────────┘    └──────────────────┘              │
│           │                       │                          │
│           ▼                       ▼                          │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  File            │    │  Update          │              │
│  │  Relationship    │───▶│  Suggester       │              │
│  │  Graph           │    │                  │              │
│  └──────────────────┘    └──────────────────┘              │
│           │                       │                          │
│           ▼                       ▼                          │
│  ┌─────────────────────────────────────────┐               │
│  │         DIVE MEMORY INTEGRATION          │               │
│  │  (Track file states, versions, changes)  │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Core Components

### 1. **Dependency Tracker** (`dive_dependency_tracker.py`)

**Purpose:** Track relationships between files

**Features:**
- Parse Python imports (`import`, `from ... import`)
- Track function calls across files
- Detect configuration dependencies
- Build dependency graph

**Data Structure:**
```python
{
    "file": "core/dive_smart_orchestrator.py",
    "imports": [
        "core/dive_memory_3file_complete.py",
        "core/dive_smart_coder.py"
    ],
    "imported_by": [
        "dive_ai_complete_system.py",
        "install.sh"
    ],
    "functions_used": {
        "dive_memory_3file_complete.py": ["load_memory", "save_memory"],
        "dive_smart_coder.py": ["execute_code"]
    }
}
```

### 2. **Impact Analyzer** (`dive_impact_analyzer.py`)

**Purpose:** Analyze impact of changes on related files

**Features:**
- Detect breaking changes (function signature changes, removed functions)
- Calculate impact score (how many files affected)
- Prioritize updates (critical, high, medium, low)
- Generate impact report

**Impact Levels:**
- **CRITICAL**: Core API changes affecting multiple components
- **HIGH**: Function signature changes
- **MEDIUM**: New features requiring updates
- **LOW**: Documentation/comment changes

**Example Output:**
```
📊 IMPACT ANALYSIS: first_run_complete.py → V21.0

🔴 CRITICAL (3 files):
  - install.sh: Calls old version check
  - README.md: References V20.4 installation
  - dive_ai_startup.py: Uses old memory structure

🟡 MEDIUM (2 files):
  - CHANGELOG.md: Needs version update
  - VERSION: Needs bump to 21.0.0
```

### 3. **File Relationship Graph** (`dive_file_graph.py`)

**Purpose:** Build and maintain graph of file relationships

**Features:**
- Nodes: Files
- Edges: Dependencies (imports, calls, configs)
- Graph traversal for impact analysis
- Visualization export (JSON, DOT format)

**Graph Structure:**
```json
{
  "nodes": [
    {"id": "core/dive_smart_orchestrator.py", "type": "core", "version": "21.0"},
    {"id": "install.sh", "type": "script", "version": "20.4"}
  ],
  "edges": [
    {"from": "install.sh", "to": "first_run_complete.py", "type": "calls"},
    {"from": "first_run_complete.py", "to": "core/dive_memory_3file_complete.py", "type": "imports"}
  ]
}
```

### 4. **Update Suggester** (`dive_update_suggester.py`)

**Purpose:** Generate actionable update suggestions

**Features:**
- Suggest specific code changes
- Provide diff previews
- Prioritize update order
- Generate update checklist

**Example Suggestion:**
```markdown
## 📝 UPDATE SUGGESTIONS for V21.0 breakthrough

### 1. install.sh (CRITICAL)
**Issue:** Calls first_run_complete.py but references old V20.4
**Suggestion:**
```bash
# OLD:
echo "🧠 Dive AI V20.4 - First Run Setup"

# NEW:
echo "🧠 Dive AI V21.0 - First Run Setup"
```

**Impact:** Installation script shows wrong version

### 2. dive_ai_startup.py (HIGH)
**Issue:** Uses old memory structure from V20.4
**Suggestion:** Update memory loading to use new 3-file system
```

---

## 🔗 Integration with Dive Memory

### **Memory Schema Extension**

Add new fields to track file states:

```python
# In dive_memory_3file_complete.py
{
    "file_tracking": {
        "file_path": "core/dive_smart_orchestrator.py",
        "version": "21.0",
        "last_modified": "2026-02-05T04:30:00",
        "dependencies": [...],
        "dependents": [...],
        "breaking_changes": [
            {
                "version": "21.0",
                "change": "Memory structure updated",
                "affected_files": [...]
            }
        ]
    }
}
```

### **Memory Operations**

1. **Track File Changes:**
   ```python
   memory.track_file_change(
       file="core/dive_smart_orchestrator.py",
       version="21.0",
       changes=["Updated memory structure"],
       breaking=True
   )
   ```

2. **Query Impact:**
   ```python
   impact = memory.get_impact_analysis(
       file="first_run_complete.py",
       version="21.0"
   )
   ```

3. **Get Update Suggestions:**
   ```python
   suggestions = memory.get_update_suggestions(
       from_version="20.4",
       to_version="21.0"
   )
   ```

---

## 🔄 Workflow

### **When Making Changes:**

```
1. Developer/AI modifies file (e.g., first_run_complete.py)
   ↓
2. Dive Update detects change
   ↓
3. Dependency Tracker builds relationship graph
   ↓
4. Impact Analyzer calculates affected files
   ↓
5. Update Suggester generates recommendations
   ↓
6. Present report to developer/AI
   ↓
7. AI automatically applies suggested updates
   ↓
8. Dive Memory records all changes
   ↓
9. Version bump + commit
```

### **Automatic Mode:**

```python
# In dive_ai_complete_system.py
from core.dive_update_system import DiveUpdateSystem

update_system = DiveUpdateSystem()

# After making changes
changed_files = ["first_run_complete.py"]
impact = update_system.analyze_impact(changed_files)

if impact.has_critical_issues():
    # Auto-apply updates
    update_system.apply_suggestions(impact.suggestions)
    print("✅ Related files updated automatically")
```

---

## 📊 Data Storage

### **File Structure:**

```
memory/
├── file_tracking/
│   ├── dependency_graph.json      # Full dependency graph
│   ├── file_states.json           # Current state of all files
│   └── impact_history.json        # History of impacts
├── updates/
│   ├── pending_updates.json       # Updates waiting to be applied
│   └── update_history.json        # History of applied updates
└── versions/
    ├── v20.4.0_files.json         # Snapshot of files at V20.4.0
    └── v21.0.0_files.json         # Snapshot of files at V21.0.0
```

---

## 🎯 Key Features

### 1. **Automatic Detection**
- Scans all Python files for imports and function calls
- Detects version mismatches automatically
- Runs on every commit/change

### 2. **Smart Analysis**
- Understands semantic changes (not just text diffs)
- Prioritizes critical updates first
- Suggests specific code changes

### 3. **Memory Integration**
- Stores file states in Dive Memory
- Tracks version history
- Enables rollback if needed

### 4. **AI-Friendly Output**
- Generates structured JSON for AI consumption
- Provides human-readable reports
- Includes code diffs and suggestions

---

## 🚀 Implementation Plan

### Phase 1: Core Components
1. Implement Dependency Tracker
2. Implement Impact Analyzer
3. Implement File Relationship Graph
4. Implement Update Suggester

### Phase 2: Memory Integration
1. Extend Dive Memory schema
2. Add file tracking operations
3. Implement version snapshots

### Phase 3: Automation
1. Auto-run on file changes
2. Auto-apply safe updates
3. Generate reports for manual review

### Phase 4: Testing
1. Test with real version breakthrough scenarios
2. Validate impact analysis accuracy
3. Test auto-update safety

---

## 📝 Example Usage

### **Scenario: Breakthrough to V21.0**

```python
# 1. Make changes to first_run_complete.py
# 2. Run Dive Update

from core.dive_update_system import DiveUpdateSystem

updater = DiveUpdateSystem()

# Analyze impact
impact = updater.analyze_impact(
    changed_files=["first_run_complete.py"],
    new_version="21.0.0"
)

# Print report
print(impact.report())

# Output:
# 📊 IMPACT ANALYSIS: V20.4.0 → V21.0.0
# 
# 🔴 CRITICAL (3 files):
#   - install.sh: Version mismatch
#   - dive_ai_startup.py: Old memory structure
#   - README.md: Outdated installation instructions
# 
# 🟡 MEDIUM (2 files):
#   - CHANGELOG.md: Needs update
#   - VERSION: Needs bump

# Auto-apply updates
updater.apply_updates(impact.suggestions, auto_commit=True)

# Output:
# ✅ Updated install.sh
# ✅ Updated dive_ai_startup.py
# ✅ Updated README.md
# ✅ Updated CHANGELOG.md
# ✅ Updated VERSION to 21.0.0
# 🎉 All related files synchronized!
```

---

## 🔐 Safety Features

1. **Dry Run Mode:** Preview changes before applying
2. **Rollback Support:** Revert to previous state if issues occur
3. **Manual Review:** Flag complex changes for human review
4. **Backup:** Auto-backup before applying updates

---

## 🎯 Success Metrics

- **Consistency:** 100% of related files updated when version changes
- **Accuracy:** 95%+ correct impact detection
- **Speed:** Analysis completes in < 5 seconds
- **Automation:** 80%+ updates applied automatically

---

## 📚 Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement core components
3. ⏳ Integrate with Dive Memory
4. ⏳ Test with real scenarios
5. ⏳ Deploy to production

---

**Status:** Design Complete - Ready for Implementation
**Version:** 1.0
**Date:** February 5, 2026
