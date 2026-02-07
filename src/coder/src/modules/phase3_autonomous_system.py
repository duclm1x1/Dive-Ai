#!/usr/bin/env python3
"""
Phase 3: The Autonomous System (SHC + CCF + DRC)

This module integrates Self-Healing Codebases (SHC), Contextual Compression with Foresight (CCF),
and Deterministic Reasoning Chains (DRC) to create a self-managing, self-healing system.

Flow:
1. If Phase 2 verification detects failures, trigger SHC
2. SHC diagnoses and attempts to fix bugs
3. CCF manages context during the healing process
4. DRC ensures reasoning is sound and deterministic
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shc', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ccf', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'drc', 'src'))

from shc_engine import CodeHealer
from ccf_engine import ContextManager
from drc_engine import ReasoningChain

class Phase3AutonomousSystem:
    """Orchestrates Phase 3 integration: SHC + CCF + DRC"""

    def __init__(self):
        self.code_healer = CodeHealer("")  # Will be set per code
        self.context_manager = ContextManager(context_limit=2000)
        self.reasoning_chain = ReasoningChain()
        logger.info("Phase 3 Autonomous System initialized.")

    def handle_verification_failure(self, failed_code: str, error_message: str, original_prompt: str) -> dict:
        """
        Main entry point: handles a verification failure by attempting autonomous healing.
        
        Returns a dictionary with healing results.
        """
        logger.info(f"\n=== PHASE 3: AUTONOMOUS SYSTEM ===\n")
        logger.info(f"Detected verification failure: {error_message}\n")

        results = {
            "original_code": failed_code,
            "error_message": error_message,
            "healing_successful": False,
            "healed_code": None,
            "reasoning_steps": [],
            "context_decisions": []
        }

        # Step 1: Set up context with foresight
        logger.info("--- Step 1: Context Setup (CCF) ---")
        self._setup_context_with_foresight(original_prompt, error_message)

        # Step 2: Build a reasoning chain for diagnosis
        logger.info("\n--- Step 2: Reasoning Chain (DRC) ---")
        reasoning_steps = self._build_diagnosis_chain(error_message)
        results["reasoning_steps"] = reasoning_steps

        # Step 3: Attempt healing
        logger.info("\n--- Step 3: Self-Healing (SHC) ---")
        self.code_healer = CodeHealer(failed_code)
        healing_successful = self.code_healer.run_healing_cycle()
        
        results["healing_successful"] = healing_successful
        if healing_successful:
            results["healed_code"] = self.code_healer.current_code
            logger.info("✅ Healing successful!")
        else:
            logger.warning("❌ Healing failed after maximum attempts.")

        return results

    def _setup_context_with_foresight(self, original_prompt: str, error_message: str):
        """Uses CCF to set up context with foresight."""
        # Add the original prompt with high relevance
        self.context_manager.add_document(
            f"Original user prompt: {original_prompt}",
            relevance_score=10.0
        )
        
        # Add the error message with high relevance
        self.context_manager.add_document(
            f"Error to fix: {error_message}",
            relevance_score=9.0
        )
        
        # Use foresight to predict what will be needed
        self.context_manager.predict_future_needs("Diagnose and fix the error")
        
        logger.info(f"Context initialized with {len(self.context_manager.documents)} documents")

    def _build_diagnosis_chain(self, error_message: str) -> list:
        """Uses DRC to build a deterministic reasoning chain for diagnosis."""
        chain = self.reasoning_chain
        
        # Step 1: Identify error type
        step1 = chain.add_step(
            "Identify Error Type",
            f"Analyzing error: {error_message}",
            ["Error Analysis"]
        )
        
        # Step 2: Determine root cause
        step2 = chain.add_step(
            "Determine Root Cause",
            "Finding the underlying issue",
            [step1]
        )
        
        # Step 3: Generate fix strategy
        step3 = chain.add_step(
            "Generate Fix Strategy",
            "Creating a repair strategy",
            [step2]
        )
        
        # Step 4: Apply fix
        step4 = chain.add_step(
            "Apply Fix",
            "Implementing the repair",
            [step3]
        )
        
        # Step 5: Verify fix
        step5 = chain.add_step(
            "Verify Fix",
            "Testing the repair",
            [step4]
        )
        
        logger.info(f"Built reasoning chain with {len(chain.steps)} steps")
        return chain.steps

    def generate_report(self, results: dict) -> str:
        """Generates a comprehensive Phase 3 report."""
        report = f"\n{'='*60}\n"
        report += f"PHASE 3: AUTONOMOUS SYSTEM REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"Error Detected: {results['error_message']}\n\n"
        
        report += f"--- Reasoning Chain (DRC) ---\n"
        for i, step in enumerate(results["reasoning_steps"], 1):
            report += f"  Step {i}: {step}\n"
        
        report += f"\n--- Healing Result (SHC) ---\n"
        if results["healing_successful"]:
            report += f"  ✅ Healing SUCCESSFUL\n"
            report += f"  Healed code length: {len(results['healed_code'])} characters\n"
        else:
            report += f"  ❌ Healing FAILED\n"
        
        report += f"\n--- Context Management (CCF) ---\n"
        report += f"  Active documents: {len(self.context_manager.documents)}\n"
        report += f"  Context size: {self.context_manager._get_current_size()} characters\n"
        
        report += f"\n{'='*60}\n"
        return report


def main():
    """Demonstrates Phase 3 Autonomous System."""
    phase3 = Phase3AutonomousSystem()
    
    # Simulate a code with a bug
    buggy_code = """
def calculate(x, y):
    result = x / y  # This is a bug - division by zero
    return result
"""
    
    error_message = "ZeroDivisionError: division by zero"
    original_prompt = "Create a calculator function"
    
    # Attempt to heal
    results = phase3.handle_verification_failure(buggy_code, error_message, original_prompt)
    
    # Generate and print the report
    report = phase3.generate_report(results)
    print(report)


if __name__ == "__main__":
    main()
