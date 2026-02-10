"""
Semantic Code Weaving (SCW) - Skill Implementation

This skill provides a framework for building and managing an 'intent graph' 
from user requirements, ensuring that all generated code maps directly to a specific goal.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class IntentNode:
    """Represents a single functional requirement in the intent graph."""
    node_id: str
    name: str
    description: str
    node_type: str  # e.g., 'feature', 'component', 'data_model'
    dependencies: List[str] = field(default_factory=list)
    is_implemented: bool = False

class SemanticCodeWeaver:
    """Manages the construction and traversal of the intent graph."""

    def __init__(self):
        self.graph: Dict[str, IntentNode] = {}
        logger.info("Semantic Code Weaver initialized.")

    def add_node(self, name: str, description: str, node_type: str, dependencies: Optional[List[str]] = None) -> str:
        """Adds a new intent node to the graph."""
        node_id = f"NODE-{uuid.uuid4().hex[:6].upper()}"
        
        if dependencies:
            for dep_id in dependencies:
                if dep_id not in self.graph:
                    raise ValueError(f"Dependency '{dep_id}' not found in the graph.")

        node = IntentNode(
            node_id=node_id,
            name=name,
            description=description,
            node_type=node_type,
            dependencies=dependencies or []
        )
        self.graph[node_id] = node
        logger.info(f"Added intent node '{node_id}' ({name}) to the graph.")
        return node_id

    def get_node(self, node_id: str) -> Optional[IntentNode]:
        """Retrieves a node by its ID."""
        return self.graph.get(node_id)

    def mark_as_implemented(self, node_id: str):
        """Marks a node as having its code implemented."""
        node = self.get_node(node_id)
        if not node:
            raise ValueError(f"Node '{node_id}' not found.")
        node.is_implemented = True
        logger.info(f"Node '{node_id}' marked as implemented.")

    def get_implementation_order(self) -> List[str]:
        """Returns a valid, topologically sorted order for implementation."""
        sorted_order = []
        visited = set()
        
        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            node = self.graph[node_id]
            for dep_id in node.dependencies:
                visit(dep_id)
            sorted_order.append(node_id)

        for node_id in self.graph:
            if node_id not in visited:
                visit(node_id)
        
        return sorted_order

    def get_unimplemented_nodes(self) -> List[IntentNode]:
        """Returns a list of all nodes that have not been implemented yet."""
        return [node for node in self.graph.values() if not node.is_implemented]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the graph to a dictionary."""
        return {
            "nodes": {node_id: node.__dict__ for node_id, node in self.graph.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticCodeWeaver':
        """Deserializes a graph from a dictionary."""
        weaver = cls()
        for node_id, node_data in data.get("nodes", {}).items():
            weaver.graph[node_id] = IntentNode(**node_data)
        return weaver
