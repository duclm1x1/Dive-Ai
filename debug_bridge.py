"""
🔗 Antigravity ↔ Dive AI Debug Bridge
======================================
Run from Antigravity to inspect, diagnose, and control Dive AI's backend.

Usage:
    python debug_bridge.py                    # Full system check
    python debug_bridge.py ping               # Quick alive check
    python debug_bridge.py logs               # View recent logs
    python debug_bridge.py logs error         # Filter logs by keyword
    python debug_bridge.py eval "expression"  # Eval in Dive AI runtime
    python debug_bridge.py cmd restart_llm    # Run a debug command
    python debug_bridge.py cmd check_imports  # Verify imports
    python debug_bridge.py cmd test_storage   # Test storage read/write
"""

import sys
import json
import urllib.request
import urllib.error

GATEWAY_URL = "http://127.0.0.1:1879"

def req_get(path):
    try:
        resp = urllib.request.urlopen(f"{GATEWAY_URL}{path}", timeout=5)
        return json.loads(resp.read())
    except urllib.error.URLError:
        return None
    except Exception as e:
        return {"error": str(e)}

def req_post(path, data):
    try:
        body = json.dumps(data).encode("utf-8")
        rq = urllib.request.Request(
            f"{GATEWAY_URL}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(rq, timeout=10)
        return json.loads(resp.read())
    except urllib.error.URLError:
        return None
    except Exception as e:
        return {"error": str(e)}

def pp(data, indent=2):
    print(json.dumps(data, indent=indent, ensure_ascii=False, default=str))

# ── Commands ──────────────────────────────────────────────────

def cmd_ping():
    r = req_get("/debug/ping")
    if not r:
        print("❌ Dive AI is NOT running (no response from port 1879)")
        return False
    print(f"✅ Dive AI is alive — v{r.get('version','?')} @ {r.get('timestamp','?')}")
    return True

def cmd_full():
    if not cmd_ping():
        return
    print("\n" + "=" * 60)
    print("📊 FULL SYSTEM STATUS")
    print("=" * 60)
    r = req_get("/debug/full")
    if not r:
        print("❌ Failed to get status")
        return

    # App
    app_info = r.get("app", {})
    print(f"\n🤿 {app_info.get('name', '?')} v{app_info.get('version', '?')}")
    uptime = r.get("uptime_seconds", -1)
    if uptime > 0:
        mins = int(uptime // 60)
        secs = int(uptime % 60)
        print(f"⏱  Uptime: {mins}m {secs}s")

    # LLM
    llm = r.get("llm", {})
    print(f"\n🧠 LLM: {'✅ initialized' if llm.get('initialized') else '❌ not initialized'}")
    if llm.get("status"):
        status = llm["status"]
        if isinstance(status, dict):
            for k, v in status.items():
                print(f"   {k}: {v}")

    # Memory
    mem = r.get("memory", {})
    print(f"\n💭 Memory: {'✅ initialized' if mem.get('initialized') else '❌ not initialized'}")
    if mem.get("initialized"):
        print(f"   Short-term: {mem.get('short_term_messages', 0)}/{mem.get('max_short_term', 20)} messages")
        print(f"   Long-term: {mem.get('long_term_facts', 0)} facts, {mem.get('long_term_topics', 0)} topics")

    # Storage
    sto = r.get("storage", {})
    print(f"\n💾 Storage:")
    if "path" in sto:
        print(f"   Path: {sto['path']}")
        print(f"   Used: {sto.get('used_mb', '?')} MB, {sto.get('file_count', '?')} files")
        print(f"   Conversations: {sto.get('conversation_count', '?')}")

    # Automation
    auto = r.get("automation", {})
    print(f"\n🤖 Automation: {'✅ allowed' if auto.get('allowed') else '❌ blocked'}")

    # Errors
    errors = r.get("recent_errors", [])
    if errors:
        print(f"\n⚠️  Recent Errors ({len(errors)}):")
        for err in errors[-5:]:
            print(f"   [{err['time'][:19]}] {err['message'][:100]}")

    print("\n" + "=" * 60)

def cmd_logs(filter_kw=None):
    if not cmd_ping():
        return
    path = "/debug/logs?limit=30"
    if filter_kw:
        path += f"&filter={filter_kw}"
    r = req_get(path)
    if not r:
        print("❌ Failed to get logs")
        return
    logs = r.get("logs", [])
    print(f"\n📜 Logs ({len(logs)} of {r.get('total', '?')}):")
    for log in logs:
        print(f"  [{log['time'][:19]}] {log['message'][:120]}")

def cmd_eval(expression):
    if not cmd_ping():
        return
    r = req_post("/debug/eval", {"expression": expression})
    if not r:
        print("❌ Failed to execute eval")
        return
    if r.get("success"):
        print(f"✅ ({r.get('type','?')}) → {r.get('result','')}")
    else:
        print(f"❌ Error: {r.get('error','')}")

def cmd_command(command):
    if not cmd_ping():
        return
    r = req_post("/debug/command", {"command": command})
    if not r:
        print("❌ Failed to execute command")
        return
    pp(r)

# ── Main ──────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    
    if not args:
        cmd_full()
    elif args[0] == "ping":
        cmd_ping()
    elif args[0] == "logs":
        cmd_logs(args[1] if len(args) > 1 else None)
    elif args[0] == "eval" and len(args) > 1:
        cmd_eval(args[1])
    elif args[0] == "cmd" and len(args) > 1:
        cmd_command(args[1])
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
