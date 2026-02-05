#!/usr/bin/env python3
"""
Example usage of the Dynamic Agent Composition (DAC) skill.
"""

import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from dac_engine import AgentComposer, AgentProfile

def main():
    """Demonstrates composing a team of agents for a project."""
    print("--- DAC Skill Example: Composing a Team for a Web App ---")

    # 1. Instantiate the composer and register available agents
    dac = AgentComposer()
    
    dac.register_agent(AgentProfile(
        agent_id="frontend-01", name="React Expert", 
        capabilities={"react", "typescript", "css"}
    ))
    dac.register_agent(AgentProfile(
        agent_id="backend-01", name="Node.js Expert", 
        capabilities={"nodejs", "api-design", "sql"}
    ))
    dac.register_agent(AgentProfile(
        agent_id="db-admin-01", name="Database Admin", 
        capabilities={"sql", "postgres-admin", "performance-tuning"}
    ))
    dac.register_agent(AgentProfile(
        agent_id="sec-ops-01", name="Security Specialist", 
        capabilities={"api-security", "authn", "authz"}
    ))
    print(f"\nRegistered {len(dac.agent_pool)} agents in the pool.")

    # 2. Define the requirements for a new project
    project_requirements = {"react", "api-design", "api-security", "sql"}
    print(f"\nProject requires the following capabilities: {project_requirements}")

    # 3. Compose the optimal team
    print("\nComposing the optimal team...")
    team = dac.compose_team(project_requirements)

    print(f"\n--- Composed Team ({len(team)} agents) ---")
    for agent in team:
        print(f"- {agent.name} (ID: {agent.agent_id}) providing: {agent.capabilities.intersection(project_requirements)}")

    # 4. Check for any uncovered capabilities
    uncovered = dac.get_uncovered_capabilities(project_requirements, team)
    if uncovered:
        print(f"\n❌ Warning: The following required capabilities could not be covered: {uncovered}")
    else:
        print("\n✅ Success: All project capabilities are covered by the composed team.")

    print("\n--- DAC Skill Example Complete ---")

if __name__ == "__main__":
    main()
