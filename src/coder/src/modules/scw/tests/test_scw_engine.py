#!/usr/bin/env python3
"""
Unit tests for the Semantic Code Weaving (SCW) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from scw_engine import SemanticCodeWeaver

@pytest.fixture
def empty_weaver():
    """Provides an empty SemanticCodeWeaver for testing."""
    return SemanticCodeWeaver()

class TestSCWEngine:

    def test_weaver_creation(self, empty_weaver):
        """Test that a weaver is created with an empty graph."""
        assert len(empty_weaver.graph) == 0

    def test_add_node(self, empty_weaver):
        """Test adding a single node to the graph."""
        node_id = empty_weaver.add_node("Test Node", "A node for testing", "test_type")
        assert len(empty_weaver.graph) == 1
        assert empty_weaver.get_node(node_id) is not None

    def test_add_node_with_dependency(self, empty_weaver):
        """Test adding a node with a dependency."""
        node1_id = empty_weaver.add_node("Dep Node", "A dependency", "dep_type")
        node2_id = empty_weaver.add_node("Main Node", "Depends on another", "main_type", dependencies=[node1_id])
        node2 = empty_weaver.get_node(node2_id)
        assert node2.dependencies == [node1_id]

    def test_add_node_with_missing_dependency_fails(self, empty_weaver):
        """Test that adding a node with a non-existent dependency raises an error."""
        with pytest.raises(ValueError):
            empty_weaver.add_node("Test Node", "desc", "type", dependencies=["MISSING-NODE"])

    def test_mark_as_implemented(self, empty_weaver):
        """Test marking a node as implemented."""
        node_id = empty_weaver.add_node("Test Node", "desc", "type")
        node = empty_weaver.get_node(node_id)
        assert node.is_implemented is False
        empty_weaver.mark_as_implemented(node_id)
        assert node.is_implemented is True

    def test_get_implementation_order(self, empty_weaver):
        """Test the topological sort for implementation order."""
        node_c_id = empty_weaver.add_node("C", "", "")
        node_b_id = empty_weaver.add_node("B", "", "", dependencies=[node_c_id])
        node_a_id = empty_weaver.add_node("A", "", "", dependencies=[node_b_id])
        
        order = empty_weaver.get_implementation_order()
        
        assert order.index(node_c_id) < order.index(node_b_id)
        assert order.index(node_b_id) < order.index(node_a_id)

    def test_get_unimplemented_nodes(self, empty_weaver):
        """Test retrieving only the unimplemented nodes."""
        node1_id = empty_weaver.add_node("Node 1", "", "")
        node2_id = empty_weaver.add_node("Node 2", "", "")
        
        assert len(empty_weaver.get_unimplemented_nodes()) == 2
        empty_weaver.mark_as_implemented(node1_id)
        assert len(empty_weaver.get_unimplemented_nodes()) == 1
        assert empty_weaver.get_unimplemented_nodes()[0].node_id == node2_id

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
