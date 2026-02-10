"""
🗜️ CONTEXT COMPRESSION (CAC)
Context-Aware Compression for efficient token usage

Based on V28's layer3_contextualcompression.py + cac/
"""

import os
import sys
import re
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class CompressionResult:
    """Result of context compression"""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    preserved_entities: List[str]
    removed_sections: List[str]


class ContextCompressionAlgorithm(BaseAlgorithm):
    """
    🗜️ Context-Aware Compression (CAC)
    
    Intelligently compresses context while preserving:
    - Key entities (names, functions, classes)
    - Important relationships
    - Critical information
    
    From V28: CAC module (8/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ContextCompression",
            name="Context Compression (CAC)",
            level="operational",
            category="context",
            version="1.0",
            description="Intelligent context compression for token efficiency",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("context", "string", True, "Context to compress"),
                    IOField("target_ratio", "number", False, "Target compression (0.3-0.9)"),
                    IOField("preserve", "array", False, "Keywords to preserve")
                ],
                outputs=[
                    IOField("compressed", "string", True, "Compressed context"),
                    IOField("stats", "object", True, "Compression statistics")
                ]
            ),
            steps=["Extract entities", "Score importance", "Prune low-value", "Reconstruct"],
            tags=["compression", "context", "cac", "tokens"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        context = params.get("context", "")
        target_ratio = params.get("target_ratio", 0.5)
        preserve = params.get("preserve", [])
        
        if not context:
            return AlgorithmResult(status="error", error="No context provided")
        
        print(f"\n🗜️ Context Compression (CAC)")
        original_tokens = self._estimate_tokens(context)
        print(f"   Original: {original_tokens} tokens")
        
        # Extract entities to preserve
        entities = self._extract_entities(context)
        entities.extend(preserve)
        
        # Compress
        compressed = self._compress(context, entities, target_ratio)
        compressed_tokens = self._estimate_tokens(compressed)
        
        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        print(f"   Compressed: {compressed_tokens} tokens ({ratio:.1%})")
        
        return AlgorithmResult(
            status="success",
            data={
                "compressed": compressed,
                "stats": {
                    "original_tokens": original_tokens,
                    "compressed_tokens": compressed_tokens,
                    "compression_ratio": ratio,
                    "preserved_entities": entities[:10],
                    "savings": original_tokens - compressed_tokens
                }
            }
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 4 chars = 1 token)"""
        return len(text) // 4
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract important entities"""
        entities = []
        
        # Function/method names
        functions = re.findall(r'def\s+(\w+)|function\s+(\w+)', text)
        entities.extend([f[0] or f[1] for f in functions])
        
        # Class names
        classes = re.findall(r'class\s+(\w+)', text)
        entities.extend(classes)
        
        # Variables (capitalized or snake_case important ones)
        variables = re.findall(r'\b([A-Z][A-Z_]+|[a-z]+_[a-z_]+)\b', text)
        entities.extend(list(set(variables))[:20])
        
        return list(set(entities))
    
    def _compress(self, text: str, preserve: List[str], target_ratio: float) -> str:
        lines = text.split('\n')
        scored_lines = []
        
        for i, line in enumerate(lines):
            score = self._score_line(line, preserve)
            scored_lines.append((score, i, line))
        
        # Sort by score
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        
        # Keep top lines based on target ratio
        target_lines = max(1, int(len(lines) * target_ratio))
        kept = sorted(scored_lines[:target_lines], key=lambda x: x[1])
        
        return '\n'.join(line for _, _, line in kept)
    
    def _score_line(self, line: str, preserve: List[str]) -> float:
        score = 0.0
        
        # Preserved entities
        for entity in preserve:
            if entity in line:
                score += 10
        
        # Code patterns
        if re.search(r'^(def|class|function|import|from)\s', line.strip()):
            score += 8
        if re.search(r'(return|yield|raise|assert)\s', line):
            score += 5
        if re.search(r'#.*TODO|#.*FIXME|#.*IMPORTANT', line, re.I):
            score += 7
        
        # Penalize empty/whitespace
        if not line.strip():
            score -= 5
        if len(line.strip()) < 5:
            score -= 2
        
        return score


def register(algorithm_manager):
    algo = ContextCompressionAlgorithm()
    algorithm_manager.register("ContextCompression", algo)
    print("✅ ContextCompression registered")


if __name__ == "__main__":
    algo = ContextCompressionAlgorithm()
    test_context = """
def calculate_total(items):
    # TODO: Add validation
    total = 0
    for item in items:
        total += item.price
    return total

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def get_total(self):
        return calculate_total(self.items)
"""
    result = algo.execute({"context": test_context, "target_ratio": 0.6})
    print(f"\nCompressed:\n{result.data['compressed']}")
