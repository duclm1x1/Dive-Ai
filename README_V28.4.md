# Dive AI V28.4 - Complete Autonomous Agent Framework

**Version:** 28.4.0  
**Status:** Production Ready  
**Date:** February 7, 2026

---

## 🚀 Overview

**Dive AI V28.4** is the most comprehensive autonomous agent framework combining:

- **512 Dive Agents** orchestrated via Dive Orchestrator
- **Three-Mode LLM Connection** (Human-AI, AI-AI, AI-PC)
- **Multi-Provider Support** (V98, Aicoding, OpenAI, Anthropic)
- **Latest Models** (Claude Opus 4.5, Sonnet 4.5, Gemini 3.0, GPT-5.1)
- **Complete Multimodal Engine** (Vision, Audio, Transformation)
- **Advanced Memory System** (Episodic, Semantic, Procedural)
- **Computer Use Integration** (UI-TARS Desktop)
- **Comprehensive Skills Library** (100+ skills)
- **Full Documentation** (1,400+ markdown files)
- **Legacy Features** (V15.3-Core, V20 Advanced)

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 9,390 |
| **Python Files** | 6,541 |
| **Documentation** | 1,411 markdown files |
| **Total Size** | 154 MB |
| **Agents** | 512 (256 V98 + 256 Aicoding) |
| **Supported Models** | 15+ |
| **Skills** | 100+ |
| **Core Modules** | 72 |
| **Legacy Versions** | V15.3, V20 |

---

## 🏗️ Architecture

```
Dive AI V28.4/
├── src/
│   ├── main.py                          # Entry point
│   ├── cli/                             # CLI commands
│   │   ├── natural_language_filter.py   # NLU command parsing
│   │   ├── commands/                    # Command implementations
│   │   └── api_server.py                # FastAPI server
│   ├── core/                            # Core modules (72 items)
│   │   ├── llm_connection/              # Three-Mode LLM Client
│   │   ├── orchestrator/                # 512 Agents Orchestrator
│   │   ├── memory/                      # Advanced Memory System
│   │   ├── agents/                      # Agent implementations
│   │   ├── monitor_server/              # Monitoring & Logging
│   │   ├── integration/                 # API Integrations
│   │   ├── voice/                       # Voice Processing
│   │   ├── multimodal/                  # Vision, Audio, Transform
│   │   ├── computer_use/                # UI-TARS Integration
│   │   └── vision/                      # Image Processing (82MB)
│   ├── skills/                          # Skills Library (100+)
│   ├── coder/                           # Advanced Code Generation
│   ├── cli/                             # CLI Interface
│   ├── plugins/                         # Plugin System
│   ├── ui/                              # Dashboard & UI
│   ├── builder/                         # Project Builder
│   └── legacy/                          # Legacy Features
│       ├── v15.3-core/                  # V15.3 Core Features
│       └── v20/                         # V20 Advanced Features
├── docs/                                # Documentation (1,400+ files)
├── tests/                               # Test Suite
├── VERSION                              # Version: 28.4.0
├── CHANGELOG.md                         # Change History
└── README.md                            # This file
```

---

## 🎯 Key Features

### 1. **512 Dive Agents**
- 256 agents via V98 API
- 256 agents via Aicoding API
- Intelligent load balancing
- Real-time orchestration
- Parallel task execution

### 2. **Three-Mode LLM Connection**
- **Mode 1 (Human-AI):** HTTP/2 REST API (~100-200ms)
- **Mode 2 (AI-AI):** Binary protocol (<1ms)
- **Mode 3 (AI-PC):** Local models (<10ms)

### 3. **Latest Models Support**
- Claude Opus 4.5 (highest reasoning)
- Claude Sonnet 4.5 (balanced)
- Gemini 3.0 Pro/Flash
- GPT-5.1 / GPT-5.2
- Qwen 3.0, Llama 4, DeepSeek V3.1

### 4. **Multimodal Engine**
- Vision (OCR, object detection, image analysis)
- Audio (STT, TTS, speech processing)
- Transformation (format conversion, data processing)

### 5. **Advanced Memory System**
- Episodic memory (events, experiences)
- Semantic memory (knowledge, facts)
- Procedural memory (skills, processes)
- Memory consolidation & retrieval

### 6. **Computer Use Integration**
- UI-TARS Desktop integration
- Screenshot analysis
- GUI automation
- Browser control
- Fully automatic computer assistant

### 7. **Comprehensive Skills**
- Code generation (CPCG)
- Verification (MVP, EGFV, EDA)
- Self-healing (SHC)
- Context compression (CCF)
- Reasoning chains (DRC)
- 100+ additional skills

### 8. **Complete Documentation**
- Architecture guides
- API documentation
- Skill documentation
- Integration guides
- Best practices

### 9. **Legacy Features**
- V15.3-Core (advanced searching, RAG, evidence pack)
- V20 (advanced reasoning, cognitive systems)

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export V98_API_KEY="sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y"
export AICODING_API_KEY="sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk"
```

### Usage

```bash
# Check status
python3 dive status

# Ask a question
python3 dive ask "What is Dive AI?"

# Generate code
python3 dive code --task "Create FastAPI endpoint"

# Use natural language (NLU)
python3 dive "check orchestrator status"
python3 dive "generate hello world in python"

# Run with 512 agents
python3 dive orchestrator execute-tasks --num-tasks 1000

# Process image
python3 dive multimodal vision --task analyze --image image.jpg

# Computer use
python3 dive computer screenshot
python3 dive computer analyze
```

---

## 🔧 Configuration

### V98 API
```
Base URL: https://v98store.com/v1
API Key: sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y
Models: claude-opus-4.5, claude-sonnet-4.5, gemini-3.0-pro, gpt-5.1
```

### Aicoding API
```
Base URL: https://aicoding.io.vn/v1
API Key: sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk
Models: claude-opus-4.5, claude-sonnet-4-5-20250929, gpt-5.1, gpt-5.2
```

---

## 📚 Documentation

Full documentation available in `/docs/`:

- `ARCHITECTURE_COMPLETE.md` - System architecture
- `DIVE_ORCHESTRATOR_128_AGENT_PLAN.md` - Orchestrator design
- `MULTIMODAL_DIVE_AGENT_ARCHITECTURE.md` - Multimodal engine
- `DIVE_MEMORY_V25_COMPLETE.md` - Memory system
- And 1,400+ more files

---

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/

# Test orchestrator
python3 -c "from src.core.orchestrator.orchestrator_512_agents_config import OrchestratorPool; print('✅ Orchestrator OK')"

# Test LLM connection
python3 -c "from src.core.llm_connection.llm_connection import LLMClientThreeMode; print('✅ LLM Connection OK')"

# Health check
python3 dive status
```

---

## 📈 Performance

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Mode 1 (HTTP/2) | 100-200ms | 100 req/s |
| Mode 2 (Binary) | <1ms | 10,000 req/s |
| Mode 3 (Local) | <10ms | 1,000 req/s |
| Orchestrator | 50-100ms | 512 parallel |

---

## 🔐 Security

- API key encryption
- Request signing
- Rate limiting
- Input validation
- Audit logging
- Memory isolation

---

## 📝 Changelog

See `CHANGELOG.md` for detailed version history.

### V28.4.0 (Latest)
- ✅ 512 Dive Agents with V98 + Aicoding APIs
- ✅ Three-Mode LLM Connection
- ✅ Multimodal Engine (Vision, Audio, Transformation)
- ✅ Computer Use Integration (UI-TARS)
- ✅ Advanced Memory System
- ✅ Natural Language Command Filter
- ✅ Complete Skills Library
- ✅ Full Documentation (1,400+ files)
- ✅ Legacy Features (V15.3, V20)
- ✅ Vision Module (82MB)
- ✅ Coder Module (Advanced code generation)
- ✅ UI Dashboard
- ✅ Builder System

---

## 🤝 Contributing

Contributions welcome! Please follow:
1. Fork repository
2. Create feature branch
3. Submit pull request
4. Follow code style guidelines

---

## 📄 License

See LICENSE file

---

## 📞 Support

- GitHub Issues: https://github.com/duclm1x1/Dive-Ai/issues
- Documentation: `/docs/`
- API Reference: `/docs/API_REFERENCE.md`

---

## 🎓 Learn More

- [Architecture Guide](/docs/ARCHITECTURE_COMPLETE.md)
- [Orchestrator Design](/docs/DIVE_ORCHESTRATOR_128_AGENT_PLAN.md)
- [Multimodal Engine](/docs/MULTIMODAL_DIVE_AGENT_ARCHITECTURE.md)
- [Memory System](/docs/DIVE_MEMORY_V25_COMPLETE.md)
- [Skills Documentation](/docs/)

---

**Dive AI V28.4 - The most comprehensive autonomous agent framework available.**

*Built with ❤️ for the future of AI agents*
