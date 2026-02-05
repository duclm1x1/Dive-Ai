"""
Dive Engine V2 - Inference-Time Scaling
========================================

This module implements inference-time compute scaling techniques:
- Multi-sample generation with majority voting
- Search-beam exploration
- Self-consistency checking
- Consensus-based answer selection

Based on:
- GPT-5.2 Reasoning Model (multi-sample, self-consistency)
- Research on inference-time scaling
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from dive_engine.core.models import ThinkingBlock, ThinkingPhase, utcnow_iso


# =============================================================================
# SAMPLE
# =============================================================================

@dataclass
class Sample:
    """A single reasoning sample."""
    sample_id: str
    content: str
    answer: str
    confidence: float = 0.0
    thinking_blocks: List[ThinkingBlock] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_answer_hash(self) -> str:
        """Get hash of answer for clustering."""
        return hashlib.md5(self.answer.encode()).hexdigest()[:8]


# =============================================================================
# MULTI-SAMPLE ENGINE
# =============================================================================

class MultiSampleEngine:
    """
    Multi-sample generation with majority voting.
    
    This engine:
    - Generates multiple independent samples
    - Clusters similar answers
    - Selects majority answer
    - Computes confidence from agreement
    """
    
    def __init__(
        self,
        llm_client: Any,
        num_samples: int = 5,
        temperature: float = 0.8,
    ):
        """
        Initialize multi-sample engine.
        
        Args:
            llm_client: LLM client
            num_samples: Number of samples to generate
            temperature: Sampling temperature
        """
        self.llm_client = llm_client
        self.num_samples = num_samples
        self.temperature = temperature
    
    async def generate_samples(
        self,
        prompt: str,
        system: str,
        tier: str = "tier_think",
    ) -> List[Sample]:
        """
        Generate multiple samples in parallel.
        
        Args:
            prompt: User prompt
            system: System prompt
            tier: Model tier
            
        Returns:
            List of samples
        """
        # Generate samples in parallel
        tasks = [
            self._generate_single_sample(prompt, system, tier, i)
            for i in range(self.num_samples)
        ]
        
        samples = await asyncio.gather(*tasks)
        return samples
    
    async def _generate_single_sample(
        self,
        prompt: str,
        system: str,
        tier: str,
        sample_idx: int,
    ) -> Sample:
        """Generate a single sample."""
        try:
            response = await self.llm_client.call_async(
                prompt=prompt,
                system=system,
                tier=tier,
                temperature=self.temperature,
            )
            
            # Extract answer (last line or after "Answer:")
            answer = self._extract_answer(response)
            
            return Sample(
                sample_id=f"sample_{sample_idx}",
                content=response,
                answer=answer,
                metadata={"temperature": self.temperature},
            )
        
        except Exception as e:
            return Sample(
                sample_id=f"sample_{sample_idx}",
                content=f"Error: {e}",
                answer="",
                metadata={"error": str(e)},
            )
    
    def _extract_answer(self, content: str) -> str:
        """Extract answer from response."""
        # Look for "Answer:" marker
        if "Answer:" in content:
            answer = content.split("Answer:")[-1].strip()
            return answer.split("\n")[0].strip()
        
        # Use last non-empty line
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        return lines[-1] if lines else content[:100]
    
    def cluster_samples(self, samples: List[Sample]) -> Dict[str, List[Sample]]:
        """
        Cluster samples by answer similarity.
        
        Args:
            samples: List of samples
            
        Returns:
            Dict mapping cluster_id to samples
        """
        clusters = defaultdict(list)
        
        for sample in samples:
            cluster_id = sample.get_answer_hash()
            clusters[cluster_id].append(sample)
        
        return dict(clusters)
    
    def select_majority(self, samples: List[Sample]) -> Tuple[Sample, float]:
        """
        Select majority answer with confidence.
        
        Args:
            samples: List of samples
            
        Returns:
            (selected_sample, confidence)
        """
        # Cluster samples
        clusters = self.cluster_samples(samples)
        
        # Find largest cluster
        largest_cluster = max(clusters.values(), key=len)
        
        # Confidence = cluster_size / total_samples
        confidence = len(largest_cluster) / len(samples)
        
        # Select representative from largest cluster
        representative = largest_cluster[0]
        representative.confidence = confidence
        
        return representative, confidence
    
    async def generate_with_voting(
        self,
        prompt: str,
        system: str,
        tier: str = "tier_think",
    ) -> Tuple[str, float, List[Sample]]:
        """
        Generate samples and return majority answer.
        
        Args:
            prompt: User prompt
            system: System prompt
            tier: Model tier
            
        Returns:
            (answer, confidence, all_samples)
        """
        # Generate samples
        samples = await self.generate_samples(prompt, system, tier)
        
        # Select majority
        selected, confidence = self.select_majority(samples)
        
        return selected.answer, confidence, samples


# =============================================================================
# SEARCH BEAM
# =============================================================================

@dataclass
class BeamState:
    """A state in beam search."""
    state_id: str
    content: str
    score: float
    parent: Optional[BeamState] = None
    depth: int = 0
    is_terminal: bool = False
    
    def get_path(self) -> List[BeamState]:
        """Get path from root to this state."""
        path = []
        current = self
        while current:
            path.append(current)
            current = current.parent
        return list(reversed(path))


# =============================================================================
# SEARCH-BEAM ENGINE
# =============================================================================

class SearchBeamEngine:
    """
    Search-beam exploration for complex reasoning.
    
    This engine:
    - Explores multiple reasoning paths
    - Prunes low-scoring paths
    - Expands promising paths
    - Returns best path
    """
    
    def __init__(
        self,
        llm_client: Any,
        beam_width: int = 3,
        max_depth: int = 5,
        scorer: Optional[Callable[[str], float]] = None,
    ):
        """
        Initialize search-beam engine.
        
        Args:
            llm_client: LLM client
            beam_width: Number of beams to maintain
            max_depth: Maximum search depth
            scorer: Function to score states
        """
        self.llm_client = llm_client
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.scorer = scorer or self._default_scorer
    
    async def search(
        self,
        initial_prompt: str,
        system: str,
        tier: str = "tier_think",
    ) -> Tuple[BeamState, List[BeamState]]:
        """
        Perform beam search.
        
        Args:
            initial_prompt: Initial prompt
            system: System prompt
            tier: Model tier
            
        Returns:
            (best_state, all_terminal_states)
        """
        # Initialize with root state
        beams = [BeamState(
            state_id="root",
            content=initial_prompt,
            score=1.0,
            depth=0,
        )]
        
        terminal_states = []
        
        # Search
        for depth in range(self.max_depth):
            # Expand each beam
            candidates = []
            
            for beam in beams:
                if beam.is_terminal:
                    terminal_states.append(beam)
                    continue
                
                # Generate expansions
                expansions = await self._expand_beam(beam, system, tier)
                candidates.extend(expansions)
            
            if not candidates:
                break
            
            # Score and prune
            for candidate in candidates:
                candidate.score = self.scorer(candidate.content)
            
            # Keep top beam_width
            candidates.sort(key=lambda x: x.score, reverse=True)
            beams = candidates[:self.beam_width]
            
            # Check for terminal states
            for beam in beams:
                if self._is_terminal(beam.content):
                    beam.is_terminal = True
                    terminal_states.append(beam)
        
        # Add remaining beams to terminal states
        terminal_states.extend([b for b in beams if not b.is_terminal])
        
        # Select best terminal state
        if terminal_states:
            best = max(terminal_states, key=lambda x: x.score)
        else:
            best = beams[0] if beams else BeamState(
                state_id="empty",
                content="",
                score=0.0,
            )
        
        return best, terminal_states
    
    async def _expand_beam(
        self,
        beam: BeamState,
        system: str,
        tier: str,
    ) -> List[BeamState]:
        """Expand a beam into multiple candidates."""
        # Generate multiple continuations
        prompt = f"{beam.content}\n\nContinue reasoning (provide 1-2 next steps):"
        
        try:
            # Generate 2-3 expansions with different temperatures
            tasks = [
                self.llm_client.call_async(
                    prompt=prompt,
                    system=system,
                    tier=tier,
                    temperature=0.7 + i * 0.1,
                    max_tokens=500,
                )
                for i in range(2)
            ]
            
            responses = await asyncio.gather(*tasks)
            
            # Create new states
            expansions = []
            for i, response in enumerate(responses):
                new_state = BeamState(
                    state_id=f"{beam.state_id}_exp{i}",
                    content=beam.content + "\n\n" + response,
                    score=0.0,  # Will be scored later
                    parent=beam,
                    depth=beam.depth + 1,
                )
                expansions.append(new_state)
            
            return expansions
        
        except Exception as e:
            print(f"Beam expansion failed: {e}")
            return []
    
    def _default_scorer(self, content: str) -> float:
        """Default scoring function."""
        # Simple heuristic: longer reasoning = better (up to a point)
        length_score = min(len(content) / 1000, 1.0)
        
        # Bonus for reasoning indicators
        reasoning_keywords = ["because", "therefore", "thus", "since", "if", "then"]
        keyword_count = sum(1 for kw in reasoning_keywords if kw in content.lower())
        keyword_score = min(keyword_count * 0.1, 0.5)
        
        return length_score * 0.5 + keyword_score * 0.5
    
    def _is_terminal(self, content: str) -> bool:
        """Check if state is terminal."""
        # Terminal if contains "Answer:" or "Conclusion:"
        return any(marker in content for marker in ["Answer:", "Conclusion:", "Final answer:"])


# =============================================================================
# SELF-CONSISTENCY CHECKER
# =============================================================================

class SelfConsistencyChecker:
    """
    Checks self-consistency across multiple samples.
    
    This checker:
    - Compares answers across samples
    - Identifies inconsistencies
    - Computes consistency score
    """
    
    def __init__(self):
        """Initialize self-consistency checker."""
        pass
    
    def check(self, samples: List[Sample]) -> Tuple[float, List[str]]:
        """
        Check self-consistency.
        
        Args:
            samples: List of samples
            
        Returns:
            (consistency_score, inconsistencies)
        """
        if len(samples) < 2:
            return 1.0, []
        
        # Cluster answers
        answer_counts = Counter([s.get_answer_hash() for s in samples])
        
        # Consistency = size_of_largest_cluster / total_samples
        largest_cluster_size = max(answer_counts.values())
        consistency_score = largest_cluster_size / len(samples)
        
        # Identify inconsistencies
        inconsistencies = []
        if consistency_score < 0.8:
            for answer_hash, count in answer_counts.items():
                if count < largest_cluster_size:
                    # Find sample with this answer
                    sample = next(s for s in samples if s.get_answer_hash() == answer_hash)
                    inconsistencies.append(
                        f"Answer variant ({count}/{len(samples)}): {sample.answer[:100]}"
                    )
        
        return consistency_score, inconsistencies


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_multi_sample_engine(
    llm_client: Any,
    num_samples: int = 5,
) -> MultiSampleEngine:
    """Create multi-sample engine."""
    return MultiSampleEngine(
        llm_client=llm_client,
        num_samples=num_samples,
    )


def create_search_beam_engine(
    llm_client: Any,
    beam_width: int = 3,
) -> SearchBeamEngine:
    """Create search-beam engine."""
    return SearchBeamEngine(
        llm_client=llm_client,
        beam_width=beam_width,
    )
