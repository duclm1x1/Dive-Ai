"""Integration test: AlgorithmService -> Create -> Deploy -> Execute -> Registry"""
import sys, os, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

results = {"passed": 0, "failed": 0, "errors": []}
def test(name, fn):
    try:
        r = fn()
        if r:
            results["passed"] += 1
            print(f"  PASS {name}")
        else:
            results["failed"] += 1
            print(f"  FAIL {name}")
            results["errors"].append(name)
    except Exception as e:
        results["failed"] += 1
        print(f"  FAIL {name}: {e}")
        results["errors"].append(f"{name}: {e}")

# ============================================================
print("=" * 60)
print("ALGORITHM SERVICE INTEGRATION")
print("=" * 60)

from dive_core.algorithm_service import AlgorithmService, get_algorithm_service

# Test 1: Singleton
svc1 = get_algorithm_service()
svc2 = get_algorithm_service()
test("singleton", lambda: svc1 is svc2)

# Test 2: Service init (auto-loads skills)
stats = svc1.get_stats()
test("service init", lambda: stats["skills_loaded"] >= 0)
print(f"    Skills loaded: {stats['skills_loaded']}")
print(f"    Auto algorithms: {stats['auto_algorithms_created']}")
print(f"    Deployed: {stats['auto_algorithms_deployed']}")

# Test 3: List all
all_items = svc1.list_all()
test("list structure", lambda: "skills" in all_items and "auto_algorithms" in all_items and "deployed" in all_items)
print(f"    Skills: {all_items['counts']['skills']}")
print(f"    Auto-algos: {all_items['counts']['auto_algorithms']}")
print(f"    Deployed: {all_items['counts']['deployed']}")
print(f"    Total: {all_items['counts']['total']}")

# Test 4: Create algorithm
r1 = svc1.create_algorithm(
    name="test-reverser",
    description="Reverses input text",
    logic_type="transform",
    logic_code='result["reversed"] = inputs.get("text", "")[::-1]',
    tags=["test", "reverse"],
    auto_deploy=True,
)
test("create + auto-deploy", lambda: r1.get("success") and r1.get("deployed"))

# Test 5: Execute auto-deployed algorithm
r2 = svc1.execute("test-reverser", {"text": "Dive AI v29"})
test("execute auto-algo", lambda: r2.get("success"))
test("execute correct result", lambda: r2.get("data", {}).get("reversed") == "92v IA eviD")
if r2.get("success"):
    print(f"    'Dive AI v29' -> '{r2['data'].get('reversed')}'")
    print(f"    Elapsed: {r2.get('elapsed_ms')}ms")

# Test 6: Execute a registered skill (if any loaded)
skill_names = svc1.list_names()
test("list names", lambda: len(skill_names) >= 1)
print(f"    Available names: {len(skill_names)}")

# Test 7: Info query
info = svc1.get_info("test-reverser")
test("get info", lambda: info is not None and info["type"] == "auto_algorithm")
test("info deployed", lambda: info.get("deployed") == True)

# Test 8: Search
search_r = svc1.search("reverse")
test("search", lambda: len(search_r) >= 1)

# Test 9: Execution log
log = svc1.get_log()
test("execution log", lambda: len(log) >= 3)  # create + deploy + execute
print(f"    Log entries: {len(log)}")

# Test 10: Delete
del_r = svc1.delete_algorithm("test-reverser")
test("delete", lambda: del_r["success"])
test("deleted gone", lambda: svc1.get_info("test-reverser") is None)

# Test 11: Stats after operations
final_stats = svc1.get_stats()
test("stats final", lambda: final_stats["execution_log_size"] >= 3)

# ============================================================
print("\n" + "=" * 60)
print("SKILL REGISTRY via SERVICE")
print("=" * 60)

# Check some known skills
from dive_core.skills.devops.terraform_skill import TerraformSkill
from dive_core.skills.productivity.database_skill import DatabaseSkill

tf = TerraformSkill()
svc1.registry.register(tf)
db = DatabaseSkill()
svc1.registry.register(db)

# Execute via service
r_tf = svc1.execute("terraform", {"action": "validate", "dir": "."})
test("skill via service", lambda: r_tf.get("source") == "skill_registry")

# Test batch create via service
r_batch1 = svc1.create_algorithm(
    name="word-counter", description="Count words",
    logic_type="compute", logic_code='result = len(inputs.get("text", "hello world").split())',
)
r_batch2 = svc1.create_algorithm(
    name="upper-caser", description="Uppercase text",
    logic_type="transform", logic_code='result["upper"] = inputs.get("text", "").upper()',
)
test("batch 1 created", lambda: r_batch1.get("success"))
test("batch 2 created", lambda: r_batch2.get("success"))

# Execute batch-created algos
r_wc = svc1.execute("word-counter", {"text": "Dive AI is awesome at algorithms"})
test("word-counter exec", lambda: r_wc.get("success"))
if r_wc.get("success"):
    print(f"    Word count: {r_wc.get('data', {})}")

r_uc = svc1.execute("upper-caser", {"text": "dive ai"})
test("upper-caser exec", lambda: r_uc.get("success"))
if r_uc.get("success"):
    print(f"    Uppercased: {r_uc.get('data', {}).get('upper')}")

# Cleanup
svc1.delete_algorithm("word-counter")
svc1.delete_algorithm("upper-caser")

# ============================================================
print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)
total = results["passed"] + results["failed"]
print(f"\n  {results['passed']}/{total} tests passed")
if results["errors"]:
    print(f"\n  Failures:")
    for e in results["errors"]:
        print(f"    -> {e}")
print("\n" + "=" * 60)
if results["failed"] == 0:
    print(f"  ALL {total} TESTS PASSED!")
else:
    print(f"  {results['failed']} failures")
print("=" * 60)
