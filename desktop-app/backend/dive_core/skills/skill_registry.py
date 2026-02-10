"""
Dive AI Skill Registry — Central catalog for all skills.
Algorithm-verified, cost-tracked, combo-aware.

Optimized by Antigravity:
  - Fixed importlib.util import (was causing ALL skills to fail loading)
  - Added 'coding' to auto-discover directories
  - Added discover result caching for repeated queries
  - Added bulk_register for mass skill loading
  - Added search_by_name for fuzzy name matching
"""
import os
import json
import time
import importlib
import importlib.util
import traceback
from typing import Dict, List, Optional, Any
from .base_skill import BaseSkill
from .skill_spec import SkillSpec, SkillCategory


class SkillRegistry:
    """
    Central registry for all Dive AI skills.
    - Register/unregister skills
    - Discover by category, tag, or natural language query
    - Track cost and execution stats
    - Support external skill installation
    - Optimized: cached discovery, bulk register, fuzzy search
    """

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._load_errors: List[Dict[str, str]] = []
        self._discover_cache: Dict[str, List] = {}  # query → results cache
        self._last_discover_time: float = 0.0
        self._auto_discover_time_ms: float = 0.0

    # ── Registration ───────────────────────────────────────

    def register(self, skill: BaseSkill) -> bool:
        """Register a skill instance."""
        try:
            name = skill.skill_spec.name
            self._skills[name] = skill
            self._discover_cache.clear()  # invalidate cache on change
            return True
        except Exception as e:
            self._load_errors.append({"skill": str(skill), "error": str(e)})
            return False

    def bulk_register(self, skills: List[BaseSkill]) -> int:
        """Register multiple skills at once. Returns count of successfully registered."""
        count = 0
        for skill in skills:
            if self.register(skill):
                count += 1
        return count

    def unregister(self, skill_name: str) -> bool:
        """Remove a skill from the registry."""
        if skill_name in self._skills:
            del self._skills[skill_name]
            self._discover_cache.clear()
            return True
        return False

    # ── Discovery ──────────────────────────────────────────

    def get(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by exact name."""
        return self._skills.get(name)

    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all skills grouped by category."""
        result: Dict[str, List[Dict]] = {}
        for skill in self._skills.values():
            cat = skill.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(skill.skill_spec.to_dict())
        return result

    def list_by_category(self, category: SkillCategory) -> List[BaseSkill]:
        """Get all skills in a category."""
        return [s for s in self._skills.values() if s.category == category]

    def list_names(self) -> List[str]:
        """Get all registered skill names."""
        return list(self._skills.keys())

    def discover(self, query: str) -> List[BaseSkill]:
        """Find skills matching a natural language query, sorted by relevance.
        Results are cached for repeated queries."""
        # Check cache first
        if query in self._discover_cache:
            return self._discover_cache[query]

        scored = []
        for skill in self._skills.values():
            score = skill.can_handle(query)
            if score > 0.1:
                scored.append((score, skill))
        scored.sort(key=lambda x: x[0], reverse=True)
        result = [s for _, s in scored]

        # Cache results (max 100 cached queries)
        if len(self._discover_cache) > 100:
            self._discover_cache.clear()
        self._discover_cache[query] = result
        return result

    def search_by_name(self, partial_name: str) -> List[BaseSkill]:
        """Fuzzy search skills by partial name match."""
        partial = partial_name.lower()
        return [
            s for name, s in self._skills.items()
            if partial in name.lower()
        ]

    def search_by_tag(self, tag: str) -> List[BaseSkill]:
        """Find skills with a specific tag."""
        tag_lower = tag.lower()
        return [
            s for s in self._skills.values()
            if tag_lower in [t.lower() for t in s.skill_spec.tags]
        ]

    # ── Stats ──────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Get registry-wide statistics."""
        total_cost = sum(s._total_cost for s in self._skills.values())
        total_executions = sum(s._execution_count for s in self._skills.values())
        cats = {}
        for s in self._skills.values():
            cat = s.category.value
            cats[cat] = cats.get(cat, 0) + 1

        return {
            "total_skills": len(self._skills),
            "categories": cats,
            "total_executions": total_executions,
            "total_cost": round(total_cost, 6),
            "load_errors": len(self._load_errors),
            "auto_discover_time_ms": self._auto_discover_time_ms,
            "cached_queries": len(self._discover_cache),
            "skills": {name: s.stats for name, s in self._skills.items()},
        }

    # ── Cost Estimation ────────────────────────────────────

    def estimate_cost(self, skill_names: List[str]) -> float:
        """Estimate cost for executing a list of skills."""
        total = 0.0
        for name in skill_names:
            skill = self.get(name)
            if skill:
                total += skill.skill_spec.cost_per_call
        return total

    # ── Auto-Discovery ─────────────────────────────────────

    def auto_discover(self, skills_dir: str = None) -> int:
        """
        Scan skill directories and auto-register all BaseSkill subclasses.
        Returns number of skills loaded.

        Optimized: Added 'coding' dir, proper importlib.util import,
        timing stats, and better error context.
        """
        t0 = time.time()

        if skills_dir is None:
            skills_dir = os.path.dirname(os.path.abspath(__file__))

        loaded = 0
        # Added 'coding' — it exists on disk but was missing from original list
        skill_dirs = ["browser", "search", "communication", "devops",
                      "ai", "coding", "productivity"]

        for subdir in skill_dirs:
            dir_path = os.path.join(skills_dir, subdir)
            if not os.path.isdir(dir_path):
                continue

            for fname in os.listdir(dir_path):
                if not fname.endswith("_skill.py"):
                    continue

                module_name = fname[:-3]  # Remove .py
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"dive_core.skills.{subdir}.{module_name}",
                        os.path.join(dir_path, fname)
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)

                        # Find BaseSkill subclasses
                        for attr_name in dir(mod):
                            attr = getattr(mod, attr_name)
                            if (isinstance(attr, type)
                                and issubclass(attr, BaseSkill)
                                and attr is not BaseSkill):
                                instance = attr()
                                if self.register(instance):
                                    loaded += 1
                except Exception as e:
                    self._load_errors.append({
                        "file": fname,
                        "dir": subdir,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    })

        self._auto_discover_time_ms = round((time.time() - t0) * 1000, 1)
        self._last_discover_time = time.time()
        return loaded


# Singleton
_registry: Optional[SkillRegistry] = None

def get_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry
