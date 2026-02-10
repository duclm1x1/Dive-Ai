"""
🏗️ HIERARCHICAL CONTEXT
Structured hierarchical context management

Based on V28's layer3_structuredhierarchicalcontext.py
"""

import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class ContextNode:
    """A node in the context hierarchy"""
    id: str
    content: str
    level: int
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    importance: float = 0.5


class HierarchicalContextAlgorithm(BaseAlgorithm):
    """
    🏗️ Hierarchical Context Manager
    
    Organizes context in hierarchical structure:
    - Project → Files → Functions → Details
    - Enables scoped context retrieval
    - Efficient memory usage
    
    From V28: layer3_structuredhierarchicalcontext.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="HierarchicalContext",
            name="Hierarchical Context",
            level="operational",
            category="context",
            version="1.0",
            description="Manage context in hierarchical structure",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "add/get/prune"),
                    IOField("node", "object", False, "Node to add"),
                    IOField("scope", "string", False, "Scope for retrieval")
                ],
                outputs=[
                    IOField("result", "object", True, "Operation result")
                ]
            ),
            steps=["Parse action", "Navigate hierarchy", "Execute operation", "Return result"],
            tags=["context", "hierarchy", "scoped", "memory"]
        )
        
        self.nodes: Dict[str, ContextNode] = {}
        self.root_ids: List[str] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "get")
        node_data = params.get("node", {})
        scope = params.get("scope", "")
        
        print(f"\n🏗️ Hierarchical Context")
        
        if action == "add":
            return self._add_node(node_data)
        elif action == "get":
            return self._get_context(scope)
        elif action == "prune":
            return self._prune(params.get("min_importance", 0.3))
        elif action == "stats":
            return self._stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _add_node(self, data: Dict) -> AlgorithmResult:
        node = ContextNode(
            id=data.get("id", str(len(self.nodes))),
            content=data.get("content", ""),
            level=data.get("level", 0),
            parent_id=data.get("parent_id"),
            importance=data.get("importance", 0.5)
        )
        
        self.nodes[node.id] = node
        
        # Link to parent
        if node.parent_id and node.parent_id in self.nodes:
            self.nodes[node.parent_id].children.append(node.id)
        else:
            self.root_ids.append(node.id)
        
        print(f"   Added: {node.id} (level {node.level})")
        
        return AlgorithmResult(
            status="success",
            data={"added": node.id, "total_nodes": len(self.nodes)}
        )
    
    def _get_context(self, scope: str) -> AlgorithmResult:
        if scope and scope in self.nodes:
            # Get subtree
            nodes = self._get_subtree(scope)
        else:
            # Get all
            nodes = list(self.nodes.values())
        
        # Sort by level then importance
        nodes.sort(key=lambda n: (n.level, -n.importance))
        
        context = "\n\n".join([
            f"[L{n.level}] {n.content}" for n in nodes
        ])
        
        print(f"   Retrieved: {len(nodes)} nodes")
        
        return AlgorithmResult(
            status="success",
            data={
                "context": context,
                "nodes": [{"id": n.id, "level": n.level} for n in nodes],
                "count": len(nodes)
            }
        )
    
    def _get_subtree(self, root_id: str) -> List[ContextNode]:
        if root_id not in self.nodes:
            return []
        
        result = [self.nodes[root_id]]
        for child_id in self.nodes[root_id].children:
            result.extend(self._get_subtree(child_id))
        
        return result
    
    def _prune(self, min_importance: float) -> AlgorithmResult:
        pruned = []
        for node_id, node in list(self.nodes.items()):
            if node.importance < min_importance and not node.children:
                del self.nodes[node_id]
                pruned.append(node_id)
                
                # Remove from parent
                if node.parent_id and node.parent_id in self.nodes:
                    parent = self.nodes[node.parent_id]
                    if node_id in parent.children:
                        parent.children.remove(node_id)
        
        print(f"   Pruned: {len(pruned)} nodes")
        
        return AlgorithmResult(
            status="success",
            data={"pruned": pruned, "remaining": len(self.nodes)}
        )
    
    def _stats(self) -> AlgorithmResult:
        levels = {}
        for node in self.nodes.values():
            levels[node.level] = levels.get(node.level, 0) + 1
        
        return AlgorithmResult(
            status="success",
            data={
                "total_nodes": len(self.nodes),
                "root_count": len(self.root_ids),
                "by_level": levels,
                "avg_importance": sum(n.importance for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0
            }
        )


def register(algorithm_manager):
    algo = HierarchicalContextAlgorithm()
    algorithm_manager.register("HierarchicalContext", algo)
    print("✅ HierarchicalContext registered")


if __name__ == "__main__":
    algo = HierarchicalContextAlgorithm()
    
    # Build hierarchy
    algo.execute({"action": "add", "node": {"id": "project", "content": "Dive AI Project", "level": 0}})
    algo.execute({"action": "add", "node": {"id": "core", "content": "Core module", "level": 1, "parent_id": "project"}})
    algo.execute({"action": "add", "node": {"id": "algo", "content": "Algorithms", "level": 2, "parent_id": "core"}})
    
    # Get context
    result = algo.execute({"action": "get", "scope": "core"})
    print(f"\nContext:\n{result.data['context']}")
