---
name: dive-memory-v3
description: "Persistent memory system for AI agents using Model Context Protocol (MCP). Use when you need to remember context across sessions, recall previous conversations, save decisions for later, search past knowledge with semantic search, build knowledge graphs linking related memories, auto-inject relevant context into prompts, deduplicate stored memories, or sync memory to cloud storage. Essential for agents that need persistent recall of solutions, preferences, and learned patterns."
---

# Dive-Memory v3: MCP-Based Persistent Memory System

Dive-Memory v3 provides long-term persistent memory for AI agents, solving the context-forgetting problem across sessions. Use when an agent needs to remember decisions, recall past solutions, save context, or search previous knowledge.

## Setup Workflow

Follow these steps in order to get the memory system running:

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the MCP Server

```bash
python3 scripts/mcp_server.py
```

### Step 3: Configure MCP Client

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dive-memory": {
      "command": "python3",
      "args": ["<path-to>/skills/dive-memory-v3/scripts/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Step 4: Verify Setup

Test with a memory add and search:

```python
from dive_memory import DiveMemory

memory = DiveMemory()
memory.add(content="Test memory", section="test", tags=["setup"])
results = memory.search(query="Test memory")
assert len(results) > 0  # Setup confirmed
```

## MCP Tools

When connected as an MCP server, these tools are available:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `memory_add` | Store a new memory with section, tags, importance | Save a solution or decision |
| `memory_search` | Semantic + keyword hybrid search | Find past solutions for a problem |
| `memory_update` | Update existing memory content or metadata | Refine a stored solution |
| `memory_delete` | Remove a memory by ID | Clean up outdated entries |
| `memory_graph` | Get knowledge graph of linked memories | Explore related concepts |
| `memory_related` | Find memories related to a given ID | Discover connections |
| `memory_stats` | Get memory count, section breakdown, usage stats | Monitor memory health |

## Core Usage (Python API)

### Store a Memory

```python
memory.add(
    content="Fixed JWT auth bug with refresh token rotation",
    section="solutions",
    subsection="authentication",
    tags=["jwt", "security", "bug-fix"],
    importance=8
)
```

### Search Memories

```python
results = memory.search(
    query="How to fix JWT authentication issues?",
    section="solutions",
    top_k=5
)
```

### Build Knowledge Graph

```python
related = memory.get_related(memory_id, max_depth=2)
graph = memory.get_graph(section="solutions")
```

### Auto-Inject Context

```python
memory.enable_context_injection()
context = memory.get_context_for_task("Implement user authentication")
```

## Memory Organization

Memories are organized by section and subsection: `solutions/authentication`, `decisions/database`, `research/ai-models`, `preferences/`, etc. Each memory has tags (list), importance (1–10), and metadata (dict). See `references/config.json` for search weights, deduplication thresholds, and graph settings.

## Key Configuration

Edit `references/config.json` to control:

- **Storage**: SQLite (default) or PostgreSQL backend
- **Embeddings**: OpenAI `text-embedding-3-small` with local fallback
- **Search**: Hybrid strategy (0.7 semantic / 0.3 keyword weight)
- **Deduplication**: 0.95 similarity threshold, auto-merge off by default
- **Context injection**: Max 5 memories, 0.5 min relevance

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/mcp_server.py` | MCP server entry point |
| `scripts/memory_cli.py` | Command-line interface for memory operations |
| `scripts/dive_memory.py` | Core memory engine |

## References

- Full Python API with all method signatures: `references/api_reference.md`
- All configuration options with defaults: `references/config.json`
