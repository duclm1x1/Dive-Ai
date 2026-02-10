#!/usr/bin/env python3
"""
Dive Context Compressor - V22 Adaptive RAG Component

Compresses retrieved context to fit token limits while preserving quality.
Part of the Adaptive RAG transformation (Week 10).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CompressionResult:
    """Result of context compression"""
    compressed_chunks: List[Dict[str, Any]]
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    quality_retained: float
    metadata: Dict[str, Any]


class DiveContextCompressor:
    """
    Compresses retrieved context intelligently.
    
    Context compression is crucial for:
    - Fitting within token limits
    - Reducing costs
    - Improving response speed
    - Maintaining quality
    """
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.compression_stats = {
            'total_compressions': 0,
            'total_tokens_saved': 0
        }
    
    def compress(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        target_tokens: Optional[int] = None
    ) -> CompressionResult:
        """
        Compress context to fit token limit.
        
        Args:
            chunks: Chunks to compress
            query: Original query
            target_tokens: Target token count (default: self.max_tokens)
            
        Returns:
            CompressionResult with compressed chunks
        """
        target = target_tokens or self.max_tokens
        
        # Calculate original tokens
        original_tokens = self._estimate_tokens(chunks)
        
        if original_tokens <= target:
            # No compression needed
            return CompressionResult(
                compressed_chunks=chunks,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                quality_retained=1.0,
                metadata={'compression_needed': False}
            )
        
        # Apply compression strategies
        compressed = self._apply_compression(chunks, query, target)
        compressed_tokens = self._estimate_tokens(compressed)
        
        # Update stats
        self.compression_stats['total_compressions'] += 1
        self.compression_stats['total_tokens_saved'] += (original_tokens - compressed_tokens)
        
        return CompressionResult(
            compressed_chunks=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            quality_retained=self._estimate_quality_retained(chunks, compressed),
            metadata={
                'compression_needed': True,
                'tokens_saved': original_tokens - compressed_tokens
            }
        )
    
    def _estimate_tokens(self, chunks: List[Dict]) -> int:
        """Estimate token count (simplified)"""
        total_chars = sum(len(c.get('content', '')) for c in chunks)
        # Rough estimate: 4 chars per token
        return total_chars // 4
    
    def _apply_compression(
        self,
        chunks: List[Dict],
        query: str,
        target_tokens: int
    ) -> List[Dict]:
        """Apply compression strategies"""
        
        # Strategy 1: Remove low-relevance chunks
        chunks = self._remove_low_relevance(chunks, query)
        
        current_tokens = self._estimate_tokens(chunks)
        if current_tokens <= target_tokens:
            return chunks
        
        # Strategy 2: Truncate individual chunks
        chunks = self._truncate_chunks(chunks, target_tokens)
        
        current_tokens = self._estimate_tokens(chunks)
        if current_tokens <= target_tokens:
            return chunks
        
        # Strategy 3: Extract key sentences
        chunks = self._extract_key_sentences(chunks, query, target_tokens)
        
        return chunks
    
    def _remove_low_relevance(
        self,
        chunks: List[Dict],
        query: str,
        threshold: float = 0.3
    ) -> List[Dict]:
        """Remove chunks below relevance threshold"""
        
        # Calculate relevance scores
        query_terms = set(query.lower().split())
        
        filtered = []
        for chunk in chunks:
            content = chunk.get('content', '').lower()
            content_terms = set(content.split())
            
            # Jaccard similarity
            intersection = len(query_terms & content_terms)
            union = len(query_terms | content_terms)
            relevance = intersection / union if union > 0 else 0
            
            # Also consider original score
            original_score = chunk.get('score', 0.5)
            combined_score = 0.7 * original_score + 0.3 * relevance
            
            if combined_score >= threshold:
                filtered.append(chunk)
        
        return filtered if filtered else chunks[:1]  # Keep at least one
    
    def _truncate_chunks(
        self,
        chunks: List[Dict],
        target_tokens: int
    ) -> List[Dict]:
        """Truncate each chunk proportionally"""
        
        total_tokens = self._estimate_tokens(chunks)
        if total_tokens <= target_tokens:
            return chunks
        
        # Calculate truncation ratio
        ratio = target_tokens / total_tokens
        
        truncated = []
        for chunk in chunks:
            content = chunk.get('content', '')
            # Truncate to ratio of original length
            truncated_length = int(len(content) * ratio)
            truncated_content = content[:truncated_length]
            
            # Try to end at sentence boundary
            last_period = truncated_content.rfind('.')
            if last_period > truncated_length * 0.8:
                truncated_content = truncated_content[:last_period+1]
            
            truncated_chunk = chunk.copy()
            truncated_chunk['content'] = truncated_content
            truncated_chunk['truncated'] = True
            truncated.append(truncated_chunk)
        
        return truncated
    
    def _extract_key_sentences(
        self,
        chunks: List[Dict],
        query: str,
        target_tokens: int
    ) -> List[Dict]:
        """Extract most relevant sentences from chunks"""
        
        query_terms = set(query.lower().split())
        
        # Extract and score sentences
        sentences = []
        for chunk in chunks:
            content = chunk.get('content', '')
            chunk_sentences = content.split('.')
            
            for sent in chunk_sentences:
                if len(sent.strip()) < 10:
                    continue
                
                # Score sentence
                sent_terms = set(sent.lower().split())
                relevance = len(query_terms & sent_terms) / max(1, len(query_terms))
                
                sentences.append({
                    'content': sent.strip() + '.',
                    'score': relevance,
                    'source': chunk.get('source')
                })
        
        # Sort by score
        sentences.sort(key=lambda x: x['score'], reverse=True)
        
        # Select sentences until target
        selected = []
        current_tokens = 0
        
        for sent in sentences:
            sent_tokens = len(sent['content']) // 4
            if current_tokens + sent_tokens <= target_tokens:
                selected.append(sent)
                current_tokens += sent_tokens
            else:
                break
        
        return selected if selected else sentences[:1]
    
    def _estimate_quality_retained(
        self,
        original: List[Dict],
        compressed: List[Dict]
    ) -> float:
        """Estimate quality retained after compression"""
        
        # Simple heuristic: ratio of chunks retained
        if not original:
            return 1.0
        
        return len(compressed) / len(original)
    
    def get_stats(self) -> Dict:
        """Get compression statistics"""
        stats = self.compression_stats.copy()
        
        if stats['total_compressions'] > 0:
            stats['avg_tokens_saved'] = (
                stats['total_tokens_saved'] / stats['total_compressions']
            )
        
        return stats


def main():
    """Test context compressor"""
    print("=== Dive Context Compressor Test ===\n")
    
    compressor = DiveContextCompressor(max_tokens=200)
    
    # Test chunks (intentionally verbose)
    test_chunks = [
        {
            'content': 'Python is a high-level, interpreted programming language. It was created by Guido van Rossum and first released in 1991. Python emphasizes code readability and uses significant indentation.',
            'score': 0.9,
            'source': 'doc1'
        },
        {
            'content': 'Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. It has a comprehensive standard library and a large ecosystem of third-party packages.',
            'score': 0.8,
            'source': 'doc2'
        },
        {
            'content': 'Python is widely used in web development, data science, machine learning, artificial intelligence, scientific computing, and automation. Popular frameworks include Django, Flask, NumPy, and TensorFlow.',
            'score': 0.7,
            'source': 'doc3'
        },
        {
            'content': 'The Python Software Foundation manages the development of Python. The language is open source and has a large, active community of developers worldwide.',
            'score': 0.6,
            'source': 'doc4'
        }
    ]
    
    query = "Python programming language"
    
    print(f"Original chunks: {len(test_chunks)}")
    print(f"Target tokens: {compressor.max_tokens}")
    print()
    
    result = compressor.compress(test_chunks, query)
    
    print(f"Compressed chunks: {len(result.compressed_chunks)}")
    print(f"Original tokens: {result.original_tokens}")
    print(f"Compressed tokens: {result.compressed_tokens}")
    print(f"Compression ratio: {result.compression_ratio:.2%}")
    print(f"Quality retained: {result.quality_retained:.2%}")
    print(f"Tokens saved: {result.metadata.get('tokens_saved', 0)}")
    print()
    
    print("Compressed content:")
    for i, chunk in enumerate(result.compressed_chunks, 1):
        content = chunk.get('content', '')
        print(f"{i}. {content[:100]}...")
    
    print("\n=== Compression Statistics ===")
    stats = compressor.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
