#!/usr/bin/env python3
"""
Unit tests for the Ethical Guardrails with Formal Verification (EGFV) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from egfv_engine import GuardrailVerifier

@pytest.fixture
def empty_verifier():
    """Provides an empty GuardrailVerifier for testing."""
    return GuardrailVerifier()

class TestEGFVEngine:

    def test_verifier_creation(self, empty_verifier):
        """Test that a verifier is created with default policies."""
        assert len(empty_verifier.policies) > 0

    def test_verify_compliant_code(self, empty_verifier):
        """Test that compliant code passes all default policies."""
        compliant_code = "def my_function(): return True"
        results = empty_verifier.verify_code(compliant_code)
        assert all(r.passed for r in results)

    def test_verify_pii_violation(self, empty_verifier):
        """Test that code violating the PII policy is caught."""
        violating_code = "def bad_function(): store_pii()"
        results = empty_verifier.verify_code(violating_code)
        pii_result = next(r for r in results if r.policy_id == "P001")
        assert pii_result.passed is False

    def test_verify_deception_violation(self, empty_verifier):
        """Test that code violating the deception policy is caught."""
        violating_code = "def bad_function(): fake_reviews()"
        results = empty_verifier.verify_code(violating_code)
        deception_result = next(r for r in results if r.policy_id == "P002")
        assert deception_result.passed is False

    def test_verify_data_deletion_violation(self, empty_verifier):
        """Test that code violating the data deletion policy is caught."""
        violating_code = "def bad_function(): prevent_data_deletion()"
        results = empty_verifier.verify_code(violating_code)
        deletion_result = next(r for r in results if r.policy_id == "P003")
        assert deletion_result.passed is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
