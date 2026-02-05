#!/usr/bin/env python3
"""
Unit tests for the Cross-Paradigm Code Generation (CPCG) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cpcg_engine import CodeTranslator

@pytest.fixture
def empty_translator():
    """Provides an empty CodeTranslator for testing."""
    return CodeTranslator()

class TestCPCGEngine:

    def test_translator_creation(self, empty_translator):
        """Test that a translator is created successfully."""
        assert empty_translator is not None

    def test_translate_unknown_requirement(self, empty_translator):
        """Test that an unknown requirement returns an empty list."""
        snippets = empty_translator.translate_requirement("An unknown requirement")
        assert len(snippets) == 0

    def test_translate_auth_requirement(self, empty_translator):
        """Test that the user authentication requirement generates both backend and frontend code."""
        snippets = empty_translator.translate_requirement("Create a user authentication feature")
        
        assert len(snippets) == 2
        
        languages = {s.language for s in snippets}
        assert "Python" in languages
        assert "JavaScript" in languages

    def test_python_snippet_for_auth(self, empty_translator):
        """Test the content of the generated Python snippet for authentication."""
        snippets = empty_translator.translate_requirement("user authentication")
        python_snippet = next(s for s in snippets if s.language == "Python")
        assert "/login" in python_snippet.code
        assert "Flask" in python_snippet.code

    def test_js_snippet_for_auth(self, empty_translator):
        """Test the content of the generated JavaScript snippet for authentication."""
        snippets = empty_translator.translate_requirement("user authentication")
        js_snippet = next(s for s in snippets if s.language == "JavaScript")
        assert "LoginForm" in js_snippet.code
        assert "React" in js_snippet.code
        assert "fetch('/login'" in js_snippet.code

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
