"""
📚 RAG ENGINE
Retrieval-Augmented Generation for code and knowledge

Based on V28's vibe_engine/rag_engine.py
"""

import os
import sys
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class Document:
    """A document in the RAG store"""
    id: str
    content: str
    metadata: Dict
    embedding: List[float] = None


class RAGEngineAlgorithm(BaseAlgorithm):
    """
    📚 RAG Engine
    
    Retrieval-Augmented Generation:
    - Document indexing
    - Semantic search
    - Context augmentation
    - Answer generation
    
    From V28: vibe_engine/rag_engine.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="RAGEngine",
            name="RAG Engine",
            level="operational",
            category="retrieval",
            version="1.0",
            description="Retrieval-Augmented Generation",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "index/search/generate"),
                    IOField("documents", "array", False, "Documents to index"),
                    IOField("query", "string", False, "Search query")
                ],
                outputs=[
                    IOField("result", "object", True, "RAG result")
                ]
            ),
            steps=["Index documents", "Embed query", "Retrieve relevant", "Generate answer"],
            tags=["rag", "retrieval", "generation", "search"]
        )
        
        self.documents: Dict[str, Document] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "search")
        
        print(f"\n📚 RAG Engine")
        
        if action == "index":
            return self._index_documents(params.get("documents", []))
        elif action == "search":
            return self._search(params.get("query", ""), params.get("top_k", 5))
        elif action == "generate":
            return self._generate(params.get("query", ""))
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _index_documents(self, docs: List[Dict]) -> AlgorithmResult:
        indexed = 0
        
        for doc_data in docs:
            doc = Document(
                id=doc_data.get("id", f"doc_{len(self.documents)}"),
                content=doc_data.get("content", ""),
                metadata=doc_data.get("metadata", {}),
                embedding=self._simple_embed(doc_data.get("content", ""))
            )
            self.documents[doc.id] = doc
            indexed += 1
        
        print(f"   Indexed: {indexed} documents")
        
        return AlgorithmResult(
            status="success",
            data={"indexed": indexed, "total_documents": len(self.documents)}
        )
    
    def _simple_embed(self, text: str) -> List[float]:
        """Simple bag-of-words embedding (placeholder for real embeddings)"""
        words = text.lower().split()
        # Create simple word frequency vector
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Normalize
        total = sum(word_freq.values())
        return [v / total for v in list(word_freq.values())[:100]]
    
    def _similarity(self, query_words: set, doc: Document) -> float:
        """Simple keyword overlap similarity"""
        doc_words = set(doc.content.lower().split())
        overlap = query_words & doc_words
        return len(overlap) / max(len(query_words), 1)
    
    def _search(self, query: str, top_k: int = 5) -> AlgorithmResult:
        if not query:
            return AlgorithmResult(status="error", error="No query provided")
        
        query_words = set(query.lower().split())
        
        # Score all documents
        scored: List[Tuple[float, Document]] = []
        for doc in self.documents.values():
            score = self._similarity(query_words, doc)
            scored.append((score, doc))
        
        # Sort and take top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {"id": doc.id, "score": score, "snippet": doc.content[:200]}
            for score, doc in scored[:top_k] if score > 0
        ]
        
        print(f"   Found: {len(results)} relevant documents")
        
        return AlgorithmResult(
            status="success",
            data={"results": results, "query": query}
        )
    
    def _generate(self, query: str) -> AlgorithmResult:
        """Generate answer using retrieved context"""
        search_result = self._search(query, top_k=3)
        
        if not search_result.data.get("results"):
            return AlgorithmResult(
                status="success",
                data={"answer": "No relevant context found.", "sources": []}
            )
        
        # Build context from retrieved docs
        context = "\n\n".join([
            r["snippet"] for r in search_result.data["results"]
        ])
        
        # Simulate generation (in real impl, call LLM)
        answer = f"Based on the retrieved context:\n\n{context[:500]}\n\n[Answer would be generated here by LLM]"
        
        return AlgorithmResult(
            status="success",
            data={
                "answer": answer,
                "sources": [r["id"] for r in search_result.data["results"]],
                "context_used": len(context)
            }
        )
    
    def _get_stats(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "total_documents": len(self.documents),
                "avg_doc_length": sum(len(d.content) for d in self.documents.values()) / len(self.documents) if self.documents else 0
            }
        )


def register(algorithm_manager):
    algo = RAGEngineAlgorithm()
    algorithm_manager.register("RAGEngine", algo)
    print("✅ RAGEngine registered")


if __name__ == "__main__":
    algo = RAGEngineAlgorithm()
    algo.execute({"action": "index", "documents": [
        {"id": "doc1", "content": "Python is a programming language known for readability."},
        {"id": "doc2", "content": "Machine learning uses algorithms to learn from data."},
        {"id": "doc3", "content": "Python is popular for machine learning projects."}
    ]})
    result = algo.execute({"action": "search", "query": "Python programming"})
    print(f"Found: {len(result.data['results'])} results")
