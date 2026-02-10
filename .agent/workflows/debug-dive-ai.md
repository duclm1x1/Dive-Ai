---
description: Debug Dive AI from Antigravity - Two-way debug bridge
---

# Dive AI Debug Bridge

Use this workflow to inspect, diagnose, and control Dive AI's backend from Antigravity.

## Quick Check
// turbo
1. Run the debug bridge ping to check if Dive AI is alive:
```
python D:\Antigravity\Dive AI\debug_bridge.py ping
```

## Full System Status
// turbo
2. Get comprehensive system status (LLM, memory, storage, errors):
```
python D:\Antigravity\Dive AI\debug_bridge.py
```

## View Recent Logs
// turbo
3. View recent backend logs:
```
python D:\Antigravity\Dive AI\debug_bridge.py logs
```

## Filter Logs by Keyword
// turbo
4. Filter logs (e.g., errors only):
```
python D:\Antigravity\Dive AI\debug_bridge.py logs error
```

## Evaluate Expression in Dive AI Runtime
5. Evaluate a Python expression inside Dive AI:
```
python D:\Antigravity\Dive AI\debug_bridge.py eval "memory.get_status()"
```

## Run Debug Commands
6. Run a debug command (restart_llm, clear_memory, dump_conversations, check_imports, test_storage, force_gc):
```
python D:\Antigravity\Dive AI\debug_bridge.py cmd check_imports
```

## Direct HTTP Access (Alternative)
// turbo-all
7. You can also call the debug endpoints directly via curl:
```
curl http://127.0.0.1:1879/debug/ping
curl http://127.0.0.1:1879/debug/full
curl http://127.0.0.1:1879/debug/logs?limit=20
```
