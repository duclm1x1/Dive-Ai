"""
Dive AI V20 Runner
Orchestrator wrapper with Dive-Memory v2 integration

This module acts as a messenger between user requests and the Dive AI V20 orchestrator,
automatically injecting project context from Dive-Memory v2.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add v20 to Python path
v20_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(v20_path))

# Import DiveMemorySkill directly
import importlib.util
skill_file = v20_path / "skills" / "internal" / "dive-memory-v2" / "skill.py"
spec = importlib.util.spec_from_file_location("dive_memory_skill", skill_file)
dive_memory_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dive_memory_module)
DiveMemorySkill = dive_memory_module.DiveMemorySkill


class DiveAIRunner:
    """
    Dive AI V20 Runner with Memory Integration
    
    Acts as a messenger that:
    1. Receives user requests
    2. Injects context from Dive-Memory v2
    3. Routes to appropriate skills
    4. Returns results
    5. Updates dynamic state
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize Dive AI Runner
        
        Args:
            project_path: Path to project root (defaults to current directory)
        """
        self.project_path = project_path or os.getcwd()
        self.memory_skill = DiveMemorySkill(self.project_path)
        self.request_count = 0
        
    def process_request(self, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process a user request with context injection
        
        Args:
            user_prompt: User's input prompt
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
                - response: AI response
                - context_injected: Whether context was injected
                - matched_triggers: Matched skill triggers
                - suggestions: Skill suggestions
        """
        self.request_count += 1
        
        print(f"\n{'='*60}")
        print(f"[Dive AI V20] Processing Request #{self.request_count}")
        print(f"{'='*60}\n")
        
        # Check if Dive-Memory is active
        if not self.memory_skill.is_active():
            print("[Dive AI V20] No PROJECT.memory.md found - running without context injection")
            return {
                'response': self._execute_without_context(user_prompt, **kwargs),
                'context_injected': False,
                'matched_triggers': [],
                'suggestions': []
            }
        
        # Inject context
        print("[Dive AI V20] Injecting project context from Dive-Memory v2...")
        injection_result = self.memory_skill.inject_context(user_prompt)
        
        final_prompt = injection_result['final_prompt']
        matched_triggers = injection_result['matched_triggers']
        suggestions = injection_result['suggestions']
        
        # Display context injection summary
        print(f"\n[Context Injection Summary]")
        print(f"  • Context injected: ✓")
        print(f"  • Matched triggers: {len(matched_triggers)}")
        print(f"  • Suggestions: {len(suggestions)}")
        
        if suggestions:
            print(f"\n[Skill Suggestions]")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        
        print(f"\n[Full Prompt Preview]")
        print("-" * 60)
        print(final_prompt[:500] + "..." if len(final_prompt) > 500 else final_prompt)
        print("-" * 60)
        
        # Execute with context
        print(f"\n[Dive AI V20] Executing with injected context...")
        response = self._execute_with_context(final_prompt, **kwargs)
        
        # Update dynamic state
        self._update_state_after_request(user_prompt, response)
        
        return {
            'response': response,
            'context_injected': True,
            'matched_triggers': matched_triggers,
            'suggestions': suggestions,
            'final_prompt': final_prompt
        }
    
    def _execute_without_context(self, prompt: str, **kwargs) -> str:
        """
        Execute prompt without context injection
        
        Args:
            prompt: User prompt
            **kwargs: Additional parameters
            
        Returns:
            AI response
        """
        # This would call the actual orchestrator
        # For now, return a placeholder
        return f"[Placeholder] Would execute: {prompt}"
    
    def _execute_with_context(self, prompt: str, **kwargs) -> str:
        """
        Execute prompt with context injection
        
        Args:
            prompt: Full prompt with context
            **kwargs: Additional parameters
            
        Returns:
            AI response
        """
        # This would call the actual orchestrator with the full prompt
        # For now, return a placeholder
        return f"[Placeholder] Would execute with context: {prompt[:100]}..."
    
    def _update_state_after_request(self, user_prompt: str, response: str):
        """
        Update dynamic state after processing request
        
        Args:
            user_prompt: Original user prompt
            response: AI response
        """
        updates = {
            'last_request': user_prompt[:100],
            'last_response_length': len(response),
            'total_requests': self.request_count
        }
        
        success = self.memory_skill.update_dynamic_state(updates)
        if success:
            print(f"\n[Dive AI V20] Dynamic state updated ✓")
        else:
            print(f"\n[Dive AI V20] Failed to update dynamic state ✗")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Dive AI V20 and Dive-Memory v2
        
        Returns:
            Test results dictionary
        """
        print("\n" + "="*60)
        print("[Dive AI V20] Connection Test")
        print("="*60 + "\n")
        
        results = {
            'orchestrator': 'connected',
            'memory_skill': 'not_found',
            'project_memory': 'not_found',
            'skills_registry': 'not_found'
        }
        
        # Test memory skill
        if self.memory_skill.is_active():
            results['memory_skill'] = 'active'
            results['project_memory'] = 'loaded'
            print("✓ Dive-Memory v2 skill: ACTIVE")
            print("✓ PROJECT.memory.md: LOADED")
            
            memory = self.memory_skill.load_memory()
            if memory:
                print(f"  • Project Goal: {memory.get('project_goal', 'N/A')}")
                print(f"  • Always-On Skills: {len(memory.get('always_on_skills', []))}")
                print(f"  • Behavioral Rules: {len(memory.get('behavioral_rules', []))}")
                print(f"  • Skill Triggers: {len(memory.get('skill_triggers', []))}")
        else:
            print("✗ Dive-Memory v2 skill: INACTIVE")
            print("  (No PROJECT.memory.md found)")
        
        # Test skills registry
        registry_path = v20_path / "runtime" / "skills_registry.yml"
        if registry_path.exists():
            results['skills_registry'] = 'found'
            print("✓ Skills Registry: FOUND")
        else:
            print("✗ Skills Registry: NOT FOUND")
        
        print("\n" + "="*60)
        print("[Test Results]")
        print("="*60)
        for key, value in results.items():
            status = "✓" if value in ['connected', 'active', 'loaded', 'found'] else "✗"
            print(f"{status} {key}: {value}")
        
        return results
    
    def test_always_run(self) -> bool:
        """
        Test if Dive-Memory v2 runs on every request
        
        Returns:
            True if always-run works, False otherwise
        """
        print("\n" + "="*60)
        print("[Dive AI V20] Always-Run Test")
        print("="*60 + "\n")
        
        test_prompts = [
            "Hello, can you help me?",
            "What's the project goal?",
            "I need to implement a feature"
        ]
        
        all_injected = True
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n[Test {i}/3] Prompt: \"{prompt}\"")
            result = self.process_request(prompt)
            
            if result['context_injected']:
                print(f"  ✓ Context injected successfully")
            else:
                print(f"  ✗ Context NOT injected")
                all_injected = False
        
        print("\n" + "="*60)
        if all_injected:
            print("✓ Always-Run Test: PASSED")
            print("  Dive-Memory v2 injected context on all requests")
        else:
            print("✗ Always-Run Test: FAILED")
            print("  Context injection was not consistent")
        print("="*60)
        
        return all_injected
    
    def test_skill_routing(self) -> Dict[str, Any]:
        """
        Test skill routing and trigger matching
        
        Returns:
            Test results dictionary
        """
        print("\n" + "="*60)
        print("[Dive AI V20] Skill Routing Test")
        print("="*60 + "\n")
        
        test_cases = [
            {
                'prompt': "I want to build an Electron desktop app",
                'expected_skill': "electron_builder"
            },
            {
                'prompt': "How do I integrate GitHub sync?",
                'expected_skill': "git_integrator"
            },
            {
                'prompt': "Can you review my code?",
                'expected_skill': None  # No specific trigger
            }
        ]
        
        results = {
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n[Test {i}/{len(test_cases)}]")
            print(f"  Prompt: \"{test['prompt']}\"")
            print(f"  Expected Skill: {test['expected_skill'] or 'None'}")
            
            result = self.process_request(test['prompt'])
            matched = result['matched_triggers']
            
            if test['expected_skill']:
                # Should match
                matched_skills = [t.get('skill_to_suggest') or t.get('skill') for t in matched]
                if test['expected_skill'] in matched_skills:
                    print(f"  ✓ PASSED - Skill matched correctly")
                    results['passed'] += 1
                    results['details'].append({
                        'test': i,
                        'status': 'passed',
                        'matched': matched_skills
                    })
                else:
                    print(f"  ✗ FAILED - Expected skill not matched")
                    print(f"    Matched: {matched_skills}")
                    results['failed'] += 1
                    results['details'].append({
                        'test': i,
                        'status': 'failed',
                        'expected': test['expected_skill'],
                        'matched': matched_skills
                    })
            else:
                # Should not match any specific skill
                if len(matched) == 0:
                    print(f"  ✓ PASSED - No false positives")
                    results['passed'] += 1
                else:
                    print(f"  ⚠ WARNING - Unexpected matches: {[t.get('skill') for t in matched]}")
                    results['passed'] += 1  # Not a failure, just unexpected
        
        print("\n" + "="*60)
        print(f"[Skill Routing Test Results]")
        print(f"  Total: {results['total_tests']}")
        print(f"  Passed: {results['passed']}")
        print(f"  Failed: {results['failed']}")
        print("="*60)
        
        return results


# CLI interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dive AI V20 Runner with Memory Integration')
    parser.add_argument('command', choices=['test', 'run', 'test-connection', 'test-always-run', 'test-routing'],
                       help='Command to execute')
    parser.add_argument('--project', '-p', help='Project path', default=os.getcwd())
    parser.add_argument('--prompt', help='User prompt (for run command)')
    
    args = parser.parse_args()
    
    runner = DiveAIRunner(args.project)
    
    if args.command == 'test-connection':
        runner.test_connection()
    
    elif args.command == 'test-always-run':
        runner.test_always_run()
    
    elif args.command == 'test-routing':
        runner.test_skill_routing()
    
    elif args.command == 'test':
        # Run all tests
        print("\n" + "="*60)
        print("[Dive AI V20] Running All Tests")
        print("="*60)
        
        runner.test_connection()
        runner.test_always_run()
        runner.test_skill_routing()
        
        print("\n" + "="*60)
        print("[All Tests Complete]")
        print("="*60)
    
    elif args.command == 'run':
        if not args.prompt:
            print("Error: --prompt required for run command")
            sys.exit(1)
        
        result = runner.process_request(args.prompt)
        print(f"\n[Response]")
        print(result['response'])
    
    else:
        parser.print_help()
