#!/usr/bin/env python3
"""
Example usage of the Deterministic Reasoning Chains (DRC) skill.
"""

import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from drc_engine import DeterministicReasoningChain, ReasoningStep

def main():
    """Demonstrates creating, verifying, and serializing a DRC."""
    print("--- DRC Skill Example: Simple Software Design Chain ---")

    # 1. Create a new reasoning chain
    design_chain = DeterministicReasoningChain()
    print(f"Created a new chain with ID: {design_chain.chain_id}")

    # 2. Add steps to the chain
    print("\nAdding reasoning steps...")
    step1_id = design_chain.add_step(
        description="Analyze user prompt for core requirements.",
        decision="Identify a need for a web application with a user database.",
        rationale="The user prompt was: \"Create a web app for users to sign up and log in.\""
    )

    step2_id = design_chain.add_step(
        description="Select frontend technology.",
        decision="Choose React.js.",
        rationale="React.js is a popular and robust choice for building interactive user interfaces.",
        dependencies=[step1_id]
    )

    step3_id = design_chain.add_step(
        description="Select backend technology.",
        decision="Choose Node.js with Express.",
        rationale="Node.js is well-suited for I/O-heavy applications like a web server, and Express is a standard framework.",
        dependencies=[step1_id]
    )

    step4_id = design_chain.add_step(
        description="Select database technology.",
        decision="Choose PostgreSQL.",
        rationale="PostgreSQL is a reliable, open-source relational database perfect for storing user data.",
        dependencies=[step1_id]
    )

    # 3. Verify each step
    print("\nVerifying steps...")
    
    def verify_requirements(step: ReasoningStep) -> bool:
        return "web application" in step.decision and "database" in step.decision

    def verify_frontend(step: ReasoningStep) -> bool:
        return "React" in step.decision

    def verify_backend(step: ReasoningStep) -> bool:
        return "Node.js" in step.decision

    def verify_database(step: ReasoningStep) -> bool:
        return "PostgreSQL" in step.decision

    design_chain.verify_step(step1_id, verify_requirements)
    design_chain.verify_step(step2_id, verify_frontend)
    design_chain.verify_step(step3_id, verify_backend)
    design_chain.verify_step(step4_id, verify_database)

    # 4. Check the final status of the chain
    print("\nChecking final chain verification status...")
    if design_chain.verify_chain():
        print("✅ Success: The entire reasoning chain has been successfully verified.")
    else:
        print("❌ Failure: Some steps in the chain could not be verified.")

    # 5. Serialize the chain to a dictionary
    print("\nSerializing the chain to a dictionary:")
    chain_data = design_chain.to_dict()
    import json
    print(json.dumps(chain_data, indent=2))

    print("\n--- DRC Skill Example Complete ---")

if __name__ == "__main__":
    main()
