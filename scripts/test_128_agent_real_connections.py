"""
Test 128-Agent Fleet with Real Claude Opus 4.5 Connections
Tests actual API connections to V98API and AICoding providers
"""

import asyncio
import sys
sys.path.append('/home/ubuntu/dive-ai-messenger/Dive-Ai')

from integration.unified_llm_client import UnifiedLLMClient, Provider
from core.dive_agent_fleet import DiveAgent, AgentStatus
from typing import List, Dict, Any
import time


class RealDiveAgent(DiveAgent):
    """Dive Agent with real Claude Opus 4.5 connection"""
    
    def __init__(self, id: int, llm_client: UnifiedLLMClient, provider: Provider):
        super().__init__(id=id, model="claude-opus-4.5", status=AgentStatus.IDLE)
        self.llm_client = llm_client
        self.provider = provider
    
    async def execute_task_real(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using real Claude Opus 4.5"""
        self.status = AgentStatus.BUSY
        self.current_task = task.get('id')
        
        start_time = time.time()
        
        try:
            # Create prompt for Claude Opus
            prompt = f"""You are Dive Agent #{self.id}.
Task: {task.get('description', 'No description')}

Please respond with a brief confirmation that you can handle this task."""
            
            # Call real Claude Opus 4.5 API
            response = self.llm_client.chat_with_claude_opus(
                message=prompt,
                max_tokens=100,
                provider=self.provider
            )
            
            execution_time = time.time() - start_time
            
            if response.status == "success":
                self.tasks_completed += 1
                self.total_time += execution_time
                self.status = AgentStatus.IDLE
                self.current_task = None
                
                return {
                    'agent_id': self.id,
                    'task_id': task.get('id'),
                    'status': 'success',
                    'result': response.content[:200],  # First 200 chars
                    'provider': response.provider,
                    'model': response.model,
                    'tokens_used': response.tokens_used,
                    'latency_ms': response.latency_ms,
                    'execution_time': execution_time
                }
            else:
                self.status = AgentStatus.ERROR
                return {
                    'agent_id': self.id,
                    'task_id': task.get('id'),
                    'status': 'error',
                    'error': response.error,
                    'provider': response.provider
                }
                
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                'agent_id': self.id,
                'task_id': task.get('id'),
                'status': 'error',
                'error': str(e)
            }


class Real128AgentFleetTester:
    """Test 128-agent fleet with real API connections"""
    
    def __init__(self):
        self.llm_client = UnifiedLLMClient()
        self.agents: List[RealDiveAgent] = []
        
        print("🚀 Initializing 128-Agent Fleet with Real Connections")
        print("="*70)
        
        # Create 128 agents (64 on V98API, 64 on AICoding)
        for i in range(128):
            provider = Provider.V98API if i < 64 else Provider.AICODING
            agent = RealDiveAgent(
                id=i,
                llm_client=self.llm_client,
                provider=provider
            )
            self.agents.append(agent)
        
        print(f"✅ Created 128 agents:")
        print(f"   - 64 agents on V98API")
        print(f"   - 64 agents on AICoding")
        print("="*70)
    
    async def test_single_agent(self):
        """Test single agent connection"""
        print("\n📊 TEST 1: Single Agent Connection")
        print("-"*70)
        
        agent = self.agents[0]
        task = {
            'id': 'test_1',
            'description': 'Test connection to Claude Opus 4.5'
        }
        
        result = await agent.execute_task_real(task)
        
        if result['status'] == 'success':
            print(f"✅ Agent {result['agent_id']} connected successfully!")
            print(f"   Provider: {result['provider']}")
            print(f"   Model: {result['model']}")
            print(f"   Latency: {result['latency_ms']:.2f}ms")
            print(f"   Tokens: {result['tokens_used']}")
            print(f"   Response: {result['result'][:100]}...")
            return True
        else:
            print(f"❌ Agent {result['agent_id']} failed!")
            print(f"   Error: {result['error']}")
            return False
    
    async def test_multiple_agents(self, num_agents: int = 10):
        """Test multiple agents in parallel"""
        print(f"\n📊 TEST 2: {num_agents} Agents in Parallel")
        print("-"*70)
        
        tasks = []
        for i in range(num_agents):
            task = {
                'id': f'test_{i}',
                'description': f'Parallel test task {i}'
            }
            tasks.append(self.agents[i].execute_task_real(task))
        
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        print(f"\n✅ Results:")
        print(f"   Total: {len(results)}")
        print(f"   Success: {success_count}")
        print(f"   Failed: {len(results) - success_count}")
        
        if success_count > 0:
            avg_latency = sum(r['latency_ms'] for r in results if r['status'] == 'success') / success_count
            print(f"   Avg Latency: {avg_latency:.2f}ms")
        
        return success_count == len(results)
    
    async def test_both_providers(self):
        """Test both V98API and AICoding providers"""
        print(f"\n📊 TEST 3: Both Providers (V98API + AICoding)")
        print("-"*70)
        
        # Test V98API agent
        v98_agent = self.agents[0]  # First 64 are V98API
        v98_task = {
            'id': 'test_v98',
            'description': 'Test V98API provider'
        }
        
        # Test AICoding agent
        aicoding_agent = self.agents[64]  # Last 64 are AICoding
        aicoding_task = {
            'id': 'test_aicoding',
            'description': 'Test AICoding provider'
        }
        
        v98_result, aicoding_result = await asyncio.gather(
            v98_agent.execute_task_real(v98_task),
            aicoding_agent.execute_task_real(aicoding_task)
        )
        
        print(f"\n✅ V98API Provider:")
        if v98_result['status'] == 'success':
            print(f"   Status: SUCCESS")
            print(f"   Latency: {v98_result['latency_ms']:.2f}ms")
            print(f"   Tokens: {v98_result['tokens_used']}")
        else:
            print(f"   Status: FAILED")
            print(f"   Error: {v98_result['error']}")
        
        print(f"\n✅ AICoding Provider:")
        if aicoding_result['status'] == 'success':
            print(f"   Status: SUCCESS")
            print(f"   Latency: {aicoding_result['latency_ms']:.2f}ms")
            print(f"   Tokens: {aicoding_result['tokens_used']}")
        else:
            print(f"   Status: FAILED")
            print(f"   Error: {aicoding_result['error']}")
        
        return v98_result['status'] == 'success' and aicoding_result['status'] == 'success'
    
    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("🧪 TESTING 128-AGENT FLEET WITH REAL CONNECTIONS")
        print("="*70)
        
        results = []
        
        # Test 1: Single agent
        result1 = await self.test_single_agent()
        results.append(("Single Agent", result1))
        
        # Test 2: Multiple agents
        result2 = await self.test_multiple_agents(10)
        results.append(("10 Agents Parallel", result2))
        
        # Test 3: Both providers
        result3 = await self.test_both_providers()
        results.append(("Both Providers", result3))
        
        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<50} {status}")
        
        all_passed = all(r for _, r in results)
        
        print("="*70)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ 128-agent fleet is ready with real Claude Opus 4.5 connections!")
        else:
            print("⚠️ SOME TESTS FAILED")
            print("❌ Check API keys and provider configurations")
        print("="*70)
        
        return all_passed


async def main():
    """Main test function"""
    tester = Real128AgentFleetTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Ready to proceed with V23.2 implementation!")
    else:
        print("\n❌ Fix connection issues before proceeding")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
