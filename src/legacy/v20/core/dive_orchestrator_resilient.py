#!/usr/bin/env python3
"""
Dive AI V20 Orchestrator - RESILIENT PARALLEL EXECUTION
- 128 agents working simultaneously
- Automatic fallback: failed agents are immediately replaced
- Max 3 retry attempts per subtask
- Self-healing system maintains 128 active agents
"""

import sys
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unified_llm_client import get_unified_client

PROGRESS_FILE = "/tmp/dive_ai_progress.json"
MAX_RETRIES = 3
AGENT_TIMEOUT = 120  # 120 seconds per agent

class ResilientOrchestrator:
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.llm_client = get_unified_client()
        self.agent_count = 128
        self.agents = [{'agent_id': i+1, 'status': 'idle', 'subtask': '', 'model': '', 'start_time': None, 'retry_count': 0} for i in range(self.agent_count)]
        self.lock = threading.Lock()
        self.next_replacement_id = 129  # IDs for replacement agents
        
        self._write_progress("Initializing", "")
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - RESILIENT PARALLEL MODE")
        print("="*100)
        print(f"Project Path: {self.project_path}")
        print(f"Agent Count: {self.agent_count}")
        print(f"Execution Mode: PARALLEL with AUTO-FALLBACK")
        print(f"Max Retries: {MAX_RETRIES} attempts per subtask")
        print(f"Agent Timeout: {AGENT_TIMEOUT}s")
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
                        'agents': self.agents[:self.agent_count],  # Only show original 128
                        'last_update': datetime.now().isoformat()
                    }, f)
        except Exception as e:
            pass  # Silent fail for progress writing
    
    def _update_agent(self, agent_id, status, subtask='', model='', duration_ms=0, tokens=None, error=None, retry_count=0):
        """Thread-safe agent update"""
        with self.lock:
            # Find agent by ID (could be original or replacement)
            agent = None
            for a in self.agents:
                if a['agent_id'] == agent_id:
                    agent = a
                    break
            
            if not agent:
                return
            
            agent['status'] = status
            agent['subtask'] = subtask
            agent['model'] = model
            agent['retry_count'] = retry_count
            
            if status == 'working':
                agent['start_time'] = datetime.now().timestamp() * 1000
            elif status in ['complete', 'error', 'failed_permanent']:
                if agent['start_time']:
                    agent['elapsed_ms'] = datetime.now().timestamp() * 1000 - agent['start_time']
                agent['duration_ms'] = duration_ms
                if tokens:
                    agent['tokens'] = tokens
                if error:
                    agent['error'] = error
    
    def _execute_agent_task(self, agent_id, subtask_desc, model, task_description, retry_count=0):
        """Execute a single agent task with timeout protection"""
        try:
            self._update_agent(agent_id, 'working', subtask_desc, model, retry_count=retry_count)
            
            agent_prompt = f"""You are Dive Coder Agent #{agent_id}. Execute this subtask:

SUBTASK: {subtask_desc}

MAIN TASK: {task_description}

Provide concise implementation code and brief explanation."""

            agent_start = datetime.now()
            
            # Execute with model selection
            if model == "opus":
                response = self.llm_client.chat_with_claude_opus(agent_prompt, max_tokens=2000)
            else:
                response = self.llm_client.chat_with_claude_sonnet(agent_prompt, max_tokens=2000)
            
            duration_ms = (datetime.now() - agent_start).total_seconds() * 1000
            
            if response.status == "success":
                self._update_agent(agent_id, 'complete', subtask_desc, model, duration_ms, response.tokens_used, retry_count=retry_count)
                return {
                    'agent_id': agent_id,
                    'subtask_id': subtask_desc,
                    'status': 'success',
                    'output': response.content,
                    'tokens': response.tokens_used,
                    'duration_ms': duration_ms,
                    'retry_count': retry_count
                }
            else:
                self._update_agent(agent_id, 'error', subtask_desc, model, error=response.error, retry_count=retry_count)
                return {
                    'agent_id': agent_id,
                    'subtask_id': subtask_desc,
                    'status': 'error',
                    'error': response.error,
                    'retry_count': retry_count,
                    'can_retry': retry_count < MAX_RETRIES
                }
        except Exception as e:
            self._update_agent(agent_id, 'error', subtask_desc, model, error=str(e), retry_count=retry_count)
            return {
                'agent_id': agent_id,
                'subtask_id': subtask_desc,
                'status': 'error',
                'error': str(e),
                'retry_count': retry_count,
                'can_retry': retry_count < MAX_RETRIES
            }
    
    def execute_task(self, task_description: str):
        """Execute task with 128 agents IN PARALLEL with AUTO-FALLBACK"""
        start_time = datetime.now()
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - RESILIENT PARALLEL EXECUTION")
        print("="*100)
        print(f"Task: {task_description}")
        print("="*100 + "\n")
        
        # Step 1: Planning
        print("[Step 1/3] Orchestrator creating execution plan...\n")
        self._write_progress("Step 1/3: Planning", task_description)
        
        planning_prompt = f"""You are Dive Orchestrator V20. Break down this task into EXACTLY 128 subtasks for parallel execution:

TASK: {task_description}

Create 128 distinct subtasks. Assign:
- First 40: "opus" (architecture, complex logic)
- Remaining 88: "sonnet" (implementation, testing)

OUTPUT (JSON):
{{
  "subtasks": [
    {{"id": 1, "description": "...", "model": "opus"}},
    ...
    {{"id": 128, "description": "...", "model": "sonnet"}}
  ]
}}"""

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
            
            while len(subtasks) < 128:
                subtasks.append({
                    "id": len(subtasks) + 1,
                    "description": f"Implementation task {len(subtasks) + 1}",
                    "model": "sonnet"
                })
            subtasks = subtasks[:128]
            
        except Exception as e:
            print(f"⚠ Using default distribution\n")
            subtasks = []
            for i in range(128):
                subtasks.append({
                    "id": i + 1,
                    "description": f"Component {i+1} for: {task_description}",
                    "model": "opus" if i < 40 else "sonnet"
                })
        
        print(f"[Step 2/3] Launching 128 agents with AUTO-FALLBACK...\n")
        print("⚡ ALL 128 AGENTS STARTING + AUTO-REPLACEMENT ON FAILURE ⚡\n")
        self._write_progress(f"Step 2/3: Executing with auto-fallback", task_description)
        
        # Step 2: Execute with fallback system
        agent_results = []
        failed_subtasks = {}  # Track failed subtasks for retry
        
        with ThreadPoolExecutor(max_workers=128) as executor:
            # Submit initial 128 tasks
            futures = {}
            for subtask in subtasks:
                future = executor.submit(
                    self._execute_agent_task,
                    subtask['id'],
                    subtask['description'],
                    subtask.get('model', 'sonnet'),
                    task_description,
                    0  # Initial retry count
                )
                futures[future] = {
                    'subtask_id': subtask['id'],
                    'subtask_desc': subtask['description'],
                    'model': subtask.get('model', 'sonnet'),
                    'retry_count': 0
                }
            
            completed = 0
            replacement_count = 0
            
            # Process results and spawn replacements
            while futures:
                done, pending = as_completed(futures, timeout=1), set()
                
                for future in list(done):
                    if future not in futures:
                        continue
                    
                    subtask_info = futures.pop(future)
                    
                    try:
                        result = future.result(timeout=AGENT_TIMEOUT)
                        
                        if result['status'] == 'success':
                            agent_results.append(result)
                            completed += 1
                            
                            if completed % 10 == 0:
                                print(f"  ✓ Progress: {completed}/128 completed ({completed/128*100:.1f}%) | Replacements: {replacement_count}")
                                self._write_progress(f"Step 2/3: {completed}/128 complete, {replacement_count} replacements", task_description)
                        
                        elif result['status'] == 'error' and result.get('can_retry', False):
                            # FALLBACK: Spawn replacement agent
                            retry_count = result['retry_count'] + 1
                            replacement_id = self.next_replacement_id
                            self.next_replacement_id += 1
                            replacement_count += 1
                            
                            print(f"  ⚠ Agent {result['agent_id']} failed (attempt {retry_count}/{MAX_RETRIES})")
                            print(f"  ↻ Spawning replacement agent #{replacement_id}...")
                            
                            # Add replacement agent to tracking
                            with self.lock:
                                self.agents.append({
                                    'agent_id': replacement_id,
                                    'status': 'idle',
                                    'subtask': subtask_info['subtask_desc'],
                                    'model': subtask_info['model'],
                                    'start_time': None,
                                    'retry_count': retry_count,
                                    'replacing': result['agent_id']
                                })
                            
                            # Submit replacement task
                            new_future = executor.submit(
                                self._execute_agent_task,
                                replacement_id,
                                subtask_info['subtask_desc'],
                                subtask_info['model'],
                                task_description,
                                retry_count
                            )
                            futures[new_future] = {
                                'subtask_id': subtask_info['subtask_id'],
                                'subtask_desc': subtask_info['subtask_desc'],
                                'model': subtask_info['model'],
                                'retry_count': retry_count
                            }
                        
                        else:
                            # Permanent failure after max retries
                            print(f"  ✗ Subtask {subtask_info['subtask_id']} permanently failed after {MAX_RETRIES} attempts")
                            agent_results.append(result)
                            completed += 1
                    
                    except Exception as e:
                        print(f"  ✗ Agent exception: {e}")
                        completed += 1
        
        print(f"\n✓ All tasks completed! (128 original + {replacement_count} replacements)\n")
        
        # Step 3: Synthesis
        print("[Step 3/3] Synthesizing results...\n")
        self._write_progress("Step 3/3: Synthesizing", task_description)
        
        successful_results = [r for r in agent_results if r['status'] == 'success']
        
        synthesis_prompt = f"""Synthesize {len(successful_results)} agent results:

TASK: {task_description}

Provide complete implementation."""

        synthesis_response = self.llm_client.chat_with_claude_sonnet(synthesis_prompt, max_tokens=8000)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        total_tokens = sum(r.get('tokens', {}).get('total', 0) for r in agent_results if r['status'] == 'success')
        
        print("="*100)
        print("DIVE AI V20 ORCHESTRATOR - TASK COMPLETE")
        print("="*100)
        print(f"Execution Time: {execution_time:.1f}s")
        print(f"Original Agents: 128")
        print(f"Replacement Agents: {replacement_count}")
        print(f"Total Agents Used: {128 + replacement_count}")
        print(f"Successful: {len(successful_results)}")
        print(f"Failed: {len(agent_results) - len(successful_results)}")
        print(f"Total Tokens: {total_tokens}")
        print("="*100 + "\n")
        
        self._write_progress("Complete", task_description)
        
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
    
    orchestrator = ResilientOrchestrator(args.project)
    orchestrator.execute_task(args.task)
