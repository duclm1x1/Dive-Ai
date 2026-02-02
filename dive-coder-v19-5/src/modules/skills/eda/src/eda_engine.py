#!/usr/bin/env python3
"""
Explainable by Design Architecture (EDA) - Skill Implementation

This skill provides a framework for embedding explanations directly into the 
code and architecture, making the AI's decisions transparent and auditable.
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class DesignDecision:
    """Represents a single, documented design choice made by the AI."""
    decision_id: str
    component: str  # The part of the system this decision affects (e.g., 'database', 'frontend_framework')
    decision: str   # The choice that was made (e.g., 'PostgreSQL', 'React')
    rationale: str  # The reason for the choice
    alternatives_considered: List[str] = field(default_factory=list)

class ExplanationEngine:
    """Manages and provides access to the documented design decisions."""

    def __init__(self):
        self.decisions: Dict[str, DesignDecision] = {}
        self.decision_counter = 0
        logger.info("Explanation Engine initialized.")

    def log_decision(self, component: str, decision: str, rationale: str, alternatives: List[str] = None) -> str:
        """Logs a new design decision."""
        self.decision_counter += 1
        decision_id = f"DEC-{self.decision_counter:04d}"
        
        new_decision = DesignDecision(
            decision_id=decision_id,
            component=component,
            decision=decision,
            rationale=rationale,
            alternatives_considered=alternatives or []
        )
        self.decisions[decision_id] = new_decision
        logger.info(f"Logged decision '{decision_id}' for component '{component}'.")
        return decision_id

    def get_decision(self, decision_id: str) -> DesignDecision:
        """Retrieves a specific decision by its ID."""
        return self.decisions.get(decision_id)

    def get_explanations_for_component(self, component: str) -> List[DesignDecision]:
        """Gets all logged decisions related to a specific component."""
        return [dec for dec in self.decisions.values() if dec.component.lower() == component.lower()]

    def generate_report(self) -> str:
        """Generates a full, human-readable report of all design decisions."""
        if not self.decisions:
            return "No design decisions have been logged."

        report = "--- System Architecture Explanation Report ---\n\n"
        for decision in self.decisions.values():
            report += f"Component: {decision.component}\n"
            report += f"  - Decision: {decision.decision}\n"
            report += f"  - Rationale: {decision.rationale}\n"
            if decision.alternatives_considered:
                report += f"  - Alternatives Considered: {', '.join(decision.alternatives_considered)}\n"
            report += "\n"
        
        return report
