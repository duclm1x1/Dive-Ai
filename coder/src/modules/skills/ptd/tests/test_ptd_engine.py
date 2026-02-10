#!/usr/bin/env python3
"""
Unit tests for the Predictive Task Decomposition (PTD) skill.
"""

import pytest
import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ptd_engine import TaskDecomposer

@pytest.fixture
def empty_decomposer():
    """Provides an empty TaskDecomposer for testing."""
    return TaskDecomposer()

class TestPTDEngine:

    def test_decomposer_creation(self, empty_decomposer):
        """Test that a decomposer is created with an empty task list."""
        assert len(empty_decomposer.tasks) == 0

    def test_add_task(self, empty_decomposer):
        """Test adding a single task."""
        task_id = empty_decomposer.add_task("Test Task", "A task for testing")
        assert len(empty_decomposer.tasks) == 1
        assert empty_decomposer.get_task(task_id) is not None

    def test_add_task_with_dependency(self, empty_decomposer):
        """Test adding a task with a dependency."""
        task1_id = empty_decomposer.add_task("Dep Task", "A dependency")
        task2_id = empty_decomposer.add_task("Main Task", "Depends on another", {task1_id})
        task2 = empty_decomposer.get_task(task2_id)
        assert task2.dependencies == {task1_id}

    def test_get_executable_tasks_initial(self, empty_decomposer):
        """Test that initially only tasks with no dependencies are executable."""
        t1 = empty_decomposer.add_task("Task 1", "")
        t2 = empty_decomposer.add_task("Task 2", "", {t1})
        executable = empty_decomposer.get_executable_tasks()
        assert len(executable) == 1
        assert executable[0].task_id == t1

    def test_get_executable_tasks_after_completion(self, empty_decomposer):
        """Test that new tasks become executable after their dependencies are met."""
        t1 = empty_decomposer.add_task("Task 1", "")
        t2 = empty_decomposer.add_task("Task 2", "", {t1})
        
        empty_decomposer.mark_as_complete(t1)
        
        executable = empty_decomposer.get_executable_tasks()
        assert len(executable) == 1
        assert executable[0].task_id == t2

    def test_is_goal_complete(self, empty_decomposer):
        """Test the goal completion check."""
        t1 = empty_decomposer.add_task("Task 1", "")
        t2 = empty_decomposer.add_task("Task 2", "")

        assert empty_decomposer.is_goal_complete() is False
        empty_decomposer.mark_as_complete(t1)
        assert empty_decomposer.is_goal_complete() is False
        empty_decomposer.mark_as_complete(t2)
        assert empty_decomposer.is_goal_complete() is True

    def test_circular_dependency_handling(self, empty_decomposer):
        """Test that a circular dependency results in no executable tasks."""
        t1 = empty_decomposer.add_task("Task 1", "", {"TASK-0002"}) # Fakes dependency
        t2 = empty_decomposer.add_task("Task 2", "", {t1})
        # This is not a perfect test, as add_task would fail. 
        # A better test would involve modifying the graph directly.
        # But for this implementation, it shows that no progress can be made.
        executable = empty_decomposer.get_executable_tasks()
        assert len(executable) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
