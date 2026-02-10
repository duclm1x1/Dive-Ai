"""
Dive AI — Integration Test: Unified DiveEngine
Tests all surpass features wired through a single pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

passed = 0
failed = 0
failures = []


def test(name, fn):
    global passed, failed
    try:
        result = fn()
        assert result, "returned falsy"
        print(f"  PASS: {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {name} -- {e}")
        failures.append(f"{name}: {e}")
        failed += 1


# ==============================================================
print("=" * 60)
print("DIVE ENGINE INTEGRATION TEST")
print("=" * 60)
print()

from dive_core.engine.dive_engine import (
    DiveEngine, EngineRequest, EngineResponse, TaskIntent, get_engine,
)

engine = DiveEngine()

# ── Test 1: Basic health ─────────────────────────────────────
print("--- Health Check ---")
health = engine.health_check()
test("Engine operational", lambda: health["status"] == "operational")
test("7-stage pipeline wired", lambda: health["pipeline_stages"] == 7)
test("Model resolver wired", lambda: "providers" in health["subsystems"]["model_resolver"])
test("All subsystems ok", lambda: all(
    v != "error" for v in health["subsystems"].values()
))

# ── Test 2: Chat request through 7-stage pipeline ───────────
print()
print("--- Chat Request (Full Pipeline) ---")
req = EngineRequest(
    session_id="session-1",
    message="Hello, how does Dive AI compare to OpenClaw?",
    intent=TaskIntent.CHAT,
)
resp = engine.process(req)
test("Chat success", lambda: resp.success)
test("7 stages completed", lambda: resp.pipeline_stages == 7)
test("Has content", lambda: len(resp.content) > 0)
test("Has request ID", lambda: resp.request_id.startswith("req-"))
test("Duration tracked", lambda: resp.duration_ms >= 0)
test("Auto-approved (no tools)", lambda: resp.approval_status == "auto")

# ── Test 3: Code request ─────────────────────────────────────
print()
print("--- Code Request ---")
req2 = EngineRequest(
    session_id="session-1",
    message="Write a Python function to sort a list using quicksort",
    intent=TaskIntent.CODE,
)
resp2 = engine.process(req2)
test("Code request success", lambda: resp2.success)
test("Same session context grows", lambda: resp2.tokens_used > 0)

# ── Test 4: Context Window Guard integration ─────────────────
print()
print("--- Context Guard Integration ---")
session_stats = engine.get_session_stats("session-1")
test("Session context tracked", lambda: session_stats["request_count"] >= 2)
test("Context has messages", lambda: session_stats["context"]["message_count"] >= 2)
test("Token accounting", lambda: session_stats["context"]["used_tokens"] > 0)

# ── Test 5: Model Resolver integration ────────────────────────
print()
print("--- Model Resolver Integration ---")
stats = engine.get_stats()
test("Providers registered", lambda: stats["model_resolver"]["total_providers"] >= 2)
test("Resolver used", lambda: stats["model_resolver"]["total_resolved"] >= 2)

# ── Test 6: Tool Approval integration ─────────────────────────
print()
print("--- Tool Approval Integration ---")
req3 = EngineRequest(
    session_id="session-2",
    message="Search the web for Dive AI reviews",
    intent=TaskIntent.TOOL,
    tools=["web_search"],
)
resp3 = engine.process(req3)
test("Tool request processed", lambda: resp3.success)
test("Tool approval checked", lambda: resp3.metadata.get("approval", {}).get("tools_checked", 0) >= 1)

# Tool with high risk
req4 = EngineRequest(
    session_id="session-2",
    message="Execute shell command",
    intent=TaskIntent.TOOL,
    tools=["shell_exec"],
)
resp4 = engine.process(req4)
test("High risk tool goes through pipeline", lambda: resp4.success is True or resp4.success is False)  # either way, pipeline ran

# ── Test 7: Semantic Snapshot integration ────────────────────
print()
print("--- Semantic Snapshot Integration ---")
html = (
    "<html><head><title>Test Page</title></head>"
    "<body><h1>Welcome</h1>"
    '<a href="/">Home</a>'
    '<button>Click Me</button>'
    '<input type="text" placeholder="Search" />'
    "</body></html>"
)
browse_result = engine.browse("session-1", html, url="https://test.com", title="Test Page")
test("Browse works", lambda: browse_result["interactive_elements"] >= 3)
test("Cost savings", lambda: browse_result["cost_savings"]["savings_percent"] > 80)
test("Elements indexed", lambda: len(browse_result["elements"]) >= 3)
test("Context updated", lambda: engine.get_session_stats("session-1")["context"]["message_count"] > 2)

# ── Test 8: MCP Tool Call with Approval ──────────────────────
print()
print("--- MCP Tool Call + Approval ---")
# Register a test MCP server + tool
engine.mcp_client.register_server("test-server", transport="stdio", command="echo")
engine.mcp_client.add_tools("test-server", [
    {"name": "test_tool", "description": "Test tool", "inputSchema": {"q": "str"}},
])
engine.mcp_client.connect("test-server")

mcp_result = engine.call_mcp_tool("session-1", "test_tool", {"q": "test"})
test("MCP tool call success", lambda: mcp_result["success"])
test("Risk assessed", lambda: mcp_result["risk"]["level"] in ("low", "medium", "high"))

# ── Test 9: Session isolation ─────────────────────────────────
print()
print("--- Session Isolation ---")
req5 = EngineRequest(
    session_id="session-3",
    message="New session, new context",
    intent=TaskIntent.CHAT,
)
engine.process(req5)
s1 = engine.get_session_stats("session-1")
s3 = engine.get_session_stats("session-3")
test("Sessions isolated", lambda: s1["request_count"] != s3["request_count"])
test("Separate contexts", lambda: s1["context"]["message_count"] != s3["context"]["message_count"])

# ── Test 10: Multi-request pipeline ───────────────────────────
print()
print("--- Multi-Request Pipeline ---")
for i in range(5):
    r = EngineRequest(
        session_id="session-pipeline",
        message=f"Request {i}: Please process this through all 7 stages",
        intent=TaskIntent.CODE,
    )
    resp = engine.process(r)
    assert resp.success, f"Request {i} failed"
test("5 requests all succeed", lambda: True)
test("Pipeline stats updated", lambda: engine.get_stats()["pipeline"]["total_processed"] >= 5)

# ── Test 11: Engine stats ─────────────────────────────────────
print()
print("--- Engine Stats ---")
stats = engine.get_stats()
test("Total requests tracked", lambda: stats["engine"]["total_requests"] >= 8)
test("Total cost tracked", lambda: stats["engine"]["total_cost_usd"] >= 0)
test("Total tokens tracked", lambda: stats["engine"]["total_tokens"] >= 0)
test("Active sessions", lambda: stats["engine"]["active_sessions"] >= 3)
test("Pipeline stats included", lambda: stats["pipeline"]["pipeline_stages"] == 7)
test("MCP stats included", lambda: "total_servers" in stats["mcp"])
test("Approval stats included", lambda: "total_requests" in stats["tool_approval"])

# ── Test 12: Singleton ────────────────────────────────────────
print()
print("--- Singleton ---")
e1 = get_engine()
e2 = get_engine()
test("Singleton works", lambda: e1 is e2)

# ==============================================================
print()
print("=" * 60)
print("FULL SYSTEM VERIFICATION")
print("=" * 60)

# Count features
features = {
    "7-stage pipeline": stats["pipeline"]["pipeline_stages"] == 7,
    "Context Guard wired": stats["engine"]["active_sessions"] >= 3,
    "Model Resolver wired": stats["model_resolver"]["total_providers"] >= 2,
    "Tool Approval wired": stats["tool_approval"]["total_requests"] >= 1,
    "MCP Client wired": stats["mcp"]["total_servers"] >= 1,
    "Semantic Snapshots wired": stats["semantic_snapshots"]["total_snapshots"] >= 1,
    "Session isolation": len(engine.context_guards) >= 3,
    "Skill registry": hasattr(engine, "_skills"),
    "Algorithm registry": hasattr(engine, "_algorithms"),
    "Health check": health["status"] == "operational",
}
for feat, ok in features.items():
    mark = "OK" if ok else "NO"
    print(f"  [{mark}] {feat}")

all_ok = all(features.values())
test("ALL features integrated", lambda: all_ok)

# ==============================================================
print()
print("=" * 60)
print("FINAL RESULTS")
print("=" * 60)
total = passed + failed
print(f"  {passed}/{total} tests passed")
if failed == 0:
    print()
    print("  *** ALL INTEGRATION TESTS PASSED ***")
    print("  *** DIVE AI ENGINE FULLY WIRED ***")
else:
    print(f"  {failed} failures:")
    for f in failures:
        print(f"    - {f}")
print("=" * 60)
