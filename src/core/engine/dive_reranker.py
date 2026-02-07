#!/usr/bin/env python3
"""
Dive Reranker - V22 Adaptive RAG Component

Reranks retrieved chunks for better quality.
Part of the Adaptive RAG transformation (Week 10).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RerankingMethod(Enum):
    """Reranking methods"""
    RELEVANCE = "relevance"  # Relevance-based
    DIVERSITY = "diversity"  # Maximize diversity
    RECENCY = "recency"  # Prefer recent content
    AUTHORITY = "authority"  # Prefer authoritative sources
    HYBRID = "hybrid"  # Combination


@dataclass
class RerankingResult:
    """Result of reranking"""
    chunks: List[Dict[str, Any]]
    method_used: RerankingMethod
    original_order: List[int]
    reranking_scores: List[float]
    metadata: Dict[str, Any]


class DiveReranker:
    """
    Reranks retrieved chunks for better quality.
    
    Reranking is crucial for Adaptive RAG - it ensures the most
    relevant and high-quality chunks are prioritized.
    """
    
    def __init__(self):
        self.reranking_stats = {
            'total_rerankings': 0,
            'by_method': {}
        }
    
    def rerank(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        method: RerankingMethod = RerankingMethod.RELEVANCE,
        top_k: Optional[int] = None
    ) -> RerankingResult:
        """
        Rerank chunks.
        
        Args:
            chunks: Chunks to rerank
            query: Original query
            method: Reranking method
            top_k: Optional limit on results
            
        Returns:
            RerankingResult with reranked chunks
        """
        # Update stats
        self.reranking_stats['total_rerankings'] += 1
        self.reranking_stats['by_method'][method.value] = \
            self.reranking_stats['by_method'].get(method.value, 0) + 1
        
        # Store original order
        original_order = list(range(len(chunks)))
        
        # Apply reranking method
        if method == RerankingMethod.RELEVANCE:
            reranked, scores = self._relevance_reranking(chunks, query)
        elif method == RerankingMethod.DIVERSITY:
            reranked, scores = self._diversity_reranking(chunks)
        elif method == RerankingMethod.RECENCY:
            reranked, scores = self._recency_reranking(chunks)
        elif method == RerankingMethod.AUTHORITY:
            reranked, scores = self._authority_reranking(chunks)
        elif method == RerankingMethod.HYBRID:
            reranked, scores = self._hybrid_reranking(chunks, query)
        else:
            reranked, scores = chunks, [c.get('score', 0.5) for c in chunks]
        
        # Apply top_k if specified
        if top_k:
            reranked = reranked[:top_k]
            scores = scores[:top_k]
        
        return RerankingResult(
            chunks=reranked,
            method_used=method,
            original_order=original_order,
            reranking_scores=scores,
            metadata={'method': method.value, 'top_k': top_k}
        )
    
    def _relevance_reranking(
        self,
        chunks: List[Dict],
        query: str
    ) -> tuple[List[Dict], List[float]]:
        """Rerank by relevance to query"""
        
        # Calculate relevance scores
        scored_chunks = []
        for chunk in chunks:
            # Simple relevance: count query terms in content
            content = chunk.get('content', '').lower()
            query_terms = query.lower().split()
            
            relevance = sum(1 for term in query_terms if term in content)
            relevance_score = relevance / max(1, len(query_terms))
            
            # Combine with original score
            original_score = chunk.get('score', 0.5)
            final_score = 0.7 * original_score + 0.3 * relevance_score
            
            scored_chunks.append((chunk, final_score))
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        reranked = [c[0] for c in scored_chunks]
        scores = [c[1] for c in scored_chunks]
        
        return reranked, scores
    
    def _diversity_reranking(
        self,
        chunks: List[Dict]
    ) -> tuple[List[Dict], List[float]]:
        """Rerank to maximize diversity"""
        
        if not chunks:
            return [], []
        
        # Start with highest scored chunk
        reranked = [chunks[0]]
        remaining = chunks[1:]
        scores = [chunks[0].get('score', 0.5)]
        
        # Iteratively add most diverse chunk
        while remaining:
            max_diversity = -1
            best_chunk = None
            best_score = 0
            
            for chunk in remaining:
                # Calculate diversity (simplified: different source)
                diversity = 1.0
                for selected in reranked:
                    if chunk.get('source') == selected.get('source'):
                        diversity *= 0.5
                
                # Combine with original score
                original_score = chunk.get('score', 0.5)
                combined = 0.5 * original_score + 0.5 * diversity
                
                if combined > max_diversity:
                    max_diversity = combined
                    best_chunk = chunk
                    best_score = combined
            
            if best_chunk:
                reranked.append(best_chunk)
                scores.append(best_score)
                remaining.remove(best_chunk)
            else:
                break
        
        return reranked, scores
    
    def _recency_reranking(
        self,
        chunks: List[Dict]
    ) -> tuple[List[Dict], List[float]]:
        """Rerank by recency"""
        
        # Sort by timestamp if available
        scored_chunks = []
        for chunk in chunks:
            timestamp = chunk.get('timestamp', 0)
            original_score = chunk.get('score', 0.5)
            
            # Combine recency with original score
            recency_score = timestamp / max(1, max(c.get('timestamp', 1) for c in chunks))
            final_score = 0.6 * original_score + 0.4 * recency_score
            
            scored_chunks.append((chunk, final_score))
        
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        reranked = [c[0] for c in scored_chunks]
        scores = [c[1] for c in scored_chunks]
        
        return reranked, scores
    
    def _authority_reranking(
        self,
        chunks: List[Dict]
    ) -> tuple[List[Dict], List[float]]:
        """Rerank by source authority"""
        
        # Authority scores for different sources
        authority_map = {
            'official_docs': 1.0,
            'verified_source': 0.9,
            'community': 0.7,
            'unknown': 0.5
        }
        
        scored_chunks = []
        for chunk in chunks:
            source_type = chunk.get('source_type', 'unknown')
            authority = authority_map.get(source_type, 0.5)
            original_score = chunk.get('score', 0.5)
            
            # Combine authority with original score
            final_score = 0.5 * original_score + 0.5 * authority
            
            scored_chunks.append((chunk, final_score))
        
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        reranked = [c[0] for c in scored_chunks]
        scores = [c[1] for c in scored_chunks]
        
        return reranked, scores
    
    def _hybrid_reranking(
        self,
        chunks: List[Dict],
        query: str
    ) -> tuple[List[Dict], List[float]]:
        """Hybrid reranking combining multiple methods"""
        
        # Get scores from different methods
        relevance_chunks, relevance_scores = self._relevance_reranking(chunks, query)
        diversity_chunks, diversity_scores = self._diversity_reranking(chunks)
        
        # Create score map
        relevance_map = {id(c): s for c, s in zip(relevance_chunks, relevance_scores)}
        diversity_map = {id(c): s for c, s in zip(diversity_chunks, diversity_scores)}
        
        # Combine scores
        scored_chunks = []
        for chunk in chunks:
            chunk_id = id(chunk)
            relevance = relevance_map.get(chunk_id, 0.5)
            diversity = diversity_map.get(chunk_id, 0.5)
            
            # Weighted combination
            final_score = 0.7 * relevance + 0.3 * diversity
            
            scored_chunks.append((chunk, final_score))
        
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        reranked = [c[0] for c in scored_chunks]
        scores = [c[1] for c in scored_chunks]
        
        return reranked, scores
    
    def get_stats(self) -> Dict:
        """Get reranking statistics"""
        return self.reranking_stats.copy()


def main():
    """Test reranker"""
    print("=== Dive Reranker Test ===\n")
    
    reranker = DiveReranker()
    
    # Test chunks
    test_chunks = [
        {'content': 'Python is a programming language', 'score': 0.8, 'source': 'doc1'},
        {'content': 'JavaScript is also a language', 'score': 0.7, 'source': 'doc2'},
        {'content': 'Python has many features', 'score': 0.6, 'source': 'doc1'},
        {'content': 'Ruby is another language', 'score': 0.5, 'source': 'doc3'},
        {'content': 'Python is used for data science', 'score': 0.9, 'source': 'doc4'}
    ]
    
    query = "Python programming"
    
    # Test each method
    methods = [
        RerankingMethod.RELEVANCE,
        RerankingMethod.DIVERSITY,
        RerankingMethod.HYBRID
    ]
    
    for method in methods:
        print(f"Method: {method.value}")
        result = reranker.rerank(test_chunks, query, method, top_k=3)
        
        print(f"Top {len(result.chunks)} chunks:")
        for i, (chunk, score) in enumerate(zip(result.chunks, result.reranking_scores), 1):
            print(f"  {i}. {chunk['content'][:50]}... (score: {score:.3f})")
        
        print("-" * 80)
        print()
    
    # Show stats
    print("=== Reranking Statistics ===")
    stats = reranker.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
