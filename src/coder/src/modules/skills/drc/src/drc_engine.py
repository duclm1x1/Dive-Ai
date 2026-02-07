#!/usr/bin/env python3
"""
Deterministic Reasoning Chains (DRC) - Skill Implementation

This skill provides a framework for creating, verifying, and executing 
deterministic reasoning chains to ensure verifiable and reproducible AI decision-making.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    """A single step in a reasoning chain."""
    step_id: str
    description: str
    decision: str
    rationale: str
    dependencies: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    verified: bool = False

class DeterministicReasoningChain:
    """Manages a chain of reasoning steps."""

    def __init__(self, chain_id: Optional[str] = None):
        self.chain_id = chain_id or str(uuid.uuid4())
        self.steps: Dict[str, ReasoningStep] = {}
        self.step_order: List[str] = []
        logger.info(f"DRC chain created with ID: {self.chain_id}")

    def add_step(self, description: str, decision: str, rationale: str, dependencies: Optional[List[str]] = None) -> str:
        """Adds a new step to the reasoning chain."""
        step_id = f"DRC-STEP-{len(self.steps) + 1:06d}"
        
        # Ensure dependencies exist
        if dependencies:
            for dep_id in dependencies:
                if dep_id not in self.steps:
                    raise ValueError(f"Dependency '{dep_id}' not found in the chain.")

        step = ReasoningStep(
            step_id=step_id,
            description=description,
            decision=decision,
            rationale=rationale,
            dependencies=dependencies or []
        )
        
        self.steps[step_id] = step
        self.step_order.append(step_id)
        logger.info(f"Added step '{step_id}' to chain '{self.chain_id}'.")
        return step_id

    def get_step(self, step_id: str) -> Optional[ReasoningStep]:
        """Retrieves a step by its ID."""
        return self.steps.get(step_id)

    def verify_step(self, step_id: str, verification_logic: callable) -> bool:
        """Verifies a single step using custom logic."""
        step = self.get_step(step_id)
        if not step:
            raise ValueError(f"Step '{step_id}' not found.")

        is_verified = verification_logic(step)
        step.verified = is_verified
        logger.info(f"Step '{step_id}' verification status: {'PASSED' if is_verified else 'FAILED'}")
        return is_verified

    def verify_chain(self) -> bool:
        """Verifies the entire chain to ensure all steps are verified."""
        return all(step.verified for step in self.steps.values())

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the chain to a dictionary."""
        return {
            "chain_id": self.chain_id,
            "total_steps": len(self.steps),
            "is_verified": self.verify_chain(),
            "steps": [self.steps[step_id].__dict__ for step_id in self.step_order]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeterministicReasoningChain':
        """Deserializes a chain from a dictionary."""
        chain = cls(chain_id=data.get("chain_id"))
        for step_data in data.get("steps", []):
            step = ReasoningStep(**step_data)
            chain.steps[step.step_id] = step
            chain.step_order.append(step.step_id)
        return chain
