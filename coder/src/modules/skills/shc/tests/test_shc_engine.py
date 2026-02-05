#!/usr/bin/env python3
"""
Unit tests for the Self-Healing Codebases (SHC) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from shc_engine import CodeHealer, run_tests

class TestSHCEngine:

    def test_run_tests_on_good_code(self):
        """Test that the simulated test runner passes good code."""
        good_code = "def func(): return True"
        result = run_tests(good_code)
        assert result.passed is True

    def test_run_tests_on_bad_code(self):
        """Test that the simulated test runner fails bad code."""
        bad_code = "this code has an error_keyword"
        result = run_tests(bad_code)
        assert result.passed is False
        assert result.error_message is not None

    def test_healing_cycle_on_healthy_code(self):
        """Test that the healing cycle does nothing if the code is already healthy."""
        healthy_code = "def func(): return True"
        healer = CodeHealer(healthy_code)
        assert healer.run_healing_cycle() is True
        assert healer.healing_attempts == 1 # It runs once to check
        assert healer.current_code == healthy_code

    def test_healing_cycle_on_fixable_bug(self):
        """Test that the healer can fix a known, fixable bug."""
        buggy_code = "result = x / y"
        healer = CodeHealer(buggy_code)
        assert healer.run_healing_cycle() is True
        assert "if y != 0 else 0" in healer.current_code

    def test_healing_cycle_on_unfixable_bug(self):
        """Test that the healer gives up after max attempts on an unknown bug."""
        class BadHealer(CodeHealer):
            def generate_patch(self, diagnosis: str) -> str:
                return self.current_code # Always generate the same buggy code

        buggy_code = "this is an error_keyword"
        healer = BadHealer(buggy_code)
        assert healer.run_healing_cycle() is False
        assert healer.healing_attempts == healer.max_attempts

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
