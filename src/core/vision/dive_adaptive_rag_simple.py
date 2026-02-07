#!/usr/bin/env python3
"""
Dive Adaptive RAG Simple - Standalone Adaptive RAG

Simplified version for easy import and use.
"""

from typing import Dict, List, Optional
from enum import Enum


class QueryType(Enum):
    """Query types"""
    FACTUAL = "factual"
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    ANALYTICAL = "analytical"


class RetrievalStrategy(Enum):
    """Retrieval strategies"""
    DENSE = "dense"
    PROPOSITION = "proposition"
    SEQUENTIAL = "sequential"
    MULTI_HOP = "multi_hop"


class DiveAdaptiveRAGSimple:
    """
    Simplified Adaptive RAG system.
    
    Adapts retrieval strategy based on query type.
    """
    
    def __init__(self):
        self.stats = {
            'total_queries': 0,
            'by_strategy': {}
        }
    
    def query(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Execute adaptive RAG query.
        
        Returns dict for easy serialization.
        """
        
        # Step 1: Classify query
        query_type = self._classify_query(query)
        
        # Step 2: Select strategy
        strategy = self._select_strategy(query_type)
        
        # Step 3: Retrieve (simulated)
        chunks = self._retrieve(query, strategy)
        
        # Step 4: Rerank (simulated)
        reranked = self._rerank(chunks, query)
        
        # Step 5: Compress (simulated)
        compressed = self._compress(reranked)
        
        # Update stats
        self.stats['total_queries'] += 1
        self.stats['by_strategy'][strategy.value] = \
            self.stats['by_strategy'].get(strategy.value, 0) + 1
        
        return {
            'classification': {
                'query_type': query_type.value,
                'confidence': 0.8
            },
            'routing': {
                'strategy': strategy.value,
                'reasoning': f"{query_type.value} query uses {strategy.value} strategy"
            },
            'retrieval': {
                'chunks_retrieved': len(chunks),
                'quality_score': 0.9
            },
            'reranking': {
                'chunks_after_reranking': len(reranked)
            },
            'compression': {
                'compressed_tokens': len(compressed) * 50,
                'compression_ratio': 0.8
            },
            'final_context': compressed,
            'metadata': {
                'rag_version': 'v22_simple',
                'adaptive_rag_enabled': True
            }
        }
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ['what is', 'who is', 'define']):
            return QueryType.FACTUAL
        elif any(kw in query_lower for kw in ['explain', 'understand', 'why']):
            return QueryType.CONCEPTUAL
        elif any(kw in query_lower for kw in ['how to', 'steps', 'implement']):
            return QueryType.PROCEDURAL
        elif any(kw in query_lower for kw in ['analyze', 'evaluate', 'compare']):
            return QueryType.ANALYTICAL
        else:
            return QueryType.FACTUAL
    
    def _select_strategy(self, query_type: QueryType) -> RetrievalStrategy:
        """Select retrieval strategy"""
        strategy_map = {
            QueryType.FACTUAL: RetrievalStrategy.DENSE,
            QueryType.CONCEPTUAL: RetrievalStrategy.PROPOSITION,
            QueryType.PROCEDURAL: RetrievalStrategy.SEQUENTIAL,
            QueryType.ANALYTICAL: RetrievalStrategy.MULTI_HOP
        }
        return strategy_map[query_type]
    
    def _retrieve(self, query: str, strategy: RetrievalStrategy) -> List[Dict]:
        """Retrieve chunks (simulated)"""
        chunk_counts = {
            RetrievalStrategy.DENSE: 5,
            RetrievalStrategy.PROPOSITION: 20,
            RetrievalStrategy.SEQUENTIAL: 15,
            RetrievalStrategy.MULTI_HOP: 15
        }
        
        count = chunk_counts[strategy]
        return [{'content': f'Chunk {i+1}', 'score': 0.9 - i*0.05} for i in range(count)]
    
    def _rerank(self, chunks: List[Dict], query: str) -> List[Dict]:
        """Rerank chunks (simulated)"""
        return chunks[:10]  # Top 10
    
    def _compress(self, chunks: List[Dict]) -> List[Dict]:
        """Compress context (simulated)"""
        return chunks[:8]  # Compress to 8
    
    def get_stats(self) -> Dict:
        """Get RAG statistics"""
        return self.stats.copy()


def main():
    """Test adaptive RAG"""
    print("=== Dive Adaptive RAG Simple Test ===\n")
    
    rag = DiveAdaptiveRAGSimple()
    
    # Test queries
    test_queries = [
        "What is Python?",
        "Explain how neural networks work",
        "How to implement a REST API",
        "Analyze algorithm performance"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        result = rag.query(query)
        
        print(f"  Type: {result['classification']['query_type']}")
        print(f"  Strategy: {result['routing']['strategy']}")
        print(f"  Retrieved: {result['retrieval']['chunks_retrieved']} chunks")
        print(f"  Final: {len(result['final_context'])} chunks")
        print()
    
    print(f"Stats: {rag.get_stats()}")


if __name__ == "__main__":
    main()
