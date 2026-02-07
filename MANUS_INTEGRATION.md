# Dive AI V28 - Manus Integration Guide

## Overview

This guide explains how Manus (or any AI agent) should use Dive AI to save tokens and credits. Instead of processing everything internally, Manus delegates heavy tasks to Dive AI via CLI or HTTP API.

---

## Principle: Delegate to Save

| Task Type | Without Dive AI | With Dive AI | Savings |
|-----------|----------------|--------------|---------|
| Simple Q&A | Manus uses own tokens | `dive ask` (nano model) | 90%+ |
| Code generation | Manus generates | `dive code` (mini model) | 70%+ |
| Code review | Manus reads + analyzes | `dive code --action review` | 80%+ |
| Search codebase | Manus reads files | `dive search --scope codebase` | 95%+ |
| Remember context | Manus re-reads files | `dive memory --action recall` | 99%+ |
| Complex planning | Manus plans internally | `dive orchestrate` | 60%+ |

---

## CLI Usage (Recommended)

### 1. Ask Questions

```bash
# Simple question (auto-routes to cheapest model)
python3 /path/to/dive ask "What is the best way to handle errors in Python?"

# With project context (uses stored memory)
python3 /path/to/dive ask "Why is the API returning 500?" --project myapp
```

### 2. Code Tasks

```bash
# Generate code
python3 /path/to/dive code --task "Create a FastAPI middleware for rate limiting" --lang python

# Review code
python3 /path/to/dive code --action review --file /path/to/app.py

# Debug code
python3 /path/to/dive code --action debug --file /path/to/broken.py

# Generate tests
python3 /path/to/dive code --action test --file /path/to/module.py

# Save output to file
python3 /path/to/dive code --task "Create auth module" --output /path/to/auth.py
```

### 3. Search

```bash
# Search codebase
python3 /path/to/dive search --query "database connection" --scope codebase --path /path/to/project

# Search memory
python3 /path/to/dive search --query "JWT" --scope memory

# Search everything
python3 /path/to/dive search --query "authentication" --scope all
```

### 4. Memory (Critical for Context Persistence)

```bash
# Store knowledge (persists across sessions!)
python3 /path/to/dive memory --action store --project myapp --content "Database is PostgreSQL on port 5432"
python3 /path/to/dive memory --action store --project myapp --content "Auth uses JWT with RS256" --category decision

# Recall all memory for a project
python3 /path/to/dive memory --action recall --project myapp

# Search memory
python3 /path/to/dive memory --action search --project myapp --query "database"

# Add changelog entry
python3 /path/to/dive memory --action changelog --project myapp --content "Added rate limiting middleware"

# List all projects
python3 /path/to/dive memory --action list --project _all
```

### 5. Orchestrate Complex Tasks

```bash
# Get a step-by-step plan for complex tasks
python3 /path/to/dive orchestrate --task "Migrate the app from Express to FastAPI" --project myapp
```

### 6. Computer Use

```bash
# GUI automation (requires UI-TARS)
python3 /path/to/dive computer --task "Open the browser and navigate to github.com"

# Browser automation
python3 /path/to/dive computer --task "Fill in the login form with test credentials" --mode browser
```

---

## HTTP API Usage (Alternative)

Start the server first:

```bash
python3 /path/to/dive serve --port 8000 &
```

Then call via curl or Python requests:

```python
import requests

BASE = "http://localhost:8000"

# Ask
r = requests.post(f"{BASE}/api/ask", json={"question": "How to fix this bug?", "project": "myapp"})
answer = r.json()["answer"]

# Code
r = requests.post(f"{BASE}/api/code", json={"task": "Create auth module", "language": "python"})
code = r.json()["code"]

# Memory
requests.post(f"{BASE}/api/memory", json={"action": "store", "project": "myapp", "content": "Uses Redis for caching"})
r = requests.post(f"{BASE}/api/memory", json={"action": "recall", "project": "myapp"})
memories = r.json()["memories"]
```

---

## Manus Workflow Example

Here is how Manus should use Dive AI in a typical coding task:

```
1. User asks: "Fix the bug in my FastAPI app"

2. Manus stores context:
   $ dive memory --action store --project userapp --content "User reported bug in FastAPI app"

3. Manus searches codebase:
   $ dive search --query "error" --scope codebase --path /path/to/userapp

4. Manus asks Dive AI to debug:
   $ dive code --action debug --file /path/to/userapp/main.py

5. Manus asks Dive AI to fix:
   $ dive code --task "Fix the authentication bug found in line 42" --output /path/to/userapp/main.py

6. Manus stores the fix in memory:
   $ dive memory --action changelog --project userapp --content "Fixed auth bug in main.py line 42"

7. Done! Manus used minimal tokens, Dive AI did the heavy lifting.
```

---

## Output Format

All CLI commands output JSON for easy parsing:

```json
{
  "status": "success",
  "command": "ask",
  "answer": "...",
  "model": "gpt-4.1-nano",
  "usage": {"prompt_tokens": 58, "completion_tokens": 42, "total_tokens": 100},
  "tier": "fast",
  "timestamp": "2026-02-07T00:00:00"
}
```

Manus can parse this JSON to extract the answer, check status, and monitor token usage.

---

## Best Practices

1. **Always store context in memory** - Use `dive memory --action store` to persist project knowledge
2. **Use search before asking** - `dive search` is free (no LLM tokens), use it first
3. **Let Dive AI choose the model** - Don't override `--model` unless necessary
4. **Use orchestrate for complex tasks** - Get a plan first, then execute steps
5. **Use changelog for tracking** - `dive memory --action changelog` keeps a record
6. **Start API server for frequent calls** - `dive serve` avoids CLI startup overhead
