"""
🔄 CROSS-EXPERT KNOWLEDGE SHARING (CEKS)
Share knowledge between specialized expert agents

Based on V28's layer6_crossexpertknowledgesharing.py + ceks/
"""

import os
import sys
import time
from typing import Dict, Any, List, Set
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class KnowledgeNode:
    """A piece of knowledge"""
    id: str
    topic: str
    content: Any
    source_expert: str
    confidence: float
    related_topics: List[str] = field(default_factory=list)


@dataclass
class Expert:
    """An expert agent with specialized knowledge"""
    id: str
    domain: str
    knowledge_ids: Set[str] = field(default_factory=set)
    trust_score: float = 1.0


class KnowledgeSharingAlgorithm(BaseAlgorithm):
    """
    🔄 Cross-Expert Knowledge Sharing (CEKS)
    
    Enables knowledge exchange:
    - Knowledge graph building
    - Cross-domain insights
    - Trust-weighted sharing
    - Conflict resolution
    
    From V28: CEKS module (7/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="KnowledgeSharing",
            name="Knowledge Sharing (CEKS)",
            level="operational",
            category="learning",
            version="1.0",
            description="Cross-expert knowledge sharing",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "share/query/connect"),
                    IOField("knowledge", "object", False, "Knowledge to share"),
                    IOField("query", "string", False, "Query topic")
                ],
                outputs=[
                    IOField("result", "object", True, "Sharing result")
                ]
            ),
            steps=["Register knowledge", "Build connections", "Resolve conflicts", "Share cross-domain"],
            tags=["knowledge", "sharing", "experts", "cross-domain"]
        )
        
        self.knowledge_base: Dict[str, KnowledgeNode] = {}
        self.experts: Dict[str, Expert] = {}
        self.connections: List[tuple] = []  # (id1, id2, strength)
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "query")
        
        print(f"\n🔄 Knowledge Sharing (CEKS)")
        
        if action == "share":
            return self._share_knowledge(params.get("knowledge", {}))
        elif action == "query":
            return self._query_knowledge(params.get("query", ""))
        elif action == "connect":
            return self._build_connections()
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _share_knowledge(self, data: Dict) -> AlgorithmResult:
        knowledge = KnowledgeNode(
            id=f"k_{len(self.knowledge_base)}",
            topic=data.get("topic", ""),
            content=data.get("content"),
            source_expert=data.get("source", "unknown"),
            confidence=data.get("confidence", 0.8),
            related_topics=data.get("related", [])
        )
        self.knowledge_base[knowledge.id] = knowledge
        
        # Register expert
        if knowledge.source_expert not in self.experts:
            self.experts[knowledge.source_expert] = Expert(
                id=knowledge.source_expert,
                domain=data.get("domain", "general")
            )
        self.experts[knowledge.source_expert].knowledge_ids.add(knowledge.id)
        
        print(f"   Shared: {knowledge.topic} from {knowledge.source_expert}")
        
        return AlgorithmResult(
            status="success",
            data={
                "shared": knowledge.id,
                "topic": knowledge.topic,
                "total_knowledge": len(self.knowledge_base)
            }
        )
    
    def _query_knowledge(self, query: str) -> AlgorithmResult:
        if not query:
            # Return all knowledge
            return AlgorithmResult(
                status="success",
                data={
                    "total": len(self.knowledge_base),
                    "topics": [k.topic for k in self.knowledge_base.values()][:20]
                }
            )
        
        # Search
        matches = []
        query_lower = query.lower()
        
        for k in self.knowledge_base.values():
            score = 0
            if query_lower in k.topic.lower():
                score += 10
            if any(query_lower in r.lower() for r in k.related_topics):
                score += 5
            if score > 0:
                matches.append((score * k.confidence, k))
        
        matches.sort(key=lambda x: -x[0])
        
        results = [
            {"id": k.id, "topic": k.topic, "confidence": k.confidence, "source": k.source_expert}
            for _, k in matches[:10]
        ]
        
        print(f"   Found: {len(results)} matches for '{query}'")
        
        return AlgorithmResult(
            status="success",
            data={"query": query, "results": results, "count": len(results)}
        )
    
    def _build_connections(self) -> AlgorithmResult:
        # Connect related knowledge nodes
        new_connections = 0
        knowledge_list = list(self.knowledge_base.values())
        
        for i, k1 in enumerate(knowledge_list):
            for k2 in knowledge_list[i+1:]:
                # Check topic overlap
                if k1.topic in k2.related_topics or k2.topic in k1.related_topics:
                    strength = 0.8
                elif any(t in k2.related_topics for t in k1.related_topics):
                    strength = 0.5
                else:
                    continue
                
                self.connections.append((k1.id, k2.id, strength))
                new_connections += 1
        
        print(f"   Built {new_connections} connections")
        
        return AlgorithmResult(
            status="success",
            data={
                "connections_created": new_connections,
                "total_connections": len(self.connections)
            }
        )
    
    def _get_stats(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "total_knowledge": len(self.knowledge_base),
                "total_experts": len(self.experts),
                "total_connections": len(self.connections),
                "experts": [
                    {"id": e.id, "domain": e.domain, "knowledge_count": len(e.knowledge_ids)}
                    for e in self.experts.values()
                ]
            }
        )


def register(algorithm_manager):
    algo = KnowledgeSharingAlgorithm()
    algorithm_manager.register("KnowledgeSharing", algo)
    print("✅ KnowledgeSharing registered")


if __name__ == "__main__":
    algo = KnowledgeSharingAlgorithm()
    algo.execute({"action": "share", "knowledge": {"topic": "Python typing", "source": "code_expert", "related": ["type hints"]}})
    algo.execute({"action": "share", "knowledge": {"topic": "Type hints", "source": "python_expert", "related": ["Python typing"]}})
    algo.execute({"action": "connect"})
    result = algo.execute({"action": "query", "query": "typing"})
    print(f"Found: {result.data['count']} results")
