"""
Test Lifecycle Bridge — verify algorithms run regularly.

Tests:
1. Smart routing (user intent → categories + algorithms)
2. Targeted execution (specific algorithms)
3. Full lifecycle (8 stages)
4. Algorithm creation from existing
5. History + stats tracking
"""
import os
import sys
import time
import json

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

from dive_core.engine.lifecycle_bridge import LifecycleBridge, get_lifecycle_bridge


def test_lifecycle_bridge():
    print("=" * 70)
    print("🔧 LIFECYCLE BRIDGE — COMPREHENSIVE TEST")
    print("=" * 70)

    bridge = get_lifecycle_bridge()
    results = {"passed": 0, "failed": 0, "tests": []}

    def run_test(name, fn):
        try:
            result = fn()
            status = "✅ PASS" if result else "❌ FAIL"
            results["passed" if result else "failed"] += 1
            results["tests"].append({"name": name, "pass": bool(result)})
            print(f"  {status}: {name}")
            return result
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({"name": name, "pass": False, "error": str(e)})
            print(f"  ❌ FAIL: {name} — {e}")
            return False

    # ═══════════════════════════════════════════════════════════
    # TEST GROUP 1: Smart Routing
    # ═══════════════════════════════════════════════════════════
    print("\n📡 GROUP 1: Smart Routing")
    print("-" * 40)

    def test_route_coding():
        r = bridge.route("write a Python function to sort a list")
        return "coding" in r.categories and len(r.algorithms) > 0

    def test_route_devops():
        r = bridge.route("deploy my Docker app to AWS cloud")
        return "devops_cloud" in r.categories

    def test_route_web():
        r = bridge.route("build a React website with responsive UI")
        return "web_frontend" in r.categories

    def test_route_security():
        r = bridge.route("scan for CVE vulnerabilities and audit security")
        return "security_passwords" in r.categories

    def test_route_vietnamese():
        r = bridge.route("viết code lập trình Python để xử lý dữ liệu")
        return "coding" in r.categories

    def test_route_multi_category():
        r = bridge.route("build a complete website, deploy to cloud, and test it")
        return len(r.categories) >= 2

    def test_route_full_lifecycle_trigger():
        r = bridge.route("build a complete end-to-end production application from scratch")
        return r.should_run_full_lifecycle

    def test_route_confidence():
        r = bridge.route("write a Python script")
        return r.confidence > 0.0

    run_test("Route → coding category", test_route_coding)
    run_test("Route → devops category", test_route_devops)
    run_test("Route → web_frontend category", test_route_web)
    run_test("Route → security category", test_route_security)
    run_test("Route → Vietnamese input", test_route_vietnamese)
    run_test("Route → multi-category", test_route_multi_category)
    run_test("Route → full lifecycle trigger", test_route_full_lifecycle_trigger)
    run_test("Route → confidence > 0", test_route_confidence)

    # ═══════════════════════════════════════════════════════════
    # TEST GROUP 2: Targeted Execution
    # ═══════════════════════════════════════════════════════════
    print("\n⚡ GROUP 2: Targeted Execution")
    print("-" * 40)

    def test_execute_coding():
        r = bridge.smart_execute("write a Python function to parse JSON")
        return r.get("success") and r.get("routing", {}).get("categories")

    def test_execute_search():
        r = bridge.smart_execute("research best practices for API design")
        return r.get("success")

    def test_execute_devops():
        r = bridge.smart_execute("deploy my application with Docker")
        return r.get("success")

    def test_execute_with_context():
        r = bridge.smart_execute(
            "build a REST API",
            context={"language": "python", "framework": "fastapi"}
        )
        return r.get("success") and r.get("execution_id")

    def test_execute_has_duration():
        r = bridge.smart_execute("generate an image of a landscape")
        return "duration_ms" in r and r["duration_ms"] >= 0

    run_test("Execute → coding task", test_execute_coding)
    run_test("Execute → search task", test_execute_search)
    run_test("Execute → devops task", test_execute_devops)
    run_test("Execute → with context", test_execute_with_context)
    run_test("Execute → has duration_ms", test_execute_has_duration)

    # ═══════════════════════════════════════════════════════════
    # TEST GROUP 3: Full Lifecycle
    # ═══════════════════════════════════════════════════════════
    print("\n🔄 GROUP 3: Full Lifecycle")
    print("-" * 40)

    def test_lifecycle_full():
        r = bridge.run_lifecycle(
            "build a complete e-commerce platform",
            {"framework": "next.js"}
        )
        return (
            r.get("status") == "completed"
            and r.get("stages_completed") == 8
        )

    def test_lifecycle_stages():
        r = bridge.run_lifecycle("create a todo app")
        stages = list(r.get("stage_results", {}).keys())
        expected = ["plan", "scaffold", "code", "build", "test", "debug", "deploy", "verify"]
        return all(s in stages for s in expected)

    def test_lifecycle_algorithms_used():
        r = bridge.run_lifecycle("deploy microservices")
        return r.get("total_algorithms", 0) > 0

    def test_smart_execute_lifecycle():
        r = bridge.smart_execute("build a complete end-to-end production app from scratch")
        return r.get("routing", {}).get("full_lifecycle") is True

    run_test("Lifecycle → 8 stages completed", test_lifecycle_full)
    run_test("Lifecycle → all stage names present", test_lifecycle_stages)
    run_test("Lifecycle → algorithms used", test_lifecycle_algorithms_used)
    run_test("Smart execute → triggers lifecycle", test_smart_execute_lifecycle)

    # ═══════════════════════════════════════════════════════════
    # TEST GROUP 4: Algorithm Learning
    # ═══════════════════════════════════════════════════════════
    print("\n🧠 GROUP 4: Algorithm Learning")
    print("-" * 40)

    def test_create_from_existing():
        r = bridge.create_from_existing(
            "MyCustomCodeGen",
            base_algorithm="CodeGenerator",
            modifications={
                "description": "Custom code generator for Python APIs",
                "extra_steps": ["api_validation", "auth_check"],
            }
        )
        return r.get("success") and r.get("derived") is True

    def test_create_with_new_category():
        r = bridge.create_from_existing(
            "VideoProcessor",
            base_algorithm="UIBuilder",
            modifications={
                "category": "media_processing",
                "steps": ["upload", "transcode", "optimize", "deliver"],
            }
        )
        return r.get("success")

    def test_suggest_algorithm():
        r = bridge.suggest_algorithm("build a real-time dashboard with charts")
        return (
            "recommended_algorithm" in r
            and "recommended_categories" in r
            and "confidence" in r
        )

    def test_derived_algorithm_runs():
        # First create, then execute
        bridge.create_from_existing(
            "TestDerivedAlgo",
            base_algorithm="DeepResearcher",
        )
        r = bridge.algorithm_engine.execute("TestDerivedAlgo", {"query": "test"})
        return r.get("success")

    run_test("Create algorithm from CodeGenerator", test_create_from_existing)
    run_test("Create algorithm with new category", test_create_with_new_category)
    run_test("Suggest algorithm for task", test_suggest_algorithm)
    run_test("Derived algorithm executes", test_derived_algorithm_runs)

    # ═══════════════════════════════════════════════════════════
    # TEST GROUP 5: Stats & History
    # ═══════════════════════════════════════════════════════════
    print("\n📊 GROUP 5: Stats & History")
    print("-" * 40)

    def test_stats():
        s = bridge.get_stats()
        return (
            "bridge" in s
            and "lifecycle" in s
            and "algorithms" in s
            and s["bridge"]["total_executions"] > 0
        )

    def test_history():
        h = bridge.get_history(5)
        return len(h) > 0 and "id" in h[0]

    def test_list_algorithms():
        algos = bridge.list_all_algorithms()
        return len(algos) >= 32

    def test_history_records_categories():
        h = bridge.get_history(1)
        return len(h) > 0 and "categories" in h[0]

    run_test("Stats → has all sections", test_stats)
    run_test("History → has records", test_history)
    run_test("List algorithms → 32+", test_list_algorithms)
    run_test("History → records categories", test_history_records_categories)

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════
    total = results["passed"] + results["failed"]
    pct = round(results["passed"] / total * 100, 1) if total > 0 else 0

    print("\n" + "=" * 70)
    print(f"📋 RESULTS: {results['passed']}/{total} passed ({pct}%)")
    print("=" * 70)

    # Show stats
    stats = bridge.get_stats()
    print(f"\n📊 Bridge Stats:")
    print(f"  Total executions: {stats['bridge']['total_executions']}")
    print(f"  Lifecycle runs: {stats['bridge']['total_lifecycle_runs']}")
    print(f"  Algorithms created: {stats['bridge']['total_algorithms_created']}")
    print(f"  Derived algorithms: {stats['bridge']['derived_algorithms']}")
    print(f"  Algorithm engine: {stats['algorithms']['total_algorithms']} algorithms, "
          f"{stats['algorithms']['deployed']} deployed")

    # Final verdict
    if results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED — Lifecycle Bridge is FULLY OPERATIONAL!")
    else:
        print(f"\n⚠️ {results['failed']} tests failed — needs attention")

    # Save report
    report_path = os.path.join(os.path.dirname(__file__), "lifecycle_bridge_report.json")
    with open(report_path, "w") as f:
        json.dump({
            "total_tests": total,
            "passed": results["passed"],
            "failed": results["failed"],
            "pass_rate": pct,
            "tests": results["tests"],
            "stats": stats,
        }, f, indent=2)
    print(f"\n📄 Report saved: {report_path}")

    return results


if __name__ == "__main__":
    test_lifecycle_bridge()
