#!/usr/bin/env python3
"""
Example usage of the Cross-Paradigm Code Generation (CPCG) skill.
"""

import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cpcg_engine import CodeTranslator

def main():
    """Demonstrates translating a high-level requirement into a full-stack implementation."""
    print("--- CPCG Skill Example: Generating a Full-Stack Feature ---")

    # 1. Instantiate the code translator
    cpcg = CodeTranslator()

    # 2. Define a high-level requirement
    requirement = "Create a complete user authentication feature."
    print(f"\nTranslating requirement: {requirement}\n")

    # 3. Generate the code snippets
    snippets = cpcg.translate_requirement(requirement)

    # 4. Display the results
    if not snippets:
        print("Could not generate code for this requirement.")
        return

    for snippet in snippets:
        print(f"--- Generated Code: {snippet.language} ---")
        print(snippet.code)
        print("------------------------------------\n")

    print("--- CPCG Skill Example Complete ---")

if __name__ == "__main__":
    main()
