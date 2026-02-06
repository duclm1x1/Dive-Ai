# Dive AI V28 - Fully Automatic Computer Assistant

**CLI + API + UI-TARS Integration | Smart Model Routing | Memory-Aware**

[![GitHub](https://img.shields.io/badge/GitHub-duclm1x1%2FDive--Ai-blue)](https://github.com/duclm1x1/Dive-Ai)
[![Version](https://img.shields.io/badge/version-28.0-green)](https://github.com/duclm1x1/Dive-Ai)
[![Status](https://img.shields.io/badge/status-production--ready-success)](https://github.com/duclm1x1/Dive-Ai)

> **V28** builds on V27.3's clean architecture, adding a unified **CLI + HTTP API** layer and **UI-TARS Desktop** integration for computer use. Designed to be called by AI agents (like Manus) to save tokens, or used standalone.

---

## Architecture

```
Manus (or any AI agent / Human)
    |
    v
dive CLI / HTTP API (port 8000)
    |
    +-- ask       --> LLM (smart model routing: nano/mini/flash)
    +-- code      --> Dive Coder Engine + LLM
    +-- search    --> Codebase grep + Memory search + LLM web
    +-- memory    --> File-based project memory (auto-persistent)
    +-- computer  --> UI-TARS Desktop (GUI/Browser automation)
    +-- skills    --> 123+ built-in skills
    +-- orchestrate --> Smart task decomposition + planning
    |
    v
Core Engine (V27.3)
    +-- Memory Loop Architecture
    +-- 128 Specialized Agents
    +-- Smart Orchestrator (7-phase)
    +-- Multi-Provider LLM (Claude, GPT, Gemini, DeepSeek)
    +-- Full-Duplex Voice
    +-- RAG Engine + Evidence Pack
```

---

## Quick Start (CLI)

```bash
# Show all commands
python3 dive --help

# Ask a question (auto-routes to cheapest model)
python3 dive ask "How to implement OAuth2 in FastAPI?"

# Generate code
python3 dive code --task "Create a REST API with CRUD" --lang python

# Review existing code
python3 dive code --action review --file ./app.py

# Search codebase
python3 dive search --query "memory leak" --scope codebase

# Store project memory (persists across sessions)
python3 dive memory --action store --project myapp --content "API uses JWT tokens"

# Recall project memory
python3 dive memory --action recall --project myapp

# Computer use via UI-TARS
python3 dive computer --task "Open Chrome and go to github.com"

# Multi-step orchestration (auto-plans complex tasks)
python3 dive orchestrate --task "Build and deploy a todo app"

# Start HTTP API server
python3 dive serve --port 8000

# Check system health
python3 dive status
```

---

## Smart Model Routing (Token Savings)

Dive AI automatically routes tasks to the cheapest sufficient model:

| Tier | Model | Use Case | Cost |
|------|-------|----------|------|
| **Fast** | gpt-4.1-nano | Simple Q&A, formatting, classification | ~$0.0001/call |
| **Standard** | gpt-4.1-mini | Coding, analysis, generation | ~$0.001/call |
| **Power** | gemini-2.5-flash | Complex reasoning, architecture, multi-step | ~$0.005/call |

This means Manus can delegate tasks to Dive AI and save 10-50x on token costs.

---

## HTTP API Endpoints

When running `python3 dive serve --port 8000`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ask` | Ask a question with optional project memory context |
| POST | `/api/code` | Code generation, review, debug, refactor, test, explain |
| POST | `/api/search` | Search codebase, web, or memory |
| POST | `/api/memory` | Store, recall, search, list, changelog |
| POST | `/api/computer` | Computer use via UI-TARS |
| POST | `/api/skills` | List or run skills |
| POST | `/api/orchestrate` | Multi-step task planning |
| GET | `/api/status` | System status and config |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI (interactive API docs) |

### API Example (curl)

```bash
# Ask
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How to fix CORS in FastAPI?", "project": "myapp"}'

# Generate code
curl -X POST http://localhost:8000/api/code \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a JWT auth middleware", "language": "python"}'

# Store memory
curl -X POST http://localhost:8000/api/memory \
  -H "Content-Type: application/json" \
  -d '{"action": "store", "project": "myapp", "content": "Using PostgreSQL with SQLAlchemy"}'
```

---

## UI-TARS Integration (Computer Use)

Dive AI integrates with [UI-TARS Desktop](https://github.com/bytedance/UI-TARS-desktop) (27.1k stars) for fully automatic computer control:

```bash
# Install UI-TARS CLI
npm install @agent-tars/cli@latest -g

# Enable in Dive AI
export DIVE_UITARS_ENABLED=true

# Use computer control
python3 dive computer --task "Open VS Code and create a new Python file"
python3 dive computer --task "Search Google for FastAPI tutorials" --mode browser
```

Supports: Local operator, Remote operator, Browser operator.

---

## Core Features (from V27.3)

| Feature | Description |
|---------|-------------|
| **128 Specialized Agents** | 1,968 capabilities across 4 eras |
| **20+ Specialized Skills** | Semantic Routing, Formal Verification, DNAS, and more |
| **Smart Orchestrator** | 7-phase intelligent processing |
| **Multi-Provider LLM** | Unified client with automatic failover |
| **Full-Duplex Voice** | Real-time voice with VAD, barge-in, wake word |
| **Optimized Memory** | 13.9x faster, 98% smaller, 50K+ scalability |
| **RAG Engine** | Adaptive retrieval, dense/sparse hybrid |
| **Evidence Pack** | Claims ledger, formal verification |
| **Monitoring Dashboard** | Real-time React dashboard |

---

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your-key"          # Required
export DIVE_LLM_MODEL="gpt-4.1-mini"     # Default model
export DIVE_UITARS_ENABLED="true"         # Enable UI-TARS
export DIVE_DEBUG="true"                  # Debug mode
```

### Config File (`.dive/config.json`)

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "fast_model": "gpt-4.1-nano",
    "standard_model": "gpt-4.1-mini",
    "power_model": "gemini-2.5-flash"
  },
  "uitars": {
    "enabled": true,
    "mode": "local"
  },
  "memory": {
    "auto_save": true
  }
}
```

---

## Project Structure

```
Dive-AI-V28/
  dive                      # CLI entry point (NEW)
  VERSION                   # 28.0.0
  README.md
  CHANGELOG.md              # Complete history (V13-V28)
  src/
    cli/                    # CLI + API layer (NEW in V28)
      main.py               #   Command router
      config.py             #   Configuration manager
      llm_adapter.py        #   Smart LLM client with model routing
      api_server.py          #   FastAPI server (all endpoints)
      commands/
        ask.py              #   Ask command
        code.py             #   Code generation/review/debug
        search.py           #   Codebase/web/memory search
        memory.py           #   Project memory CRUD
        computer.py         #   UI-TARS computer use
        skills.py           #   Skills management
        orchestrate.py      #   Multi-step orchestration
        serve.py            #   API server launcher
        status.py           #   System status
    core/                   # Core engine (from V27.3)
      orchestrator/         #   Smart Orchestrator (11 modules)
      memory/               #   Memory System (7 modules)
      voice/                #   Voice & Audio (16 modules)
      llm/                  #   LLM Clients (13 modules)
      search/               #   Search Engine (11 modules)
      workflow/             #   Workflow Engine (9 modules)
      engine/               #   RAG, Evidence, Verification (20 modules)
    skills/                 # 123+ built-in skills
    agents/                 # 128 Agent definitions
    monitor/                # Monitoring backend
    plugins/                # Plugin system (MCP)
    ui/                     # React Dashboard
    context/                # Context management
  memory/                   # Project memory storage (auto-created)
```

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **V28.0** | Feb 2026 | CLI + API + UI-TARS integration, smart model routing |
| **V27.3** | Feb 2026 | Clean architecture (94% file reduction, 0 duplicates) |
| **V27.2** | Jan 2026 | Full feature set (8,839 files) |
| **V25** | 2025 | 6-Layer Orchestration |
| **V15** | 2025 | DiveCoder foundation |

---

## Requirements

- Python 3.11+
- Node.js 22+ (for UI-TARS, optional)
- 8GB RAM (16GB recommended)
- Internet connection

---

**Dive AI V28.0** - Fully Automatic Computer Assistant
**Release**: February 7, 2026
**Status**: Production Ready
