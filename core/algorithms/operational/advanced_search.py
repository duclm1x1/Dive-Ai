"""
🔎 ADVANCED SEARCH
Advanced code and content search capabilities

Based on V28's vibe_engine/advanced_search.py
"""

import os
import sys
import re
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class SearchResult:
    """A search result"""
    file_path: str
    line_number: int
    content: str
    match_type: str
    score: float


class AdvancedSearchAlgorithm(BaseAlgorithm):
    """
    🔎 Advanced Search
    
    Advanced search capabilities:
    - Semantic search
    - Regex patterns
    - Fuzzy matching
    - Code-aware search
    
    From V28: vibe_engine/advanced_search.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AdvancedSearch",
            name="Advanced Search",
            level="operational",
            category="search",
            version="1.0",
            description="Advanced code and content search",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("query", "string", True, "Search query"),
                    IOField("search_type", "string", False, "literal/regex/fuzzy/semantic"),
                    IOField("scope", "string", False, "Directory scope")
                ],
                outputs=[
                    IOField("results", "array", True, "Search results")
                ]
            ),
            steps=["Parse query", "Select search strategy", "Execute search", "Rank results"],
            tags=["search", "code", "semantic", "fuzzy"]
        )
        
        self.index: Dict[str, str] = {}  # Simple in-memory index
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        query = params.get("query", "")
        search_type = params.get("search_type", "literal")
        scope = params.get("scope", ".")
        
        if not query:
            return AlgorithmResult(status="error", error="No query provided")
        
        print(f"\n🔎 Advanced Search")
        print(f"   Query: {query}, Type: {search_type}")
        
        if search_type == "literal":
            results = self._literal_search(query, scope)
        elif search_type == "regex":
            results = self._regex_search(query, scope)
        elif search_type == "fuzzy":
            results = self._fuzzy_search(query, scope)
        elif search_type == "semantic":
            results = self._semantic_search(query, scope)
        else:
            results = self._literal_search(query, scope)
        
        print(f"   Found: {len(results)} results")
        
        return AlgorithmResult(
            status="success",
            data={
                "results": [self._result_to_dict(r) for r in results[:50]],
                "total": len(results),
                "query": query,
                "search_type": search_type
            }
        )
    
    def _literal_search(self, query: str, scope: str) -> List[SearchResult]:
        results = []
        
        try:
            scope_path = Path(scope)
            if not scope_path.exists():
                return results
            
            for file_path in scope_path.rglob("*.py"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.split('\n'), 1):
                        if query.lower() in line.lower():
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=i,
                                content=line.strip()[:200],
                                match_type="literal",
                                score=1.0
                            ))
                except Exception:
                    pass
        except Exception:
            pass
        
        return results
    
    def _regex_search(self, pattern: str, scope: str) -> List[SearchResult]:
        results = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            scope_path = Path(scope)
            
            for file_path in scope_path.rglob("*.py"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.split('\n'), 1):
                        if regex.search(line):
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=i,
                                content=line.strip()[:200],
                                match_type="regex",
                                score=1.0
                            ))
                except Exception:
                    pass
        except re.error:
            pass
        
        return results
    
    def _fuzzy_search(self, query: str, scope: str) -> List[SearchResult]:
        """Simple fuzzy matching based on character overlap"""
        results = []
        query_chars = set(query.lower())
        
        try:
            scope_path = Path(scope)
            
            for file_path in scope_path.rglob("*.py"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.split('\n'), 1):
                        line_chars = set(line.lower())
                        overlap = len(query_chars & line_chars) / len(query_chars) if query_chars else 0
                        
                        if overlap > 0.7:  # 70% character overlap
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=i,
                                content=line.strip()[:200],
                                match_type="fuzzy",
                                score=overlap
                            ))
                except Exception:
                    pass
        except Exception:
            pass
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results
    
    def _semantic_search(self, query: str, scope: str) -> List[SearchResult]:
        """Semantic search using keyword matching (placeholder for real embeddings)"""
        keywords = query.lower().split()
        results = []
        
        try:
            scope_path = Path(scope)
            
            for file_path in scope_path.rglob("*.py"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.split('\n'), 1):
                        line_lower = line.lower()
                        matches = sum(1 for k in keywords if k in line_lower)
                        
                        if matches > 0:
                            score = matches / len(keywords)
                            results.append(SearchResult(
                                file_path=str(file_path),
                                line_number=i,
                                content=line.strip()[:200],
                                match_type="semantic",
                                score=score
                            ))
                except Exception:
                    pass
        except Exception:
            pass
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results
    
    def _result_to_dict(self, result: SearchResult) -> Dict:
        return {
            "file": result.file_path,
            "line": result.line_number,
            "content": result.content,
            "match_type": result.match_type,
            "score": result.score
        }


def register(algorithm_manager):
    algo = AdvancedSearchAlgorithm()
    algorithm_manager.register("AdvancedSearch", algo)
    print("✅ AdvancedSearch registered")


if __name__ == "__main__":
    algo = AdvancedSearchAlgorithm()
    result = algo.execute({
        "query": "def execute",
        "search_type": "literal",
        "scope": "."
    })
    print(f"Found: {result.data['total']} results")
