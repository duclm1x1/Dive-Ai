#!/usr/bin/env python3
"""
Dive Multi-Strategy Retriever - V22 Adaptive RAG Component

Implements multiple retrieval strategies for different query types.
Part of the Adaptive RAG transformation (Week 9).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from core.dive_rag_router import RetrievalStrategy


@dataclass
class RetrievalResult:
    """Result from retrieval"""
    chunks: List[Dict[str, Any]]
    strategy_used: RetrievalStrategy
    metadata: Dict[str, Any]
    quality_score: float


class DiveMultiStrategyRetriever:
    """
    Implements multiple RAG retrieval strategies.
    
    This is the core of Adaptive RAG - instead of one-size-fits-all,
    we have specialized strategies for different query types.
    """
    
    def __init__(self, knowledge_base: Optional[List[Dict]] = None):
        self.knowledge_base = knowledge_base or []
        self.retrieval_stats = {
            'total_retrievals': 0,
            'by_strategy': {}
        }
    
    def retrieve(
        self,
        query: str,
        strategy: RetrievalStrategy,
        parameters: Dict,
        context: Optional[Dict] = None
    ) -> RetrievalResult:
        """
        Retrieve using specified strategy.
        
        Args:
            query: Query string
            strategy: Retrieval strategy to use
            parameters: Strategy parameters
            context: Optional context
            
        Returns:
            RetrievalResult with chunks and metadata
        """
        # Update stats
        self.retrieval_stats['total_retrievals'] += 1
        self.retrieval_stats['by_strategy'][strategy.value] = \
            self.retrieval_stats['by_strategy'].get(strategy.value, 0) + 1
        
        # Route to appropriate strategy
        if strategy == RetrievalStrategy.DENSE:
            return self._dense_retrieval(query, parameters)
        elif strategy == RetrievalStrategy.SPARSE:
            return self._sparse_retrieval(query, parameters)
        elif strategy == RetrievalStrategy.HYBRID:
            return self._hybrid_retrieval(query, parameters)
        elif strategy == RetrievalStrategy.PROPOSITION:
            return self._proposition_retrieval(query, parameters)
        elif strategy == RetrievalStrategy.MULTI_HOP:
            return self._multi_hop_retrieval(query, parameters, context)
        elif strategy == RetrievalStrategy.PARALLEL:
            return self._parallel_retrieval(query, parameters)
        elif strategy == RetrievalStrategy.SEQUENTIAL:
            return self._sequential_retrieval(query, parameters)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _dense_retrieval(self, query: str, params: Dict) -> RetrievalResult:
        """
        Dense vector retrieval using embeddings.
        
        Best for: Factual queries, semantic similarity
        """
        top_k = params.get('top_k', 5)
        threshold = params.get('similarity_threshold', 0.7)
        
        # Simulate dense retrieval
        # In real implementation, would use vector database
        chunks = [
            {
                'content': f"Dense result {i+1} for: {query}",
                'score': 0.9 - (i * 0.1),
                'source': f'doc_{i+1}'
            }
            for i in range(top_k)
        ]
        
        return RetrievalResult(
            chunks=chunks,
            strategy_used=RetrievalStrategy.DENSE,
            metadata={'method': 'cosine_similarity', 'threshold': threshold},
            quality_score=0.8
        )
    
    def _sparse_retrieval(self, query: str, params: Dict) -> RetrievalResult:
        """
        Sparse keyword-based retrieval (BM25).
        
        Best for: Exact keyword matching
        """
        top_k = params.get('top_k', 10)
        min_score = params.get('min_score', 0.5)
        
        # Simulate BM25 retrieval
        chunks = [
            {
                'content': f"Sparse result {i+1} for: {query}",
                'score': 0.85 - (i * 0.08),
                'source': f'doc_{i+1}'
            }
            for i in range(top_k)
        ]
        
        return RetrievalResult(
            chunks=chunks,
            strategy_used=RetrievalStrategy.SPARSE,
            metadata={'method': 'bm25', 'min_score': min_score},
            quality_score=0.7
        )
    
    def _hybrid_retrieval(self, query: str, params: Dict) -> RetrievalResult:
        """
        Hybrid retrieval combining dense and sparse.
        
        Best for: Balanced semantic + keyword matching
        """
        dense_weight = params.get('dense_weight', 0.7)
        sparse_weight = params.get('sparse_weight', 0.3)
        top_k = params.get('top_k', 10)
        
        # Get results from both strategies
        dense_results = self._dense_retrieval(query, {'top_k': top_k})
        sparse_results = self._sparse_retrieval(query, {'top_k': top_k})
        
        # Combine and rerank
        combined = []
        for i in range(min(len(dense_results.chunks), len(sparse_results.chunks))):
            dense_chunk = dense_results.chunks[i]
            sparse_chunk = sparse_results.chunks[i]
            
            # Weighted combination
            combined_score = (
                dense_chunk['score'] * dense_weight +
                sparse_chunk['score'] * sparse_weight
            )
            
            combined.append({
                'content': f"Hybrid result {i+1} for: {query}",
                'score': combined_score,
                'source': f'doc_{i+1}',
                'dense_score': dense_chunk['score'],
                'sparse_score': sparse_chunk['score']
            })
        
        # Sort by combined score
        combined.sort(key=lambda x: x['score'], reverse=True)
        
        return RetrievalResult(
            chunks=combined[:top_k],
            strategy_used=RetrievalStrategy.HYBRID,
            metadata={
                'dense_weight': dense_weight,
                'sparse_weight': sparse_weight
            },
            quality_score=0.85
        )
    
    def _proposition_retrieval(self, query: str, params: Dict) -> RetrievalResult:
        """
        Proposition-based retrieval for better semantics.
        
        Best for: Conceptual queries requiring comprehensive understanding
        """
        top_k = params.get('top_k', 20)
        rerank = params.get('rerank', True)
        
        # Simulate proposition-based chunking
        # In real implementation, would split documents into propositions
        chunks = [
            {
                'content': f"Proposition {i+1}: {query}",
                'score': 0.9 - (i * 0.04),
                'source': f'doc_{i//3+1}',
                'proposition_id': i+1
            }
            for i in range(top_k)
        ]
        
        if rerank:
            # Simulate reranking
            chunks.sort(key=lambda x: x['score'], reverse=True)
        
        return RetrievalResult(
            chunks=chunks,
            strategy_used=RetrievalStrategy.PROPOSITION,
            metadata={'chunk_type': 'proposition', 'reranked': rerank},
            quality_score=0.9
        )
    
    def _multi_hop_retrieval(
        self,
        query: str,
        params: Dict,
        context: Optional[Dict]
    ) -> RetrievalResult:
        """
        Multi-hop reasoning retrieval.
        
        Best for: Analytical queries requiring deep reasoning
        """
        max_hops = params.get('max_hops', 3)
        top_k_per_hop = params.get('top_k_per_hop', 5)
        
        all_chunks = []
        current_query = query
        
        for hop in range(max_hops):
            # Retrieve for current query
            hop_results = self._dense_retrieval(
                current_query,
                {'top_k': top_k_per_hop}
            )
            
            for chunk in hop_results.chunks:
                chunk['hop'] = hop + 1
                all_chunks.append(chunk)
            
            # Generate next query based on results
            # In real implementation, would use LLM to generate follow-up query
            current_query = f"{query} (hop {hop+2})"
        
        return RetrievalResult(
            chunks=all_chunks,
            strategy_used=RetrievalStrategy.MULTI_HOP,
            metadata={'hops': max_hops, 'total_chunks': len(all_chunks)},
            quality_score=0.95
        )
    
    def _parallel_retrieval(self, query: str, params: Dict) -> RetrievalResult:
        """
        Parallel retrieval for comparative queries.
        
        Best for: Comparative queries needing multiple perspectives
        """
        num_branches = params.get('num_branches', 2)
        top_k_per_branch = params.get('top_k_per_branch', 5)
        
        all_chunks = []
        
        # Split query into branches
        # In real implementation, would identify comparison aspects
        for branch in range(num_branches):
            branch_query = f"{query} (aspect {branch+1})"
            branch_results = self._dense_retrieval(
                branch_query,
                {'top_k': top_k_per_branch}
            )
            
            for chunk in branch_results.chunks:
                chunk['branch'] = branch + 1
                all_chunks.append(chunk)
        
        return RetrievalResult(
            chunks=all_chunks,
            strategy_used=RetrievalStrategy.PARALLEL,
            metadata={'branches': num_branches, 'total_chunks': len(all_chunks)},
            quality_score=0.9
        )
    
    def _sequential_retrieval(self, query: str, params: Dict) -> RetrievalResult:
        """
        Sequential retrieval for procedural queries.
        
        Best for: Procedural queries needing step-by-step content
        """
        max_steps = params.get('max_steps', 5)
        top_k_per_step = params.get('top_k_per_step', 3)
        
        all_chunks = []
        
        for step in range(max_steps):
            step_query = f"{query} (step {step+1})"
            step_results = self._dense_retrieval(
                step_query,
                {'top_k': top_k_per_step}
            )
            
            for chunk in step_results.chunks:
                chunk['step'] = step + 1
                all_chunks.append(chunk)
        
        return RetrievalResult(
            chunks=all_chunks,
            strategy_used=RetrievalStrategy.SEQUENTIAL,
            metadata={'steps': max_steps, 'total_chunks': len(all_chunks)},
            quality_score=0.85
        )
    
    def get_stats(self) -> Dict:
        """Get retrieval statistics"""
        return self.retrieval_stats.copy()


def main():
    """Test multi-strategy retriever"""
    print("=== Dive Multi-Strategy Retriever Test ===\n")
    
    retriever = DiveMultiStrategyRetriever()
    
    # Test each strategy
    test_cases = [
        ("What is Python?", RetrievalStrategy.DENSE, {'top_k': 5}),
        ("Explain neural networks", RetrievalStrategy.PROPOSITION, {'top_k': 20}),
        ("How to implement REST API", RetrievalStrategy.SEQUENTIAL, {'max_steps': 3}),
        ("Analyze algorithm performance", RetrievalStrategy.MULTI_HOP, {'max_hops': 2}),
        ("Compare Python vs JavaScript", RetrievalStrategy.PARALLEL, {'num_branches': 2})
    ]
    
    for query, strategy, params in test_cases:
        print(f"Query: {query}")
        print(f"Strategy: {strategy.value}")
        
        result = retriever.retrieve(query, strategy, params)
        
        print(f"Retrieved: {len(result.chunks)} chunks")
        print(f"Quality: {result.quality_score:.2f}")
        print(f"Metadata: {result.metadata}")
        print(f"Sample chunk: {result.chunks[0]['content']}")
        print("-" * 80)
        print()
    
    # Show stats
    print("=== Retrieval Statistics ===")
    stats = retriever.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
