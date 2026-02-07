#!/usr/bin/env python3
"""
Predictive Task Decomposition (PTD) - Skill Implementation

This skill provides a framework for decomposing a high-level goal into a 
directed acyclic graph (DAG) of smaller, executable tasks, identifying opportunities
for parallel execution.
"""

import logging
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a single, executable task in the decomposition graph."""
    task_id: str
    name: str
    description: str
    dependencies: Set[str] = field(default_factory=set)
    is_complete: bool = False

class TaskDecomposer:
    """Decomposes a high-level goal into a task graph."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
        logger.info("Task Decomposer initialized.")

    def add_task(self, name: str, description: str, dependencies: Set[str] = None) -> str:
        """Adds a new task to the graph."""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:04d}"
        
        if dependencies:
            for dep_id in dependencies:
                if dep_id not in self.tasks:
                    raise ValueError(f"Dependency '{dep_id}' not found in the task graph.")

        task = Task(
            task_id=task_id,
            name=name,
            description=description,
            dependencies=dependencies or set()
        )
        self.tasks[task_id] = task
        logger.info(f"Added task '{task_id}' ({name}) to the graph.")
        return task_id

    def get_task(self, task_id: str) -> Task:
        """Retrieves a task by its ID."""
        return self.tasks.get(task_id)

    def get_executable_tasks(self) -> List[Task]:
        """Returns a list of all tasks whose dependencies are met."""
        executable = []
        for task in self.tasks.values():
            if task.is_complete:
                continue
            
            # Check if all dependencies are complete
            if all(self.tasks[dep_id].is_complete for dep_id in task.dependencies):
                executable.append(task)
        
        return executable

    def mark_as_complete(self, task_id: str):
        """Marks a task as complete."""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task '{task_id}' not found.")
        task.is_complete = True
        logger.info(f"Task '{task_id}' marked as complete.")

    def is_goal_complete(self) -> bool:
        """Checks if all tasks in the graph are complete."""
        return all(task.is_complete for task in self.tasks.values())
