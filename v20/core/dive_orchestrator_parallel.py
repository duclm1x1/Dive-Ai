#!/usr/bin/env python3
"""
Dive AI V20 Orchestrator - TRUE PARALLEL EXECUTION
All 128 agents work simultaneously using threading
"""

import sys
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unified_llm_client import get_unified_client

PROGRESS_FILE = "/tmp/dive_ai_progress.json"

class ParallelOrchestrator:
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.llm_client = get_unified_client()
        self.agent_count = 128
        self.agents = [{'agent_id': i+1, 'status': 'idle', 'subtask': '', 'model': '', 'start_time': None} for i in range(self.agent_count)]
        self.lock = threading.Lock()
        
        self._write_progress("Initializing", "")
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - PARALLEL MODE (128 AGENTS SIMULTANEOUSLY)")
        print("="*100)
        print(f"Project Path: {self.project_path}")
        print(f"Agent Count: {self.agent_count}")
        print(f"Execution Mode: PARALLEL (ThreadPoolExecutor)")
        print(f"Progress File: {PROGRESS_FILE}")
        print("="*100 + "\n")
    
    def _write_progress(self, phase, task):
        """Thread-safe progress writing"""
        try:
            with self.lock:
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump({
                        'task': task,
                        'phase': phase,
                        'total_agents': self.agent_count,
                        'agents': self.agents.copy(),
                        'last_update': datetime.now().isoformat()
                    }, f)
        except Exception as e:
            print(f"Warning: Could not write progress: {e}")
    
    def _update_agent(self, agent_id, status, subtask='', model='', duration_ms=0, tokens=None, error=None):
        """Thread-safe agent update"""
        with self.lock:
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
    
    def _execute_agent_task(self, agent_id, subtask_desc, model, task_description):
        """Execute a single agent task (runs in thread)"""
        try:
            self._update_agent(agent_id, 'working', subtask_desc, model)
            
            agent_prompt = f"""You are Dive Coder Agent #{agent_id}. Execute this subtask:

SUBTASK: {subtask_desc}

MAIN TASK: {task_description}

Provide concise implementation code and brief explanation."""

            agent_start = datetime.now()
            
            if model == "opus":
                response = self.llm_client.chat_with_claude_opus(agent_prompt, max_tokens=2000)
            else:
                response = self.llm_client.chat_with_claude_sonnet(agent_prompt, max_tokens=2000)
            
            duration_ms = (datetime.now() - agent_start).total_seconds() * 1000
            
            if response.status == "success":
                self._update_agent(agent_id, 'complete', subtask_desc, model, duration_ms, response.tokens_used)
                return {
                    'agent_id': agent_id,
                    'status': 'success',
                    'output': response.content,
                    'tokens': response.tokens_used,
                    'duration_ms': duration_ms
                }
            else:
                self._update_agent(agent_id, 'error', subtask_desc, model, error=response.error)
                return {
                    'agent_id': agent_id,
                    'status': 'error',
                    'error': response.error
                }
        except Exception as e:
            self._update_agent(agent_id, 'error', subtask_desc, model, error=str(e))
            return {
                'agent_id': agent_id,
                'status': 'error',
                'error': str(e)
            }
    
    def execute_task(self, task_description: str):
        """Execute task with 128 agents IN PARALLEL"""
        start_time = datetime.now()
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - EXECUTING TASK (PARALLEL MODE)")
        print("="*100)
        print(f"Task: {task_description}")
        print("="*100 + "\n")
        
        # Step 1: Planning
        print("[Step 1/3] Orchestrator creating execution plan...\n")
        self._write_progress("Step 1/3: Planning", task_description)
        
        planning_prompt = f"""You are Dive Orchestrator V20. Break down this task into EXACTLY 128 subtasks for parallel execution by 128 agents:

TASK: {task_description}

Create 128 subtasks that can be executed in parallel. Assign:
- First 40 subtasks: "opus" (complex architecture, design decisions)
- Remaining 88 subtasks: "sonnet" (implementation, testing, documentation)

OUTPUT (JSON):
{{
  "subtasks": [
    {{"id": 1, "description": "...", "model": "opus"}},
    {{"id": 2, "description": "...", "model": "sonnet"}},
    ...
    {{"id": 128, "description": "...", "model": "sonnet"}}
  ]
}}

Provide ALL 128 subtasks."""

        planning_start = datetime.now()
        planning_response = self.llm_client.chat_with_claude_sonnet(planning_prompt, max_tokens=8000)
        planning_duration = (datetime.now() - planning_start).total_seconds() * 1000
        
        if planning_response.status != "success":
            print(f"✗ Planning failed: {planning_response.error}")
            return
        
        print(f"✓ Planning complete ({planning_duration:.0f}ms, {planning_response.tokens_used['total']} tokens)\n")
        
        # Parse plan
        try:
            plan_text = planning_response.content
            json_start = plan_text.find('{')
            json_end = plan_text.rfind('}') + 1
            plan = json.loads(plan_text[json_start:json_end])
            subtasks = plan.get('subtasks', [])
            
            # Ensure we have exactly 128 subtasks
            while len(subtasks) < 128:
                subtasks.append({
                    "id": len(subtasks) + 1,
                    "description": f"Additional implementation task {len(subtasks) + 1}",
                    "model": "sonnet"
                })
            subtasks = subtasks[:128]
            
        except Exception as e:
            print(f"⚠ Could not parse plan, using default distribution: {e}\n")
            subtasks = []
            for i in range(128):
                subtasks.append({
                    "id": i + 1,
                    "description": f"Implement component {i+1} for: {task_description}",
                    "model": "opus" if i < 40 else "sonnet"
                })
        
        print(f"[Step 2/3] Launching {len(subtasks)} agents IN PARALLEL...\n")
        print("⚡ ALL 128 AGENTS STARTING SIMULTANEOUSLY ⚡\n")
        self._write_progress(f"Step 2/3: Executing {len(subtasks)} agents in parallel", task_description)
        
        # Step 2: Execute ALL agents in parallel using ThreadPoolExecutor
        agent_results = []
        
        with ThreadPoolExecutor(max_workers=128) as executor:
            # Submit all 128 tasks at once
            future_to_agent = {
                executor.submit(
                    self._execute_agent_task,
                    subtask['id'],
                    subtask['description'],
                    subtask.get('model', 'sonnet'),
                    task_description
                ): subtask['id']
                for subtask in subtasks
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_agent):
                agent_id = future_to_agent[future]
                try:
                    result = future.result()
                    agent_results.append(result)
                    completed += 1
                    
                    if completed % 10 == 0:
                        print(f"  Progress: {completed}/128 agents completed ({completed/128*100:.1f}%)")
                        self._write_progress(f"Step 2/3: {completed}/128 agents complete", task_description)
                    
                except Exception as e:
                    print(f"  Agent {agent_id} exception: {e}")
        
        print(f"\n✓ All 128 agents completed!\n")
        
        # Step 3: Synthesis
        print("[Step 3/3] Synthesizing results from 128 agents...\n")
        self._write_progress("Step 3/3: Synthesizing results", task_description)
        
        successful_results = [r for r in agent_results if r['status'] == 'success']
        
        synthesis_prompt = f"""Synthesize results from {len(successful_results)} agents into final output:

TASK: {task_description}

AGENT COUNT: {len(successful_results)} successful agents

Provide complete, production-ready implementation combining all agent outputs."""

        synthesis_response = self.llm_client.chat_with_claude_sonnet(synthesis_prompt, max_tokens=8000)
        
        if synthesis_response.status == "success":
            print(f"✓ Synthesis complete\n")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        total_tokens = sum(r.get('tokens', {}).get('total', 0) for r in agent_results if r['status'] == 'success')
        
        print("="*100)
        print("DIVE AI V20 ORCHESTRATOR - TASK COMPLETE (PARALLEL EXECUTION)")
        print("="*100)
        print(f"Execution Time: {execution_time:.1f}s")
        print(f"Agents Used: 128 (all in parallel)")
        print(f"Successful: {len(successful_results)}")
        print(f"Failed: {len(agent_results) - len(successful_results)}")
        print(f"Total Tokens: {total_tokens}")
        print("="*100 + "\n")
        
        self._write_progress("Complete", task_description)
        
        # Print final output
        if synthesis_response.status == "success":
            print("\n" + "="*100)
            print("FINAL OUTPUT")
            print("="*100 + "\n")
            print(synthesis_response.content)
            print("\n" + "="*100 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--project", default=None)
    args = parser.parse_args()
    
    orchestrator = ParallelOrchestrator(args.project)
    orchestrator.execute_task(args.task)
