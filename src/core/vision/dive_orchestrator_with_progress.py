#!/usr/bin/env python3
"""
Dive AI V20 Orchestrator with Progress Tracking
"""

import sys
import json
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_llm_client import get_unified_client

PROGRESS_FILE = "/tmp/dive_ai_progress.json"

class DiveOrchestratorWithProgress:
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.llm_client = get_unified_client()
        self.agent_count = 128
        self.agents = [{'agent_id': i+1, 'status': 'idle', 'subtask': '', 'model': '', 'start_time': None} for i in range(self.agent_count)]
        
        self._write_progress("Initializing", "")
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - INITIALIZING")
        print("="*100)
        print(f"Project Path: {self.project_path}")
        print(f"Agent Count: {self.agent_count}")
        print(f"Progress File: {PROGRESS_FILE}")
        print("="*100 + "\n")
    
    def _write_progress(self, phase, task):
        """Write progress to JSON file"""
        try:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump({
                    'task': task,
                    'phase': phase,
                    'total_agents': self.agent_count,
                    'agents': self.agents,
                    'last_update': datetime.now().isoformat()
                }, f)
        except Exception as e:
            print(f"Warning: Could not write progress: {e}")
    
    def _update_agent(self, agent_id, status, subtask='', model='', duration_ms=0, tokens=None, error=None):
        """Update agent status"""
        if 1 <= agent_id <= self.agent_count:
            agent = self.agents[agent_id - 1]
            agent['status'] = status
            agent['subtask'] = subtask
            agent['model'] = model
            
            if status == 'working':
                agent['start_time'] = datetime.now().timestamp() * 1000
            elif status in ['complete', 'error']:
                if agent['start_time']:
                    agent['elapsed_ms'] = datetime.now().timestamp() * 1000 - agent['start_time']
                agent['duration_ms'] = duration_ms
                if tokens:
                    agent['tokens'] = tokens
                if error:
                    agent['error'] = error
    
    def execute_task(self, task_description: str):
        """Execute task with 128 agents"""
        start_time = datetime.now()
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - EXECUTING TASK")
        print("="*100)
        print(f"Task: {task_description}")
        print("="*100 + "\n")
        
        # Step 1: Planning
        print("[Step 1/4] Orchestrator analyzing task...\\n")
        self._write_progress("Step 1/4: Planning", task_description)
        
        planning_prompt = f"""You are Dive Orchestrator V20. Break down this task into exactly 10 subtasks for agents:

TASK: {task_description}

OUTPUT (JSON):
{{
  "subtasks": [
    {{"id": 1, "description": "...", "model": "opus" or "sonnet"}}
  ]
}}"""

        planning_start = datetime.now()
        planning_response = self.llm_client.chat_with_claude_sonnet(planning_prompt, max_tokens=2000)
        planning_duration = (datetime.now() - planning_start).total_seconds() * 1000
        
        if planning_response.status != "success":
            print(f"✗ Planning failed: {planning_response.error}")
            return
        
        print(f"✓ Planning complete ({planning_duration:.0f}ms, {planning_response.tokens_used['total']} tokens)\\n")
        
        # Parse plan
        try:
            plan_text = planning_response.content
            json_start = plan_text.find('{')
            json_end = plan_text.rfind('}') + 1
            plan = json.loads(plan_text[json_start:json_end])
            subtasks = plan.get('subtasks', [])[:10]
        except:
            subtasks = [{
                "id": i+1,
                "description": f"Subtask {i+1} for: {task_description}",
                "model": "opus" if i < 3 else "sonnet"
            } for i in range(10)]
        
        print(f"[Step 2/4] Parsed {len(subtasks)} subtasks\\n")
        self._write_progress(f"Step 2/4: Executing {len(subtasks)} subtasks", task_description)
        
        # Step 3: Execute subtasks
        print(f"[Step 3/4] Executing subtasks with agents...\\n")
        
        agent_results = []
        
        for subtask in subtasks:
            agent_id = subtask['id']
            subtask_desc = subtask['description']
            model = subtask.get('model', 'sonnet')
            
            self._update_agent(agent_id, 'working', subtask_desc, model)
            self._write_progress(f"Step 3/4: Agent {agent_id}/{len(subtasks)}", task_description)
            
            print(f"  [Agent {agent_id}] {model.upper()} working on: {subtask_desc[:50]}...")
            
            agent_prompt = f"""Execute this subtask: {subtask_desc}

MAIN TASK: {task_description}

Provide implementation code and explanation."""

            agent_start = datetime.now()
            
            if model == "opus":
                response = self.llm_client.chat_with_claude_opus(agent_prompt, max_tokens=3000)
            else:
                response = self.llm_client.chat_with_claude_sonnet(agent_prompt, max_tokens=3000)
            
            duration_ms = (datetime.now() - agent_start).total_seconds() * 1000
            
            if response.status == "success":
                print(f"    ✓ Complete ({duration_ms:.0f}ms, {response.tokens_used['total']} tokens)")
                self._update_agent(agent_id, 'complete', subtask_desc, model, duration_ms, response.tokens_used)
                agent_results.append({
                    'agent_id': agent_id,
                    'output': response.content,
                    'tokens': response.tokens_used
                })
            else:
                print(f"    ✗ Failed: {response.error}")
                self._update_agent(agent_id, 'error', subtask_desc, model, error=response.error)
            
            self._write_progress(f"Step 3/4: Agent {agent_id}/{len(subtasks)} complete", task_description)
        
        print()
        
        # Step 4: Synthesis
        print("[Step 4/4] Synthesizing results...\\n")
        self._write_progress("Step 4/4: Synthesizing results", task_description)
        
        synthesis_prompt = f"""Synthesize these agent results into final output:

TASK: {task_description}

RESULTS: {json.dumps(agent_results, indent=2)}

Provide complete implementation."""

        synthesis_response = self.llm_client.chat_with_claude_sonnet(synthesis_prompt, max_tokens=8000)
        
        if synthesis_response.status == "success":
            print(f"✓ Synthesis complete\\n")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print("="*100)
        print("DIVE AI V20 ORCHESTRATOR - TASK COMPLETE")
        print("="*100)
        print(f"Execution Time: {execution_time:.1f}s")
        print(f"Agents Used: {len(subtasks)}")
        print("="*100 + "\\n")
        
        self._write_progress("Complete", task_description)
        
        # Print final output
        if synthesis_response.status == "success":
            print("\\n" + "="*100)
            print("FINAL OUTPUT")
            print("="*100 + "\\n")
            print(synthesis_response.content)
            print("\\n" + "="*100 + "\\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--project", default=None)
    args = parser.parse_args()
    
    orchestrator = DiveOrchestratorWithProgress(args.project)
    orchestrator.execute_task(args.task)
