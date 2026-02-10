#!/usr/bin/env python3
"""
Dive Orchestrator V28.6
=======================
Quản lý 512 Dive Coder Agents
Mỗi agent = 1 Dive AI hoàn chỉnh (DiveAgentCore)
Unified via V98 + Aicoding APIs (không tách riêng)
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    BEST_PERFORMANCE = "best_performance"
    RANDOM = "random"
    ADAPTIVE = "adaptive"


class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class OrchestratorConfig:
    """Configuration for Dive Orchestrator"""
    total_agents: int = 512
    max_concurrent: int = 512
    load_balance: LoadBalanceStrategy = LoadBalanceStrategy.ADAPTIVE
    
    # API Configuration (Unified - không tách riêng)
    v98_base_url: str = "https://v98store.com/v1"
    v98_api_key: str = ""
    aicoding_base_url: str = "https://aicoding.io.vn/v1"
    aicoding_api_key: str = ""
    
    # Models (Latest only)
    primary_model: str = "claude-opus-4.5"
    secondary_model: str = "claude-sonnet-4.5"
    fast_model: str = "gemini-3.0-pro"
    
    # Memory
    memory_dir: str = "/tmp/dive_orchestrator_memory"
    
    # Auto-deploy
    auto_deploy_memory: bool = True
    auto_deploy_monitor: bool = True


class DiveOrchestratorV286:
    """
    Dive Orchestrator V28.6
    
    Quản lý 512 Dive Coder Agents.
    Mỗi agent là 1 DiveAgentCore hoàn chỉnh.
    Unified API routing (V98 + Aicoding load balanced).
    """
    
    def __init__(self, config: OrchestratorConfig = None):
        self.config = config or OrchestratorConfig()
        self.agents = {}
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.execution_log = []
        self._round_robin_index = 0
        
        # Metrics
        self.total_tasks_submitted = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        self.start_time = datetime.now()
    
    async def initialize(self):
        """Initialize 512 Dive Coder Agents"""
        print(f"🚀 Dive Orchestrator V28.6 - Initializing {self.config.total_agents} agents...")
        print(f"   Each agent = 1 Complete Dive AI (14 modules)")
        print()
        
        # Import DiveAgentCore
        from src.core.agent.dive_agent_core import DiveAgentCore
        
        agent_config = {
            'v98_base_url': self.config.v98_base_url,
            'v98_api_key': self.config.v98_api_key,
            'aicoding_base_url': self.config.aicoding_base_url,
            'aicoding_api_key': self.config.aicoding_api_key,
            'memory_dir': self.config.memory_dir
        }
        
        # Create agents in batches
        batch_size = 64
        for batch_start in range(0, self.config.total_agents, batch_size):
            batch_end = min(batch_start + batch_size, self.config.total_agents)
            batch_tasks = []
            
            for i in range(batch_start, batch_end):
                agent = DiveAgentCore(
                    agent_id=f"dive-coder-{i:03d}",
                    agent_name=f"Dive Coder Agent #{i}"
                )
                batch_tasks.append(agent.initialize(agent_config))
                self.agents[agent.agent_id] = agent
            
            await asyncio.gather(*batch_tasks)
            print(f"   ✅ Batch {batch_start}-{batch_end-1} initialized ({batch_end}/{self.config.total_agents})")
        
        print()
        print(f"✅ All {self.config.total_agents} agents ready!")
        print(f"   Total module instances: {self.config.total_agents * 14}")
        
        # Auto-deploy Memory
        if self.config.auto_deploy_memory:
            await self._deploy_shared_memory()
        
        return True
    
    async def _deploy_shared_memory(self):
        """Deploy shared memory across all agents"""
        print("📦 Deploying shared Dive Memory...")
        import os
        os.makedirs(self.config.memory_dir, exist_ok=True)
        
        # Store orchestrator info in shared memory
        shared_info = {
            'orchestrator_version': '28.6.0',
            'total_agents': self.config.total_agents,
            'initialized_at': datetime.now().isoformat(),
            'config': {
                'primary_model': self.config.primary_model,
                'secondary_model': self.config.secondary_model,
                'load_balance': self.config.load_balance.value
            }
        }
        
        with open(os.path.join(self.config.memory_dir, 'orchestrator_state.json'), 'w') as f:
            json.dump(shared_info, f, indent=2)
        
        print("   ✅ Shared Memory deployed")
    
    # ================================================================
    # TASK SUBMISSION & EXECUTION
    # ================================================================
    
    async def submit_task(self, task: Dict[str, Any],
                          priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Submit a task for execution"""
        task_id = f"task-{self.total_tasks_submitted:06d}"
        task['task_id'] = task_id
        task['priority'] = priority.value
        task['submitted_at'] = datetime.now().isoformat()
        
        self.total_tasks_submitted += 1
        
        # Select agent
        agent = await self._select_agent()
        
        # Execute
        result = await agent.execute(task)
        result['task_id'] = task_id
        
        self.results[task_id] = result
        
        if result.get('status') == 'success':
            self.total_tasks_completed += 1
        else:
            self.total_tasks_failed += 1
        
        return task_id
    
    async def submit_batch(self, tasks: List[Dict[str, Any]],
                           max_concurrent: int = None) -> List[str]:
        """Submit batch of tasks for parallel execution"""
        max_concurrent = max_concurrent or self.config.max_concurrent
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def submit_with_semaphore(task):
            async with semaphore:
                return await self.submit_task(task)
        
        task_ids = await asyncio.gather(
            *[submit_with_semaphore(t) for t in tasks]
        )
        
        return list(task_ids)
    
    async def _select_agent(self):
        """Select agent based on load balancing strategy"""
        agent_list = list(self.agents.values())
        
        if self.config.load_balance == LoadBalanceStrategy.ROUND_ROBIN:
            agent = agent_list[self._round_robin_index % len(agent_list)]
            self._round_robin_index += 1
            return agent
        
        elif self.config.load_balance == LoadBalanceStrategy.LEAST_BUSY:
            return min(agent_list, key=lambda a: a.tasks_completed)
        
        elif self.config.load_balance == LoadBalanceStrategy.BEST_PERFORMANCE:
            ready_agents = [a for a in agent_list if a.state.value == 'ready']
            if ready_agents:
                return min(ready_agents, key=lambda a: a.avg_response_time or float('inf'))
            return agent_list[0]
        
        elif self.config.load_balance == LoadBalanceStrategy.ADAPTIVE:
            # Adaptive: combine least-busy + best-performance
            ready_agents = [a for a in agent_list if a.state.value == 'ready']
            if not ready_agents:
                ready_agents = agent_list
            
            # Score = tasks_completed * 0.3 + avg_response_time * 0.7
            return min(ready_agents, key=lambda a: (
                a.tasks_completed * 0.3 +
                (a.avg_response_time or 0) * 0.7
            ))
        
        else:
            import random
            return random.choice(agent_list)
    
    # ================================================================
    # STATUS & MONITORING
    # ================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        agent_states = {}
        for agent in self.agents.values():
            state = agent.state.value
            agent_states[state] = agent_states.get(state, 0) + 1
        
        return {
            'version': '28.6.0',
            'total_agents': len(self.agents),
            'agent_states': agent_states,
            'total_tasks_submitted': self.total_tasks_submitted,
            'total_tasks_completed': self.total_tasks_completed,
            'total_tasks_failed': self.total_tasks_failed,
            'success_rate': (
                self.total_tasks_completed / self.total_tasks_submitted
                if self.total_tasks_submitted > 0 else 0
            ),
            'uptime_seconds': uptime,
            'load_balance': self.config.load_balance.value,
            'modules_per_agent': 14,
            'total_module_instances': len(self.agents) * 14,
            'primary_model': self.config.primary_model,
            'secondary_model': self.config.secondary_model
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get status of specific agent"""
        agent = self.agents.get(agent_id)
        if agent:
            return agent.get_status()
        return None


# ================================================================
# QUICK START
# ================================================================

async def quick_start(
    v98_api_key: str = "",
    aicoding_api_key: str = "",
    num_agents: int = 512
) -> DiveOrchestratorV286:
    """Quick start Dive Orchestrator with 512 agents"""
    config = OrchestratorConfig(
        total_agents=num_agents,
        v98_api_key=v98_api_key,
        aicoding_api_key=aicoding_api_key
    )
    
    orchestrator = DiveOrchestratorV286(config)
    await orchestrator.initialize()
    
    return orchestrator


if __name__ == "__main__":
    print("Dive Orchestrator V28.6")
    print("512 Dive Coder Agents - Each is a Complete Dive AI")
    print()
    print("Usage:")
    print("  orchestrator = await quick_start(v98_api_key='...', aicoding_api_key='...')")
    print("  task_id = await orchestrator.submit_task({'type': 'code', 'content': 'Create FastAPI app'})")
    print("  results = await orchestrator.submit_batch([task1, task2, ..., task512])")
