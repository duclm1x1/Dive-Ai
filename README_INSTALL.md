# Dive AI V20.4 - Installation Guide

## 🚀 Quick Install (Recommended)

```bash
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai
./install.sh
```

The `install.sh` script will automatically:
- ✅ Setup API keys (interactive)
- ✅ Run first-run setup
- ✅ Test all API connections
- ✅ Run health checks
- ✅ Load memory system
- ✅ Verify installation

**Total time**: ~2-3 minutes

## 📋 What Gets Installed

### 1. API Keys Setup
- OpenAI API key
- V98API key  
- AICoding API key
- Anthropic API key (optional)

### 2. First Run Setup
- Initialize memory database
- Create project structure
- Setup logging
- Verify dependencies

### 3. Connection Tests
- Test OpenAI connection
- Test V98API connection
- Test AICoding connection
- Verify model availability

### 4. Health Checks
- Memory system status
- Orchestrator readiness
- Coder readiness
- Interrupt handler status

### 5. Memory Loading
- Load existing memory files
- Initialize knowledge graph
- Verify memory integrity

## 🎯 After Installation

Start using Dive AI:

```bash
python3 dive_ai_complete_system.py
```

Or use individual components:

```bash
# Smart Orchestrator
python3 core/dive_smart_orchestrator.py

# Smart Coder
python3 core/dive_smart_coder.py

# Memory System
python3 core/dive_memory_3file_complete.py
```

## 📚 Documentation

- `README_V20.4.0.md` - Complete feature guide
- `CHANGELOG.md` - Version history
- `ARCHITECTURE_COMPLETE.md` - System architecture
- `POST_CLONE_INSTRUCTIONS.md` - Manual installation steps

## ⚠️ Troubleshooting

### Installation fails
```bash
# Check Python version (3.11+ recommended)
python3 --version

# Install dependencies manually
pip3 install -r requirements.txt

# Run install again
./install.sh
```

### API tests fail
```bash
# Check API keys in .env
cat .env

# Re-run setup
python3 setup_api_keys.py

# Test again
python3 first_run_llm_test.py
```

### Memory not loading
```bash
# Check memory directory
ls -la memory/

# Verify memory files
find memory -name "*.md"

# Re-run startup
python3 dive_ai_startup.py
```

## 🔗 Links

- **Repository**: https://github.com/duclm1x1/Dive-Ai
- **Issues**: https://github.com/duclm1x1/Dive-Ai/issues
- **Releases**: https://github.com/duclm1x1/Dive-Ai/releases

---

**Dive AI V20.4** - The AI that thinks, adapts, and never forgets! 🚀
