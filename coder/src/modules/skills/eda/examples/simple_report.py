#!/usr/bin/env python3
"""
Example usage of the Explainable by Design Architecture (EDA) skill.
"""

import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from eda_engine import ExplanationEngine

def main():
    """Demonstrates logging design decisions and generating a report."""
    print("--- EDA Skill Example: Documenting the Architecture of a Web App ---")

    # 1. Instantiate the explanation engine
    eda = ExplanationEngine()

    # 2. Log decisions as they are made by the AI
    print("\nLogging architectural decisions...")
    eda.log_decision(
        component="Backend Language",
        decision="Python",
        rationale="Excellent for web development with mature frameworks like Flask/Django. Large talent pool.",
        alternatives=["Node.js", "Go"]
    )
    eda.log_decision(
        component="Frontend Framework",
        decision="Vue.js",
        rationale="Gentle learning curve and excellent documentation. Good performance for single-page applications.",
        alternatives=["React", "Svelte"]
    )
    eda.log_decision(
        component="Database",
        decision="PostgreSQL",
        rationale="Open-source, reliable, and supports advanced SQL features and JSON.",
        alternatives=["MySQL", "MongoDB"]
    )

    # 3. Query for a specific explanation
    print("\nQuerying for a specific decision...")
    db_decision = eda.get_explanations_for_component("Database")[0]
    print(f"Why was {db_decision.decision} chosen? Because: {db_decision.rationale}")

    # 4. Generate the final, full-system report
    print("\n--- Generating Full Architectural Report ---")
    report = eda.generate_report()
    print(report)

    print("--- EDA Skill Example Complete ---")

if __name__ == "__main__":
    main()
