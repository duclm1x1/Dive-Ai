#!/usr/bin/env python3
"""
Unit tests for the Dynamic Agent Composition (DAC) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from dac_engine import AgentComposer, AgentProfile

@pytest.fixture
def composer_with_agents():
    """Provides an AgentComposer instance populated with agents."""
    composer = AgentComposer()
    composer.register_agent(AgentProfile("fe", "Frontend", "", {"react", "css"}))
    composer.register_agent(AgentProfile("be", "Backend", "", {"nodejs", "sql"}))
    composer.register_agent(AgentProfile("db", "Database", "", {"sql", "postgres"}))
    return composer

class TestDACEngine:

    def test_agent_registration(self):
        """Test that agents can be registered and retrieved."""
        composer = AgentComposer()
        agent = AgentProfile("test-id", "Test Agent", "", {"testing"})
        composer.register_agent(agent)
        assert composer.get_agent("test-id") is not None
        with pytest.raises(ValueError):
            composer.register_agent(agent) # Cannot register the same ID twice

    def test_compose_team_simple(self, composer_with_agents):
        """Test composing a team with a simple requirement."""
        team = composer_with_agents.compose_team({"react"})
        assert len(team) == 1
        assert team[0].agent_id == "fe"

    def test_compose_team_multiple_disjoint(self, composer_with_agents):
        """Test composing a team for capabilities spread across multiple agents."""
        team = composer_with_agents.compose_team({"react", "nodejs"})
        assert len(team) == 2
        agent_ids = {agent.agent_id for agent in team}
        assert "fe" in agent_ids
        assert "be" in agent_ids

    def test_compose_team_overlapping(self, composer_with_agents):
        """Test that the composer selects agents efficiently for overlapping capabilities."""
        # Requires 'sql' and 'nodejs'. The 'be' agent covers both.
        team = composer_with_agents.compose_team({"sql", "nodejs"})
        assert len(team) == 1
        assert team[0].agent_id == "be"

    def test_compose_team_complex_overlap(self, composer_with_agents):
        """Test a more complex scenario with overlapping capabilities."""
        # Requires 'react', 'sql', and 'postgres'.
        # 'fe' has 'react'. 'be' has 'sql'. 'db' has 'sql' and 'postgres'.
        # Optimal team is 'fe' and 'db'.
        team = composer_with_agents.compose_team({"react", "sql", "postgres"})
        assert len(team) == 2
        agent_ids = {agent.agent_id for agent in team}
        assert "fe" in agent_ids
        assert "db" in agent_ids

    def test_uncovered_capabilities(self, composer_with_agents):
        """Test identifying capabilities that cannot be covered."""
        reqs = {"react", "java"}
        team = composer_with_agents.compose_team(reqs)
        uncovered = composer_with_agents.get_uncovered_capabilities(reqs, team)
        assert uncovered == {"java"}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
