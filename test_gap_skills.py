"""Test all gap-closing skills — Priority 1 + Priority 2."""
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

from dive_core.skills.skill_registry import SkillRegistry
reg = SkillRegistry()

# === PRIORITY 1: Quick wins ===
print("=" * 60)
print("PRIORITY 1: QUICK WIN SKILLS")
print("=" * 60)

# K8s
from dive_core.skills.devops.k8s_skill import K8sSkill
k8s = K8sSkill()
reg.register(k8s)
test("k8s load", lambda: reg.get("k8s-manager") is not None)
test("k8s spec", lambda: k8s.skill_spec.name == "k8s-manager")
r = k8s.execute({"action": "pods"})
# kubectl likely not installed, just check it handles gracefully
test("k8s pods (graceful)", lambda: r.status in ("success", "failure"))

# Cloud Deploy
from dive_core.skills.devops.cloud_deploy_skill import CloudDeploySkill
cloud = CloudDeploySkill()
reg.register(cloud)
test("cloud-deploy load", lambda: reg.get("cloud-deploy") is not None)
r = cloud.execute({"provider": "aws", "action": "status"})
test("cloud-deploy (graceful)", lambda: r.status in ("success", "failure"))

# Compression
from dive_core.skills.devops.compression_skill import CompressionSkill
comp = CompressionSkill()
reg.register(comp)
test("compression load", lambda: reg.get("compression") is not None)

# Test actual zip/extract cycle
tmpdir = tempfile.mkdtemp()
test_file = os.path.join(tmpdir, "test.txt")
with open(test_file, "w") as f: f.write("Hello Dive AI " * 100)
zip_out = os.path.join(tmpdir, "test.zip")
r = comp.execute({"action": "compress", "source": test_file, "output": zip_out, "format": "zip"})
test("zip compress", lambda: r.status == "success" and os.path.exists(zip_out))
test("zip ratio", lambda: r.data.get("ratio") is not None)

extract_dir = os.path.join(tmpdir, "extracted")
r = comp.execute({"action": "extract", "source": zip_out, "output": extract_dir})
test("zip extract", lambda: r.status == "success" and r.data.get("total_files") == 1)

r = comp.execute({"action": "list", "source": zip_out})
test("zip list", lambda: r.status == "success" and len(r.data.get("files", [])) == 1)
shutil.rmtree(tmpdir)

# Network Tools
from dive_core.skills.devops.network_skill import NetworkSkill
net = NetworkSkill()
reg.register(net)
test("network-tools load", lambda: reg.get("network-tools") is not None)

r = net.execute({"action": "dns", "host": "google.com"})
test("dns lookup", lambda: r.status == "success" and r.data.get("ip"))
print(f"    google.com -> {r.data.get('ip')}")

r = net.execute({"action": "port-scan", "host": "127.0.0.1", "ports": "80,443,3000,8080"})
test("port scan", lambda: r.status == "success" and len(r.data.get("ports", [])) == 4)
print(f"    open ports on localhost: {r.data.get('open_ports', [])}")

# Clipboard
from dive_core.skills.devops.clipboard_skill import ClipboardSkill
clip = ClipboardSkill()
reg.register(clip)
test("clipboard load", lambda: reg.get("clipboard") is not None)

r = clip.execute({"action": "copy", "text": "Dive AI Gap Test 2026"})
test("clipboard copy", lambda: r.status == "success")
r = clip.execute({"action": "paste"})
test("clipboard paste", lambda: r.status == "success" and "Dive AI" in r.data.get("text", ""))
r = clip.execute({"action": "history"})
test("clipboard history", lambda: r.status == "success")

# === PRIORITY 2: Important ===
print("\n" + "=" * 60)
print("PRIORITY 2: IMPORTANT SKILLS")
print("=" * 60)

# Skill Generator
from dive_core.skills.ai.skill_generator_skill import SkillGeneratorSkill
gen = SkillGeneratorSkill()
reg.register(gen)
test("skill-generator load", lambda: reg.get("skill-generator") is not None)

r = gen.execute({"name": "test-autogen", "description": "Auto-generated test skill",
                 "category": "CUSTOM", "tags": ["test", "auto"]})
test("skill gen creates file", lambda: r.status == "success" and r.data.get("installed"))
test("skill gen valid syntax", lambda: r.data.get("valid_syntax"))
# Clean up temp file
if r.data.get("file_path") and os.path.exists(r.data["file_path"]):
    os.unlink(r.data["file_path"])
print(f"    generated: {r.data.get('class_name')} -> {r.data.get('file_path')}")

# Proactive Heartbeat
from dive_core.skills.proactive_heartbeat import ProactiveHeartbeat, HeartbeatMonitor
hb = ProactiveHeartbeat()
hb.add_monitor(HeartbeatMonitor("test", lambda: False, lambda: None, interval=60))
test("heartbeat init", lambda: len(hb.monitors) == 1)
status = hb.get_status()
test("heartbeat status", lambda: status["total_monitors"] == 1 and not status["running"])
hb.start()
import time; time.sleep(0.5)
test("heartbeat running", lambda: hb.get_status()["running"])
hb.stop()
test("heartbeat stopped", lambda: not hb.get_status()["running"])

# Sandbox Executor
from dive_core.skills.sandbox_executor import SandboxExecutor
sb = SandboxExecutor()
test("sandbox init", lambda: sb.timeout == 30 and sb.memory_limit == "256m")
stats = sb.get_stats()
test("sandbox stats", lambda: stats["security"]["network"] == "disabled")
print(f"    Docker available: {stats['available']}")

# Repo Monitor
from dive_core.skills.devops.repo_monitor_skill import RepoMonitorSkill
repo = RepoMonitorSkill()
reg.register(repo)
test("repo-monitor load", lambda: reg.get("repo-monitor") is not None)
test("repo-monitor spec", lambda: repo.skill_spec.tags and "github" in repo.skill_spec.tags)

# === FINAL SUMMARY ===
print("\n" + "=" * 60)
print("FINAL GAP-CLOSING RESULTS")
print("=" * 60)
total = results["passed"] + results["failed"]
print(f"\n  {results['passed']}/{total} tests passed")
print(f"\n  Skills registered: {len(reg.list_names())}")
names = reg.list_names()
for n in sorted(names):
    print(f"    - {n}")

if results["errors"]:
    print(f"\n  Failures:")
    for e in results["errors"]:
        print(f"    -> {e}")

print("\n" + "=" * 60)
if results["failed"] == 0:
    print(f"  ALL {total} TESTS PASSED - All gaps closed!")
print("=" * 60)
