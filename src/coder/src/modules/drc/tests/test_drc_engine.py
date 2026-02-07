#!/usr/bin/env python3
"""
Unit tests for the Deterministic Reasoning Chains (DRC) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from drc_engine import DeterministicReasoningChain, ReasoningStep

@pytest.fixture
def empty_chain():
    """Provides an empty DRC for testing."""
    return DeterministicReasoningChain()

class TestDRCEngine:

    def test_chain_creation(self, empty_chain):
        """Test that a chain is created with a unique ID."""
        assert empty_chain.chain_id is not None
        assert len(empty_chain.steps) == 0

    def test_add_step(self, empty_chain):
        """Test adding a single step to the chain."""
        step_id = empty_chain.add_step("desc", "dec", "rat")
        assert len(empty_chain.steps) == 1
        assert empty_chain.get_step(step_id) is not None

    def test_add_step_with_dependency(self, empty_chain):
        """Test adding a step that depends on another."""
        step1_id = empty_chain.add_step("desc1", "dec1", "rat1")
        step2_id = empty_chain.add_step("desc2", "dec2", "rat2", dependencies=[step1_id])
        step2 = empty_chain.get_step(step2_id)
        assert step2.dependencies == [step1_id]

    def test_add_step_with_missing_dependency_fails(self, empty_chain):
        """Test that adding a step with a non-existent dependency raises an error."""
        with pytest.raises(ValueError):
            empty_chain.add_step("desc", "dec", "rat", dependencies=["MISSING-STEP"])

    def test_step_verification(self, empty_chain):
        """Test the verification of a single step."""
        step_id = empty_chain.add_step("desc", "dec", "rat")
        
        # Test successful verification
        assert empty_chain.verify_step(step_id, lambda step: True) is True
        assert empty_chain.get_step(step_id).verified is True

        # Test failed verification
        assert empty_chain.verify_step(step_id, lambda step: False) is False
        assert empty_chain.get_step(step_id).verified is False

    def test_chain_verification(self, empty_chain):
        """Test the verification of the entire chain."""
        step1_id = empty_chain.add_step("desc1", "dec1", "rat1")
        step2_id = empty_chain.add_step("desc2", "dec2", "rat2")

        # Chain is not verified if steps are not verified
        assert empty_chain.verify_chain() is False

        empty_chain.verify_step(step1_id, lambda s: True)
        assert empty_chain.verify_chain() is False

        empty_chain.verify_step(step2_id, lambda s: True)
        assert empty_chain.verify_chain() is True

    def test_serialization_deserialization(self, empty_chain):
        """Test that a chain can be serialized to and from a dictionary."""
        step1_id = empty_chain.add_step("desc1", "dec1", "rat1")
        empty_chain.verify_step(step1_id, lambda s: True)

        chain_data = empty_chain.to_dict()
        loaded_chain = DeterministicReasoningChain.from_dict(chain_data)

        assert loaded_chain.chain_id == empty_chain.chain_id
        assert len(loaded_chain.steps) == len(empty_chain.steps)
        assert loaded_chain.verify_chain() is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
