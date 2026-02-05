# 🧠 Dive AI V21.0 - Unified Brain System

**Complete AI Development Platform with Doc-First Workflow**

[![Version](https://img.shields.io/badge/version-21.0.0-blue.svg)](https://github.com/duclm1x1/Dive-Ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)](https://python.org)

---

## 🌟 What is Dive AI V21.0?

Dive AI V21.0 is a revolutionary AI development platform with a **Unified Brain Architecture** powered by Dive Memory V3. It implements a "**Doc First, Code Later**" philosophy where knowledge accumulates over time instead of being lost between sessions.

### Core Philosophy

> **"Document before code, knowledge before action"**

- 📝 Research → Document → Task → Code
- 🧠 AI always has full context from memory
- 💾 Knowledge preserved across sessions
- 🚀 No redundant work, ever

---

## ✨ Key Features

### 🧠 Unified Brain Architecture

```
Dive AI V21.0
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
└── ✋ Dive Coder & 128 Agents (Hands/Feet)
    ├── Check memory before coding
    ├── Execute with context
    └── Store execution results
```

### 📚 Doc-First Workflow

**2-File System** for every project:
1. **Full Documentation** (`memory/docs/`) - Research, architecture, decisions
2. **Criteria & Checklist** (`memory/tasks/`) - Acceptance criteria, tasks, progress

### 🚀 Performance

- **13.9x faster** memory operations (vs V19)
- **98% smaller** database footprint
- **Sub-15ms** semantic search
- **242 memories/second** throughput
- **50K+ memories** scalable

### 🔗 Knowledge Graph

- Automatic linking of related memories
- Graph visualization and export
- Relationship tracking with strength scores
- Multi-depth traversal

### 💉 Context Injection

- Auto-inject relevant context for tasks
- Hybrid search (70% semantic + 30% keyword)
- Importance-based ranking
- Access pattern tracking

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone repository
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup API keys
python3 setup_api_keys.py

# 4. Run first-time setup
python3 first_run_complete.py
```

### First Project

```python
from core.dive_enhanced_workflow import DiveEnhancedWorkflow

# Initialize workflow
workflow = DiveEnhancedWorkflow(project_name="my-project")

# Create project documentation (2 files)
doc_id, criteria_id = workflow.create_project_docs(
    project_id="my-first-project",
    title="My First Project",
    full_doc="""
    ## Research
    
    [Your research findings here]
    
    ## Architecture
    
    [Your architecture design here]
    """,
    criteria=[
        "Feature A implemented",
        "Feature B tested",
        "Documentation complete"
    ]
)

# Load enhanced context (AI auto-reads everything)
context = workflow.load_enhanced_context("my-first-project")

# AI now has:
# - Full documentation
# - Criteria checklist
# - Related memories
# - Knowledge graph
# - Injected context
```

---

## 📁 Project Structure

```
Dive-Ai/
├── core/                          # Brain system
│   ├── dive_memory_brain.py       # Central memory hub
│   ├── dive_orchestrator_brain.py # Decision-making
│   ├── dive_doc_first_workflow.py # Doc-first workflow
│   └── dive_enhanced_workflow.py  # Enhanced with V3
│
├── memory/                        # Memory storage
│   ├── projects/                  # Project databases
│   ├── docs/                      # Full documentation
│   ├── tasks/                     # Criteria & checklists
│   ├── knowledge-graph/           # Graph exports
│   └── exports/                   # Version snapshots
│
├── agents/                        # 128 specialized agents
├── skills/                        # 20+ specialized skills
├── integration/                   # LLM clients, memory integration
├── orchestrator/                  # Task orchestration
│
├── first_run_complete.py          # First-time setup
├── stress_test_complete.py        # Comprehensive tests
├── setup_api_keys.py              # API key setup
└── README.md                      # This file
```

---

## 🎯 Workflow

### 1. Research & Document

```python
# Create full documentation
workflow.create_project_docs(
    project_id="auth-system",
    title="Authentication System",
    full_doc="""
    ## Research
    - JWT vs Session-based auth
    - Security considerations
    - Performance implications
    
    ## Decisions
    - Use JWT with RS256
    - 15-minute access tokens
    - 7-day refresh tokens
    """,
    criteria=[
        "User can register",
        "User can login",
        "Token refresh working",
        "Security audit passed"
    ]
)
```

### 2. AI Loads Context

```python
# AI automatically loads:
# - Full documentation
# - Criteria checklist
# - Related memories
# - Knowledge graph
context = workflow.load_enhanced_context("auth-system")
```

### 3. AI Understands "Done"

AI knows exactly what "done" means from acceptance criteria:
- ✅ User can register
- ✅ User can login
- ✅ Token refresh working
- ✅ Security audit passed

### 4. AI Executes with Context

AI codes with full context from memory - no guessing, no redundant work.

### 5. Store Results

```python
# Results automatically stored in memory
# Available for future reference
```

---

## 🧪 Testing

### Run Comprehensive Stress Test

```bash
python3 stress_test_complete.py
```

Tests include:
- ✅ Memory System Performance (1000 memories)
- ✅ Doc-First Workflow (10 projects)
- ✅ Knowledge Graph (100 interconnected memories)
- ✅ Context Injection (50 diverse memories)
- ✅ Version Control (10 snapshots)
- ✅ Concurrent Operations (10 threads × 50 memories)
- ✅ Large-Scale Data (10 × 10KB documents)
- ✅ Error Handling

### Expected Results

```
📊 Results: 8/8 tests passed (100.0%)
⏱️  Total duration: ~30s
🎉 ALL TESTS PASSED!
```

---

## 📊 Performance Benchmarks

| Metric | V19 | V20.2.1 | V21.0 | Improvement |
|--------|-----|---------|-------|-------------|
| Memory Operations | 17.4/s | 242/s | 242/s | **13.9x** |
| Database Size (2K memories) | 302MB | 7.29MB | 7.29MB | **98% smaller** |
| Semantic Search | 74ms | 11ms | 11ms | **6.7x faster** |
| Knowledge Graph | ❌ | ❌ | ✅ | **NEW** |
| Context Injection | ❌ | ❌ | ✅ | **NEW** |
| Doc-First Workflow | ❌ | ❌ | ✅ | **NEW** |

---

## 🔐 Security

All API keys are stored securely in `.env` files (never committed to git).

### Setup API Keys

```bash
python3 setup_api_keys.py
```

Supports:
- OpenAI (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)
- Anthropic (Claude Sonnet 4.5, Opus 4.5)
- V98API (Multi-model provider)
- AICoding (Vietnamese AI provider)

See [SECURITY.md](SECURITY.md) for details.

---

## 📚 Documentation

- [SECURITY.md](SECURITY.md) - Security guide
- [PROVIDER_INSTRUCTION_MANUAL.md](PROVIDER_INSTRUCTION_MANUAL.md) - API providers
- [memory/docs/](memory/docs/) - Project documentation
- [memory/tasks/](memory/tasks/) - Criteria & checklists

---

## 🎓 Examples

### Example 1: Create Research Document

```python
from core.dive_doc_first_workflow import DiveDocFirstWorkflow

workflow = DiveDocFirstWorkflow()

# Create research document
doc_id = workflow.create_doc(
    doc_id="jwt-research",
    title="JWT Authentication Research",
    content="""
    ## Why JWT?
    - Stateless authentication
    - Scalable across microservices
    
    ## Implementation
    - Use RS256 algorithm
    - Short-lived tokens (15 min)
    """,
    doc_type="research",
    tags=["authentication", "jwt"]
)

# Reference: @doc/jwt-research
```

### Example 2: Create Task with Doc Reference

```python
# Create task that references the doc
task_id = workflow.create_task(
    task_id="implement-jwt",
    title="Implement JWT Authentication",
    description="Build JWT auth based on research",
    acceptance_criteria=[
        "User can login",
        "Tokens use RS256",
        "Tokens expire in 15 min"
    ],
    doc_references=["@doc/jwt-research"]
)
```

### Example 3: AI Auto-Loads Context

```python
# AI automatically loads:
# - Task details
# - Referenced documents
# - Related memories
# - Knowledge graph
context = workflow.load_task_context("implement-jwt")

# AI now has FULL context - no manual pasting needed!
```

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Dive Memory V3 for the optimized memory system
- All contributors and testers
- The open-source community

---

## 📞 Support

- GitHub Issues: [https://github.com/duclm1x1/Dive-Ai/issues](https://github.com/duclm1x1/Dive-Ai/issues)
- Documentation: [https://github.com/duclm1x1/Dive-Ai/wiki](https://github.com/duclm1x1/Dive-Ai/wiki)

---

## 🚀 What's Next?

- [ ] Cloud sync for memories
- [ ] Web UI for knowledge graph visualization
- [ ] Multi-user collaboration
- [ ] Plugin system for extensions
- [ ] Mobile app

---

**Made with 🧠 by the Dive AI Team**

*"Doc First, Code Later - Knowledge that Compounds"*
