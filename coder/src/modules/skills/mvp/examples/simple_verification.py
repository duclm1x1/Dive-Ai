#!/usr/bin/env python3
"""
Example usage of the Multi-Layered Verification Protocol (MVP) skill.
"""

import sys
import os
import json

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mvp_engine import (
    VerificationProtocol,
    StaticAnalysisVerifier,
    UnitTestVerifier,
    IntegrationTestVerifier
)

def main():
    """Demonstrates setting up and running the MVP."""
    print("--- MVP Skill Example: Verifying a Simple Python Function ---")

    # 1. Instantiate the protocol and register verifier agents
    mvp = VerificationProtocol()
    mvp.register_verifier(StaticAnalysisVerifier())
    mvp.register_verifier(UnitTestVerifier())
    mvp.register_verifier(IntegrationTestVerifier())
    print("\nRegistered 3 verifier agents: Static, Unit, and Integration.")

    # 2. Define the code to be verified
    code_to_verify = """
import math

def calculate_circle_area(radius: float) -> float:
    \"\"\"Calculates the area of a circle given its radius.\"\"\"
    if radius < 0:
        raise ValueError("Radius cannot be negative.")
    return math.pi * radius ** 2
"""
    print("\nCode to be verified:")
    print(code_to_verify)

    # 3. Run the verification protocol
    print("\nRunning verification protocol...")
    mvp.run_protocol(code_to_verify)

    # 4. Get and display the final report
    report = mvp.get_report()
    print("\n--- Verification Report ---")
    print(json.dumps(report, indent=2))

    if report["is_fully_verified"]:
        print("\n✅ Success: The code has passed all verification layers.")
    else:
        print("\n❌ Failure: The code did not pass all verification checks.")

    print("\n--- MVP Skill Example Complete ---")

if __name__ == "__main__":
    main()
