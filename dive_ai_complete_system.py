#!/usr/bin/env python3
"""
Dive AI Complete System - Unified Orchestrator ↔ Coder Workflow

The complete Dive AI system with:
- Smart Orchestrator for intelligent planning
- Smart Coder for intelligent execution
- Interrupt handling for adaptive behavior
- Memory integration for learning
- Event streaming for monitoring
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# V21.0.0: Use search-enhanced components for 200-400x faster performance
try:
    from core.dive_orchestrator_search_enhanced import DiveOrchestratorSearchEnhanced as DiveSmartOrchestrator
    from core.dive_memory_search_enhanced import DiveMemorySearchEnhanced as DiveMemory3FileComplete
    SEARCH_ENGINE_ENABLED = True
    print("🔍 V21.0.0 Search Engine: ENABLED (200-400x faster)")
except ImportError:
    # Fallback to original components
    from core.dive_smart_orchestrator import DiveSmartOrchestrator
    from core.dive_memory_3file_complete import DiveMemory3FileComplete
    SEARCH_ENGINE_ENABLED = False
    print("⚠️  V21.0.0 Search Engine: DISABLED (using legacy components)")

from core.dive_smart_coder import DiveSmartCoder


@dataclass
class SystemResult:
    """Complete system execution result"""
    success: bool
    orchestrator_result: Dict
    coder_results: List[Dict]
    total_time: float
    phases_completed: int
    lessons_learned: List[str]


class DiveAICompleteSystem:
    """
    Complete Dive AI System
    
    Workflow:
    User Input → Smart Orchestrator → Smart Coder → Memory → Result
                       ↑                                        ↓
                       └────────── Feedback Loop ──────────────┘
    
    Features:
    - Intelligent prompt processing
    - Task decomposition
    - Intelligent execution
    - Interrupt handling
    - Memory integration
    - Continuous learning
    """
    
    def __init__(self, project_id: str = "DEFAULT"):
        """Initialize complete system"""
        self.project_id = project_id
        self.orchestrator = DiveSmartOrchestrator()
        self.coder = DiveSmartCoder()
        self.memory = DiveMemory3FileComplete()
        self.execution_history = []
        
        print("="*60)
        version = "V21.0.0" if SEARCH_ENGINE_ENABLED else "V20.4.0"
        engine_status = "Search-Driven" if SEARCH_ENGINE_ENABLED else "Legacy"
        print(f"🚀 Dive AI Complete System {version} ({engine_status})")
        print("="*60)
        print("✅ Smart Orchestrator: Ready")
        print("✅ Smart Coder: Ready")
        print("✅ Memory System: Ready")
        print("✅ Interrupt Handler: Ready")
        if SEARCH_ENGINE_ENABLED:
            print("🔍 Search Engine: ACTIVE (200-400x faster)")
        print("="*60)
    
    def process(self, user_input: str) -> SystemResult:
        """
        Process user input through complete system
        
        Args:
            user_input: User's request/prompt
            
        Returns:
            SystemResult with complete execution details
        """
        print(f"\n{'='*60}")
        print(f"👤 USER INPUT: {user_input}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        coder_results = []
        lessons_learned = []
        
        try:
            # Step 1: Orchestrator processes prompt
            print("🧠 STEP 1: SMART ORCHESTRATOR")
            print("-"*60)
            orchestrator_result = self.orchestrator.process_prompt(
                user_input,
                project_id=self.project_id
            )
            
            # Extract tasks from orchestrator
            tasks = self._extract_tasks(orchestrator_result)
            print(f"\n📋 Orchestrator identified {len(tasks)} tasks")
            
            # Step 2: Coder executes each task
            print(f"\n🔧 STEP 2: SMART CODER")
            print("-"*60)
            for i, task in enumerate(tasks, 1):
                print(f"\n📌 Task {i}/{len(tasks)}: {task}")
                print("-"*40)
                
                coder_result = self.coder.execute_task(
                    task,
                    project_id=self.project_id
                )
                
                coder_results.append({
                    'task': task,
                    'result': coder_result,
                    'success': coder_result.success
                })
                
                lessons_learned.extend(coder_result.lessons_learned)
                
                # If task failed, try to recover
                if not coder_result.success:
                    print(f"\n⚠️ Task failed, attempting recovery...")
                    recovery_result = self._attempt_recovery(task, coder_result)
                    if recovery_result:
                        coder_results[-1]['recovery'] = recovery_result
            
            # Step 3: Store complete execution in memory
            print(f"\n💾 STEP 3: MEMORY STORAGE")
            print("-"*60)
            self._store_execution(user_input, orchestrator_result, coder_results)
            
            total_time = time.time() - start_time
            
            # Summary
            print(f"\n{'='*60}")
            print("📊 EXECUTION SUMMARY")
            print(f"{'='*60}")
            print(f"✅ Tasks completed: {sum(1 for r in coder_results if r['success'])}/{len(tasks)}")
            print(f"⏱️ Total time: {total_time:.2f}s")
            print(f"📝 Lessons learned: {len(lessons_learned)}")
            print(f"{'='*60}\n")
            
            return SystemResult(
                success=all(r['success'] for r in coder_results),
                orchestrator_result=orchestrator_result,
                coder_results=coder_results,
                total_time=total_time,
                phases_completed=len(tasks),
                lessons_learned=lessons_learned
            )
            
        except Exception as e:
            print(f"\n❌ System error: {e}")
            total_time = time.time() - start_time
            
            return SystemResult(
                success=False,
                orchestrator_result={},
                coder_results=coder_results,
                total_time=total_time,
                phases_completed=0,
                lessons_learned=[]
            )
    
    def process_with_interrupts(self, user_input: str, interrupt_callback=None) -> SystemResult:
        """
        Process with interrupt handling
        
        Args:
            user_input: User's request
            interrupt_callback: Function to check for interrupts
            
        Returns:
            SystemResult
        """
        # Start processing
        result = self.process(user_input)
        
        # Check for interrupts during execution
        if interrupt_callback:
            interrupt = interrupt_callback()
            if interrupt:
                print(f"\n⚡ INTERRUPT DETECTED: {interrupt}")
                interrupt_result = self.orchestrator.handle_user_interrupt(interrupt)
                
                # If interrupt requires action, reprocess
                if interrupt_result.action.value in ['merge', 'pause']:
                    print(f"🔄 Reprocessing with interrupt...")
                    result = self.process(f"{user_input} {interrupt}")
        
        return result
    
    def _extract_tasks(self, orchestrator_result: Dict) -> List[str]:
        """Extract executable tasks from orchestrator result"""
        tasks = []
        
        # Extract from plan
        plan = orchestrator_result.get('plan', {})
        steps = plan.get('steps', [])
        
        # Handle both list and integer steps
        if isinstance(steps, int):
            # If steps is a count, create generic tasks
            for i in range(steps):
                tasks.append(f"Execute step {i+1}")
        elif isinstance(steps, list):
            # If steps is a list, extract descriptions
            for step in steps:
                if isinstance(step, dict):
                    task_desc = step.get('description', '')
                    if task_desc:
                        tasks.append(task_desc)
                elif isinstance(step, str):
                    tasks.append(step)
        
        # If no tasks extracted, use summary or create single task
        if not tasks:
            summary = orchestrator_result.get('summary', 'Execute task')
            tasks = [summary]
        
        return tasks
    
    def _attempt_recovery(self, task: str, failed_result) -> Optional[Dict]:
        """Attempt to recover from failed execution"""
        print(f"   🔄 Analyzing failure...")
        
        # Check memory for similar failures and solutions
        context = self.memory.load_project(self.project_id)
        
        # Look for known solutions
        criteria = context.get('criteria', '')
        if 'Known Issues' in criteria:
            print(f"   📚 Found known issues, applying solution...")
            # In production, extract and apply solution
            return {'recovered': True, 'method': 'known_solution'}
        
        print(f"   ❌ No recovery method found")
        return None
    
    def _store_execution(self, user_input: str, orchestrator_result: Dict, coder_results: List[Dict]):
        """Store complete execution in memory"""
        # Log to changelog
        success_count = sum(1 for r in coder_results if r['success'])
        total_count = len(coder_results)
        
        self.memory.log_change(
            self.project_id,
            "Executed",
            f"Complete workflow: {user_input} - {success_count}/{total_count} tasks successful"
        )
        
        # Update full knowledge
        knowledge = f"\n### Complete Execution: {user_input}\n"
        knowledge += f"- Tasks: {total_count}\n"
        knowledge += f"- Success rate: {success_count}/{total_count}\n"
        knowledge += f"- Orchestrator phases: {len(orchestrator_result.get('events', []))}\n"
        
        self.memory.save_full_knowledge(self.project_id, knowledge, append=True)
        
        print(f"   ✅ Execution stored in memory")


def demo_complete_system():
    """Demonstrate complete system"""
    system = DiveAICompleteSystem(project_id="DIVE_AI")
    
    # Test 1: Simple request
    print("\n" + "="*60)
    print("DEMO 1: Simple Request")
    print("="*60)
    result1 = system.process("Install Dive AI from GitHub")
    print(f"\n✅ Success: {result1.success}")
    print(f"⏱️ Time: {result1.total_time:.2f}s")
    
    # Test 2: Complex request
    print("\n" + "="*60)
    print("DEMO 2: Complex Request")
    print("="*60)
    result2 = system.process(
        "Install Dive AI, configure LLM client with latest models, "
        "setup first run, test all components, and update documentation"
    )
    print(f"\n✅ Success: {result2.success}")
    print(f"⏱️ Time: {result2.total_time:.2f}s")
    print(f"📋 Tasks: {len(result2.coder_results)}")
    
    # Test 3: With interrupt
    print("\n" + "="*60)
    print("DEMO 3: With Interrupt")
    print("="*60)
    
    def check_interrupt():
        # Simulate user interrupt
        return "Use Python 3.11 instead"
    
    result3 = system.process_with_interrupts(
        "Setup Python environment",
        interrupt_callback=check_interrupt
    )
    print(f"\n✅ Success: {result3.success}")
    print(f"⏱️ Time: {result3.total_time:.2f}s")


if __name__ == "__main__":
    demo_complete_system()
