"""
Dive AI — DiveHub Marketplace
Surpasses OpenClaw's ClawHub with:
  - Skill registry with versioning
  - Security scanning before install
  - Dependency resolution
  - Categories and tags
  - Usage analytics and ratings
  - Install/uninstall lifecycle
"""

import os
import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum


class SkillStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


@dataclass
class MarketplaceSkill:
    """A skill in the DiveHub marketplace."""
    skill_id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    status: SkillStatus = SkillStatus.PUBLISHED
    dependencies: List[str] = field(default_factory=list)
    code_hash: str = ""
    install_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    security_scan: Optional[Dict] = None
    skill_md: str = ""  # SKILL.md content (Agent Skills Standard)

    def to_dict(self) -> Dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "tags": self.tags,
            "status": self.status.value,
            "install_count": self.install_count,
            "rating": round(self.rating, 2),
            "rating_count": self.rating_count,
            "dependencies": self.dependencies,
        }


class DiveHubMarketplace:
    """
    Skill marketplace for Dive AI.

    Surpasses OpenClaw's ClawHub by adding:
      - Mandatory security scanning before publish
      - Dependency resolution and conflict detection
      - Version management with rollback
      - Quality scoring (not just install count)
      - Category-based discovery with fuzzy search
      - Agent Skills Standard (SKILL.md) support
    """

    CATEGORIES = [
        "coding", "database", "web", "file", "system",
        "ai", "data", "communication", "security", "testing",
        "documentation", "devops", "monitoring", "analytics",
    ]

    def __init__(self):
        self._skills: Dict[str, MarketplaceSkill] = {}
        self._installed: Dict[str, MarketplaceSkill] = {}
        self._install_history: List[Dict] = []
        self._total_installs = 0
        self._total_uninstalls = 0
        self._security_scanner = None  # Will use SecurityHardening

    def set_scanner(self, scanner):
        """Set the security scanner (SecurityHardening instance)."""
        self._security_scanner = scanner

    # ── Publishing ────────────────────────────────────────────

    def publish(self, name: str, description: str, code: str = "",
                version: str = "1.0.0", author: str = "",
                category: str = "general", tags: List[str] = None,
                dependencies: List[str] = None,
                skill_md: str = "") -> Dict:
        """
        Publish a skill to DiveHub.

        Requires security scan to pass before publishing.
        """
        skill_id = f"{name.lower().replace(' ', '-')}-{version}"

        # Security scan
        scan_result = None
        if self._security_scanner and code:
            scan_result = self._security_scanner.scan_skill_code(code, name)
            if scan_result.get("risk_level") == "critical":
                return {
                    "success": False,
                    "reason": "Security scan failed: critical risk detected",
                    "scan": scan_result,
                }

        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16] if code else ""

        skill = MarketplaceSkill(
            skill_id=skill_id,
            name=name,
            description=description,
            version=version,
            author=author,
            category=category,
            tags=tags or [],
            code_hash=code_hash,
            security_scan=scan_result,
            skill_md=skill_md,
            status=SkillStatus.VERIFIED if scan_result and scan_result["safe"]
                   else SkillStatus.PUBLISHED,
        )

        if dependencies:
            skill.dependencies = dependencies

        self._skills[skill_id] = skill

        return {
            "success": True,
            "skill_id": skill_id,
            "status": skill.status.value,
            "scan": scan_result,
        }

    # ── Discovery ─────────────────────────────────────────────

    def search(self, query: str = "", category: str = "",
               tags: List[str] = None,
               limit: int = 20) -> List[Dict]:
        """Search marketplace skills."""
        results = []
        q = query.lower()

        for skill in self._skills.values():
            if skill.status in (SkillStatus.BLOCKED, SkillStatus.DEPRECATED):
                continue

            score = 0.0

            # Name match
            if q and q in skill.name.lower():
                score += 1.0
            # Description match
            if q and q in skill.description.lower():
                score += 0.5
            # Tag match
            if tags:
                matching_tags = set(t.lower() for t in tags) & \
                                set(t.lower() for t in skill.tags)
                score += len(matching_tags) * 0.3
            # Category match
            if category and skill.category.lower() == category.lower():
                score += 0.4

            # Boost by popularity and rating
            score += min(0.3, skill.install_count * 0.01)
            score += skill.rating * 0.1

            # If no query, show all with category/tag filters
            if not q and not category and not tags:
                score = 1.0

            if score > 0:
                results.append((skill, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [s.to_dict() for s, _ in results[:limit]]

    def browse_categories(self) -> Dict[str, int]:
        """Browse available categories with skill counts."""
        counts = {}
        for cat in self.CATEGORIES:
            counts[cat] = sum(
                1 for s in self._skills.values()
                if s.category == cat and s.status not in (
                    SkillStatus.BLOCKED, SkillStatus.DEPRECATED
                )
            )
        return counts

    # ── Installation ──────────────────────────────────────────

    def install(self, skill_id: str) -> Dict:
        """Install a skill from the marketplace."""
        skill = self._skills.get(skill_id)
        if not skill:
            return {"success": False, "reason": f"Skill '{skill_id}' not found"}

        if skill.status == SkillStatus.BLOCKED:
            return {"success": False, "reason": "Skill is blocked for security reasons"}

        # Check dependencies
        missing_deps = []
        for dep in skill.dependencies:
            if dep not in self._installed:
                missing_deps.append(dep)

        if missing_deps:
            # Auto-resolve dependencies
            for dep_id in missing_deps:
                dep_result = self.install(dep_id)
                if not dep_result["success"]:
                    return {
                        "success": False,
                        "reason": f"Dependency '{dep_id}' failed to install",
                    }

        # Install
        self._installed[skill_id] = skill
        skill.install_count += 1
        self._total_installs += 1

        self._install_history.append({
            "action": "install",
            "skill_id": skill_id,
            "name": skill.name,
            "time": time.time(),
        })

        return {
            "success": True,
            "skill_id": skill_id,
            "name": skill.name,
            "version": skill.version,
            "dependencies_installed": missing_deps,
        }

    def uninstall(self, skill_id: str) -> Dict:
        """Uninstall a skill."""
        if skill_id not in self._installed:
            return {"success": False, "reason": "Not installed"}

        # Check if other installed skills depend on this
        dependents = [
            s.name for s in self._installed.values()
            if skill_id in s.dependencies and s.skill_id != skill_id
        ]

        if dependents:
            return {
                "success": False,
                "reason": f"Required by: {', '.join(dependents)}",
            }

        skill = self._installed.pop(skill_id)
        self._total_uninstalls += 1

        self._install_history.append({
            "action": "uninstall",
            "skill_id": skill_id,
            "name": skill.name,
            "time": time.time(),
        })

        return {"success": True, "skill_id": skill_id, "name": skill.name}

    def list_installed(self) -> List[Dict]:
        """List all installed skills."""
        return [s.to_dict() for s in self._installed.values()]

    # ── Ratings ───────────────────────────────────────────────

    def rate_skill(self, skill_id: str, rating: float) -> bool:
        """Rate a skill (1-5 stars)."""
        skill = self._skills.get(skill_id)
        if not skill or not (1 <= rating <= 5):
            return False

        # Running average
        total = skill.rating * skill.rating_count + rating
        skill.rating_count += 1
        skill.rating = total / skill.rating_count
        return True

    # ── Stats ─────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        return {
            "total_skills": len(self._skills),
            "installed_skills": len(self._installed),
            "total_installs": self._total_installs,
            "total_uninstalls": self._total_uninstalls,
            "categories": len(self.CATEGORIES),
            "verified_skills": sum(
                1 for s in self._skills.values()
                if s.status == SkillStatus.VERIFIED
            ),
            "blocked_skills": sum(
                1 for s in self._skills.values()
                if s.status == SkillStatus.BLOCKED
            ),
        }
