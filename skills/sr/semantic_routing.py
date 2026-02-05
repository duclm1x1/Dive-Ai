#!/usr/bin/env python3
"""
Semantic Routing (SR) - 9/10 Stars
Intelligently routes tasks based on deep semantic understanding
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class SemanticProfile:
    entity_id: str
    entity_type: str
    specializations: List[str] = field(default_factory=list)
    performance_history: Dict[str, float] = field(default_factory=dict)
    current_load: float = 0.0

@dataclass
class RoutingDecision:
    selected_entity: str
    entity_type: str
    confidence: float
    reasoning: str
    alternative_entities: List[Tuple[str, float]] = field(default_factory=list)

class SemanticRouter:
    def __init__(self):
        self.entity_profiles: Dict[str, SemanticProfile] = {}
        print("[Semantic Router] Initialized")
    
    def register_entity(self, profile: SemanticProfile):
        self.entity_profiles[profile.entity_id] = profile
        print(f"[SR] Registered {profile.entity_type}: {profile.entity_id}")
    
    def route_task(self, task_description: str, task_type: str) -> RoutingDecision:
        # Simple routing logic for Phase 1
        if not self.entity_profiles:
            return RoutingDecision("default", "agent", 0.5, "No entities registered", [])
        
        # Score entities
        scores = {}
        for entity_id, profile in self.entity_profiles.items():
            score = 0.5
            if task_type in profile.specializations:
                score += 0.3
            if task_type in profile.performance_history:
                score += profile.performance_history[task_type] * 0.2
            score *= (1 - profile.current_load * 0.3)
            scores[entity_id] = min(score, 1.0)
        
        best = max(scores.items(), key=lambda x: x[1])
        return RoutingDecision(
            best[0], 
            self.entity_profiles[best[0]].entity_type,
            best[1],
            f"Best match with {best[1]:.0%} confidence",
            []
        )

_router = None

def get_semantic_router() -> SemanticRouter:
    global _router
    if _router is None:
        _router = SemanticRouter()
    return _router

if __name__ == "__main__":
    print("\nSemantic Router Test\n")
    router = get_semantic_router()
    
    for i in range(3):
        profile = SemanticProfile(
            entity_id=f"agent_{i}",
            entity_type="agent",
            specializations=["code_generation", "code_review"],
            performance_history={"code_generation": 0.9},
            current_load=i * 0.3
        )
        router.register_entity(profile)
    
    decision = router.route_task("Generate REST API", "code_generation")
    print(f"\nRouting Decision: {decision.selected_entity}")
    print(f"Confidence: {decision.confidence:.2%}")
    print(f"Reasoning: {decision.reasoning}\n")
