#!/usr/bin/env python3
"""
Dive AI V20 Orchestrator - WITH CAPABILITY MONITORING
Tracks whether agents are using their full capabilities
"""

import sys
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unified_llm_client import get_unified_client
from capability_monitor import CapabilityMonitor

class MonitoredOrchestrator:
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.llm_client = get_unified_client()
        self.capability_monitor = CapabilityMonitor()
        self.agent_count = 128
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - WITH CAPABILITY MONITORING")
        print("="*100)
        print(f"Project Path: {self.project_path}")
        print(f"Agent Count: {self.agent_count}")
        print(f"Monitoring: Skills, Tools, RAG, MCP, Dive Memory")
        print("="*100 + "\n")
    
    def _analyze_agent_output(self, agent_id: int, prompt: str, output: str):
        """Analyze agent output to detect capability usage"""
        
        # Detect skills mentioned
        skills = ['web_developer', 'backend_engineer', 'frontend_engineer', 'security_expert',
                 'test_engineer', 'database_architect', 'api_designer', 'devops_engineer']
        for skill in skills:
            if skill.replace('_', ' ') in output.lower() or skill in output.lower():
                self.capability_monitor.track_skill(agent_id, skill)
        
        # Detect tool usage patterns
        if 'search' in output.lower() or 'find' in output.lower() or 'query' in output.lower():
            self.capability_monitor.track_tool(agent_id, 'RAG_search')
        
        if 'file' in output.lower() or 'read' in output.lower() or 'write' in output.lower():
            self.capability_monitor.track_tool(agent_id, 'MCP_filesystem')
        
        if 'database' in output.lower() or 'sql' in output.lower() or 'query' in output.lower():
            self.capability_monitor.track_tool(agent_id, 'MCP_database')
        
        if 'memory' in output.lower() or 'remember' in output.lower() or 'recall' in output.lower():
            self.capability_monitor.track_tool(agent_id, 'dive_memory_read')
        
        if 'test' in output.lower() or 'unit test' in output.lower():
            self.capability_monitor.track_skill(agent_id, 'test_engineer')
        
        # Detect features
        if 'stream' in output.lower():
            self.capability_monitor.track_feature(agent_id, 'streaming')
        
        if 'function' in output.lower() or 'tool call' in output.lower():
            self.capability_monitor.track_feature(agent_id, 'function_calling')
    
    def _execute_agent_with_monitoring(self, agent_id: int, subtask_desc: str, model: str, task_description: str):
        """Execute agent task with capability monitoring"""
        
        self.capability_monitor.start_agent(agent_id)
        
        try:
            # Enhanced prompt that encourages capability usage
            agent_prompt = f"""You are Dive Coder Agent #{agent_id} with FULL CAPABILITIES:

🎯 YOUR SUBTASK: {subtask_desc}

📋 MAIN TASK: {task_description}

🛠️ YOUR AVAILABLE CAPABILITIES:
- Dive Memory: Access project memory and past decisions
- RAG Search: Semantic search across codebase
- MCP Tools: File system, terminal, database access
- 61+ Skills: web_developer, security_expert, test_engineer, etc.
- Code Execution: Run and test code
- Multi-Provider: Automatic failover and optimization

💡 INSTRUCTIONS:
1. Check Dive Memory for relevant context
2. Use RAG to find similar implementations
3. Activate appropriate skills for your subtask
4. Use MCP tools if you need to access files/database
5. Include tests and documentation
6. Mention which capabilities you're using

Provide implementation with explanation of capabilities used."""

            agent_start = datetime.now()
            
            # Execute with model selection
            if model == "opus":
                response = self.llm_client.chat_with_claude_opus(agent_prompt, max_tokens=3000)
            else:
                response = self.llm_client.chat_with_claude_sonnet(agent_prompt, max_tokens=2000)
            
            duration_ms = (datetime.now() - agent_start).total_seconds() * 1000
            
            if response.status == "success":
                # Analyze output for capability usage
                self._analyze_agent_output(agent_id, agent_prompt, response.content)
                
                self.capability_monitor.end_agent(agent_id)
                
                return {
                    'agent_id': agent_id,
                    'status': 'success',
                    'output': response.content,
                    'tokens': response.tokens_used,
                    'duration_ms': duration_ms
                }
            else:
                self.capability_monitor.end_agent(agent_id)
                return {
                    'agent_id': agent_id,
                    'status': 'error',
                    'error': response.error
                }
        
        except Exception as e:
            self.capability_monitor.end_agent(agent_id)
            return {
                'agent_id': agent_id,
                'status': 'error',
                'error': str(e)
            }
    
    def execute_task(self, task_description: str):
        """Execute task with 128 agents and monitor capabilities"""
        
        start_time = datetime.now()
        
        print("[Step 1/3] Planning with Orchestrator...\n")
        
        planning_prompt = f"""Break down this task into EXACTLY 128 subtasks:

TASK: {task_description}

Assign:
- First 40: "opus" (architecture, design, complex logic)
- Remaining 88: "sonnet" (implementation, testing, documentation)

OUTPUT (JSON):
{{
  "subtasks": [
    {{"id": 1, "description": "...", "model": "opus"}},
    ...
  ]
}}"""

        planning_response = self.llm_client.chat_with_claude_sonnet(planning_prompt, max_tokens=8000)
        
        if planning_response.status != "success":
            print(f"✗ Planning failed: {planning_response.error}")
            return
        
        print(f"✓ Planning complete\n")
        
        # Parse plan
        try:
            plan_text = planning_response.content
            json_start = plan_text.find('{')
            json_end = plan_text.rfind('}') + 1
            plan = json.loads(plan_text[json_start:json_end])
            subtasks = plan.get('subtasks', [])[:128]
        except:
            subtasks = [
                {"id": i+1, "description": f"Component {i+1} for: {task_description}", 
                 "model": "opus" if i < 40 else "sonnet"}
                for i in range(128)
            ]
        
        print(f"[Step 2/3] Executing 128 agents with capability monitoring...\n")
        
        results = []
        with ThreadPoolExecutor(max_workers=128) as executor:
            futures = [
                executor.submit(
                    self._execute_agent_with_monitoring,
                    subtask['id'],
                    subtask['description'],
                    subtask.get('model', 'sonnet'),
                    task_description
                )
                for subtask in subtasks
            ]
            
            completed = 0
            for future in futures:
                try:
                    result = future.result(timeout=120)
                    results.append(result)
                    completed += 1
                    
                    if completed % 10 == 0:
                        print(f"  Progress: {completed}/128 completed ({completed/128*100:.1f}%)")
                except Exception as e:
                    print(f"  Agent error: {e}")
                    completed += 1
        
        print(f"\n✓ All agents completed!\n")
        
        # Get capability statistics
        stats = self.capability_monitor.get_utilization_stats()
        
        print("="*100)
        print("DIVE AI V20 - EXECUTION COMPLETE")
        print("="*100)
        print(f"Execution Time: {(datetime.now() - start_time).total_seconds():.1f}s")
        print(f"Agents: {stats.get('total_agents', 0)}")
        print(f"\n📊 CAPABILITY UTILIZATION:")
        util = stats.get('utilization_percentage', {})
        print(f"  Dive Memory:  {util.get('memory', 0):.1f}% ({stats.get('agents_using_memory', 0)} agents)")
        print(f"  RAG Search:   {util.get('rag', 0):.1f}% ({stats.get('agents_using_rag', 0)} agents)")
        print(f"  MCP Tools:    {util.get('mcp', 0):.1f}% ({stats.get('agents_using_mcp', 0)} agents)")
        print(f"  Skills:       {util.get('skills', 0):.1f}%")
        print("="*100 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--project", default=None)
    args = parser.parse_args()
    
    orchestrator = MonitoredOrchestrator(args.project)
    orchestrator.execute_task(args.task)
