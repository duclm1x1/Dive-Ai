# Dive AI V20.3.0 - Intelligent Adaptive Execution

> **"The AI that thinks before it acts, and adapts while it works"**

## 🎉 What's New in V20.3.0

### 🧠 Smart Orchestrator
Revolutionary 7-phase intelligent prompt processing system inspired by top-tier AI models (Claude Opus 4.5, Manus, GPT Codex):

**7-Phase Processing**:
1. **ANALYZE** - Intent detection, complexity assessment, confidence scoring
2. **THINK FIRST** - Identify ALL resources before acting (no reactive behavior)
3. **PLAN** - Structured task decomposition with dependencies
4. **ROUTE** - Multi-model selection (Claude Opus/Sonnet, GPT Codex, Gemini)
5. **EXECUTE** - Batch parallel operations for efficiency
6. **OBSERVE** - Update plan based on results, store in memory
7. **FINISH** - Complete or continue with updated context

### ⚡ Interrupt Handling
Manus-inspired adaptive execution that handles user input during task execution:

- **Quick Analysis** (< 100ms) - No blocking, instant response
- **Priority Detection** - Urgent/High/Normal/Low
- **Intent Recognition** - Modify/Extend/Cancel/Pause/Question
- **Smart Actions**:
  - **MERGE** - Merge modification into current task
  - **PAUSE** - Pause, handle urgent request, resume
  - **QUEUE** - Queue for later
  - **IGNORE** - Not relevant

**Example**:
```
AI: Installing Dive AI... (step 2/5)
User: "Use Python 3.11 instead"
AI: ⚡ INTERRUPT DETECTED
    Priority: normal
    Intent: modify_current_task
    Action: merge
    🔀 Merging into current plan...
    ✅ Continue with Python 3.11
```

### 📊 Intelligence Comparison

| Feature | V20.2.1 | V20.3.0 | Top-Tier AI |
|---------|---------|---------|-------------|
| Intent Detection | ❌ | ✅ | ✅ |
| Task Decomposition | ❌ | ✅ | ✅ |
| Multi-Model Routing | ❌ | ✅ | ✅ |
| Interrupt Handling | ❌ | ✅ | ✅ |
| Parallel Execution | ❌ | ✅ | ✅ |
| Memory Integration | ✅ | ✅ | ✅ |
| Event Streaming | ❌ | ✅ | ✅ |

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai

# Setup API keys (one command!)
python3 setup_api_keys.py

# Install dependencies
pip install -r requirements.txt

# Run first-time setup
python3 first_run_complete.py
```

### Usage

```python
from core.dive_smart_orchestrator import DiveSmartOrchestrator

# Initialize
orchestrator = DiveSmartOrchestrator()

# Process prompt
result = orchestrator.process_prompt(
    "Install Dive AI, configure LLM client, and test setup",
    project_id="my-project"
)

# Handle interrupt during execution
interrupt = orchestrator.handle_user_interrupt("Use Python 3.11 instead")
```

## 🎯 Key Features

### 1. **Smart Orchestrator**
- 7-phase intelligent processing
- Intent detection with confidence scoring
- Automatic task decomposition
- Multi-model routing
- Parallel execution planning
- Memory-aware decisions

### 2. **Interrupt Handler**
- Quick analysis (< 100ms)
- Priority-based handling
- Context merging
- Seamless resume
- No blocking

### 3. **3-File Memory System**
- `{PROJECT}_FULL.md` - Complete knowledge
- `{PROJECT}_CRITERIA.md` - Execution guidelines
- `{PROJECT}_CHANGELOG.md` - Version history

### 4. **Auto-Loading**
- Memory loaded on startup (60ms)
- Full context immediately available
- No manual setup needed

### 5. **Multi-Model Support**
- Claude Opus 4.5
- Claude Sonnet 4.5
- GPT-5.2 Codex
- Gemini 3.0 Pro
- Automatic failover

## 📚 Architecture

```
User Prompt
    ↓
Smart Orchestrator (7 phases)
    ├─→ Dive Memory Brain (check history)
    ├─→ Intent Detector (analyze)
    ├─→ Planner (decompose)
    ├─→ Model Router (select best model)
    ├─→ Executor (parallel execution)
    ├─→ Interrupt Handler (adaptive)
    └─→ Memory (store results)
    ↓
Result + Knowledge Accumulated
```

## 🧪 Testing

```bash
# Test Smart Orchestrator
python3 core/dive_smart_orchestrator.py

# Test Interrupt Handler
python3 core/dive_interrupt_handler.py

# Test Complete Workflow
python3 test_complete_3file_workflow.py
```

## 📊 Performance

- **Intent Detection**: < 50ms
- **Quick Interrupt Analysis**: < 100ms
- **Memory Loading**: 60ms (37 items)
- **Task Decomposition**: < 200ms
- **Parallel Execution**: Up to 5x faster

## 🎓 Philosophy

> **"Doc First, Code Later - Think Before Act - Adapt While Work"**

Dive AI V20.3.0 combines:
- **Intelligence** from top-tier AI models
- **Memory** that never forgets
- **Adaptability** to handle interrupts
- **Efficiency** through parallel execution

## 📝 Version History

### V20.3.0 (2026-02-05) - Current
- Smart Orchestrator with 7-phase processing
- Interrupt handling with adaptive execution
- Multi-model routing
- Event stream management

### V20.2.1 (2026-02-04)
- 3-file memory system
- Auto-loading on startup
- Doc-first workflow

### V20.2.0 (2026-02-03)
- Dive Memory V3 (13.9x faster)
- 128 specialized agents
- 20+ specialized skills

## 🔗 Links

- **Repository**: https://github.com/duclm1x1/Dive-Ai
- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 📄 License

MIT License - See LICENSE file

## 🙏 Credits

Inspired by:
- **Manus AI** - Interrupt handling and adaptive execution
- **Claude Opus 4.5** - Intent detection and ambiguity handling
- **GPT Codex** - "Think first, batch everything" philosophy
- **Gemini** - Multi-modal reasoning

---

**Dive AI V20.3.0** - The AI that thinks, adapts, and never forgets! 🚀
