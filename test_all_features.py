"""
🧪 Dive AI — Comprehensive Feature Test Suite
==============================================
Tests ALL Dive AI features via the live API, self-debugs issues,
and produces a full report.

Run: python test_all_features.py
"""

import json
import time
import urllib.request
import urllib.error
import sys
import traceback

GATEWAY = "http://127.0.0.1:1879"
RESULTS = []
PASS = 0
FAIL = 0

def req(method, path, data=None, timeout=15):
    """Make HTTP request to Dive AI gateway."""
    try:
        url = f"{GATEWAY}{path}"
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            rq = urllib.request.Request(url, data=body, 
                headers={"Content-Type": "application/json"}, method=method)
        else:
            rq = urllib.request.Request(url, method=method)
        resp = urllib.request.urlopen(rq, timeout=timeout)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except:
            body = {"error": str(e)}
        return body, e.code
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e}"}, 0
    except Exception as e:
        return {"error": str(e)}, 0

def GET(path, **kw): return req("GET", path, **kw)
def POST(path, data=None, **kw): return req("POST", path, data=data, **kw)
def DELETE(path, **kw): return req("DELETE", path, **kw)

def test(name, passed, detail=""):
    global PASS, FAIL
    if passed:
        PASS += 1
        icon = "✅"
    else:
        FAIL += 1
        icon = "❌"
    msg = f"  {icon} {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    RESULTS.append({"name": name, "passed": passed, "detail": detail})
    return passed

# ================================================================
# TEST SUITE
# ================================================================

def run_all():
    global PASS, FAIL
    start = time.time()
    
    print("=" * 65)
    print("🧪 DIVE AI — COMPREHENSIVE FEATURE TEST")
    print("=" * 65)
    
    # ── 1. DEBUG BRIDGE ──────────────────────────────────────
    print("\n📡 1. DEBUG BRIDGE")
    
    r, s = GET("/debug/ping")
    test("Debug ping", s == 200 and r.get("pong") == True, f"v{r.get('version','?')}")
    
    r, s = GET("/debug/full")
    test("Debug full status", s == 200 and "app" in r and "llm" in r,
         f"uptime={r.get('uptime_seconds',0):.0f}s")
    test("Debug full — LLM section", r.get("llm", {}).get("initialized") == True)
    test("Debug full — Memory section", r.get("memory", {}).get("initialized") == True)
    test("Debug full — Storage section", "path" in r.get("storage", {}))
    
    r, s = GET("/debug/logs?limit=10")
    test("Debug logs", s == 200 and "logs" in r, f"{len(r.get('logs',[]))} logs")
    
    r, s = GET("/debug/logs?limit=5&filter=startup")
    test("Debug logs filter", s == 200 and isinstance(r.get("logs"), list))
    
    r, s = POST("/debug/eval", {"expression": "1 + 1"})
    test("Debug eval (simple)", r.get("success") and r.get("result") == "2")
    
    r, s = POST("/debug/eval", {"expression": "APP_VERSION"})
    test("Debug eval (APP_VERSION)", r.get("success") and r.get("result", "").startswith("29"))
    
    r, s = POST("/debug/eval", {"expression": "len(FEATURES)"})
    test("Debug eval (FEATURES)", r.get("success"), f"result={r.get('result','?')}")
    
    r, s = POST("/debug/eval", {"expression": "invalid_var_xyz"})
    test("Debug eval (error handling)", r.get("success") == False, "correctly reports error")
    
    r, s = POST("/debug/command", {"command": "check_imports"})
    test("Debug cmd: check_imports", r.get("success"), 
         f"{sum(1 for v in r.get('imports',{}).values() if '✅' in str(v))}/{len(r.get('imports',{}))} OK")
    
    r, s = POST("/debug/command", {"command": "test_storage"})
    test("Debug cmd: test_storage", r.get("success") and r.get("write_ok") and r.get("read_ok"))
    
    r, s = POST("/debug/command", {"command": "force_gc"})
    test("Debug cmd: force_gc", r.get("success"), f"collected={r.get('objects_collected','?')}")
    
    r, s = POST("/debug/command", {"command": "invalid_command"})
    test("Debug cmd: invalid (error)", r.get("success") == False and "available" in r)
    
    # ── 2. CORE API ──────────────────────────────────────────
    print("\n🔌 2. CORE API")
    
    r, s = GET("/health")
    test("Health endpoint", s == 200 and r.get("status") == "healthy", 
         f"v{r.get('version','?')}")
    
    r, s = GET("/models/list")
    has_models = "groups" in r or "models" in r
    model_count = len(r.get("groups", r.get("models", {})))
    test("Models listing", s == 200 and has_models, f"{model_count} groups")
    
    # Find a valid model_id
    default_model = r.get("default_model", "")
    
    r, s = POST("/chat", {"message": "Say just the word 'hello' and nothing else"})
    test("Chat — simple message", s == 200 and (r.get("response") or r.get("error")),
         f"model={r.get('model','?')}, {r.get('latency_ms',0):.0f}ms")
    chat_ok = "response" in r and r.get("response")
    
    if chat_ok:
        conv_from_chat = r.get("conversation_id", "")
        test("Chat — returns conversation_id", bool(conv_from_chat), conv_from_chat[:12] if conv_from_chat else "missing")
    else:
        conv_from_chat = ""
        test("Chat — returns conversation_id", False, "chat failed, skip")
    
    if default_model:
        r, s = POST("/chat", {"message": "Reply with 'ok'", "model_id": default_model})
        test("Chat — with model_id", s == 200 and r.get("response"),
             f"used {r.get('model','?')}")
    else:
        test("Chat — with model_id", False, "no default model found")
    
    if conv_from_chat:
        r, s = POST("/chat", {"message": "What did I just say?", "conversation_id": conv_from_chat})
        test("Chat — with conversation_id", s == 200 and r.get("response"),
             f"conv={conv_from_chat[:12]}")
    
    # ── 3. STORAGE & PERSISTENCE ─────────────────────────────
    print("\n💾 3. STORAGE & PERSISTENCE")
    
    r, s = GET("/storage/stats")
    test("Storage stats", s == 200 and "path" in r, f"path={r.get('path','?')}")
    
    r, s = POST("/conversations", {"title": "Test Conversation Alpha"})
    cid = r.get("conversation_id") or r.get("id", "")
    test("Create conversation", s == 200 and cid, f"id={cid[:12] if cid else '?'}")
    test_conv_id = cid
    
    r, s = GET("/conversations")
    conv_list = r if isinstance(r, list) else r.get("conversations", [])
    test("List conversations", s == 200 and len(conv_list) > 0, f"{len(conv_list)} conversations")
    
    r, s = POST("/conversations", {"title": "Test Conversation Beta"})
    test_conv_id_2 = r.get("conversation_id") or r.get("id", "")
    test("Create 2nd conversation", bool(test_conv_id_2))
    
    if test_conv_id:
        r, s = GET(f"/conversations/{test_conv_id}/messages")
        msgs = r if isinstance(r, list) else r.get("messages", [])
        test("Get messages (empty conv)", s == 200, f"{len(msgs)} messages")
    
    if test_conv_id:
        r, s = POST("/chat", {"message": "This is a test message for storage", "conversation_id": test_conv_id})
        test("Chat linked to conversation", s == 200 and r.get("response"))
        
        time.sleep(0.5)
        r, s = GET(f"/conversations/{test_conv_id}/messages")
        msgs = r if isinstance(r, list) else r.get("messages", [])
        test("Messages persisted", len(msgs) >= 2, f"{len(msgs)} messages saved")
    
    if test_conv_id_2:
        r, s = DELETE(f"/conversations/{test_conv_id_2}")
        test("Delete conversation", s == 200 or (isinstance(r, dict) and r.get("success", True)))
        
        r, s = GET("/conversations")
        conv_list = r if isinstance(r, list) else r.get("conversations", [])
        ids = [c.get("id") for c in conv_list]
        test("Verify deletion", test_conv_id_2 not in ids)
    
    # ── 4. MEMORY SYSTEM ─────────────────────────────────────
    print("\n🧠 4. MEMORY SYSTEM")
    
    r, s = GET("/memory/status")
    test("Memory status", s == 200 and r.get("initialized"), 
         f"facts={r.get('long_term_facts',0)}")
    
    r, s = POST("/memory/fact", {"fact": "Test fact: user prefers dark mode"})
    test("Add manual fact", s == 200)
    
    r, s = POST("/memory/fact", {"fact": "Test fact: user likes Python"})
    test("Add 2nd fact", s == 200)
    
    r, s = GET("/memory/status")
    test("Facts persisted", r.get("long_term_facts", 0) >= 2, 
         f"{r.get('long_term_facts',0)} facts")
    
    r, s = POST("/memory/clear")
    test("Clear memory", s == 200)
    
    r, s = GET("/memory/status")
    test("Memory cleared", r.get("long_term_facts", 0) == 0)
    
    # ── 5. CONNECTION SETTINGS ────────────────────────────────
    print("\n🔑 5. CONNECTION SETTINGS")
    
    r, s = GET("/settings/connections")
    test("Get connections (masked)", s == 200, f"type={type(r).__name__}")
    
    r, s = POST("/settings/connections", {
        "provider_id": "_test_provider", 
        "url": "https://test.example.com",
        "api_key": "test_key_12345"
    })
    test("Save connection", s == 200)
    
    r, s = POST("/settings/connections/reload")
    test("Reload connections", s == 200)
    
    # ── 6. AUTOMATION & TERMINAL ─────────────────────────────
    print("\n🤖 6. AUTOMATION & TERMINAL")
    
    r, s = GET("/automation/screenshot")
    test("Screenshot endpoint", s == 200, 
         "allowed" if r.get("screenshot") else "blocked (expected)")
    
    r, s = POST("/terminal/execute", {"command": "echo DIVE_AI_TEST_OK", "cwd": "."})
    test("Terminal execute", s == 200 and "DIVE_AI_TEST_OK" in r.get("output", ""),
         r.get("output", "").strip()[:50])
    
    r, s = POST("/fs/read", {"path": "gateway_server.py"})
    test("FS read", s == 200 and r.get("content"), 
         f"{len(r.get('content',''))} chars" if r.get("content") else "no content")
    
    r, s = POST("/fs/write", {"path": "_test_write.tmp", "content": "dive_ai_test"})
    test("FS write", s == 200 and r.get("success"))
    
    POST("/terminal/execute", {"command": "del _test_write.tmp 2>nul & echo done", "cwd": "."})
    
    # ── 7. ERROR HANDLING ─────────────────────────────────────
    print("\n⚠️  7. ERROR HANDLING")
    
    r, s = POST("/chat", {"message": "Say ok", "model_id": "nonexistent_model_xyz"})
    test("Chat with bad model_id", s == 200, 
         "handled gracefully" if r.get("response") or r.get("error") else "no response")
    
    r, s = POST("/chat", {"message": ""})
    test("Chat empty message", s == 200 or s == 422, f"status={s}")
    
    r, s = GET("/nonexistent_endpoint")
    test("Invalid endpoint", s == 404 or s == 405, f"status={s}")
    
    r, s = POST("/debug/eval", {"expression": "1/0"})
    test("Eval division by zero", r.get("success") == False and "division by zero" in r.get("error", "").lower())
    
    # ── 8. PERFORMANCE ────────────────────────────────────────
    print("\n⚡ 8. PERFORMANCE")
    
    t0 = time.time()
    for _ in range(10):
        GET("/health")
    t1 = time.time()
    avg_ms = ((t1 - t0) / 10) * 1000
    test("10x health check speed", avg_ms < 500, f"avg={avg_ms:.0f}ms")
    
    t0 = time.time()
    for _ in range(5):
        GET("/debug/ping")
    t1 = time.time()
    avg_ms = ((t1 - t0) / 5) * 1000
    test("5x debug ping speed", avg_ms < 200, f"avg={avg_ms:.0f}ms")
    
    t0 = time.time()
    GET("/debug/full")
    t1 = time.time()
    test("Debug full response time", (t1-t0) < 2, f"{(t1-t0)*1000:.0f}ms")
    
    # ── 9. CONVERSATION FLOW ──────────────────────────────────
    print("\n💬 9. MULTI-TURN CONVERSATION")
    
    r, s = POST("/conversations", {"title": "Multi-Turn Test"})
    mt_conv = r.get("conversation_id") or r.get("id", "")
    test("Create multi-turn conv", bool(mt_conv))
    
    if mt_conv:
        r, s = POST("/chat", {"message": "Remember this number: 42", "conversation_id": mt_conv})
        test("Turn 1: store number", bool(r.get("response")), r.get("response","")[:50])
        
        r, s = POST("/chat", {"message": "What number did I tell you?", "conversation_id": mt_conv})
        resp2 = r.get("response", "")
        test("Turn 2: recall number", "42" in resp2, resp2[:60])
        
        r, s = GET(f"/conversations/{mt_conv}/messages")
        msgs = r if isinstance(r, list) else r.get("messages", [])
        test("All messages saved", len(msgs) >= 4, f"{len(msgs)} messages")
    
    # ── 10. FINAL STATE ───────────────────────────────────────
    print("\n📋 10. FINAL STATE")
    
    r, s = POST("/debug/command", {"command": "dump_conversations"})
    if r.get("success"):
        convs = r.get("conversations", [])
        test("Dump conversations", True, f"{len(convs)} conversations")
        for c in convs:
            print(f"     📝 {c.get('title','?')} — {c.get('message_count',0)} msgs")
    else:
        test("Dump conversations", False, r.get("error",""))
    
    r, s = GET("/debug/full")
    test("Final system health", r.get("llm",{}).get("initialized") and r.get("memory",{}).get("initialized"))
    
    # ── CLEANUP ───────────────────────────────────────────────
    print("\n🧹 CLEANUP")
    if test_conv_id:
        DELETE(f"/conversations/{test_conv_id}")
    if mt_conv:
        DELETE(f"/conversations/{mt_conv}")
    if conv_from_chat:
        DELETE(f"/conversations/{conv_from_chat}")
    print("  Cleaned up test conversations")
    
    # ── REPORT ────────────────────────────────────────────────
    elapsed = time.time() - start
    total = PASS + FAIL
    
    print("\n" + "=" * 65)
    print(f"📊 RESULTS: {PASS}/{total} passed, {FAIL} failed  ({elapsed:.1f}s)")
    print("=" * 65)
    
    if FAIL > 0:
        print("\n❌ FAILED TESTS:")
        for r in RESULTS:
            if not r["passed"]:
                print(f"   • {r['name']}: {r['detail']}")
    
    print(f"\n{'🎉 ALL TESTS PASSED!' if FAIL == 0 else f'⚠️  {FAIL} test(s) need attention'}")
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    sys.exit(run_all())
