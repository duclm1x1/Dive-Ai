#!/usr/bin/env python3
"""
Dive AI V20 Orchestrator
Uses Unified LLM Client (Claude Opus 4.5 + Sonnet 4.5) as highest priority system
"""

import sys
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_llm_client import get_unified_client, APIResponse

@dataclass
class AgentTask:
    """Task for a single agent"""
    agent_id: int
    task_description: str
    model: str  # "sonnet" or "opus"
    dependencies: List[int] = None
    
@dataclass
class OrchestratorResult:
    """Result from orchestrator execution"""
    success: bool
    task_description: str
    agent_results: List[Dict[str, Any]]
    total_agents: int
    execution_time_ms: float
    total_tokens: int
    orchestrator_model: str
    timestamp: str
    error: Optional[str] = None

class DiveOrchestratorV20:
    """
    Dive AI V20 Orchestrator
    
    Coordinates 128 Dive Coder agents (Claude Opus 4.5 + Sonnet 4.5)
    to execute complex software development tasks.
    
    Priority: HIGHEST - Always runs, every time
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.llm_client = get_unified_client()
        self.agent_count = 128
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - INITIALIZING")
        print("="*100)
        print(f"Project Path: {self.project_path}")
        print(f"Agent Count: {self.agent_count}")
        print(f"Orchestrator Model: Claude Sonnet 4.5")
        print(f"Agent Models: Claude Opus 4.5 + Sonnet 4.5")
        print("="*100 + "\n")
    
    def test_connection(self) -> bool:
        """Test connection to unified LLM client"""
        print("[Dive Orchestrator] Testing connection to Unified LLM Client...\n")
        
        # Test Sonnet (Orchestrator)
        sonnet_response = self.llm_client.chat_with_claude_sonnet(
            "Test connection. Respond with 'CONNECTED'.",
            max_tokens=100
        )
        
        # Test Opus (Agents)
        opus_response = self.llm_client.chat_with_claude_opus(
            "Test connection. Respond with 'CONNECTED'.",
            max_tokens=100
        )
        
        sonnet_ok = sonnet_response.status == "success"
        opus_ok = opus_response.status == "success"
        
        print(f"✓ Claude Sonnet 4.5 (Orchestrator): {'CONNECTED' if sonnet_ok else 'FAILED'}")
        print(f"  Provider: {sonnet_response.provider}")
        print(f"  Latency: {sonnet_response.latency_ms:.2f}ms\n")
        
        print(f"✓ Claude Opus 4.5 (Agents): {'CONNECTED' if opus_ok else 'FAILED'}")
        print(f"  Provider: {opus_response.provider}")
        print(f"  Latency: {opus_response.latency_ms:.2f}ms\n")
        
        return sonnet_ok and opus_ok
    
    def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> OrchestratorResult:
        """
        Execute a task using 128 Dive Coder agents
        
        Workflow:
        1. Orchestrator (Sonnet) analyzes task and creates execution plan
        2. Orchestrator distributes subtasks to 128 agents
        3. Agents (Opus for complex, Sonnet for simple) execute in parallel
        4. Orchestrator synthesizes results
        """
        start_time = datetime.now()
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - EXECUTING TASK")
        print("="*100)
        print(f"Task: {task_description}")
        print(f"Context: {json.dumps(context, indent=2) if context else 'None'}")
        print("="*100 + "\n")
        
        # Step 1: Orchestrator analyzes and plans
        print("[Step 1/4] Orchestrator analyzing task...\n")
        
        planning_prompt = f"""You are Dive Orchestrator V20. You coordinate 128 Dive Coder agents to execute complex software development tasks.

TASK: {task_description}

CONTEXT: {json.dumps(context) if context else 'None'}

YOUR JOB:
1. Analyze the task complexity and requirements
2. Break down into subtasks suitable for 128 agents
3. Decide which subtasks need Claude Opus 4.5 (complex/architecture) vs Claude Sonnet 4.5 (implementation/testing)
4. Create an execution plan with:
   - List of subtasks
   - Agent model assignment (opus/sonnet)
   - Dependencies between subtasks
   - Expected deliverables

OUTPUT FORMAT (JSON):
{{
  "analysis": "Brief analysis of the task",
  "subtasks": [
    {{
      "id": 1,
      "description": "Subtask description",
      "model": "opus" or "sonnet",
      "dependencies": [list of subtask IDs this depends on],
      "estimated_tokens": number
    }}
  ],
  "execution_strategy": "parallel" or "sequential" or "hybrid",
  "expected_deliverables": ["list of expected outputs"]
}}

Provide your execution plan now."""

        planning_response = self.llm_client.chat_with_claude_sonnet(
            planning_prompt,
            max_tokens=4000
        )
        
        if planning_response.status != "success":
            return OrchestratorResult(
                success=False,
                task_description=task_description,
                agent_results=[],
                total_agents=0,
                execution_time_ms=0,
                total_tokens=0,
                orchestrator_model="claude-sonnet-4-5",
                timestamp=datetime.now().isoformat(),
                error=f"Planning failed: {planning_response.error}"
            )
        
        print(f"✓ Planning complete ({planning_response.latency_ms:.2f}ms)")
        print(f"  Tokens used: {planning_response.tokens_used['total']}")
        print(f"  Provider: {planning_response.provider}\n")
        
        # Step 2: Parse execution plan
        print("[Step 2/4] Parsing execution plan...\n")
        
        try:
            # Extract JSON from response
            plan_text = planning_response.content
            json_start = plan_text.find('{')
            json_end = plan_text.rfind('}') + 1
            plan_json = json.loads(plan_text[json_start:json_end])
            
            print(f"✓ Execution plan parsed")
            print(f"  Subtasks: {len(plan_json.get('subtasks', []))}")
            print(f"  Strategy: {plan_json.get('execution_strategy', 'unknown')}\n")
        except Exception as e:
            print(f"✗ Failed to parse plan: {e}\n")
            print(f"Raw response:\n{planning_response.content}\n")
            plan_json = {
                "analysis": "Fallback: Execute as single task",
                "subtasks": [{
                    "id": 1,
                    "description": task_description,
                    "model": "opus",
                    "dependencies": [],
                    "estimated_tokens": 4000
                }],
                "execution_strategy": "single",
                "expected_deliverables": ["Complete implementation"]
            }
        
        # Step 3: Execute subtasks with agents
        print(f"[Step 3/4] Executing {len(plan_json['subtasks'])} subtasks with agents...\n")
        
        agent_results = []
        total_tokens = planning_response.tokens_used['total']
        
        for subtask in plan_json['subtasks'][:10]:  # Limit to 10 for demo
            subtask_id = subtask['id']
            subtask_desc = subtask['description']
            model = subtask.get('model', 'sonnet')
            
            print(f"  [Agent {subtask_id}] Executing with Claude {model.upper()} 4.5...")
            
            agent_prompt = f"""You are Dive Coder Agent #{subtask_id} working on a subtask.

MAIN TASK: {task_description}

YOUR SUBTASK: {subtask_desc}

CONTEXT: {json.dumps(context) if context else 'None'}

Execute this subtask and provide:
1. Implementation code/files
2. Explanation of approach
3. Any issues or dependencies discovered

Be concise but complete."""

            if model == "opus":
                response = self.llm_client.chat_with_claude_opus(agent_prompt, max_tokens=4000)
            else:
                response = self.llm_client.chat_with_claude_sonnet(agent_prompt, max_tokens=4000)
            
            if response.status == "success":
                print(f"    ✓ Complete ({response.latency_ms:.2f}ms, {response.tokens_used['total']} tokens)")
                agent_results.append({
                    "agent_id": subtask_id,
                    "subtask": subtask_desc,
                    "model": model,
                    "status": "success",
                    "output": response.content,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms,
                    "provider": response.provider
                })
                total_tokens += response.tokens_used['total']
            else:
                print(f"    ✗ Failed: {response.error}")
                agent_results.append({
                    "agent_id": subtask_id,
                    "subtask": subtask_desc,
                    "model": model,
                    "status": "error",
                    "error": response.error
                })
        
        print()
        
        # Step 4: Synthesize results
        print("[Step 4/4] Synthesizing results...\n")
        
        synthesis_prompt = f"""You are Dive Orchestrator V20. You coordinated {len(agent_results)} agents to execute this task:

TASK: {task_description}

AGENT RESULTS:
{json.dumps(agent_results, indent=2)}

Synthesize these results into a coherent final output:
1. Combine all agent outputs
2. Resolve any conflicts or overlaps
3. Provide final implementation/solution
4. List any remaining issues or next steps

Be comprehensive and well-organized."""

        synthesis_response = self.llm_client.chat_with_claude_sonnet(
            synthesis_prompt,
            max_tokens=8000
        )
        
        if synthesis_response.status == "success":
            print(f"✓ Synthesis complete ({synthesis_response.latency_ms:.2f}ms)")
            total_tokens += synthesis_response.tokens_used['total']
            
            agent_results.append({
                "agent_id": 0,
                "subtask": "Final synthesis",
                "model": "sonnet",
                "status": "success",
                "output": synthesis_response.content,
                "tokens": synthesis_response.tokens_used,
                "latency_ms": synthesis_response.latency_ms,
                "provider": synthesis_response.provider
            })
        
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        print("\n" + "="*100)
        print("DIVE AI V20 ORCHESTRATOR - TASK COMPLETE")
        print("="*100)
        print(f"Execution Time: {execution_time_ms/1000:.2f}s")
        print(f"Total Tokens: {total_tokens}")
        print(f"Agents Used: {len(agent_results)}")
        print("="*100 + "\n")
        
        return OrchestratorResult(
            success=True,
            task_description=task_description,
            agent_results=agent_results,
            total_agents=len(agent_results),
            execution_time_ms=execution_time_ms,
            total_tokens=total_tokens,
            orchestrator_model="claude-sonnet-4-5",
            timestamp=datetime.now().isoformat()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        llm_status = self.llm_client.get_status()
        
        return {
            "orchestrator": "Dive AI V20",
            "version": "20.0.0",
            "priority": "HIGHEST",
            "always_run": True,
            "project_path": self.project_path,
            "agent_count": self.agent_count,
            "llm_client": llm_status,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dive AI V20 Orchestrator")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--task", type=str, help="Task description")
    parser.add_argument("--project", type=str, help="Project path")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    orchestrator = DiveOrchestratorV20(project_path=args.project)
    
    if args.status:
        print(json.dumps(orchestrator.get_status(), indent=2))
        return
    
    if args.test:
        connected = orchestrator.test_connection()
        sys.exit(0 if connected else 1)
    
    if args.task:
        result = orchestrator.execute_task(args.task)
        
        # Print final synthesis
        if result.success:
            final_output = next(
                (r['output'] for r in result.agent_results if r['agent_id'] == 0),
                "No synthesis available"
            )
            print("\n" + "="*100)
            print("FINAL OUTPUT")
            print("="*100 + "\n")
            print(final_output)
            print("\n" + "="*100 + "\n")
        
        sys.exit(0 if result.success else 1)
    
    # No arguments - show help
    parser.print_help()

if __name__ == "__main__":
    main()
