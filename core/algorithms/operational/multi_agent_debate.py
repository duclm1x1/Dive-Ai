"""
🗣️ MULTI-AGENT DEBATE
Enable structured debate between agents for better decisions

Based on V28's vibe_engine/multi_agent_debate.py
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class DebatePosition:
    """A position in the debate"""
    agent_id: str
    stance: str  # "for", "against", "neutral"
    argument: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class DebateRound:
    """A round of debate"""
    round_number: int
    positions: List[DebatePosition]
    consensus_reached: bool = False


class MultiAgentDebateAlgorithm(BaseAlgorithm):
    """
    🗣️ Multi-Agent Debate
    
    Structured debate for decisions:
    - Opposing viewpoints
    - Evidence-based arguments
    - Consensus building
    - Best solution selection
    
    From V28: vibe_engine/multi_agent_debate.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="MultiAgentDebate",
            name="Multi-Agent Debate",
            level="operational",
            category="decision",
            version="1.0",
            description="Structured debate for better decisions",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("topic", "string", True, "Debate topic"),
                    IOField("positions", "array", False, "Initial positions"),
                    IOField("max_rounds", "integer", False, "Max debate rounds")
                ],
                outputs=[
                    IOField("conclusion", "object", True, "Debate conclusion"),
                    IOField("rounds", "array", True, "Debate history")
                ]
            ),
            steps=["Present positions", "Exchange arguments", "Evaluate evidence", "Reach consensus"],
            tags=["debate", "multi-agent", "decision", "consensus"]
        )
        
        self.rounds: List[DebateRound] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        topic = params.get("topic", "")
        positions = params.get("positions", [])
        max_rounds = params.get("max_rounds", 3)
        
        if not topic:
            return AlgorithmResult(status="error", error="No topic provided")
        
        print(f"\n🗣️ Multi-Agent Debate")
        print(f"   Topic: {topic}")
        
        # Initialize positions
        debate_positions = []
        for i, pos in enumerate(positions):
            debate_positions.append(DebatePosition(
                agent_id=pos.get("agent", f"agent_{i}"),
                stance=pos.get("stance", "neutral"),
                argument=pos.get("argument", ""),
                evidence=pos.get("evidence", []),
                confidence=pos.get("confidence", 0.5)
            ))
        
        # If no positions, generate default opposing views
        if not debate_positions:
            debate_positions = self._generate_default_positions(topic)
        
        # Run debate rounds
        consensus = False
        for round_num in range(1, max_rounds + 1):
            round_result = self._run_round(round_num, debate_positions, topic)
            self.rounds.append(round_result)
            
            if round_result.consensus_reached:
                consensus = True
                break
            
            # Update positions based on round
            debate_positions = self._update_positions(debate_positions, round_result)
        
        # Determine winner/conclusion
        conclusion = self._determine_conclusion(debate_positions, consensus)
        
        print(f"   Rounds: {len(self.rounds)}")
        print(f"   Consensus: {'Yes' if consensus else 'No'}")
        
        return AlgorithmResult(
            status="success",
            data={
                "conclusion": conclusion,
                "consensus_reached": consensus,
                "rounds": len(self.rounds),
                "positions": [
                    {"agent": p.agent_id, "stance": p.stance, "confidence": p.confidence}
                    for p in debate_positions
                ]
            }
        )
    
    def _generate_default_positions(self, topic: str) -> List[DebatePosition]:
        return [
            DebatePosition("advocate", "for", f"I support this approach for {topic}", confidence=0.7),
            DebatePosition("critic", "against", f"I have concerns about {topic}", confidence=0.6),
            DebatePosition("mediator", "neutral", f"Let's examine {topic} objectively", confidence=0.5)
        ]
    
    def _run_round(self, round_num: int, positions: List[DebatePosition], topic: str) -> DebateRound:
        # Simulate debate round
        updated_positions = []
        
        for pos in positions:
            new_confidence = pos.confidence
            
            # Simulate influence from other positions
            for other in positions:
                if other.agent_id != pos.agent_id:
                    if other.confidence > pos.confidence:
                        new_confidence += 0.05 * (other.confidence - pos.confidence)
            
            updated_positions.append(DebatePosition(
                agent_id=pos.agent_id,
                stance=pos.stance,
                argument=f"Round {round_num}: {pos.argument}",
                evidence=pos.evidence,
                confidence=min(0.99, new_confidence)
            ))
        
        # Check consensus
        stances = [p.stance for p in updated_positions]
        consensus = len(set(stances)) == 1
        
        return DebateRound(
            round_number=round_num,
            positions=updated_positions,
            consensus_reached=consensus
        )
    
    def _update_positions(self, positions: List[DebatePosition], round_result: DebateRound) -> List[DebatePosition]:
        # Use positions from round result
        return round_result.positions
    
    def _determine_conclusion(self, positions: List[DebatePosition], consensus: bool) -> Dict:
        if consensus:
            return {
                "decision": positions[0].stance,
                "confidence": max(p.confidence for p in positions),
                "method": "consensus"
            }
        
        # Pick highest confidence
        winner = max(positions, key=lambda p: p.confidence)
        return {
            "decision": winner.stance,
            "confidence": winner.confidence,
            "method": "majority",
            "winning_agent": winner.agent_id
        }


def register(algorithm_manager):
    algo = MultiAgentDebateAlgorithm()
    algorithm_manager.register("MultiAgentDebate", algo)
    print("✅ MultiAgentDebate registered")


if __name__ == "__main__":
    algo = MultiAgentDebateAlgorithm()
    result = algo.execute({
        "topic": "Should we use microservices?",
        "positions": [
            {"agent": "architect", "stance": "for", "argument": "Better scalability"},
            {"agent": "developer", "stance": "against", "argument": "Too complex"}
        ],
        "max_rounds": 3
    })
    print(f"Conclusion: {result.data['conclusion']}")
