"""
🔍 EVIDENCE COLLECTOR
Collect and organize evidence for decisions

Based on V28's vibe_engine/evidence_collector.py
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


class EvidenceType(Enum):
    FACTUAL = "factual"
    STATISTICAL = "statistical"
    TESTIMONIAL = "testimonial"
    EXPERIMENTAL = "experimental"
    ANALYTICAL = "analytical"


@dataclass
class Evidence:
    """A piece of evidence"""
    id: str
    type: EvidenceType
    content: str
    source: str
    reliability: float  # 0-1
    supports_claim: str
    timestamp: float


class EvidenceCollectorAlgorithm(BaseAlgorithm):
    """
    🔍 Evidence Collector
    
    Collects and organizes evidence:
    - Evidence gathering
    - Reliability scoring
    - Claim validation
    - Evidence synthesis
    
    From V28: vibe_engine/evidence_collector.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="EvidenceCollector",
            name="Evidence Collector",
            level="operational",
            category="decision",
            version="1.0",
            description="Collect and organize evidence for decisions",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "collect/evaluate/synthesize"),
                    IOField("evidence", "object", False, "Evidence to add"),
                    IOField("claim", "string", False, "Claim to validate")
                ],
                outputs=[
                    IOField("result", "object", True, "Evidence result")
                ]
            ),
            steps=["Collect evidence", "Score reliability", "Match to claims", "Synthesize"],
            tags=["evidence", "decision", "validation"]
        )
        
        self.evidence_store: List[Evidence] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "collect")
        
        print(f"\n🔍 Evidence Collector")
        
        if action == "collect":
            return self._collect(params.get("evidence", {}))
        elif action == "evaluate":
            return self._evaluate_claim(params.get("claim", ""))
        elif action == "synthesize":
            return self._synthesize(params.get("claim", ""))
        elif action == "stats":
            return self._get_stats()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _collect(self, evidence_data: Dict) -> AlgorithmResult:
        evidence = Evidence(
            id=f"ev_{len(self.evidence_store)}",
            type=EvidenceType(evidence_data.get("type", "factual")),
            content=evidence_data.get("content", ""),
            source=evidence_data.get("source", "unknown"),
            reliability=evidence_data.get("reliability", 0.7),
            supports_claim=evidence_data.get("claim", ""),
            timestamp=time.time()
        )
        self.evidence_store.append(evidence)
        
        print(f"   Collected: {evidence.type.value} evidence")
        
        return AlgorithmResult(
            status="success",
            data={"collected": evidence.id, "total_evidence": len(self.evidence_store)}
        )
    
    def _evaluate_claim(self, claim: str) -> AlgorithmResult:
        if not claim:
            return AlgorithmResult(status="error", error="No claim provided")
        
        # Find supporting and contradicting evidence
        supporting = []
        contradicting = []
        
        claim_lower = claim.lower()
        for ev in self.evidence_store:
            if claim_lower in ev.supports_claim.lower() or claim_lower in ev.content.lower():
                supporting.append(ev)
            # Simple heuristic for contradiction
            elif "not" in ev.content.lower() or "false" in ev.content.lower():
                contradicting.append(ev)
        
        # Calculate confidence
        support_score = sum(e.reliability for e in supporting)
        contradict_score = sum(e.reliability for e in contradicting)
        
        if support_score + contradict_score > 0:
            confidence = support_score / (support_score + contradict_score)
        else:
            confidence = 0.5  # No evidence either way
        
        verdict = "supported" if confidence > 0.6 else "disputed" if confidence < 0.4 else "inconclusive"
        
        return AlgorithmResult(
            status="success",
            data={
                "claim": claim,
                "verdict": verdict,
                "confidence": confidence,
                "supporting_count": len(supporting),
                "contradicting_count": len(contradicting)
            }
        )
    
    def _synthesize(self, claim: str) -> AlgorithmResult:
        """Synthesize all evidence for a claim"""
        relevant = [
            ev for ev in self.evidence_store
            if not claim or claim.lower() in ev.supports_claim.lower() or claim.lower() in ev.content.lower()
        ]
        
        if not relevant:
            return AlgorithmResult(
                status="success",
                data={"synthesis": "No relevant evidence found.", "count": 0}
            )
        
        # Sort by reliability
        relevant.sort(key=lambda e: e.reliability, reverse=True)
        
        synthesis = f"Based on {len(relevant)} pieces of evidence:\n"
        for ev in relevant[:5]:
            synthesis += f"- [{ev.type.value}] {ev.content[:100]} (reliability: {ev.reliability:.0%})\n"
        
        return AlgorithmResult(
            status="success",
            data={"synthesis": synthesis, "count": len(relevant)}
        )
    
    def _get_stats(self) -> AlgorithmResult:
        by_type = {}
        for ev in self.evidence_store:
            by_type[ev.type.value] = by_type.get(ev.type.value, 0) + 1
        
        return AlgorithmResult(
            status="success",
            data={
                "total_evidence": len(self.evidence_store),
                "by_type": by_type,
                "avg_reliability": sum(e.reliability for e in self.evidence_store) / len(self.evidence_store) if self.evidence_store else 0
            }
        )


def register(algorithm_manager):
    algo = EvidenceCollectorAlgorithm()
    algorithm_manager.register("EvidenceCollector", algo)
    print("✅ EvidenceCollector registered")


if __name__ == "__main__":
    algo = EvidenceCollectorAlgorithm()
    algo.execute({"action": "collect", "evidence": {"type": "factual", "content": "Python is interpreted", "claim": "Python performance", "reliability": 0.9}})
    algo.execute({"action": "collect", "evidence": {"type": "experimental", "content": "Tests show Python can be slow for loops", "claim": "Python performance", "reliability": 0.8}})
    result = algo.execute({"action": "evaluate", "claim": "Python performance"})
    print(f"Verdict: {result.data['verdict']}")
