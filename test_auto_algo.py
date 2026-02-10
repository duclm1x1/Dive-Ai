"""Test: Auto Algorithm Creator + Final Gap Skills."""
import sys, os
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

# ══════════════════════════════════════════════════
print("=" * 60)
print("AUTO ALGORITHM CREATOR SYSTEM")
print("=" * 60)

from dive_core.auto_algorithm_creator import AutoAlgorithmCreator, AlgorithmBlueprint
import tempfile, shutil

# Use temp dir for testing
tmpdir = tempfile.mkdtemp()
creator = AutoAlgorithmCreator(algorithms_dir=tmpdir)

test("creator init", lambda: creator is not None)
test("empty registry", lambda: len(creator.list_algorithms()) == 0)

# Test 1: Create a TRANSFORM algorithm
r1 = creator.create(AlgorithmBlueprint(
    name="text-reverser",
    description="Reverses input text",
    logic_type="transform",
    logic_code='result["reversed"] = inputs.get("text", "")[::-1]',
    tags=["text", "reverse", "string"],
    input_schema={"text": {"type": "string"}},
    output_schema={"reversed": "string"},
))
test("create transform", lambda: r1["success"])
test("transform valid syntax", lambda: r1.get("valid_syntax"))
test("transform file exists", lambda: os.path.exists(r1["file_path"]))
print(f"    Created: {r1.get('class_name')} -> {r1.get('file_path')}")

# Test 2: Create a COMPUTE algorithm
r2 = creator.create(AlgorithmBlueprint(
    name="fibonacci-gen",
    description="Generates Fibonacci sequence",
    logic_type="compute",
    logic_code='result = list(range(inputs.get("n", 10)))',
    tags=["math", "fibonacci", "sequence"],
    input_schema={"n": {"type": "integer"}},
    output_schema={"result": "list"},
))
test("create compute", lambda: r2["success"])
test("compute valid syntax", lambda: r2.get("valid_syntax"))

# Test 3: Create a VALIDATOR algorithm with schema verifier
r3 = creator.create(AlgorithmBlueprint(
    name="email-validator",
    description="Validates email format",
    logic_type="validator",
    logic_code='if "@" not in str(data.get("email", "")): errors.append("Missing @")',
    tags=["email", "validate", "format"],
    verifier_type="schema",
    output_schema={"valid": "boolean", "errors": "list"},
))
test("create validator", lambda: r3["success"])
test("validator has verifier", lambda: r3.get("has_verifier"))

# Test 4: Create a PIPELINE algorithm
r4 = creator.create(AlgorithmBlueprint(
    name="data-cleaner",
    description="Multi-step data cleaning pipeline",
    logic_type="pipeline",
    logic_code='steps_done.append("strip")',
    tags=["data", "clean", "pipeline"],
))
test("create pipeline", lambda: r4["success"])

# Test 5: Hot-deploy and run the text-reverser
# Generated files import from dive_core, so ensure sys.path is set
import sys as _sys
if os.path.join(os.path.dirname(__file__), 'desktop-app', 'backend') not in _sys.path:
    _sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'desktop-app', 'backend'))
deploy_r = creator.deploy("text-reverser")
test("deploy success", lambda: deploy_r.get("success"))
test("deploy has instance", lambda: deploy_r.get("instance") is not None)
if not deploy_r.get("success"):
    print(f"    DEPLOY ERROR: {deploy_r.get('error')}")
    print(f"    TRACEBACK: {deploy_r.get('traceback', 'N/A')[:500]}")

if deploy_r.get("instance"):
    instance = deploy_r["instance"]
    exec_r = instance.execute({"text": "Hello Dive AI"})
    test("execute reverse", lambda: exec_r.status == "success")
    test("reverse correct", lambda: "IA eviD olleH" in str(exec_r.data.get("reversed", "")))
    print(f"    'Hello Dive AI' -> '{exec_r.data.get('reversed')}'")

# Test 6: Deploy and run fibonacci
deploy_fib = creator.deploy("fibonacci-gen")
test("deploy fib", lambda: deploy_fib.get("success"))
if deploy_fib.get("instance"):
    fib_r = deploy_fib["instance"].execute({"n": 5})
    test("fib exec", lambda: fib_r.status == "success")
    print(f"    Fib result = {fib_r.data}")

# Test 7: Batch create
batch_r = creator.create_many([
    AlgorithmBlueprint(name="word-counter", description="Count words in text",
        logic_type="compute", logic_code='result = len(inputs.get("text", "").split())',
        tags=["word", "count"]),
    AlgorithmBlueprint(name="json-formatter", description="Format JSON data",
        logic_type="transform", logic_code='result["formatted"] = True',
        tags=["json", "format"]),
])
test("batch create", lambda: batch_r["created"] == 2)
test("batch total", lambda: batch_r["total"] == 2)

# Test 8: Registry and stats
algos = creator.list_algorithms()
test("registry count", lambda: len(algos) >= 5)

stats = creator.get_stats()
test("stats total", lambda: stats["total_algorithms"] >= 5)
test("stats verifiers", lambda: stats["with_verifiers"] >= 1)
print(f"    Total: {stats['total_algorithms']} algorithms, {stats['with_verifiers']} with verifiers")

# Test 9: Quick helpers
qr = creator.quick_transform("uppercaser", "Uppercase text",
    logic='result["upper"] = inputs.get("text", "").upper()')
test("quick transform", lambda: qr["success"])

# Test 10: Delete
test("delete algo", lambda: creator.delete_algorithm("uppercaser"))
test("after delete", lambda: creator.get_algorithm("uppercaser") is None)

# Cleanup
shutil.rmtree(tmpdir)

# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("FINAL GAP SKILLS")
print("=" * 60)

from dive_core.skills.skill_registry import SkillRegistry
reg = SkillRegistry()

# Terraform
from dive_core.skills.devops.terraform_skill import TerraformSkill
tf = TerraformSkill(); reg.register(tf)
test("terraform load", lambda: reg.get("terraform") is not None)
r = tf.execute({"action": "init"}); test("terraform graceful", lambda: r.status in ("success", "failure"))

# Release Manager
from dive_core.skills.devops.release_skill import ReleaseSkill
rel = ReleaseSkill(); reg.register(rel)
test("release-manager load", lambda: reg.get("release-manager") is not None)

# API Tester
from dive_core.skills.devops.api_test_skill import APITestSkill
api = APITestSkill(); reg.register(api)
test("api-tester load", lambda: reg.get("api-tester") is not None)

r = api.execute({"action": "request", "url": "https://httpbin.org/get"})
test("api request", lambda: r.status == "success" and r.data.get("status") == 200)
print(f"    httpbin.org latency: {r.data.get('latency_ms')}ms")

r = api.execute({"action": "assert", "url": "https://httpbin.org/get",
    "expect": {"status": 200, "contains": "httpbin"}})
test("api assert", lambda: r.status == "success" and r.data.get("passed"))

# Database
from dive_core.skills.productivity.database_skill import DatabaseSkill
db = DatabaseSkill(); reg.register(db)
test("database load", lambda: reg.get("database") is not None)

# Test real SQLite operations
import tempfile as tf2
db_file = os.path.join(tf2.gettempdir(), "dive_test.db")
r = db.execute({"action": "create", "db": db_file, "table": "users",
    "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}})
test("db create table", lambda: r.status == "success")

r = db.execute({"action": "insert", "db": db_file, "table": "users",
    "data": [{"name": "Duc", "age": 28}, {"name": "Alice", "age": 30}]})
test("db insert", lambda: r.status == "success" and r.data.get("inserted") == 2)

r = db.execute({"action": "query", "db": db_file, "query": "SELECT * FROM users"})
test("db query", lambda: r.status == "success" and r.data.get("count") == 2)
print(f"    Rows: {r.data.get('rows')}")

r = db.execute({"action": "schema", "db": db_file, "table": "users"})
test("db schema", lambda: r.status == "success" and r.data.get("row_count") == 2)

os.unlink(db_file)

# ══════════════════════════════════════════════════
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
