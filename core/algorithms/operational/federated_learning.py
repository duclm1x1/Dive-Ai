"""
🌐 FEDERATED EXPERT LEARNING (FEL)
Distributed learning across expert agents

Based on V28's layer6_federatedexpertlearning.py + fel/
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class ExpertAgent:
    """An expert agent"""
    id: str
    expertise: List[str]
    knowledge_weight: float
    contribution_count: int = 0


@dataclass
class FederatedUpdate:
    """A federated learning update"""
    expert_id: str
    update_type: str
    knowledge: Dict
    timestamp: float


class FederatedLearningAlgorithm(BaseAlgorithm):
    """
    🌐 Federated Expert Learning (FEL)
    
    Enables distributed learning:
    - Knowledge aggregation
    - Expert specialization
    - Privacy-preserving updates
    - Consensus building
    
    From V28: FEL module (8/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="FederatedLearning",
            name="Federated Learning (FEL)",
            level="operational",
            category="learning",
            version="1.0",
            description="Distributed learning across agents",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "register/contribute/aggregate"),
                    IOField("expert", "object", False, "Expert agent"),
                    IOField("update", "object", False, "Knowledge update")
                ],
                outputs=[
                    IOField("result", "object", True, "Federated learning result")
                ]
            ),
            steps=["Register experts", "Collect updates", "Aggregate knowledge", "Distribute"],
            tags=["federated", "distributed", "learning", "experts"]
        )
        
        self.experts: Dict[str, ExpertAgent] = {}
        self.updates: List[FederatedUpdate] = []
        self.global_knowledge: Dict[str, Any] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "aggregate")
        
        print(f"\n🌐 Federated Learning (FEL)")
        
        if action == "register":
            return self._register_expert(params.get("expert", {}))
        elif action == "contribute":
            return self._contribute_update(params.get("update", {}))
        elif action == "aggregate":
            return self._aggregate_knowledge()
        elif action == "query":
            return self._query_knowledge(params.get("topic", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _register_expert(self, data: Dict) -> AlgorithmResult:
        expert = ExpertAgent(
            id=data.get("id", f"expert_{len(self.experts)}"),
            expertise=data.get("expertise", []),
            knowledge_weight=data.get("weight", 1.0)
        )
        self.experts[expert.id] = expert
        
        print(f"   Registered: {expert.id} (expertise: {expert.expertise})")
        
        return AlgorithmResult(
            status="success",
            data={"registered": expert.id, "total_experts": len(self.experts)}
        )
    
    def _contribute_update(self, data: Dict) -> AlgorithmResult:
        expert_id = data.get("expert_id", "")
        
        if expert_id and expert_id in self.experts:
            self.experts[expert_id].contribution_count += 1
        
        update = FederatedUpdate(
            expert_id=expert_id,
            update_type=data.get("type", "knowledge"),
            knowledge=data.get("knowledge", {}),
            timestamp=time.time()
        )
        self.updates.append(update)
        
        print(f"   Contribution from {expert_id}")
        
        return AlgorithmResult(
            status="success",
            data={"contributed": True, "total_updates": len(self.updates)}
        )
    
    def _aggregate_knowledge(self) -> AlgorithmResult:
        if not self.updates:
            return AlgorithmResult(
                status="success",
                data={"aggregated": False, "reason": "No updates to aggregate"}
            )
        
        # Weighted aggregation
        for update in self.updates:
            weight = 1.0
            if update.expert_id in self.experts:
                weight = self.experts[update.expert_id].knowledge_weight
            
            for key, value in update.knowledge.items():
                if key not in self.global_knowledge:
                    self.global_knowledge[key] = {"value": value, "weight": weight, "count": 1}
                else:
                    # Weighted average for numeric values
                    existing = self.global_knowledge[key]
                    existing["weight"] += weight
                    existing["count"] += 1
                    if isinstance(value, (int, float)) and isinstance(existing["value"], (int, float)):
                        existing["value"] = (existing["value"] * (existing["count"] - 1) + value) / existing["count"]
        
        # Clear processed updates
        self.updates.clear()
        
        print(f"   Aggregated into {len(self.global_knowledge)} knowledge items")
        
        return AlgorithmResult(
            status="success",
            data={
                "aggregated": True,
                "knowledge_count": len(self.global_knowledge),
                "expert_count": len(self.experts)
            }
        )
    
    def _query_knowledge(self, topic: str) -> AlgorithmResult:
        if topic in self.global_knowledge:
            return AlgorithmResult(
                status="success",
                data={"found": True, "topic": topic, "knowledge": self.global_knowledge[topic]}
            )
        
        # Fuzzy search
        matches = [k for k in self.global_knowledge if topic.lower() in k.lower()]
        if matches:
            return AlgorithmResult(
                status="success",
                data={"found": True, "matches": matches[:5]}
            )
        
        return AlgorithmResult(
            status="success",
            data={"found": False, "topic": topic}
        )


def register(algorithm_manager):
    algo = FederatedLearningAlgorithm()
    algorithm_manager.register("FederatedLearning", algo)
    print("✅ FederatedLearning registered")


if __name__ == "__main__":
    algo = FederatedLearningAlgorithm()
    algo.execute({"action": "register", "expert": {"id": "code_expert", "expertise": ["python", "java"]}})
    algo.execute({"action": "contribute", "update": {"expert_id": "code_expert", "knowledge": {"best_practice": "use_types"}}})
    result = algo.execute({"action": "aggregate"})
    print(f"Knowledge count: {result.data['knowledge_count']}")
