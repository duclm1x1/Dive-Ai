#!/usr/bin/env python3
"""
Dive RAG Router - V22 Adaptive RAG Component

Routes queries to optimal retrieval strategy based on classification.
Part of the Adaptive RAG transformation (Week 8).
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

from core.dive_query_classifier import QueryType, QueryComplexity, QueryClassification


class RetrievalStrategy(Enum):
    """RAG retrieval strategies"""
    DENSE = "dense"  # Dense vector retrieval
    SPARSE = "sparse"  # BM25/keyword retrieval
    HYBRID = "hybrid"  # Dense + Sparse
    PROPOSITION = "proposition"  # Proposition-based
    MULTI_HOP = "multi_hop"  # Multi-hop reasoning
    PARALLEL = "parallel"  # Parallel retrieval
    SEQUENTIAL = "sequential"  # Sequential retrieval


@dataclass
class RoutingDecision:
    """RAG routing decision"""
    strategy: RetrievalStrategy
    parameters: Dict
    reasoning: str
    estimated_quality: float
    estimated_latency: float


class DiveRAGRouter:
    """
    Routes queries to optimal RAG strategy.
    
    The RAG Router is the key to Adaptive RAG - it ensures
    each query uses the best retrieval strategy for its type.
    
    Strategy Selection:
    - Factual queries → Dense retrieval (fast, accurate)
    - Conceptual queries → Proposition-based (comprehensive)
    - Procedural queries → Sequential retrieval (step-by-step)
    - Analytical queries → Multi-hop reasoning (deep)
    - Comparative queries → Parallel retrieval (compare)
    - Creative queries → Hybrid (diverse)
    """
    
    def __init__(self):
        # Strategy mapping
        self.strategy_map = {
            QueryType.FACTUAL: {
                QueryComplexity.SIMPLE: RetrievalStrategy.DENSE,
                QueryComplexity.MODERATE: RetrievalStrategy.HYBRID,
                QueryComplexity.COMPLEX: RetrievalStrategy.HYBRID
            },
            QueryType.CONCEPTUAL: {
                QueryComplexity.SIMPLE: RetrievalStrategy.DENSE,
                QueryComplexity.MODERATE: RetrievalStrategy.PROPOSITION,
                QueryComplexity.COMPLEX: RetrievalStrategy.PROPOSITION
            },
            QueryType.PROCEDURAL: {
                QueryComplexity.SIMPLE: RetrievalStrategy.DENSE,
                QueryComplexity.MODERATE: RetrievalStrategy.SEQUENTIAL,
                QueryComplexity.COMPLEX: RetrievalStrategy.SEQUENTIAL
            },
            QueryType.ANALYTICAL: {
                QueryComplexity.SIMPLE: RetrievalStrategy.HYBRID,
                QueryComplexity.MODERATE: RetrievalStrategy.MULTI_HOP,
                QueryComplexity.COMPLEX: RetrievalStrategy.MULTI_HOP
            },
            QueryType.COMPARATIVE: {
                QueryComplexity.SIMPLE: RetrievalStrategy.HYBRID,
                QueryComplexity.MODERATE: RetrievalStrategy.PARALLEL,
                QueryComplexity.COMPLEX: RetrievalStrategy.PARALLEL
            },
            QueryType.CREATIVE: {
                QueryComplexity.SIMPLE: RetrievalStrategy.DENSE,
                QueryComplexity.MODERATE: RetrievalStrategy.HYBRID,
                QueryComplexity.COMPLEX: RetrievalStrategy.HYBRID
            }
        }
        
        # Strategy parameters
        self.strategy_params = {
            RetrievalStrategy.DENSE: {
                'top_k': 5,
                'similarity_threshold': 0.7
            },
            RetrievalStrategy.SPARSE: {
                'top_k': 10,
                'min_score': 0.5
            },
            RetrievalStrategy.HYBRID: {
                'dense_weight': 0.7,
                'sparse_weight': 0.3,
                'top_k': 10
            },
            RetrievalStrategy.PROPOSITION: {
                'top_k': 20,
                'chunk_size': 'proposition',
                'rerank': True
            },
            RetrievalStrategy.MULTI_HOP: {
                'max_hops': 3,
                'top_k_per_hop': 5
            },
            RetrievalStrategy.PARALLEL: {
                'num_branches': 2,
                'top_k_per_branch': 5
            },
            RetrievalStrategy.SEQUENTIAL: {
                'max_steps': 5,
                'top_k_per_step': 3
            }
        }
        
        # Performance characteristics
        self.strategy_performance = {
            RetrievalStrategy.DENSE: {'quality': 0.8, 'latency': 0.1},
            RetrievalStrategy.SPARSE: {'quality': 0.7, 'latency': 0.05},
            RetrievalStrategy.HYBRID: {'quality': 0.85, 'latency': 0.15},
            RetrievalStrategy.PROPOSITION: {'quality': 0.9, 'latency': 0.3},
            RetrievalStrategy.MULTI_HOP: {'quality': 0.95, 'latency': 0.5},
            RetrievalStrategy.PARALLEL: {'quality': 0.9, 'latency': 0.4},
            RetrievalStrategy.SEQUENTIAL: {'quality': 0.85, 'latency': 0.35}
        }
    
    def route(
        self,
        classification: QueryClassification,
        constraints: Optional[Dict] = None
    ) -> RoutingDecision:
        """
        Route query to optimal strategy.
        
        Args:
            classification: Query classification
            constraints: Optional constraints (latency, quality)
            
        Returns:
            RoutingDecision with strategy and parameters
        """
        # Get base strategy from mapping
        strategy = self.strategy_map[classification.query_type][classification.complexity]
        
        # Apply constraints if provided
        if constraints:
            strategy = self._apply_constraints(strategy, constraints)
        
        # Get parameters
        parameters = self.strategy_params[strategy].copy()
        
        # Get performance characteristics
        perf = self.strategy_performance[strategy]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            classification.query_type,
            classification.complexity,
            strategy
        )
        
        return RoutingDecision(
            strategy=strategy,
            parameters=parameters,
            reasoning=reasoning,
            estimated_quality=perf['quality'],
            estimated_latency=perf['latency']
        )
    
    def _apply_constraints(
        self,
        strategy: RetrievalStrategy,
        constraints: Dict
    ) -> RetrievalStrategy:
        """Apply constraints to strategy selection"""
        
        # If latency constraint is tight, use faster strategy
        if constraints.get('max_latency', 1.0) < 0.2:
            if strategy in [RetrievalStrategy.MULTI_HOP, RetrievalStrategy.PARALLEL]:
                return RetrievalStrategy.HYBRID
            if strategy == RetrievalStrategy.PROPOSITION:
                return RetrievalStrategy.DENSE
        
        # If quality requirement is high, use better strategy
        if constraints.get('min_quality', 0.0) > 0.9:
            if strategy == RetrievalStrategy.DENSE:
                return RetrievalStrategy.HYBRID
            if strategy == RetrievalStrategy.SPARSE:
                return RetrievalStrategy.HYBRID
        
        return strategy
    
    def _generate_reasoning(
        self,
        query_type: QueryType,
        complexity: QueryComplexity,
        strategy: RetrievalStrategy
    ) -> str:
        """Generate human-readable reasoning for strategy selection"""
        
        reasons = {
            (QueryType.FACTUAL, RetrievalStrategy.DENSE): 
                "Factual query best served by dense retrieval for precise matching",
            (QueryType.CONCEPTUAL, RetrievalStrategy.PROPOSITION):
                "Conceptual query needs proposition-based retrieval for comprehensive understanding",
            (QueryType.PROCEDURAL, RetrievalStrategy.SEQUENTIAL):
                "Procedural query requires sequential retrieval to maintain step order",
            (QueryType.ANALYTICAL, RetrievalStrategy.MULTI_HOP):
                "Analytical query benefits from multi-hop reasoning for deep analysis",
            (QueryType.COMPARATIVE, RetrievalStrategy.PARALLEL):
                "Comparative query uses parallel retrieval to compare multiple options",
            (QueryType.CREATIVE, RetrievalStrategy.HYBRID):
                "Creative query leverages hybrid retrieval for diverse perspectives"
        }
        
        key = (query_type, strategy)
        return reasons.get(key, f"Using {strategy.value} strategy for {query_type.value} query")
    
    def get_strategy_info(self, strategy: RetrievalStrategy) -> Dict:
        """Get detailed information about a strategy"""
        return {
            'strategy': strategy.value,
            'parameters': self.strategy_params[strategy],
            'performance': self.strategy_performance[strategy],
            'description': self._get_strategy_description(strategy)
        }
    
    def _get_strategy_description(self, strategy: RetrievalStrategy) -> str:
        """Get strategy description"""
        descriptions = {
            RetrievalStrategy.DENSE: "Dense vector retrieval using embeddings",
            RetrievalStrategy.SPARSE: "Sparse keyword-based retrieval (BM25)",
            RetrievalStrategy.HYBRID: "Combination of dense and sparse retrieval",
            RetrievalStrategy.PROPOSITION: "Proposition-based chunking for better semantics",
            RetrievalStrategy.MULTI_HOP: "Multi-hop reasoning for complex queries",
            RetrievalStrategy.PARALLEL: "Parallel retrieval for comparative analysis",
            RetrievalStrategy.SEQUENTIAL: "Sequential retrieval for procedural content"
        }
        return descriptions.get(strategy, "Unknown strategy")


def main():
    """Test RAG router"""
    from core.dive_query_classifier import DiveQueryClassifier
    
    print("=== Dive RAG Router Test ===\n")
    
    classifier = DiveQueryClassifier()
    router = DiveRAGRouter()
    
    # Test queries
    test_queries = [
        "What is Python?",
        "Explain how neural networks work",
        "How to implement a REST API in FastAPI",
        "Analyze the performance of this algorithm",
        "Compare Python vs JavaScript for web development",
        "Design and implement a distributed caching system"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        
        # Classify
        classification = classifier.classify(query)
        print(f"Classification: {classification.query_type.value} ({classification.complexity.value})")
        
        # Route
        decision = router.route(classification)
        print(f"Strategy: {decision.strategy.value}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Quality: {decision.estimated_quality:.2f}")
        print(f"Latency: {decision.estimated_latency:.2f}s")
        print(f"Parameters: {decision.parameters}")
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()
