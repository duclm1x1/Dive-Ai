"""Debug SkillRegistry load errors to find root cause."""
import sys
sys.path.insert(0, r"D:\Antigravity\Dive AI\desktop-app\backend")
from dive_core.skills.skill_registry import SkillRegistry

r = SkillRegistry()
loaded = r.auto_discover()
print(f"Loaded: {loaded}")
print(f"Errors: {len(r._load_errors)}")
for i, e in enumerate(r._load_errors[:10]):
    print(f"  [{i}] {e.get('file','?')}: {str(e.get('error',''))[:120]}")
