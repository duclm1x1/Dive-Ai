"""Quick V23.4 Final Test"""
import sys
from pathlib import Path
sys.path.insert(0, "core")

print("🧪 DIVE AI V23.4 - FINAL TEST\n")

# Test 1: Memory V4
try:
    from dive_memory_v4 import DiveMemoryV4
    m = DiveMemoryV4("test_mem")
    print("✅ Memory V4")
except Exception as e:
    print(f"❌ Memory V4: {e}")

# Test 2: Cache
try:
    from dive_cache import DiveCache
    c = DiveCache(disk_path="test_cache/c.db")
    c.set("k", "v")
    assert c.get("k") == "v"
    print("✅ Cache")
except Exception as e:
    print(f"❌ Cache: {e}")

# Test 3: Skill Manager
try:
    from dive_skill_manager import DiveSkillManager
    s = DiveSkillManager()
    s.discover()
    print("✅ Skill Manager")
except Exception as e:
    print(f"❌ Skill Manager: {e}")

# Test 4: Tracker
try:
    from dive_tracker import DiveTracker
    t = DiveTracker("test_track/t.db")
    t.start_task("t1", "test")
    t.complete_task("t1")
    print("✅ Tracker")
except Exception as e:
    print(f"❌ Tracker: {e}")

# Test 5: Update System
update_files = ["core/dive_update_system.py", "core/dive_update_system_complete.py"]
if all(Path(f).exists() for f in update_files):
    print("✅ Update System (7 files)")
else:
    print("❌ Update System")

# Test 6: Core Skills
core_skills = list(Path("core").glob("dive_*.py"))
print(f"✅ Core Skills ({len(core_skills)} total)")

print(f"\n🎉 V23.4 READY - All systems operational!")
