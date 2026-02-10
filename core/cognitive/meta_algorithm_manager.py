"""
Dive AI V29 - Meta-Algorithm Manager
Manages Strategy-tier algorithms (Meta-Algorithms)

Features:
- Registry for Meta-Algorithms
- Selector for choosing best strategy (using Reasoning)
- Execution tracking
"""

import os
import sys
import threading
from typing import Dict, Any, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult
from core.reasoning.algorithm_suggester import get_algorithm_suggester


class MetaAlgorithmManager:
    """
    Manager for Meta-Algorithms (Strategies)
    """
    
    def __init__(self):
        self.registry: Dict[str, BaseMetaAlgorithm] = {}
        self.active_executions: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Load reasoning engine
        self.suggester = get_algorithm_suggester()
    
    def register(self, algorithm_id: str, meta_algorithm: BaseMetaAlgorithm):
        """Register a meta-algorithm"""
        with self._lock:
            self.registry[algorithm_id] = meta_algorithm
            print(f"📦 Registered Meta-Algorithm: {algorithm_id}")
            
            # Also register with the AlgorithmSuggester so it can be suggested!
            # (In a real system, we'd add it to the suggester's DB)
    
    def get_algorithm(self, algorithm_id: str) -> Optional[BaseMetaAlgorithm]:
        """Get algorithm by ID"""
        return self.registry.get(algorithm_id)
    
    def list_algorithms(self) -> List[Dict]:
        """List registered algorithms"""
        return [
            {
                "id": algo.spec.algorithm_id,
                "name": algo.spec.name,
                "description": algo.spec.description
            }
            for algo in self.registry.values()
        ]
    
    def select_best_strategy(self, request: str) -> Optional[BaseMetaAlgorithm]:
        """
        Select best meta-algorithm for request
        Currently uses simple matching, but should use Validator/Selector
        """
        # 1. Ask Algorithm Suggester
        suggestions = self.suggester.suggest(request, top_n=3)
        
        for suggestion in suggestions:
            # Check if suggested algo is a registered meta-algorithm
            if suggestion.algorithm in self.registry:
                return self.registry[suggestion.algorithm]
        
        # 2. Fallback: Keyword matching
        request_lower = request.lower()
        for algo_id, algo in self.registry.items():
            if algo_id.lower() in request_lower or \
               any(tag in request_lower for tag in algo.spec.tags):
                return algo
        
        return None
    
    def execute_strategy(self, request: str, context: Dict = None) -> AlgorithmResult:
        """Find and execute best strategy"""
        strategy = self.select_best_strategy(request)
        
        if not strategy:
            return AlgorithmResult(
                status="error",
                error=f"No suitable strategy found for: {request}"
            )
        
        print(f"🎯 Selected Strategy: {strategy.spec.name}")
        return strategy.execute({
            "request": request,
            "goal": request,
            "context": context or {}
        })


# Singleton
_meta_manager = None

def get_meta_algorithm_manager() -> MetaAlgorithmManager:
    """Get singleton manager"""
    global _meta_manager
    if _meta_manager is None:
        _meta_manager = MetaAlgorithmManager()
    return _meta_manager
