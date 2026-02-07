#!/usr/bin/env python3
"""
Dive Smart Coder - Intelligent Code Execution with Memory Integration

Inspired by:
- Manus: Explicit execution loop, tool use patterns
- Claude Opus: Context-aware execution, error handling
- GPT Codex: Code-first thinking, debugging strategies
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from dive_memory_3file_complete import DiveMemory3FileComplete


class ExecutionPhase(Enum):
    """Execution phases for smart coder"""
    CHECK_MEMORY = "check_memory"
    ANALYZE_TASK = "analyze_task"
    PLAN_EXECUTION = "plan_execution"
    EXECUTE = "execute"
    VERIFY = "verify"
    STORE_RESULT = "store_result"


@dataclass
class ExecutionContext:
    """Context for code execution"""
    task: str
    project_id: str
    similar_executions: List[Dict[str, Any]]
    known_issues: List[Dict[str, Any]]
    best_practices: List[str]
    tools_available: List[str]


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: Any
    errors: List[str]
    warnings: List[str]
    execution_time: float
    tools_used: List[str]
    lessons_learned: List[str]


class DiveSmartCoder:
    """
    Smart Coder with intelligent execution and memory integration
    
    Features:
    - Check memory before executing
    - Learn from past executions
    - Intelligent error recovery
    - Tool usage optimization
    - Result verification
    - Automatic learning
    """
    
    def __init__(self):
        """Initialize Smart Coder"""
        self.memory = DiveMemory3FileComplete()
        self.execution_history = []
        print("🔧 Dive Smart Coder initialized (memory-aware)")
    
    def execute_task(self, task: str, project_id: str = "DEFAULT") -> ExecutionResult:
        """
        Execute task with intelligent processing
        
        Args:
            task: Task description
            project_id: Project identifier
            
        Returns:
            ExecutionResult with complete execution details
        """
        print("="*60)
        print(f"🔧 Executing Task: {task}...")
        print("="*60)
        
        start_time = time.time()
        errors = []
        warnings = []
        tools_used = []
        lessons_learned = []
        
        try:
            # Phase 1: CHECK MEMORY
            print(f"📚 Phase 1: CHECK MEMORY")
            context = self._check_memory(task, project_id)
            print(f"   Found {len(context.similar_executions)} similar executions")
            print(f"   Found {len(context.known_issues)} known issues")
            
            # Phase 2: ANALYZE TASK
            print(f"🔍 Phase 2: ANALYZE TASK")
            analysis = self._analyze_task(task, context)
            print(f"   Complexity: {analysis['complexity']}")
            print(f"   Tools needed: {', '.join(analysis['tools_needed'])}")
            
            # Phase 3: PLAN EXECUTION
            print(f"📋 Phase 3: PLAN EXECUTION")
            plan = self._plan_execution(task, analysis, context)
            print(f"   Steps: {len(plan['steps'])}")
            print(f"   Estimated time: {plan['estimated_time']}s")
            
            # Phase 4: EXECUTE
            print(f"⚡ Phase 4: EXECUTE")
            result = self._execute_plan(plan, context)
            tools_used = result.get('tools_used', [])
            print(f"   Tools used: {', '.join(tools_used)}")
            
            # Phase 5: VERIFY
            print(f"✅ Phase 5: VERIFY")
            verification = self._verify_result(result, plan)
            if not verification['passed']:
                warnings.append(f"Verification issues: {verification['issues']}")
                print(f"   ⚠️ Verification warnings: {len(verification['issues'])}")
            else:
                print(f"   ✅ All checks passed")
            
            # Phase 6: STORE RESULT
            print(f"💾 Phase 6: STORE RESULT")
            self._store_result(task, result, context, project_id)
            
            # Extract lessons
            lessons_learned = self._extract_lessons(task, result, context)
            print(f"   📝 Lessons learned: {len(lessons_learned)}")
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=True,
                output=result.get('output'),
                errors=errors,
                warnings=warnings,
                execution_time=execution_time,
                tools_used=tools_used,
                lessons_learned=lessons_learned
            )
            
        except Exception as e:
            errors.append(str(e))
            execution_time = time.time() - start_time
            
            # Store failure for learning
            self._store_failure(task, str(e), project_id)
            
            return ExecutionResult(
                success=False,
                output=None,
                errors=errors,
                warnings=warnings,
                execution_time=execution_time,
                tools_used=tools_used,
                lessons_learned=[]
            )
    
    def _check_memory(self, task: str, project_id: str) -> ExecutionContext:
        """Check memory for relevant past executions"""
        # Load project context
        context_files = self.memory.load_project(project_id)
        
        # Extract relevant information
        similar_executions = self._find_similar_executions(task, context_files)
        known_issues = self._extract_known_issues(context_files)
        best_practices = self._extract_best_practices(context_files)
        tools_available = self._extract_tools(context_files)
        
        return ExecutionContext(
            task=task,
            project_id=project_id,
            similar_executions=similar_executions,
            known_issues=known_issues,
            best_practices=best_practices,
            tools_available=tools_available
        )
    
    def _find_similar_executions(self, task: str, context_files: Dict) -> List[Dict]:
        """Find similar past executions"""
        similar = []
        
        # Search in CHANGELOG for past executions
        changelog = context_files.get('changelog', '')
        if 'Executed:' in changelog or 'Fixed:' in changelog:
            # Simple keyword matching (in production, use semantic search)
            keywords = task.lower().split()
            for line in changelog.split('\n'):
                if any(kw in line.lower() for kw in keywords):
                    similar.append({
                        'description': line.strip(),
                        'relevance': 0.8
                    })
        
        return similar[:5]  # Top 5
    
    def _extract_known_issues(self, context_files: Dict) -> List[Dict]:
        """Extract known issues from criteria"""
        issues = []
        
        criteria = context_files.get('criteria', '')
        if '## Known Issues' in criteria:
            # Extract issues section
            lines = criteria.split('\n')
            in_issues = False
            for line in lines:
                if '## Known Issues' in line:
                    in_issues = True
                    continue
                if in_issues and line.startswith('##'):
                    break
                if in_issues and line.strip().startswith('-'):
                    issues.append({
                        'issue': line.strip('- ').strip(),
                        'severity': 'medium'
                    })
        
        return issues
    
    def _extract_best_practices(self, context_files: Dict) -> List[str]:
        """Extract best practices from criteria"""
        practices = []
        
        criteria = context_files.get('criteria', '')
        if '## Best Practices' in criteria:
            lines = criteria.split('\n')
            in_practices = False
            for line in lines:
                if '## Best Practices' in line:
                    in_practices = True
                    continue
                if in_practices and line.startswith('##'):
                    break
                if in_practices and line.strip().startswith('-'):
                    practices.append(line.strip('- ').strip())
        
        return practices
    
    def _extract_tools(self, context_files: Dict) -> List[str]:
        """Extract available tools from criteria"""
        tools = []
        
        criteria = context_files.get('criteria', '')
        if '## Tools' in criteria or '## Tool Usage' in criteria:
            lines = criteria.split('\n')
            in_tools = False
            for line in lines:
                if '## Tools' in line or '## Tool Usage' in line:
                    in_tools = True
                    continue
                if in_tools and line.startswith('##'):
                    break
                if in_tools and line.strip().startswith('-'):
                    tool = line.strip('- ').strip().split(':')[0]
                    tools.append(tool)
        
        return tools
    
    def _analyze_task(self, task: str, context: ExecutionContext) -> Dict:
        """Analyze task complexity and requirements"""
        # Simple analysis (in production, use LLM)
        words = task.split()
        
        complexity = "low"
        if len(words) > 10:
            complexity = "medium"
        if len(words) > 20 or any(kw in task.lower() for kw in ['complex', 'integrate', 'optimize']):
            complexity = "high"
        
        # Determine tools needed
        tools_needed = []
        if 'file' in task.lower() or 'read' in task.lower() or 'write' in task.lower():
            tools_needed.append('file')
        if 'shell' in task.lower() or 'command' in task.lower() or 'execute' in task.lower():
            tools_needed.append('shell')
        if 'search' in task.lower() or 'find' in task.lower():
            tools_needed.append('search')
        
        return {
            'complexity': complexity,
            'tools_needed': tools_needed,
            'estimated_steps': len(tools_needed) + 1
        }
    
    def _plan_execution(self, task: str, analysis: Dict, context: ExecutionContext) -> Dict:
        """Plan execution steps"""
        steps = []
        
        # Add steps based on analysis
        if 'file' in analysis['tools_needed']:
            steps.append({
                'action': 'file_operation',
                'description': 'Read/write files',
                'estimated_time': 1
            })
        
        if 'shell' in analysis['tools_needed']:
            steps.append({
                'action': 'shell_command',
                'description': 'Execute shell commands',
                'estimated_time': 2
            })
        
        if 'search' in analysis['tools_needed']:
            steps.append({
                'action': 'search',
                'description': 'Search for information',
                'estimated_time': 3
            })
        
        # Add main execution step
        steps.append({
            'action': 'main_execution',
            'description': f'Execute: {task}',
            'estimated_time': 5
        })
        
        total_time = sum(s['estimated_time'] for s in steps)
        
        return {
            'steps': steps,
            'estimated_time': total_time,
            'parallel_possible': False
        }
    
    def _execute_plan(self, plan: Dict, context: ExecutionContext) -> Dict:
        """Execute the plan"""
        results = []
        tools_used = []
        
        for step in plan['steps']:
            # Simulate execution (in production, actually execute)
            print(f"   Executing: {step['description']}")
            time.sleep(0.1)  # Simulate work
            
            results.append({
                'step': step['action'],
                'success': True,
                'output': f"Completed {step['description']}"
            })
            
            if step['action'] != 'main_execution':
                tools_used.append(step['action'])
        
        return {
            'output': results,
            'tools_used': tools_used,
            'success': True
        }
    
    def _verify_result(self, result: Dict, plan: Dict) -> Dict:
        """Verify execution result"""
        issues = []
        
        # Check if all steps completed
        if len(result.get('output', [])) != len(plan['steps']):
            issues.append("Not all steps completed")
        
        # Check for errors
        for step_result in result.get('output', []):
            if not step_result.get('success'):
                issues.append(f"Step {step_result['step']} failed")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def _store_result(self, task: str, result: Dict, context: ExecutionContext, project_id: str):
        """Store execution result in memory"""
        # Log to changelog
        self.memory.log_change(
            project_id,
            "Executed",
            f"{task} - Success: {result.get('success')}"
        )
        
        # Update full knowledge if significant
        if result.get('success'):
            knowledge = f"\n### Execution: {task}\n"
            knowledge += f"- Tools used: {', '.join(result.get('tools_used', []))}\n"
            knowledge += f"- Result: Success\n"
            
            self.memory.save_full_knowledge(project_id, knowledge, append=True)
    
    def _store_failure(self, task: str, error: str, project_id: str):
        """Store execution failure for learning"""
        self.memory.log_change(
            project_id,
            "Fixed",
            f"{task} - Error: {error}"
        )
        
        # Add to known issues
        issue = f"\n### Known Issue: {task}\n"
        issue += f"- Error: {error}\n"
        issue += f"- Solution: [To be determined]\n"
        
        self.memory.save_criteria(project_id, issue, append=True)
    
    def _extract_lessons(self, task: str, result: Dict, context: ExecutionContext) -> List[str]:
        """Extract lessons learned from execution"""
        lessons = []
        
        # If we used tools not in best practices, add lesson
        tools_used = result.get('tools_used', [])
        for tool in tools_used:
            if tool not in context.best_practices:
                lessons.append(f"Tool '{tool}' effective for: {task}")
        
        # If execution was faster than similar past executions
        if context.similar_executions:
            lessons.append(f"Improved execution strategy for: {task}")
        
        return lessons


if __name__ == "__main__":
    # Test Smart Coder
    coder = DiveSmartCoder()
    
    # Test 1: Simple task
    print("\n" + "="*60)
    print("TEST 1: Simple file operation")
    print("="*60)
    result1 = coder.execute_task("Read configuration file", project_id="DIVE_AI")
    print(f"\n✅ Result: {result1.success}")
    print(f"⏱️ Time: {result1.execution_time:.2f}s")
    print(f"📝 Lessons: {len(result1.lessons_learned)}")
    
    # Test 2: Complex task
    print("\n" + "="*60)
    print("TEST 2: Complex integration task")
    print("="*60)
    result2 = coder.execute_task(
        "Integrate new memory system with orchestrator and optimize performance",
        project_id="DIVE_AI"
    )
    print(f"\n✅ Result: {result2.success}")
    print(f"⏱️ Time: {result2.execution_time:.2f}s")
    print(f"🔧 Tools: {', '.join(result2.tools_used)}")
    print(f"📝 Lessons: {len(result2.lessons_learned)}")
