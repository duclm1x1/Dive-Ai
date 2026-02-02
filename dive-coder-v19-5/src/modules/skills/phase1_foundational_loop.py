#!/usr/bin/env python3
"""
Phase 1: The Foundational Loop (PTD + DAC + CPCG)

This module integrates Predictive Task Decomposition (PTD), Dynamic Agent Composition (DAC),
and Cross-Paradigm Code Generation (CPCG) to create a powerful code generation pipeline.

Flow:
1. User provides a high-level prompt
2. PTD decomposes it into a task graph
3. DAC assembles the best team of agents for each task
4. CPCG generates code across multiple languages
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add skills to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ptd', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dac', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cpcg', 'src'))

from ptd_engine import TaskDecomposer
from dac_engine import AgentComposer
from cpcg_engine import CodeTranslator

class Phase1FoundationalLoop:
    """Orchestrates the Phase 1 integration: PTD -> DAC -> CPCG"""

    def __init__(self):
        self.task_decomposer = TaskDecomposer()
        self.agent_composer = AgentComposer()
        self.code_translator = CodeTranslator()
        logger.info("Phase 1 Foundational Loop initialized.")

    def process_user_prompt(self, prompt: str) -> dict:
        """
        Main entry point: takes a user prompt and generates code.
        
        Returns a dictionary with:
        - tasks: The decomposed task graph
        - agents: The assembled agent teams
        - code_snippets: The generated code
        """
        logger.info(f"\n=== PHASE 1: FOUNDATIONAL LOOP ===")
        logger.info(f"User Prompt: {prompt}\n")

        # Step 1: Decompose the prompt into tasks using PTD
        logger.info("--- Step 1: Task Decomposition (PTD) ---")
        tasks = self._decompose_prompt(prompt)

        # Step 2: For each task, compose an agent team using DAC
        logger.info("\n--- Step 2: Agent Composition (DAC) ---")
        agent_teams = self._compose_agents_for_tasks(tasks)

        # Step 3: Generate code using CPCG
        logger.info("\n--- Step 3: Code Generation (CPCG) ---")
        code_snippets = self._generate_code_for_tasks(tasks)

        return {
            "prompt": prompt,
            "tasks": tasks,
            "agent_teams": agent_teams,
            "code_snippets": code_snippets
        }

    def _decompose_prompt(self, prompt: str) -> list:
        """Uses PTD to decompose the prompt into a task graph."""
        # Simulate task decomposition
        if "login" in prompt.lower():
            task_ids = []
            t1 = self.task_decomposer.add_task("Create Backend API", "Implement authentication endpoint")
            task_ids.append(t1)
            t2 = self.task_decomposer.add_task("Create Frontend Form", "Build login UI component", {t1})
            task_ids.append(t2)
            return task_ids
        else:
            t1 = self.task_decomposer.add_task("Main Task", f"Implement: {prompt}")
            return [t1]

    def _compose_agents_for_tasks(self, task_ids: list) -> dict:
        """Uses DAC to assemble the best agent team for each task."""
        agent_teams = {}
        for task_id in task_ids:
            task = self.task_decomposer.get_task(task_id)
            if task:
                # Compose agents based on task description
                if "backend" in task.description.lower() or "api" in task.description.lower():
                    agents = self.agent_composer.compose_team(["Python Specialist", "Database Expert"])
                elif "frontend" in task.description.lower() or "ui" in task.description.lower():
                    agents = self.agent_composer.compose_team(["JavaScript Specialist", "UI/UX Expert"])
                else:
                    agents = self.agent_composer.compose_team(["Generalist"])
                
                agent_teams[task_id] = agents
                logger.info(f"Task {task_id}: Assembled team of {len(agents)} agents")
        
        return agent_teams

    def _generate_code_for_tasks(self, task_ids: list) -> dict:
        """Uses CPCG to generate code for each task."""
        code_snippets = {}
        for task_id in task_ids:
            task = self.task_decomposer.get_task(task_id)
            if task:
                snippets = self.code_translator.translate_requirement(task.description)
                code_snippets[task_id] = snippets
                logger.info(f"Task {task_id}: Generated {len(snippets)} code snippets")
        
        return code_snippets

    def generate_report(self, result: dict) -> str:
        """Generates a human-readable report of the entire process."""
        report = f"\n{'='*60}\n"
        report += f"PHASE 1 FOUNDATIONAL LOOP REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"User Prompt: {result['prompt']}\n\n"
        
        report += f"--- Tasks Decomposed ---\n"
        for task_id in result['tasks']:
            task = self.task_decomposer.get_task(task_id)
            if task:
                report += f"  {task_id}: {task.name}\n"
                report += f"    Description: {task.description}\n"
        
        report += f"\n--- Agent Teams Composed ---\n"
        for task_id, agents in result['agent_teams'].items():
            report += f"  {task_id}: {', '.join(agents)}\n"
        
        report += f"\n--- Code Generated ---\n"
        for task_id, snippets in result['code_snippets'].items():
            report += f"  {task_id}: {len(snippets)} languages\n"
            for snippet in snippets:
                report += f"    - {snippet.language}\n"
        
        report += f"\n{'='*60}\n"
        return report


def main():
    """Demonstrates the Phase 1 Foundational Loop."""
    loop = Phase1FoundationalLoop()
    
    # Example: User wants to build a login page
    user_prompt = "Build a complete user login feature with backend API and frontend form"
    result = loop.process_user_prompt(user_prompt)
    
    # Generate and print the report
    report = loop.generate_report(result)
    print(report)


if __name__ == "__main__":
    main()
