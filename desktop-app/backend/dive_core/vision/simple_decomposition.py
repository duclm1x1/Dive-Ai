#!/usr/bin/env python3
"""
Example usage of the Predictive Task Decomposition (PTD) skill.
"""

import sys
import os

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ptd_engine import TaskDecomposer

def main():
    """Demonstrates decomposing a goal and executing tasks in parallel."""
    print("--- PTD Skill Example: Decomposing a Web App Project ---")

    # 1. Instantiate the decomposer and build the task graph
    ptd = TaskDecomposer()
    
    print("\nDecomposing high-level goal into a task graph...")
    t_schema = ptd.add_task("Design DB Schema", "Define user and post tables")
    t_ui = ptd.add_task("Design UI Mockups", "Create wireframes for the app")
    t_api = ptd.add_task("Develop Backend API", "Build CRUD endpoints", {t_schema})
    t_frontend = ptd.add_task("Develop Frontend", "Build React components", {t_ui})
    t_integrate = ptd.add_task("Integrate FE/BE", "Connect frontend to API", {t_api, t_frontend})

    # 2. Simulate a parallel execution loop
    while not ptd.is_goal_complete():
        executable_tasks = ptd.get_executable_tasks()
        
        if not executable_tasks:
            print("\nError: No executable tasks found, but goal is not complete. Check for circular dependencies.")
            break

        print(f"\n--- Executing Batch of {len(executable_tasks)} Parallel Tasks ---")
        for task in executable_tasks:
            print(f"  - Starting: {task.name} ({task.task_id})")
            # In a real system, this would be dispatched to an agent
            ptd.mark_as_complete(task.task_id)
            print(f"  - Completed: {task.name}")
    
    print("\n✅ Success: The entire project goal is complete.")
    print("\n--- PTD Skill Example Complete ---")

if __name__ == "__main__":
    main()
