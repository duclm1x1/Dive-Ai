#!/usr/bin/env python3
"""
Example usage of the Self-Healing Codebases (SHC) skill.
"""

import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from shc_engine import CodeHealer

def main():
    """Demonstrates the self-healing workflow on a piece of buggy code."""
    print("--- SHC Skill Example: Healing a Division-by-Zero Bug ---")

    # 1. Define a piece of code with a simulated bug
    buggy_code = """
# Initial buggy code
def risky_division(x, y):
    # This line will fail if y is zero
    result = x / y # This is a bug
    return result
"""

    # 2. Initialize the CodeHealer with the buggy code
    healer = CodeHealer(buggy_code)

    # 3. Run the healing cycle
    # The healer will internally run tests, detect the failure, diagnose,
    # generate a patch, and verify the fix.
    healer.run_healing_cycle()

    print("\n--- SHC Skill Example Complete ---")

if __name__ == "__main__":
    main()
