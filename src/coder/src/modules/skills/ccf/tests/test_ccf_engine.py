#!/usr/bin/env python3
"""
Unit tests for the Contextual Compression with Foresight (CCF) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ccf_engine import ContextManager

@pytest.fixture
def empty_manager():
    """Provides an empty ContextManager for testing."""
    return ContextManager(context_limit=100)

class TestCCFEngine:

    def test_manager_creation(self, empty_manager):
        """Test that a manager is created with the correct limit."""
        assert empty_manager.context_limit == 100
        assert len(empty_manager.documents) == 0

    def test_add_document(self, empty_manager):
        """Test adding a single document."""
        empty_manager.add_document("Test content")
        assert len(empty_manager.documents) == 1
        assert empty_manager._get_current_size() == 12

    def test_compression_not_needed(self, empty_manager):
        """Test that compression doesn't happen if the context is within limits."""
        empty_manager.add_document("Short content")
        initial_size = empty_manager._get_current_size()
        empty_manager.compress_context()
        assert empty_manager._get_current_size() == initial_size

    def test_compression_by_summarization(self):
        """Test that the least relevant document gets summarized first."""
        manager = ContextManager(context_limit=120)
        manager.add_document("This is a very long document that is not very relevant.", relevance_score=1.0) # 55 chars
        manager.add_document("This is a highly relevant document that should not be touched.", relevance_score=10.0) # 66 chars
        
        # Total size is 121, which is over the limit of 120
        manager.compress_context()
        
        low_rel_doc = next(d for d in manager.documents.values() if d.relevance_score == 1.0)
        high_rel_doc = next(d for d in manager.documents.values() if d.relevance_score == 10.0)

        assert low_rel_doc.is_summarized is True
        assert high_rel_doc.is_summarized is False

    def test_compression_by_deletion(self):
        """Test that the least relevant document is deleted if summarization is not enough."""
        # Use a very small limit
        manager = ContextManager(context_limit=50)
        manager.add_document("This is a very long document that will be summarized and then deleted.", relevance_score=1.0) # 74 chars
        manager.add_document("This is another long document that will be summarized but should remain.", relevance_score=2.0) # 77 chars
        
        manager.compress_context()

        # After summarization, the context is still too large, so the least relevant doc is deleted.
        assert len(manager.documents) == 1
        assert list(manager.documents.values())[0].relevance_score == 2.0

    def test_foresight_boosts_relevance(self, empty_manager):
        """Test that the foresight mechanism correctly boosts the relevance of a document."""
        doc_id = empty_manager.add_document("This document is about the database.", relevance_score=5.0)
        doc = empty_manager.documents[doc_id]

        empty_manager.predict_future_needs("Time to work on the database setup")
        
        assert doc.relevance_score > 5.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
