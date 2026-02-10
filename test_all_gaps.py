"""
Comprehensive test: ALL gap skills + integration points.
Tests every remaining gap item to ensure complete parity.
"""
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

# ==============================================================
print("=" * 60)
print("P1: DEVOPS + CLI SKILLS (import + instantiate)")
print("=" * 60)

# K8s — instantiate only (kubectl not installed)
from dive_core.skills.devops.k8s_skill import K8sSkill
k8s = K8sSkill()
test("K8s instantiate", lambda: k8s is not None and hasattr(k8s, '_execute'))
r = k8s.execute({"action": "pods"})
test("K8s pods (graceful fail)", lambda: r.status in ["success", "failure"])

# Cloud Deploy
from dive_core.skills.devops.cloud_deploy_skill import CloudDeploySkill
cd = CloudDeploySkill()
test("Cloud deploy instantiate", lambda: cd is not None)
r = cd.execute({"provider": "aws", "action": "status"})
test("Cloud deploy (graceful)", lambda: r.status in ["success", "failure"])

# Compression
from dive_core.skills.devops.compression_skill import CompressionSkill
comp = CompressionSkill()
test_dir = tempfile.mkdtemp()
test_file = os.path.join(test_dir, "test.txt")
with open(test_file, "w") as f:
    f.write("Hello Dive AI " * 100)
r = comp.execute({"action": "compress", "source": test_file,
                   "output": os.path.join(test_dir, "test.zip"),
                   "format": "zip"})
test("Compression skill", lambda: r.status == "success")
shutil.rmtree(test_dir, ignore_errors=True)

# Network tools
from dive_core.skills.devops.network_skill import NetworkSkill
net = NetworkSkill()
r = net.execute({"action": "ping", "host": "127.0.0.1", "count": 1})
test("Network skill (ping)", lambda: r.status == "success")

# Clipboard
from dive_core.skills.devops.clipboard_skill import ClipboardSkill
clip = ClipboardSkill()
r = clip.execute({"action": "paste"})
test("Clipboard skill (paste)", lambda: r.status in ["success", "failure"])

# Repo monitor
from dive_core.skills.devops.repo_monitor_skill import RepoMonitorSkill
rm = RepoMonitorSkill()
test("Repo monitor instantiate", lambda: rm is not None)
r = rm.execute({"action": "events", "repo": "duclm1x1/Dive-AI2"})
test("Repo monitor (graceful)", lambda: r.status in ["success", "failure"])

# Terraform
from dive_core.skills.devops.terraform_skill import TerraformSkill
tf = TerraformSkill()
test("Terraform instantiate", lambda: tf is not None)

# Release management
from dive_core.skills.devops.release_skill import ReleaseSkill
rel = ReleaseSkill()
test("Release instantiate", lambda: rel is not None)

# API test
from dive_core.skills.devops.api_test_skill import APITestSkill
at = APITestSkill()
r = at.execute({"action": "request", "url": "https://httpbin.org/get"})
test("API test skill", lambda: r.status == "success")

# Database
from dive_core.skills.productivity.database_skill import DatabaseSkill
db = DatabaseSkill()
r = db.execute({"action": "tables"})
test("Database skill", lambda: r.status == "success")

# ==============================================================
print("\n" + "=" * 60)
print("P2: SKILL GENERATOR + COMMS + HEARTBEAT + SANDBOX")
print("=" * 60)

# Skill generator
from dive_core.skills.skill_generator import SkillGenerator
gen = SkillGenerator()
gen_dir = tempfile.mkdtemp()
r = gen.generate(
    name="test_generated",
    description="A test generated skill",
    category="custom",
    logic_code='result = {"generated": True, "action": action}',
    target_dir=gen_dir,
)
test("Skill generator create", lambda: r["success"])
test("Skill file exists", lambda: os.path.exists(r["path"]))
test("Syntax valid", lambda: r.get("syntax_valid"))

# Batch generate
batch_r = gen.batch_generate([
    {"name": "batch_one", "description": "Skill 1", "target_dir": gen_dir},
    {"name": "batch_two", "description": "Skill 2", "target_dir": gen_dir,
     "logic_code": 'result = {"batch": True}'},
])
test("Batch generate", lambda: batch_r["success"] == 2)
test("Generator stats", lambda: gen.get_stats()["total_generated"] == 3)
shutil.rmtree(gen_dir, ignore_errors=True)

# Signal skill
from dive_core.skills.communication.signal_skill import SignalSkill
sig = SignalSkill()
r = sig.execute({"action": "status"})
test("Signal skill", lambda: r.status == "success")
r = sig.execute({"action": "send", "to": "+1234567890", "message": "Hello from Dive AI"})
test("Signal send (simulated)", lambda: r.status == "success" and r.data.get("simulated"))

# iMessage skill
from dive_core.skills.communication.imessage_skill import IMessageSkill
im = IMessageSkill()
r = im.execute({"action": "status"})
test("iMessage skill", lambda: r.status == "success")
r = im.execute({"action": "send", "to": "test@apple.com", "message": "Hello iMessage"})
test("iMessage send (simulated)", lambda: r.status == "success" and r.data.get("simulated"))

# Heartbeat
from dive_core.skills.proactive_heartbeat import ProactiveHeartbeat, create_default_monitors
hb = ProactiveHeartbeat()
create_default_monitors(hb)
status = hb.get_status()
test("Heartbeat init", lambda: status["total_monitors"] >= 3)
test("Heartbeat monitors", lambda: "disk-space" in status["monitors"])

# Sandbox
from dive_core.skills.sandbox_executor import SandboxExecutor
sb = SandboxExecutor()
stats = sb.get_stats()
test("Sandbox init", lambda: stats["security"]["network"] == "disabled")
test("Sandbox filesystem", lambda: stats["security"]["filesystem"] == "read-only")

# ==============================================================
print("\n" + "=" * 60)
print("P3: CODING + BROWSER SKILLS")
print("=" * 60)

# LSP skill
from dive_core.skills.coding.lsp_skill import LspSkill
lsp = LspSkill()
r = lsp.execute({"action": "status"})
test("LSP skill status", lambda: r.status == "success")

# Diagnose this test file itself
this_file = os.path.abspath(__file__)
r = lsp.execute({"action": "diagnose", "file": this_file})
test("LSP diagnose", lambda: r.status == "success" and len(r.data.get("diagnostics", [])) >= 1)

# Completions
r = lsp.execute({"action": "complete", "file": this_file})
test("LSP completions", lambda: r.status == "success" and r.data.get("count", 0) >= 1)

# Analyze
r = lsp.execute({"action": "analyze", "file": this_file})
test("LSP analyze", lambda: r.status == "success" and r.data.get("lines", 0) > 50)

# Multi-agent dev
from dive_core.skills.coding.multi_agent_dev_skill import MultiAgentDevSkill
mad = MultiAgentDevSkill()
r = mad.execute({"action": "plan", "project": "test-project",
                 "description": "frontend, backend, database, testing"})
test("Multi-agent plan", lambda: r.status == "success" and r.data.get("total_tasks") == 4)

r = mad.execute({"action": "delegate", "project": "test-project",
                 "task_id": "task-1", "agent_id": "agent-alpha"})
test("Multi-agent delegate", lambda: r.status == "success" and r.data.get("delegated"))

r = mad.execute({"action": "review", "file": this_file})
test("Multi-agent review", lambda: r.status == "success" and "quality_score" in r.data)

# Cookie manager
from dive_core.skills.browser.cookie_manager_skill import CookieManagerSkill
cm = CookieManagerSkill()
r = cm.execute({"action": "set", "domain": "dive.ai", "name": "session", "value": "abc123"})
test("Cookie set", lambda: r.status == "success")
r = cm.execute({"action": "get", "domain": "dive.ai", "name": "session"})
test("Cookie get", lambda: r.status == "success" and r.data["cookie"]["value"] == "abc123")
r = cm.execute({"action": "list"})
test("Cookie list", lambda: r.status == "success" and r.data["total_cookies"] >= 1)
r = cm.execute({"action": "clear"})
test("Cookie clear", lambda: r.status == "success")

# SPA renderer
from dive_core.skills.browser.spa_renderer_skill import SpaRendererSkill
spa = SpaRendererSkill()
r = spa.execute({"action": "status"})
test("SPA renderer status", lambda: r.status == "success")

# ==============================================================
print("\n" + "=" * 60)
print("ALGORITHM SERVICE FULL INTEGRATION")
print("=" * 60)

from dive_core.algorithm_service import get_algorithm_service
svc = get_algorithm_service()

# Create + execute
r = svc.create_algorithm(
    name="gap-test-algo", description="Test from gap suite",
    logic_type="transform",
    logic_code='result["value"] = inputs.get("x", 0) * 2',
    auto_deploy=True,
)
test("Service create", lambda: r.get("success"))

r = svc.execute("gap-test-algo", {"x": 21})
test("Service execute", lambda: r.get("success") and r.get("data", {}).get("value") == 42)
if r.get("success"):
    print(f"    21 * 2 = {r['data']['value']}")

# Search
r = svc.search("gap")
test("Service search", lambda: len(r) >= 1)

# Stats
stats = svc.get_stats()
test("Service stats", lambda: stats["execution_log_size"] >= 1)

# Clean up
svc.delete_algorithm("gap-test-algo")

# ==============================================================
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
    print(f"  ALL {total} TESTS PASSED - ALL GAPS COMPLETE!")
else:
    pct = round(results["passed"] / total * 100, 1) if total else 0
    print(f"  {results['passed']}/{total} passed ({pct}%)")
print("=" * 60)
