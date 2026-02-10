"""
💉 DEPENDENCY INJECTOR
Manage dependencies via injection

Based on V28's core_engine/dependency_injector.py
"""

import os
import sys
from typing import Dict, Any, Type, Optional, Callable
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class Dependency:
    """A registered dependency"""
    name: str
    type: str  # singleton, factory, instance
    resolver: Callable
    instance: Any = None


class DependencyInjectorAlgorithm(BaseAlgorithm):
    """
    💉 Dependency Injector
    
    Manages dependencies:
    - Singleton registration
    - Factory injection
    - Lazy initialization
    - Scoped dependencies
    
    From V28: core_engine/dependency_injector.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="DependencyInjector",
            name="Dependency Injector",
            level="operational",
            category="system",
            version="1.0",
            description="Manage dependencies via injection",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "register/resolve/list"),
                    IOField("name", "string", False, "Dependency name"),
                    IOField("type", "string", False, "Dependency type")
                ],
                outputs=[
                    IOField("result", "any", True, "Dependency or status")
                ]
            ),
            steps=["Register dependencies", "Resolve on demand", "Cache singletons", "Manage lifecycle"],
            tags=["dependency", "injection", "ioc"]
        )
        
        self.dependencies: Dict[str, Dependency] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "list")
        
        print(f"\n💉 Dependency Injector")
        
        if action == "register":
            return self._register(
                params.get("name", ""),
                params.get("type", "singleton"),
                params.get("factory")
            )
        elif action == "resolve":
            return self._resolve(params.get("name", ""))
        elif action == "list":
            return self._list()
        elif action == "clear":
            return self._clear()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _register(self, name: str, dep_type: str, factory: Optional[Callable]) -> AlgorithmResult:
        if not name:
            return AlgorithmResult(status="error", error="Dependency name required")
        
        # Create a default factory if none provided
        if factory is None:
            factory = lambda: {"name": name}
        
        self.dependencies[name] = Dependency(
            name=name,
            type=dep_type,
            resolver=factory
        )
        
        print(f"   Registered: {name} ({dep_type})")
        
        return AlgorithmResult(
            status="success",
            data={"registered": name, "type": dep_type}
        )
    
    def _resolve(self, name: str) -> AlgorithmResult:
        if name not in self.dependencies:
            return AlgorithmResult(status="error", error=f"Dependency not found: {name}")
        
        dep = self.dependencies[name]
        
        if dep.type == "singleton":
            if dep.instance is None:
                dep.instance = dep.resolver()
            instance = dep.instance
        elif dep.type == "factory":
            instance = dep.resolver()
        else:
            instance = dep.resolver()
        
        return AlgorithmResult(
            status="success",
            data={"name": name, "type": dep.type, "resolved": True}
        )
    
    def _list(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "dependencies": [
                    {"name": d.name, "type": d.type, "instantiated": d.instance is not None}
                    for d in self.dependencies.values()
                ],
                "count": len(self.dependencies)
            }
        )
    
    def _clear(self) -> AlgorithmResult:
        count = len(self.dependencies)
        self.dependencies.clear()
        return AlgorithmResult(status="success", data={"cleared": count})


def register(algorithm_manager):
    algo = DependencyInjectorAlgorithm()
    algorithm_manager.register("DependencyInjector", algo)
    print("✅ DependencyInjector registered")


if __name__ == "__main__":
    algo = DependencyInjectorAlgorithm()
    algo.execute({"action": "register", "name": "db", "type": "singleton"})
    algo.execute({"action": "register", "name": "logger", "type": "factory"})
    result = algo.execute({"action": "list"})
    print(f"Registered: {result.data['count']} dependencies")
