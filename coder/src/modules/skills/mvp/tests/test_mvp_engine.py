#!/usr/bin/env python3
"""
Unit tests for the Multi-Layered Verification Protocol (MVP) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mvp_engine import (
    VerificationProtocol,
    StaticAnalysisVerifier,
    UnitTestVerifier,
    IntegrationTestVerifier,
    VerificationLevel
)

@pytest.fixture
def mvp_instance():
    """Provides a VerificationProtocol instance with standard verifiers."""
    protocol = VerificationProtocol()
    protocol.register_verifier(StaticAnalysisVerifier())
    protocol.register_verifier(UnitTestVerifier())
    protocol.register_verifier(IntegrationTestVerifier())
    return protocol

class TestMVPEngine:

    def test_protocol_registration(self):
        """Test that verifiers are registered correctly."""
        protocol = VerificationProtocol()
        assert len(protocol.verifiers) == 0
        protocol.register_verifier(StaticAnalysisVerifier())
        assert len(protocol.verifiers) == 1

    def test_run_protocol_on_good_code(self, mvp_instance):
        """Test running the protocol on code that should pass all checks."""
        good_code = "import os\ndef my_func(): return True"
        results = mvp_instance.run_protocol(good_code)
        assert len(results) == 3
        assert all(r.passed for r in results)

    def test_run_protocol_on_bad_code(self, mvp_instance):
        """Test running the protocol on code that should fail some checks."""
        bad_code = "x = 1 / 0"
        results = mvp_instance.run_protocol(bad_code)
        
        # Expecting static analysis and unit test to fail based on simple heuristics
        static_result = next(r for r in results if r.level == VerificationLevel.STATIC_ANALYSIS)
        unit_test_result = next(r for r in results if r.level == VerificationLevel.UNIT_TEST)
        
        assert static_result.passed is False
        assert unit_test_result.passed is False

    def test_report_generation(self, mvp_instance):
        """Test the generation of the final report."""
        good_code = "import os\ndef my_func(): return True"
        mvp_instance.run_protocol(good_code)
        report = mvp_instance.get_report()

        assert report["total_checks"] == 3
        assert report["passed_checks"] == 3
        assert report["failed_checks"] == 0
        assert report["is_fully_verified"] is True

    def test_report_generation_with_failures(self, mvp_instance):
        """Test report generation when there are verification failures."""
        bad_code = "x = 1 / 0"
        mvp_instance.run_protocol(bad_code)
        report = mvp_instance.get_report()

        assert report["total_checks"] == 3
        assert report["passed_checks"] == 1 # Integration test passes by default
        assert report["failed_checks"] == 2
        assert report["is_fully_verified"] is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
