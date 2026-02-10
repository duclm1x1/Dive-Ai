#!/usr/bin/env python3
"""
Dive Query Classifier - V22 Adaptive RAG Component

Classifies queries to determine optimal retrieval strategy.
Part of the Adaptive RAG transformation (Week 8).
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Types of queries"""
    FACTUAL = "factual"  # Simple fact lookup
    CONCEPTUAL = "conceptual"  # Understanding concepts
    PROCEDURAL = "procedural"  # How-to instructions
    ANALYTICAL = "analytical"  # Deep analysis needed
    COMPARATIVE = "comparative"  # Comparing options
    CREATIVE = "creative"  # Creative generation


class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class QueryClassification:
    """Result of query classification"""
    query_type: QueryType
    complexity: QueryComplexity
    keywords: List[str]
    entities: List[str]
    intent: str
    confidence: float
    metadata: Dict


class DiveQueryClassifier:
    """
    Classifies queries for optimal RAG strategy selection.
    
    Different query types need different retrieval strategies:
    - Factual: Dense retrieval
    - Conceptual: Proposition-based
    - Procedural: Sequential retrieval
    - Analytical: Multi-hop reasoning
    - Comparative: Parallel retrieval
    - Creative: Diverse retrieval
    """
    
    def __init__(self):
        # Keywords for each query type
        self.type_keywords = {
            QueryType.FACTUAL: ['what is', 'who is', 'when', 'where', 'define'],
            QueryType.CONCEPTUAL: ['explain', 'understand', 'concept', 'theory', 'why'],
            QueryType.PROCEDURAL: ['how to', 'steps', 'guide', 'tutorial', 'implement'],
            QueryType.ANALYTICAL: ['analyze', 'evaluate', 'compare', 'assess', 'investigate'],
            QueryType.COMPARATIVE: ['vs', 'versus', 'difference', 'better', 'compare'],
            QueryType.CREATIVE: ['create', 'generate', 'design', 'build', 'develop']
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            'simple': ['what', 'list', 'show', 'get'],
            'moderate': ['how', 'why', 'explain'],
            'complex': ['analyze', 'design', 'architect', 'optimize', 'refactor']
        }
    
    def classify(self, query: str, context: Optional[Dict] = None) -> QueryClassification:
        """
        Classify a query.
        
        Args:
            query: Query string
            context: Optional context
            
        Returns:
            QueryClassification with type, complexity, and metadata
        """
        query_lower = query.lower()
        
        # Determine query type
        query_type = self._classify_type(query_lower)
        
        # Determine complexity
        complexity = self._classify_complexity(query_lower)
        
        # Extract keywords
        keywords = self._extract_keywords(query_lower)
        
        # Extract entities (simplified)
        entities = self._extract_entities(query)
        
        # Determine intent
        intent = self._determine_intent(query_type, complexity)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_lower, query_type)
        
        return QueryClassification(
            query_type=query_type,
            complexity=complexity,
            keywords=keywords,
            entities=entities,
            intent=intent,
            confidence=confidence,
            metadata={
                'query_length': len(query),
                'word_count': len(query.split()),
                'has_context': context is not None
            }
        )
    
    def _classify_type(self, query: str) -> QueryType:
        """Classify query type based on keywords"""
        scores = {}
        
        for query_type, keywords in self.type_keywords.items():
            score = sum(1 for kw in keywords if kw in query)
            scores[query_type] = score
        
        # Get type with highest score
        max_score = max(scores.values())
        if max_score == 0:
            return QueryType.FACTUAL  # Default
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _classify_complexity(self, query: str) -> QueryComplexity:
        """Classify query complexity"""
        # Count complexity indicators
        simple_count = sum(1 for kw in self.complexity_indicators['simple'] if kw in query)
        moderate_count = sum(1 for kw in self.complexity_indicators['moderate'] if kw in query)
        complex_count = sum(1 for kw in self.complexity_indicators['complex'] if kw in query)
        
        # Also consider query length
        word_count = len(query.split())
        
        if complex_count > 0 or word_count > 20:
            return QueryComplexity.COMPLEX
        elif moderate_count > 0 or word_count > 10:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for'}
        words = query.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords[:10]  # Top 10 keywords
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities (simplified)"""
        # In real implementation, would use NER
        # For now, extract capitalized words
        words = query.split()
        entities = [w for w in words if w[0].isupper() and len(w) > 1]
        return entities
    
    def _determine_intent(self, query_type: QueryType, complexity: QueryComplexity) -> str:
        """Determine user intent"""
        intents = {
            (QueryType.FACTUAL, QueryComplexity.SIMPLE): "quick_lookup",
            (QueryType.FACTUAL, QueryComplexity.MODERATE): "detailed_lookup",
            (QueryType.CONCEPTUAL, QueryComplexity.SIMPLE): "basic_understanding",
            (QueryType.CONCEPTUAL, QueryComplexity.MODERATE): "deep_understanding",
            (QueryType.CONCEPTUAL, QueryComplexity.COMPLEX): "comprehensive_understanding",
            (QueryType.PROCEDURAL, QueryComplexity.SIMPLE): "quick_howto",
            (QueryType.PROCEDURAL, QueryComplexity.MODERATE): "detailed_guide",
            (QueryType.PROCEDURAL, QueryComplexity.COMPLEX): "comprehensive_implementation",
            (QueryType.ANALYTICAL, QueryComplexity.MODERATE): "basic_analysis",
            (QueryType.ANALYTICAL, QueryComplexity.COMPLEX): "deep_analysis",
            (QueryType.COMPARATIVE, QueryComplexity.MODERATE): "simple_comparison",
            (QueryType.COMPARATIVE, QueryComplexity.COMPLEX): "detailed_comparison",
            (QueryType.CREATIVE, QueryComplexity.MODERATE): "basic_creation",
            (QueryType.CREATIVE, QueryComplexity.COMPLEX): "advanced_creation"
        }
        
        return intents.get((query_type, complexity), "general_query")
    
    def _calculate_confidence(self, query: str, query_type: QueryType) -> float:
        """Calculate classification confidence"""
        # Count matching keywords
        keywords = self.type_keywords[query_type]
        matches = sum(1 for kw in keywords if kw in query)
        
        # Confidence based on matches
        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.7
        else:
            return 0.5


def main():
    """Test query classifier"""
    print("=== Dive Query Classifier Test ===\n")
    
    classifier = DiveQueryClassifier()
    
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
        classification = classifier.classify(query)
        print(f"Type: {classification.query_type.value}")
        print(f"Complexity: {classification.complexity.value}")
        print(f"Intent: {classification.intent}")
        print(f"Confidence: {classification.confidence:.2f}")
        print(f"Keywords: {', '.join(classification.keywords[:5])}")
        print(f"Entities: {', '.join(classification.entities) if classification.entities else 'None'}")
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()
