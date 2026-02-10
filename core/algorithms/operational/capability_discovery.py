"""
🔍 CAPABILITY DISCOVERY
Discover and catalog system capabilities

Based on V28's core_engine/capability_discovery.py
"""

import os
import sys
import importlib
from typing import Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class Capability:
    """A discovered capability"""
    id: str
    name: str
    category: str
    description: str
    source: str
    parameters: List[str] = field(default_factory=list)


class CapabilityDiscoveryAlgorithm(BaseAlgorithm):
    """
    🔍 Capability Discovery
    
    Discovers system capabilities:
    - Algorithm detection
    - Tool discovery
    - API enumeration
    - Skill cataloging
    
    From V28: core_engine/capability_discovery.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="CapabilityDiscovery",
            name="Capability Discovery",
            level="operational",
            category="meta",
            version="1.0",
            description="Discover and catalog system capabilities",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "discover/list/search"),
                    IOField("category", "string", False, "Filter by category"),
                    IOField("query", "string", False, "Search query")
                ],
                outputs=[
                    IOField("capabilities", "array", True, "Discovered capabilities")
                ]
            ),
            steps=["Scan modules", "Extract metadata", "Catalog capabilities", "Index for search"],
            tags=["discovery", "capability", "meta"]
        )
        
        self.capabilities: Dict[str, Capability] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "discover")
        
        print(f"\n🔍 Capability Discovery")
        
        if action == "discover":
            return self._discover_capabilities()
        elif action == "list":
            return self._list_capabilities(params.get("category"))
        elif action == "search":
            return self._search_capabilities(params.get("query", ""))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _discover_capabilities(self) -> AlgorithmResult:
        discovered = 0
        
        # Discover algorithms
        algo_dir = Path(__file__).parent
        for py_file in algo_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            capability = Capability(
                id=py_file.stem,
                name=py_file.stem.replace("_", " ").title(),
                category="algorithm",
                description=f"Algorithm: {py_file.stem}",
                source=str(py_file)
            )
            self.capabilities[capability.id] = capability
            discovered += 1
        
        # Add built-in capabilities
        built_ins = [
            Capability("file_operations", "File Operations", "tool", "Read, write, and manage files", "built-in"),
            Capability("code_execution", "Code Execution", "tool", "Execute code in various languages", "built-in"),
            Capability("web_browsing", "Web Browsing", "tool", "Browse and interact with web pages", "built-in"),
            Capability("model_inference", "Model Inference", "api", "Call LLM models for inference", "built-in")
        ]
        
        for cap in built_ins:
            self.capabilities[cap.id] = cap
            discovered += 1
        
        print(f"   Discovered: {discovered} capabilities")
        
        return AlgorithmResult(
            status="success",
            data={
                "discovered": discovered,
                "by_category": self._group_by_category()
            }
        )
    
    def _list_capabilities(self, category: str = None) -> AlgorithmResult:
        caps = list(self.capabilities.values())
        
        if category:
            caps = [c for c in caps if c.category == category]
        
        return AlgorithmResult(
            status="success",
            data={
                "capabilities": [
                    {"id": c.id, "name": c.name, "category": c.category, "description": c.description}
                    for c in caps
                ],
                "count": len(caps)
            }
        )
    
    def _search_capabilities(self, query: str) -> AlgorithmResult:
        if not query:
            return self._list_capabilities()
        
        query_lower = query.lower()
        matches = [
            c for c in self.capabilities.values()
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]
        
        return AlgorithmResult(
            status="success",
            data={
                "query": query,
                "results": [
                    {"id": c.id, "name": c.name, "category": c.category}
                    for c in matches
                ],
                "count": len(matches)
            }
        )
    
    def _group_by_category(self) -> Dict[str, int]:
        groups = {}
        for cap in self.capabilities.values():
            groups[cap.category] = groups.get(cap.category, 0) + 1
        return groups


def register(algorithm_manager):
    algo = CapabilityDiscoveryAlgorithm()
    algorithm_manager.register("CapabilityDiscovery", algo)
    print("✅ CapabilityDiscovery registered")


if __name__ == "__main__":
    algo = CapabilityDiscoveryAlgorithm()
    result = algo.execute({"action": "discover"})
    print(f"Discovered: {result.data['discovered']} capabilities")
