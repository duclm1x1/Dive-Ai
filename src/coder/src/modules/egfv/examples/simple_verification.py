#!/usr/bin/env python3
"""
Example usage of the Ethical Guardrails with Formal Verification (EGFV) skill.
"""

import sys
import os
import logging

# Configure logging to see the engine's decisions
logging.basicConfig(level=logging.INFO, format=\'%(levelname)s: %(message)s\')

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from egfv_engine import GuardrailVerifier

def main():
    """Demonstrates verifying code against a set of ethical policies."""
    print("--- EGFV Skill Example: Verifying AI-Generated Code ---")

    # 1. Instantiate the verifier
    egfv = GuardrailVerifier()

    # 2. Define a piece of code that violates a policy
    violating_code = """
# This function clearly violates the policy against storing PII.
def process_user(user):
    # ... some processing ...
    # Forbidden action:
    log_user_credentials(user.name, user.password)
"""
    print("\n--- Verifying Code with a Policy Violation ---")
    results_1 = egfv.verify_code(violating_code)
    if not all(r.passed for r in results_1):
        print("\nVerification found one or more issues.")

    # 3. Define a piece of compliant code
    compliant_code = """
# This function is compliant.
def get_user_greeting(user):
    return f"Welcome, {user.name}!"
"""
    print("\n--- Verifying Compliant Code ---")
    results_2 = egfv.verify_code(compliant_code)
    if all(r.passed for r in results_2):
        print("\nVerification passed. The code is compliant with all policies.")

    print("\n--- EGFV Skill Example Complete ---")

if __name__ == "__main__":
    main()
