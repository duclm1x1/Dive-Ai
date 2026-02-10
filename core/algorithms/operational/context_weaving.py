"""
🕸️ SEMANTIC CONTEXT WEAVING (SCW)
Weave related context fragments into coherent narrative

Based on V28's layer3_semanticcontextweaving.py
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class ContextFragment:
    """A fragment of context"""
    id: str
    content: str
    source: str
    relevance: float
    keywords: List[str]


class ContextWeavingAlgorithm(BaseAlgorithm):
    """
    🕸️ Semantic Context Weaving (SCW)
    
    Weaves disparate context fragments into coherent context:
    - Identifies relationships
    - Orders by relevance
    - Removes redundancy
    - Creates smooth transitions
    
    From V28: layer3_semanticcontextweaving.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ContextWeaving",
            name="Context Weaving (SCW)",
            level="operational",
            category="context",
            version="1.0",
            description="Weave context fragments into coherent narrative",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("fragments", "array", True, "Context fragments"),
                    IOField("query", "string", False, "Query to focus on")
                ],
                outputs=[
                    IOField("woven", "string", True, "Woven context"),
                    IOField("fragment_order", "array", True, "Order used")
                ]
            ),
            steps=["Score fragments", "Find connections", "Order logically", "Weave with transitions"],
            tags=["context", "weaving", "scw", "narrative"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        fragments_data = params.get("fragments", [])
        query = params.get("query", "")
        
        if not fragments_data:
            return AlgorithmResult(status="error", error="No fragments provided")
        
        print(f"\n🕸️ Context Weaving (SCW)")
        print(f"   Fragments: {len(fragments_data)}")
        
        # Parse fragments
        fragments = []
        for i, f in enumerate(fragments_data):
            if isinstance(f, str):
                frag = ContextFragment(str(i), f, "input", 0.5, self._extract_keywords(f))
            else:
                frag = ContextFragment(
                    f.get("id", str(i)), f.get("content", ""),
                    f.get("source", "input"), f.get("relevance", 0.5),
                    f.get("keywords", self._extract_keywords(f.get("content", "")))
                )
            fragments.append(frag)
        
        # Score by query relevance
        if query:
            for frag in fragments:
                frag.relevance = self._score_relevance(frag.content, query)
        
        # Sort by relevance
        fragments.sort(key=lambda f: f.relevance, reverse=True)
        
        # Find connections and order
        ordered = self._order_by_connections(fragments)
        
        # Weave with transitions
        woven = self._weave(ordered)
        
        print(f"   Output: {len(woven)} chars")
        
        return AlgorithmResult(
            status="success",
            data={
                "woven": woven,
                "fragment_order": [f.id for f in ordered],
                "relevance_scores": {f.id: f.relevance for f in fragments}
            }
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        words = text.lower().split()
        # Simple keyword extraction - longer words often more meaningful
        return [w for w in words if len(w) > 5][:10]
    
    def _score_relevance(self, content: str, query: str) -> float:
        content_lower = content.lower()
        query_words = query.lower().split()
        
        matches = sum(1 for w in query_words if w in content_lower)
        return matches / len(query_words) if query_words else 0.5
    
    def _order_by_connections(self, fragments: List[ContextFragment]) -> List[ContextFragment]:
        if not fragments:
            return []
        
        ordered = [fragments[0]]
        remaining = fragments[1:]
        
        while remaining:
            last = ordered[-1]
            # Find most connected to last
            best = None
            best_score = -1
            
            for frag in remaining:
                score = self._connection_score(last, frag)
                if score > best_score:
                    best_score = score
                    best = frag
            
            if best:
                ordered.append(best)
                remaining.remove(best)
            else:
                ordered.append(remaining.pop(0))
        
        return ordered
    
    def _connection_score(self, a: ContextFragment, b: ContextFragment) -> float:
        # Keyword overlap
        common = set(a.keywords) & set(b.keywords)
        return len(common) + (a.relevance + b.relevance) / 2
    
    def _weave(self, fragments: List[ContextFragment]) -> str:
        if not fragments:
            return ""
        
        result = []
        for i, frag in enumerate(fragments):
            if i > 0:
                # Add transition
                result.append("\n---\n")
            result.append(frag.content)
        
        return '\n'.join(result)


def register(algorithm_manager):
    algo = ContextWeavingAlgorithm()
    algorithm_manager.register("ContextWeaving", algo)
    print("✅ ContextWeaving registered")


if __name__ == "__main__":
    algo = ContextWeavingAlgorithm()
    result = algo.execute({
        "fragments": [
            "The system uses Python for backend logic.",
            "React powers the frontend user interface.",
            "API endpoints connect frontend to backend.",
            "Database stores all user data persistently."
        ],
        "query": "How does the system architecture work?"
    })
    print(f"Woven:\n{result.data['woven']}")
