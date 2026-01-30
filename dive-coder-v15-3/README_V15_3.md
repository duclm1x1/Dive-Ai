# Dive Coder V15.3 - "Best of All" Edition

**Version:** 15.3  
**Codename:** Best of All  
**Release Date:** January 30, 2026  
**Status:** ✅ Production Ready

---

## 🎯 Vision

**Dive Coder V15.3** is the definitive, production-ready version of Dive Coder, combining the best features from all previous versions:

- **V15 Foundation:** Dive Engine, Antigravity Plugin, MCP Support
- **V15.2 Core:** Simplified pipeline, Robust monitoring, Provider optimization
- **V14.4 Features:** RAG, Search, Governance, Graph, Builder, 61 Skills
- **Dive Context:** Documentation server, MCP tools, 100+ libraries

This is the **"Best of All"** - a complete, enterprise-grade code intelligence platform.

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         Dive Coder V15.3 - Complete Architecture                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CLI Layer (45+ Commands)                                │   │
│  │  ├─ Core: status, doctor, explain, fix, process         │   │
│  │  ├─ Search: search, index-build, v13-rag, kb-update     │   │
│  │  ├─ Analysis: graph-*, select-tests                     │   │
│  │  ├─ Governance: review, sarif, baseline-*, gatekeeper   │   │
│  │  ├─ Building: build, autopatch, resolve, patch-check    │   │
│  │  ├─ Advanced: dag-run, debate, iko-*, evidencepack      │   │
│  │  ├─ Monitoring: monitor-status, monitor-events          │   │
│  │  ├─ Antigravity: antigravity-start, antigravity-tools   │   │
│  │  └─ Dive Context: context-search, context-get           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Unified Entry Point (divecoder_v15_3.py)                │   │
│  │  ├─ V15 Components (Dive Engine, Antigravity, MCP)      │   │
│  │  ├─ V15.2 Components (Monitoring, Event System)         │   │
│  │  ├─ V14.4 Components (RAG, Governance, Graph, Builder)  │   │
│  │  └─ Dive Context (Documentation, MCP Tools)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  V15 Advanced Features (10 modules)                      │   │
│  │  ├─ Dive Engine (orchestrator, thinking, artifacts)     │   │
│  │  ├─ Antigravity Plugin (MCP + HTTP)                     │   │
│  │  ├─ Dive Context (documentation server)                 │   │
│  │  ├─ Advanced Tools                                      │   │
│  │  └─ Thinking Engine (dual router, effort controller)    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  V14.4 Modules (20 modules)                              │   │
│  │  ├─ RAG (semantic search, reranking)                    │   │
│  │  ├─ Search (hybrid, semantic, vector)                   │   │
│  │  ├─ Graph (import graph, impact analysis)               │   │
│  │  ├─ Governance (quality gates, SARIF)                   │   │
│  │  ├─ Builder (project scaffold)                          │   │
│  │  ├─ Workflows (doctor, explain, fix)                    │   │
│  │  ├─ DAG & Debate (orchestration)                        │   │
│  │  └─ 61 Professional Skills                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  V15.2 Monitoring & Storage                              │   │
│  │  ├─ Dive Monitor UI (React frontend)                    │   │
│  │  ├─ Monitor Server (FastAPI)                            │   │
│  │  ├─ Robust Event Emitter (buffer, retry, health check)  │   │
│  │  ├─ Event Storage (SQLite)                              │   │
│  │  ├─ LLM Client (multi-provider)                         │   │
│  │  └─ Provider Optimizer (cost/speed optimization)        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone or extract V15.3
cd dive-coder-v15-3

# Install Python dependencies
pip install -r requirements.txt

# Install Dive Context dependencies
cd dive-context && pnpm install && pnpm build && cd ..

# Install frontend dependencies (optional)
cd monitor_server && pip install -r requirements.txt && cd ..
cd ui && npm install && cd ..
```

### Startup

```bash
# Terminal 1: Start Dive Monitor Server
python monitor_server/app/main.py

# Terminal 2: Start Dive Context MCP Server
node dive-context/dist/index-github.js

# Terminal 3: Use Dive Coder V15.3
python divecoder_v15_3.py status
```

---

## 📋 CLI Commands (45+)

### Core Commands (5)
- `status` - Check system status
- `doctor` - Environment + repo readiness
- `explain` - Grounded repo explanation
- `fix` - Bugfix flow scaffold
- `process` - Process a request

### Search & RAG (4)
- `search` - Hybrid search
- `index-build` - Build search index
- `v13-rag` - V13 RAG retrieval
- `kb-update` - Update knowledge base

### Analysis & Graph (3)
- `graph-build` - Build import graph
- `graph-impact` - Compute impacted files
- `select-tests` - Select affected tests

### Review & Governance (7)
- `review` - Analyze repo
- `sarif` - Generate SARIF report
- `baseline set` - Set baseline
- `baseline compare` - Compare baseline
- `gatekeeper` - Gatekeeper runner
- `evidencepack` - Evidence pack management
- `patch-check` - Validate patch

### Building & Patching (5)
- `build` - Build project
- `autopatch` - Auto-generate patches
- `resolve` - Verification loop
- `golden` - Golden config
- `v13-init` - V13 initialization

### Workflows & Modes (6)
- `mode list` - List available modes
- `mode apply` - Create run workspace
- `mode run` - Run mode workflow
- `cache-design init` - Initialize cache design
- `cache-design validate` - Validate artifacts
- `investigate` - Investigation workflow

### Advanced Orchestration (5)
- `dag-run` - Run DAG workflow
- `debate` - Multi-agent debate
- `iko new` - Create IKO
- `iko show` - Show IKO
- `iko list` - List IKOs

### Skills & Bootstrap (4)
- `skills-reindex` - Rebuild skill automap
- `v13-preflight` - V13 preflight check
- `v13-self-review` - V13 self-review
- `v13-search` - V13 search

### Monitoring (3+)
- `monitor-status` - Check monitoring status
- `monitor-events` - Stream monitoring events
- `monitor-config` - Configure monitoring

### Antigravity (2+)
- `antigravity-start` - Start Antigravity plugin
- `antigravity-tools` - List available tools

### Dive Context (2+)
- `context-search` - Search documentation
- `context-get` - Get library documentation

---

## 🔧 Python API

```python
from divecoder_v15_3 import DiveCoderV153, DiveCoderV153Config

# Initialize with default config
coder = DiveCoderV153()

# Or with custom config
config = DiveCoderV153Config(
    enable_dive_engine=True,
    enable_monitoring=True,
    enable_rag=True,
    enable_dive_context=True,
)
coder = DiveCoderV153(config)

# Process a request
result = coder.process_request(
    "Review this code for security issues",
    use_rag=True,
    use_dive_context=True,
    run_governance=True,
    generate_evidence=True
)

print(f"Success: {result.success}")
print(f"Response: {result.response}")
print(f"Evidence: {result.evidence}")

# Get status
status = coder.get_status()
print(f"Components: {status['components']}")

# Get component info
engine_info = coder.get_component_info('dive_engine')
print(f"Dive Engine: {engine_info}")
```

---

## 📦 File Structure

```
dive-coder-v15-3/
├── divecoder_v15_3.py              # Main entry point (NEW)
├── README_V15_3.md                 # This file (NEW)
├── requirements.txt                # Python dependencies (NEW)
│
├── V15 Components
│   ├── .shared/vibe-coder-v13/     # All V15 modules (30+)
│   ├── antigravity_plugin/         # Antigravity plugin
│   ├── monitor_server/             # Monitor server
│   └── dive-context/               # Dive Context (NEW)
│
├── V15.2 Components
│   ├── (integrated into .shared/)
│
├── V14.4 Components
│   ├── (all in .shared/vibe-coder-v13/)
│
├── Skills & Configuration
│   ├── .agent/skills/              # 61+ skills
│   ├── .vibe/                      # Reports & artifacts
│   └── configs/                    # Configuration files
│
└── Frontend
    ├── ui/                         # React frontend
    └── monitor_server/app/         # FastAPI backend
```

---

## ✨ Key Features

### 1. Unified Architecture
- Single entry point (`divecoder_v15_3.py`)
- Seamless integration of V15, V15.2, V14.4, and Dive Context
- Simplified pipeline from V15.2 applied to V15 Dive Engine

### 2. Complete Feature Set
- **RAG System:** Semantic search with reranking
- **Hybrid Search:** FTS + Vector + Pointer search
- **Quality Governance:** SARIF export, Claims ledger
- **Graph Analysis:** Dependency analysis, impact calculation
- **Project Builder:** NextJS, NestJS, Expo scaffolds
- **61 Professional Skills:** Deep domain knowledge
- **45+ CLI Commands:** Complete automation suite

### 3. Advanced Orchestration
- **Dive Engine:** Central orchestrator with thinking engine
- **DAG Engine:** Complex workflow execution
- **Multi-agent Debate:** Advanced reasoning
- **Antigravity Plugin:** MCP + HTTP integration

### 4. Enterprise Monitoring
- **Real-time Observability:** SSE streaming
- **Robust Event System:** Buffer, retry, health check
- **Provider Optimization:** Cost/speed/quality trade-offs
- **Faithfulness Checking:** Response validation

### 5. Documentation Intelligence
- **Dive Context:** 100+ popular libraries
- **MCP Tools:** Standardized documentation access
- **Auto-discovery:** Suggest relevant skills
- **Offline Mode:** 24-hour cache

---

## 🔐 Security Features

- **Prompt Injection Detection:** LLM-based validation
- **Rate Limiting:** Tiered access control
- **Content Filtering:** Safe-by-default validation
- **Claims Ledger:** Audit trail for all operations
- **Evidence Packing:** Reproducible results

---

## 📈 Performance Metrics

| Metric | V14.4 | V15 | V15.2 | V15.3 |
| :--- | :--- | :--- | :--- | :--- |
| **Python Files** | 156 | 645 | ~50 | 650+ |
| **CLI Commands** | 41 | 40 | ~8 | 45+ |
| **Modules** | 20 | 30 | ~5 | 30+ |
| **Skills** | 61 | 61 | 0 | 61+ |
| **Total Size** | ~500MB | ~600MB | ~100MB | ~700MB |
| **Production Ready** | ✅ | ✅ | ⚠️ | ✅✅ |

---

## 🚀 Deployment Options

### 1. Local Development
```bash
python divecoder_v15_3.py status
```

### 2. Docker
```bash
docker build -t dive-coder-v15-3 .
docker run -p 8787:8787 dive-coder-v15-3
```

### 3. Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

### 4. MCP Server (Cursor IDE)
```json
{
  "mcpServers": {
    "dive-coder-v15-3": {
      "command": "python",
      "args": ["divecoder_v15_3.py"],
      "env": {
        "GITHUB_TOKEN": "your_token"
      }
    }
  }
}
```

---

## 📚 Documentation

- **Architecture:** See `ARCHITECTURE.md` in each component
- **API Reference:** See docstrings in `divecoder_v15_3.py`
- **Dive Context:** See `dive-context/README.md`
- **Skills:** See `.agent/skills/` directory
- **Examples:** See `examples/` directory

---

## 🔄 Upgrade Path

### From V14.4
1. Backup your data
2. Extract V15.3
3. Copy your custom skills to `.agent/skills/`
4. Run `python divecoder_v15_3.py skills-reindex`
5. Enjoy enhanced monitoring and Dive Context!

### From V15.2
1. Extract V15.3
2. Copy your configurations
3. Run `python divecoder_v15_3.py status`
4. All V14.4 features are now available!

---

## 🤝 Contributing

To extend Dive Coder V15.3:

1. **Add Skills:** Edit `.agent/skills/` and run `skills-reindex`
2. **Add Commands:** Edit `divecoder_v15_3.py` and extend CLI
3. **Add Modules:** Create new module in `.shared/vibe-coder-v13/`
4. **Improve Dive Context:** Edit `dive-context/src/lib/registry.ts`

---

## 📞 Support

- **Issues:** Check existing issues or create new one
- **Documentation:** See `.agent/skills/` for detailed guides
- **Examples:** See `examples/` directory
- **Community:** Contribute improvements via PR

---

## 📝 License

Same as Dive Coder - MIT License

---

## 🎉 Changelog

### V15.3 (January 30, 2026)
- ✅ Integrated V15 (Dive Engine, Antigravity, MCP)
- ✅ Integrated V15.2 (Monitoring, Event System, Optimization)
- ✅ Integrated V14.4 (RAG, Governance, Graph, Builder, 61 Skills)
- ✅ Integrated Dive Context (Documentation Server, 100+ Libraries)
- ✅ Created unified entry point (`divecoder_v15_3.py`)
- ✅ Extended CLI to 45+ commands
- ✅ Added comprehensive documentation
- ✅ Production-ready release

---

**Dive Coder V15.3 - The Best of All Worlds 🚀**
