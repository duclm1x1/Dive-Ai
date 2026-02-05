# Dive Coder V15.3 - Installation Guide

## Prerequisites

- Python 3.9+
- Node.js 18+ (for Dive Context)
- pnpm or npm (for Dive Context)
- Git

## Step 1: Extract V15.3

```bash
tar -xzf Dive_Coder_V15_3.tar.gz
cd dive-coder-v15-3
```

## Step 2: Install Python Dependencies

```bash
# Install main dependencies
pip install -r requirements-v15-3.txt

# Or install specific components
pip install fastapi uvicorn  # V15 components
pip install sentence-transformers langchain  # V14.4 RAG
pip install networkx  # V14.4 Graph
pip install semgrep  # V14.4 Governance
```

## Step 3: Install Dive Context

```bash
cd dive-context
pnpm install
pnpm build
cd ..
```

## Step 4: Configure Environment

Create `.env` file:

```bash
# LLM Providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# GitHub (for Dive Context)
export GITHUB_TOKEN="ghp_..."

# Monitoring
export MONITOR_URL="http://localhost:8787"

# Dive Context
export DIVE_CONTEXT_PORT=3000
```

## Step 5: Verify Installation

```bash
# Check status
python divecoder_v15_3.py status

# Should output:
# {
#   "version": "15.3",
#   "codename": "Best of All",
#   "components": {
#     "v15": {...},
#     "v152": {...},
#     "v144": {...},
#     "dive_context": true
#   }
# }
```

## Step 6: Start Services

### Terminal 1: Monitor Server

```bash
cd monitor_server
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787
```

### Terminal 2: Dive Context MCP Server

```bash
cd dive-context
node dist/index-github.js
```

### Terminal 3: Use Dive Coder

```bash
python divecoder_v15_3.py status
python divecoder_v15_3.py process --input "Review this code"
```

## Optional: Frontend UI

```bash
cd ui
npm install
npm start
```

Open http://localhost:3000 in your browser.

## Troubleshooting

### Issue: Python version mismatch

```bash
# Use Python 3.9+
python3.9 -m pip install -r requirements-v15-3.txt
```

### Issue: pnpm not found

```bash
npm install -g pnpm
```

### Issue: Port already in use

```bash
# Change port in environment
export MONITOR_URL="http://localhost:8788"
```

### Issue: Missing dependencies

```bash
# Install system dependencies
sudo apt-get install graphviz  # For graph visualization
```

## Next Steps

1. Read `README_V15_3.md` for usage guide
2. Explore `.agent/skills/` for available skills
3. Check `examples/` for sample workflows
4. Review `dive-context/README.md` for documentation server

---

**Dive Coder V15.3 - Ready to use! 🚀**
