#!/usr/bin/env python3
"""
Dive Coder Wrapper - Clean interface for Master Orchestrator
Uses importlib to avoid import conflicts
"""

import sys
import os
import importlib.util
from typing import Dict, List, Any, Optional

class DiveCoderWrapper:
    """
    Wrapper for Dive Coder v19.3 that handles imports cleanly
    """
    
    def __init__(self, dive_coder_path: str = '/home/ubuntu/dive-coder-v19.3'):
        """Initialize Dive Coder wrapper"""
        self.dive_coder_path = dive_coder_path
        self.orchestrator = None
        self.agents = []
        self.router = None
        
        # Load modules using importlib
        self._load_modules()
    
    def _load_module_from_path(self, module_name: str, file_path: str):
        """Load a module from file path using importlib"""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        return None
    
    def _load_modules(self):
        """Load Dive Coder modules"""
        try:
            # Load orchestrator
            orchestrator_path = os.path.join(
                self.dive_coder_path, 
                'orchestrator', 
                'dive_orchestrator.py'
            )
            orchestrator_module = self._load_module_from_path(
                'dive_coder_orchestrator',
                orchestrator_path
            )
            
            if orchestrator_module:
                self.orchestrator = orchestrator_module.get_orchestrator(num_agents=8)
            
            # Load agent
            agent_path = os.path.join(
                self.dive_coder_path,
                'agents',
                'dive_coder_agent.py'
            )
            agent_module = self._load_module_from_path(
                'dive_coder_agent',
                agent_path
            )
            
            # Load semantic router
            router_path = os.path.join(
                self.dive_coder_path,
                'skills',
                'sr',
                'semantic_routing.py'
            )
            router_module = self._load_module_from_path(
                'dive_coder_semantic_routing',
                router_path
            )
            
            if router_module:
                self.router = router_module.get_semantic_router()
            
            # Initialize agents
            if agent_module and self.orchestrator:
                for i in range(8):
                    agent = agent_module.DiveCoderAgent(f"agent_{i}")
                    self.orchestrator.register_agent(f"agent_{i}", agent)
                    self.agents.append(agent)
            
            print(f"✓ Dive Coder Wrapper: Loaded successfully")
            print(f"  - Orchestrator: {'Ready' if self.orchestrator else 'Failed'}")
            print(f"  - Agents: {len(self.agents)}")
            print(f"  - Router: {'Ready' if self.router else 'Failed'}")
            
        except Exception as e:
            print(f"✗ Dive Coder Wrapper: Failed to load ({str(e)})")
    
    def is_ready(self) -> bool:
        """Check if wrapper is ready"""
        return (self.orchestrator is not None and 
                len(self.agents) > 0 and 
                self.router is not None)
    
    def submit_task(self, task: Dict[str, Any]) -> str:
        """Submit task to Dive Coder orchestrator"""
        if not self.is_ready():
            raise RuntimeError("Dive Coder wrapper not ready")
        
        # Convert dict to Task object and submit
        # (Implementation depends on Dive Coder's Task class)
        task_id = task.get('task_id', 'unknown')
        self.orchestrator.submit_task(task)
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status from orchestrator"""
        if not self.is_ready():
            return {"status": "error", "message": "Wrapper not ready"}
        
        return self.orchestrator.get_task_status(task_id)
    
    def get_capabilities(self) -> List[str]:
        """Get list of all capabilities"""
        if not self.agents:
            return []
        
        # Get capabilities from first agent (all agents are identical)
        return list(self.agents[0].capabilities.keys()) if self.agents else []

# Global instance
_dive_coder_wrapper = None

def get_dive_coder_wrapper() -> Optional[DiveCoderWrapper]:
    """Get or create Dive Coder wrapper instance"""
    global _dive_coder_wrapper
    if _dive_coder_wrapper is None:
        _dive_coder_wrapper = DiveCoderWrapper()
    return _dive_coder_wrapper if _dive_coder_wrapper.is_ready() else None

if __name__ == "__main__":
    # Test wrapper
    print("\nTesting Dive Coder Wrapper...")
    print("=" * 80)
    
    wrapper = get_dive_coder_wrapper()
    
    if wrapper and wrapper.is_ready():
        print("\n✓ Dive Coder Wrapper: OPERATIONAL")
        print(f"✓ Capabilities: {len(wrapper.get_capabilities())}")
    else:
        print("\n✗ Dive Coder Wrapper: FAILED")
    
    print("=" * 80 + "\n")
