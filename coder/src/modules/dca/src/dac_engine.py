#!/usr/bin/env python3
"""
Dynamic Agent Composition (DAC) - Skill Implementation

This skill provides a framework for dynamically composing a team of specialist 
agents best suited for a given task, based on their advertised capabilities.
"""

import logging
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class AgentProfile:
    """Represents a specialist agent available for composition."""
    agent_id: str
    name: str
    description: str
    capabilities: Set[str] = field(default_factory=set)

class AgentComposer:
    """Manages a pool of agents and composes teams for tasks."""

    def __init__(self):
        self.agent_pool: Dict[str, AgentProfile] = {}
        logger.info("Agent Composer initialized.")

    def register_agent(self, agent_profile: AgentProfile):
        """Adds a new agent to the available pool."""
        if agent_profile.agent_id in self.agent_pool:
            raise ValueError(f"Agent with ID '{agent_profile.agent_id}' is already registered.")
        self.agent_pool[agent_profile.agent_id] = agent_profile
        logger.info(f"Registered agent: {agent_profile.name} ({agent_profile.agent_id})")

    def get_agent(self, agent_id: str) -> AgentProfile:
        """Retrieves an agent profile by its ID."""
        return self.agent_pool.get(agent_id)

    def compose_team(self, required_capabilities: Set[str]) -> List[AgentProfile]:
        """Composes the best possible team based on required capabilities."""
        if not required_capabilities:
            return []

        team: List[AgentProfile] = []
        team_agent_ids = set()
        covered_capabilities = set()

        # Loop until all required capabilities are covered
        while not required_capabilities.issubset(covered_capabilities):
            best_agent = None
            best_agent_contribution = -1

            # Find the agent that adds the most new capabilities
            for agent in self.agent_pool.values():
                if agent.agent_id in team_agent_ids:
                    continue

                new_capabilities = agent.capabilities.intersection(required_capabilities - covered_capabilities)
                contribution = len(new_capabilities)

                if contribution > best_agent_contribution:
                    best_agent = agent
                    best_agent_contribution = contribution
            
            if best_agent and best_agent_contribution > 0:
                team.append(best_agent)
                team_agent_ids.add(best_agent.agent_id)
                covered_capabilities.update(best_agent.capabilities)
            else:
                # No more agents can contribute, break to avoid infinite loop
                break
        
        logger.info(f"Composed a team of {len(team)} agents to cover {len(covered_capabilities.intersection(required_capabilities))} of {len(required_capabilities)} required capabilities.")
        return team

    def get_uncovered_capabilities(self, required_capabilities: Set[str], team: List[AgentProfile]) -> Set[str]:
        """Returns the set of required capabilities not covered by the composed team."""
        team_capabilities = set()
        for agent in team:
            team_capabilities.update(agent.capabilities)
        return required_capabilities - team_capabilities
