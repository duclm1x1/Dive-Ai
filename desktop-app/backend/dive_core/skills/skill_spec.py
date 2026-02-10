"""
Dive AI Skill Specification — Algorithm-Verified Skills
Every skill has formal input/output schemas, verification, cost tracking, and combo support.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
from enum import Enum


class SkillCategory(str, Enum):
    BROWSER = "browser"
    SEARCH = "search"
    COMMUNICATION = "communication"
    DEVOPS = "devops"
    AI = "ai"
    PRODUCTIVITY = "productivity"
    SYSTEM = "system"
    DATA = "data"
    MEDIA = "media"
    FINANCE = "finance"
    SMART_HOME = "smart_home"
    CODING = "coding"
    GIT = "git"
    CUSTOM = "custom"


@dataclass
class SkillSpec:
    """
    Extended AlgorithmSpec for skills.
    Dive AI advantage: verification + combo chaining + cost tracking.
    """
    # Identity
    name: str
    description: str
    version: str = "1.0.0"
    category: SkillCategory = SkillCategory.CUSTOM
    author: str = "dive-ai"

    # Algorithm properties
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    verifier: Optional[Callable] = None
    cost_per_call: float = 0.0

    # Discovery
    tags: List[str] = field(default_factory=list)
    trigger_patterns: List[str] = field(default_factory=list)

    # Combo chaining
    combo_compatible: List[str] = field(default_factory=list)
    combo_position: str = "any"  # "start", "middle", "end", "any"
    max_chain_depth: int = 5

    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    python_packages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category.value,
            "author": self.author,
            "tags": self.tags,
            "cost_per_call": self.cost_per_call,
            "combo_position": self.combo_position,
            "combo_compatible": self.combo_compatible,
            "has_verifier": self.verifier is not None,
        }
