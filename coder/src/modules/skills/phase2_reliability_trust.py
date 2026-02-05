#!/usr/bin/env python3
"""
Phase 2: Adding Reliability and Trust (MVP + EGFV + EDA)

This module integrates Multi-Layered Verification Protocol (MVP), Ethical Guardrails (EGFV),
and Explainable by Design Architecture (EDA) to ensure code quality, safety, and transparency.

Flow:
1. Receive generated code from Phase 1
2. MVP runs comprehensive tests and verification
3. EGFV checks ethical compliance
4. EDA logs all decisions for transparency
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mvp', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'egfv', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'eda', 'src'))

from mvp_engine import VerificationEngine
from egfv_engine import GuardrailVerifier
from eda_engine import ExplanationEngine

class Phase2ReliabilityTrust:
    """Orchestrates Phase 2 integration: MVP -> EGFV -> EDA"""

    def __init__(self):
        self.verifier = VerificationEngine()
        self.guardrail_checker = GuardrailVerifier()
        self.explanation_engine = ExplanationEngine()
        logger.info("Phase 2 Reliability & Trust initialized.")

    def verify_generated_code(self, code_snippets: dict) -> dict:
        """
        Main entry point: verifies code for quality, safety, and transparency.
        
        Returns a dictionary with verification results.
        """
        logger.info(f"\n=== PHASE 2: RELIABILITY & TRUST ===\n")

        results = {
            "code_snippets": code_snippets,
            "verification_results": {},
            "ethical_results": {},
            "decisions_logged": {}
        }

        for task_id, snippets in code_snippets.items():
            logger.info(f"--- Verifying Task {task_id} ---")
            
            for snippet in snippets:
                # Step 1: MVP verification
                logger.info(f"Running MVP verification for {snippet.language}...")
                mvp_results = self.verifier.verify_code(snippet.code)
                results["verification_results"][f"{task_id}_{snippet.language}"] = mvp_results
                
                # Step 2: EGFV ethical checks
                logger.info(f"Running EGFV ethical checks for {snippet.language}...")
                ethical_results = self.guardrail_checker.verify_code(snippet.code)
                results["ethical_results"][f"{task_id}_{snippet.language}"] = ethical_results
                
                # Step 3: EDA logging
                logger.info(f"Logging decision for {snippet.language} implementation...")
                decision_id = self.explanation_engine.log_decision(
                    component=f"{task_id}_{snippet.language}",
                    decision=f"Implemented in {snippet.language}",
                    rationale=f"Generated code for {task_id} using {snippet.language}",
                    alternatives=[f"Alternative language options"]
                )
                results["decisions_logged"][f"{task_id}_{snippet.language}"] = decision_id

        return results

    def generate_report(self, results: dict) -> str:
        """Generates a comprehensive Phase 2 report."""
        report = f"\n{'='*60}\n"
        report += f"PHASE 2: RELIABILITY & TRUST REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"--- Verification Results (MVP) ---\n"
        for key, result in results["verification_results"].items():
            report += f"  {key}: {'✅ PASSED' if result else '❌ FAILED'}\n"
        
        report += f"\n--- Ethical Verification Results (EGFV) ---\n"
        for key, ethical_checks in results["ethical_results"].items():
            passed_count = sum(1 for r in ethical_checks if r.passed)
            total_count = len(ethical_checks)
            report += f"  {key}: {passed_count}/{total_count} policies passed\n"
        
        report += f"\n--- Decisions Logged (EDA) ---\n"
        for key, decision_id in results["decisions_logged"].items():
            report += f"  {key}: {decision_id}\n"
        
        report += f"\n--- Full Architecture Explanation ---\n"
        report += self.explanation_engine.generate_report()
        
        report += f"\n{'='*60}\n"
        return report


def main():
    """Demonstrates Phase 2 Reliability & Trust."""
    from phase1_foundational_loop import Phase1FoundationalLoop
    
    # First, generate code using Phase 1
    phase1 = Phase1FoundationalLoop()
    phase1_result = phase1.process_user_prompt("Build a login page")
    
    # Then, verify it using Phase 2
    phase2 = Phase2ReliabilityTrust()
    phase2_result = phase2.verify_generated_code(phase1_result["code_snippets"])
    
    # Generate and print the report
    report = phase2.generate_report(phase2_result)
    print(report)


if __name__ == "__main__":
    main()
