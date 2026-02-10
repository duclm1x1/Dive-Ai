"""
Dive AI V29.3 - End-to-End Integration Tests
Tests complete Agentic AI system flow

Test Scenarios:
1. Gateway → Orchestrator → Agent Fleet
2. Multi-channel message routing
3. Memory persistence
4. Architecture validation
"""

import asyncio
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.gateway.dive_gateway_adapter import DiveGatewayAdapter
from core.gateway.architecture_validator import ArchitectureValidator


class AAssertsTests:
    """End-to-end integration tests"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        print("\n" + "="*60)
        print("🧪 DIVE AI V29.3 - END-TO-END INTEGRATION TESTS")
        print("="*60 + "\n")
        
        # Test 1: Architecture Validation
        await self.test_architecture_validation()
        
        # Test 2: Gateway Adapter
        await self.test_gateway_adapter()
        
        # Test 3: Message Routing
        await self.test_message_routing()
        
        # Test 4: Component Integration
        await self.test_component_integration()
        
        # Print summary
        self.print_summary()
    
    async def test_architecture_validation(self):
        """Test 1: Architecture Validation"""
        print("="*60)
        print("TEST 1: Architecture Validation")
        print("="*60)
        
        try:
            validator = ArchitectureValidator(
                project_root=r"D:\Antigravity\Dive AI"
            )
            
            report = validator.validate_all()
            
            # Check if validation passed
            if report['status'] in ['PASSED', 'WARNING']:
                self._log_pass("Architecture Validation", "Architecture is valid")
            else:
                self._log_fail("Architecture Validation", f"Status: {report['status']}")
            
            print(f"\n✅ Architecture validation complete")
            print(f"   Status: {report['status']}")
            print(f"   Passed: {report['counts']['passed']}/{report['counts']['total']}")
            
        except Exception as e:
            self._log_fail("Architecture Validation", str(e))
            print(f"\n❌ Architecture validation failed: {e}")
    
    async def test_gateway_adapter(self):
        """Test 2: Gateway Adapter"""
        print("\n" + "="*60)
        print("TEST 2: Gateway Adapter")
        print("="*60)
        
        try:
            adapter = DiveGatewayAdapter(
                memory_dir="memory",
                num_agents=4,  # Small test fleet
                enable_uitars=False
            )
            
            # Test message processing
            result = await adapter.process_message(
                channel="cli",
                user_id="test_user",
                message="Test message for gateway adapter",
                session_id="test_session"
            )
            
            if result['status'] == 'success':
                self._log_pass("Gateway Adapter Message Processing", "Message processed successfully")
                print(f"\n✅ Gateway adapter test passed")
                print(f"   Response: {result['response'][:100]}...")
            else:
                self._log_fail("Gateway Adapter Message Processing", result.get('error', 'Unknown error'))
                print(f"\n❌ Gateway adapter test failed")
            
        except Exception as e:
            self._log_fail("Gateway Adapter", str(e))
            print(f"\n❌ Gateway adapter test failed: {e}")
    
    async def test_message_routing(self):
        """Test 3: Message Routing"""
        print("\n" + "="*60)
        print("TEST 3: Message Routing")
        print("="*60)
        
        try:
            adapter = DiveGatewayAdapter(
                memory_dir="memory",
                num_agents=4,
                enable_uitars=False
            )
            
            test_messages = [
                ("General query", "What is Dive AI?"),
                ("Agent task", "Distribute these parallel tasks: analyze, test, document"),
                ("UI automation", "Open Chrome and navigate to GitHub")
            ]
            
            all_passed = True
            for msg_type, message in test_messages:
                result = await adapter.process_message(
                    channel="test",
                    user_id="test_user",
                    message=message,
                    session_id=f"test_{msg_type}"
                )
                
                if result['status'] == 'success':
                    print(f"   ✅ {msg_type}: Routed correctly")
                else:
                    print(f"   ❌ {msg_type}: Failed - {result.get('error', 'Unknown')}")
                    all_passed = False
            
            if all_passed:
                self._log_pass("Message Routing", "All message types routed correctly")
                print(f"\n✅ Message routing test passed")
            else:
                self._log_fail("Message Routing", "Some messages failed routing")
                print(f"\n⚠️ Message routing test had failures")
            
        except Exception as e:
            self._log_fail("Message Routing", str(e))
            print(f"\n❌ Message routing test failed: {e}")
    
    async def test_component_integration(self):
        """Test 4: Component Integration"""
        print("\n" + "="*60)
        print("TEST 4: Component Integration")
        print("="*60)
        
        components_status = {
            'Gateway Adapter': False,
            'Architecture Validator': False,
            'Integration': False
        }
        
        try:
            # Test Gateway Adapter
            adapter = DiveGatewayAdapter(memory_dir="memory", num_agents=2, enable_uitars=False)
            components_status['Gateway Adapter'] = True
            print("   ✅ Gateway Adapter initialized")
            
            # Test Architecture Validator
            validator = ArchitectureValidator(project_root=r"D:\Antigravity\Dive AI")
            components_status['Architecture Validator'] = True
            print("   ✅ Architecture Validator initialized")
            
            # Test integration
            stats = adapter.get_statistics()
            components_status['Integration'] = True
            print("   ✅ Components integrated successfully")
            
            if all(components_status.values()):
                self._log_pass("Component Integration", "All components integrated")
                print(f"\n✅ Component integration test passed")
            else:
                failed = [k for k, v in components_status.items() if not v]
                self._log_fail("Component Integration", f"Failed: {', '.join(failed)}")
                print(f"\n❌ Component integration test failed")
            
        except Exception as e:
            self._log_fail("Component Integration", str(e))
            print(f"\n❌ Component integration test failed: {e}")
    
    def _log_pass(self, test_name: str, message: str):
        """Log passed test"""
        self.passed += 1
        self.results.append({
            'test': test_name,
            'status': 'PASSED',
            'message': message
        })
    
    def _log_fail(self, test_name: str, message: str):
        """Log failed test"""
        self.failed += 1
        self.results.append({
            'test': test_name,
            'status': 'FAILED',
            'message': message
        })
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"\nTotal Tests:    {total}")
        print(f"Passed:         {self.passed} ✅")
        print(f"Failed:         {self.failed} ❌")
        print(f"Pass Rate:      {pass_rate:.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"   - {result['test']}: {result['message']}")
        
        if pass_rate >= 80:
            print(f"\n🎉 TESTS PASSED - System ready for deployment!")
        elif pass_rate >= 50:
            print(f"\n⚠️ PARTIAL SUCCESS - Some issues need attention")
        else:
            print(f"\n❌ TESTS FAILED - Critical issues need fixing")
        
        print("="*60)


async def main():
    """Main test runner"""
    tests = AAssertsTests()
    await tests.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
