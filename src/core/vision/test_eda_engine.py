#!/usr/bin/env python3
"""
Unit tests for the Explainable by Design Architecture (EDA) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from eda_engine import ExplanationEngine

@pytest.fixture
def empty_engine():
    """Provides an empty ExplanationEngine for testing."""
    return ExplanationEngine()

class TestEDAEngine:

    def test_engine_creation(self, empty_engine):
        """Test that an engine is created with an empty decision log."""
        assert len(empty_engine.decisions) == 0

    def test_log_decision(self, empty_engine):
        """Test logging a single decision."""
        decision_id = empty_engine.log_decision("Test Component", "Choice A", "Because it is simple.")
        assert len(empty_engine.decisions) == 1
        assert empty_engine.get_decision(decision_id) is not None

    def test_get_explanations_for_component(self, empty_engine):
        """Test retrieving all decisions for a specific component."""
        empty_engine.log_decision("Database", "Postgres", "It is robust.")
        empty_engine.log_decision("Database", "Use ORM", "It is safer.")
        empty_engine.log_decision("Cache", "Redis", "It is fast.")

        db_decisions = empty_engine.get_explanations_for_component("Database")
        cache_decisions = empty_engine.get_explanations_for_component("Cache")

        assert len(db_decisions) == 2
        assert len(cache_decisions) == 1

    def test_generate_report_empty(self, empty_engine):
        """Test that the report for an empty log is handled gracefully."""
        report = empty_engine.generate_report()
        assert "No design decisions" in report

    def test_generate_report_full(self, empty_engine):
        """Test that the full report contains all logged information."""
        empty_engine.log_decision("Database", "Postgres", "It is robust.", ["MySQL"])
        report = empty_engine.generate_report()

        assert "Component: Database" in report
        assert "Decision: Postgres" in report
        assert "Rationale: It is robust." in report
        assert "Alternatives Considered: MySQL" in report

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
