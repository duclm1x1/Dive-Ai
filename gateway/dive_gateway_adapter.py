"""
Dive AI V29.3 - Gateway Adapter
Connects Gateway Server to existing Dive AI Agentic components

This adapter bridges the new Gateway layer with:
- Smart Orchestrator (existing)
- 128-Agent Fleet (existing)
- Memory Brain (existing)
- UI-TARS Client (V28.7)
"""

import sys
import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import existing Dive AI components
try:
    from core.dive_smart_orchestrator import DiveSmartOrchestrator
    from core.dive_agent_fleet import DiveAgentFleet
    from core.dive_memory_brain import DiveMemory3FileComplete
    from core.dive_uitars_client import UITARSClient
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("   Some features may not be available.")


class DiveGatewayAdapter:
    """
    Gateway Adapter - Bridge between Gateway and Dive AI Core
    
    Responsibilities:
    - Route messages to Smart Orchestrator
    - Manage 128-agent fleet execution
    - Integrate memory context
    - Handle UI-TARS commands
    - Provide unified response format
    """
    
    def __init__(
        self,
        memory_dir: str = "memory",
        num_agents: int = 128,
        enable_uitars: bool = False
    ):
        """
        Initialize Gateway Adapter
        
        Args:
            memory_dir: Directory for memory storage
            num_agents: Number of agents in fleet (default 128)
            enable_uitars: Enable UI-TARS integration
        """
        print("🔧 Initializing Dive Gateway Adapter...")
        
        # Initialize core components
        try:
            self.orchestrator = DiveSmartOrchestrator(memory_dir=memory_dir)
            print("   ✅ Smart Orchestrator loaded")
        except Exception as e:
            print(f"   ⚠️ Orchestrator init failed: {e}")
            self.orchestrator = None
        
        try:
            self.agent_fleet = DiveAgentFleet(num_agents=num_agents)
            print(f"   ✅ {num_agents}-Agent Fleet loaded")
        except Exception as e:
            print(f"   ⚠️ Agent Fleet init failed: {e}")
            self.agent_fleet = None
        
        try:
            self.memory = DiveMemory3FileComplete(memory_dir)
            print("   ✅ Memory Brain loaded")
        except Exception as e:
            print(f"   ⚠️ Memory init failed: {e}")
            self.memory = None
        
        # UI-TARS (optional)
        self.uitars = None
        if enable_uitars:
            try:
                self.uitars = UITARSClient()
                print("   ✅ UI-TARS Client loaded")
            except Exception as e:
                print(f"   ⚠️ UI-TARS init failed: {e}")
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        print("✅ Gateway Adapter initialized successfully!\n")
    
    async def process_message(
        self,
        channel: str,
        user_id: str,
        message: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process message through Dive AI system
        
        Args:
            channel: Channel name (telegram, discord, cli, web)
            user_id: User identifier
            message: User message
            session_id: Session identifier
            metadata: Additional metadata
        
        Returns:
            Response dict with status, response, and details
        """
        self.total_requests += 1
        start_time = datetime.now()
        
        try:
            # 1. Detect message type
            message_type = self._detect_message_type(message)
            
            # 2. Route to appropriate handler
            if message_type == "ui_automation":
                result = await self._handle_ui_automation(message, session_id)
            elif message_type == "agent_task":
                result = await self._handle_agent_task(message, session_id)
            else:
                result = await self._handle_orchestrator(message, session_id)
            
            # 3. Update statistics
            self.successful_requests += 1
            
            # 4. Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'response': result.get('summary', result.get('response', 'Task completed')),
                'details': result,
                'metadata': {
                    'channel': channel,
                    'user_id': user_id,
                    'session_id': session_id,
                    'message_type': message_type,
                    'duration_seconds': duration,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.failed_requests += 1
            
            return {
                'status': 'error',
                'response': f"Error processing message: {str(e)}",
                'error': str(e),
                'metadata': {
                    'channel': channel,
                    'user_id': user_id,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def _detect_message_type(self, message: str) -> str:
        """
        Detect message type for routing
        
        Returns:
            'ui_automation', 'agent_task', or 'general'
        """
        message_lower = message.lower()
        
        # UI automation keywords
        ui_keywords = ["open", "click", "type", "navigate", "screenshot", "browser", "window"]
        if any(kw in message_lower for kw in ui_keywords):
            return "ui_automation"
        
        # Agent task keywords (parallel execution)
        agent_keywords = ["parallel", "concurrent", "batch", "multiple", "distribute"]
        if any(kw in message_lower for kw in agent_keywords):
            return "agent_task"
        
        return "general"
    
    async def _handle_orchestrator(self, message: str, session_id: str) -> Dict[str, Any]:
        """Handle message through Smart Orchestrator"""
        
        if not self.orchestrator:
            return {
                'summary': 'Orchestrator not available',
                'status': 'error'
            }
        
        # Use existing Smart Orchestrator
        result = self.orchestrator.process_prompt(
            prompt=message,
            project_id=session_id
        )
        
        return result
    
    async def _handle_agent_task(self, message: str, session_id: str) -> Dict[str, Any]:
        """Handle message requiring agent fleet"""
        
        if not self.agent_fleet:
            return {
                'response': 'Agent fleet not available',
                'status': 'error'
            }
        
        # Decompose into subtasks
        # In production, use Orchestrator to decompose
        subtasks = self._decompose_message(message)
        
        # Distribute to agent fleet
        results = await self.agent_fleet.distribute_tasks(subtasks)
        
        # Get statistics
        stats = self.agent_fleet.get_statistics()
        
        return {
            'summary': f"Completed {stats['total_tasks_completed']} tasks using {stats['total_agents']} agents",
            'results': results,
            'statistics': stats
        }
    
    async def _handle_ui_automation(self, message: str, session_id: str) -> Dict[str, Any]:
        """Handle UI automation through UI-TARS"""
        
        if not self.uitars:
            return {
                'response': 'UI-TARS not available. Please enable UI automation.',
                'status': 'error'
            }
        
        # Execute through UI-TARS
        results = []
        for action_result in self.uitars.execute_command(message):
            results.append(action_result)
        
        return {
            'summary': f"Executed {len(results)} UI actions",
            'results': results
        }
    
    def _decompose_message(self, message: str) -> List[Dict[str, Any]]:
        """
        Simple message decomposition
        In production, use Orchestrator's decomposition
        """
        # Split by common delimiters
        parts = message.replace(" and ", "|").replace(", ", "|").split("|")
        
        subtasks = []
        for i, part in enumerate(parts):
            subtasks.append({
                'id': f"task_{i}",
                'description': part.strip(),
                'type': 'execution'
            })
        
        return subtasks if subtasks else [{'id': 'task_0', 'description': message, 'type': 'execution'}]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        
        stats = {
            'adapter': {
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'failed_requests': self.failed_requests,
                'success_rate': self.successful_requests / self.total_requests if self.total_requests > 0 else 0
            }
        }
        
        # Add agent fleet stats if available
        if self.agent_fleet:
            stats['agent_fleet'] = self.agent_fleet.get_statistics()
        
        # Add orchestrator status
        stats['orchestrator'] = {
            'available': self.orchestrator is not None
        }
        
        # Add UI-TARS status
        stats['uitars'] = {
            'available': self.uitars is not None
        }
        
        return stats
    
    def print_statistics(self):
        """Print detailed statistics"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 GATEWAY ADAPTER STATISTICS")
        print("="*60)
        
        print(f"\nAdapter:")
        print(f"  Total Requests:      {stats['adapter']['total_requests']}")
        print(f"  Successful:          {stats['adapter']['successful_requests']}")
        print(f"  Failed:              {stats['adapter']['failed_requests']}")
        print(f"  Success Rate:        {stats['adapter']['success_rate']*100:.1f}%")
        
        print(f"\nComponents:")
        print(f"  Orchestrator:        {'✅ Available' if stats['orchestrator']['available'] else '❌ Not Available'}")
        print(f"  UI-TARS:             {'✅ Available' if stats['uitars']['available'] else '❌ Not Available'}")
        
        if 'agent_fleet' in stats:
            fleet = stats['agent_fleet']
            print(f"\nAgent Fleet:")
            print(f"  Total Agents:        {fleet['total_agents']}")
            print(f"  Idle:                {fleet['idle_agents']}")
            print(f"  Busy:                {fleet['busy_agents']}")
            print(f"  Tasks Completed:     {fleet['total_tasks_completed']}")
            print(f"  Utilization:         {fleet['utilization']*100:.1f}%")
        
        print("="*60)


# Test function
async def test_adapter():
    """Test Gateway Adapter"""
    print("\n🧪 Testing Gateway Adapter\n")
    
    # Initialize adapter
    adapter = DiveGatewayAdapter(
        memory_dir="memory",
        num_agents=8,  # Small test fleet
        enable_uitars=False
    )
    
    # Test 1: General message
    print("\n" + "="*60)
    print("TEST 1: General Message (Orchestrator)")
    print("="*60)
    result1 = await adapter.process_message(
        channel="cli",
        user_id="test_user",
        message="Analyze the Dive AI architecture",
        session_id="test_session_1"
    )
    print(f"Status: {result1['status']}")
    print(f"Response: {result1['response']}")
    
    # Test 2: Agent task
    print("\n" + "="*60)
    print("TEST 2: Agent Task (Fleet)")
    print("="*60)
    result2 = await adapter.process_message(
        channel="cli",
        user_id="test_user",
        message="Distribute and execute these parallel tasks: analyze code, run tests, generate docs",
        session_id="test_session_2"
    )
    print(f"Status: {result2['status']}")
    print(f"Response: {result2['response']}")
    
    # Show statistics
    adapter.print_statistics()


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_adapter())
