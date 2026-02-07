"""Dive Skill Manager - Auto-discover and manage skills"""
import os, sys, importlib.util
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SkillMeta:
    name: str
    path: str
    loaded: bool = False

class DiveSkillManager:
    def __init__(self, paths=["skills"]):
        self.paths, self.skills, self.modules = paths, {}, {}
        print("✅ Dive Skill Manager initialized")
    
    def discover(self):
        found = []
        for base in self.paths:
            for skill_file in Path(base).rglob("SKILL.md"):
                name = skill_file.parent.name
                self.skills[name] = SkillMeta(name, str(skill_file.parent))
                found.append(name)
        print(f"✅ Discovered {len(found)} skills")
        return found
    
    def load(self, name: str):
        if name not in self.skills:
            raise ValueError(f"Skill not found: {name}")
        skill = self.skills[name]
        skill_file = Path(skill.path) / "skill.py"
        spec = importlib.util.spec_from_file_location(name, skill_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        self.modules[name] = module
        skill.loaded = True
        print(f"✅ Loaded: {name}")
        return module
    
    def list_skills(self):
        return list(self.skills.values())
    
    def get_stats(self):
        total = len(self.skills)
        loaded = len([s for s in self.skills.values() if s.loaded])
        return {"total_skills": total, "loaded_skills": loaded, "categories": {}}
