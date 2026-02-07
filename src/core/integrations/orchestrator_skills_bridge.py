#!/usr/bin/env python3
"""
Orchestrator ↔ Skills Integration Bridge
Connects Orchestrator with Skills System for intelligent skill selection and execution
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SkillExecution:
    """Skill execution record"""
    skill_id: str
    skill_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    tokens_used: int
    success: bool
    error: Optional[str] = None


class OrchestratorSkillsBridge:
    """
    Bridges Orchestrator and Skills System
    Intelligently selects and executes skills based on task requirements
    """
    
    def __init__(self, orchestrator, skills_system):
        """
        Initialize bridge
        
        Args:
            orchestrator: Orchestrator instance
            skills_system: Skills system instance
        """
        self.orchestrator = orchestrator
        self.skills = skills_system
        self.skill_cache = {}
        self.execution_log = []
        self.skill_performance = {}
    
    async def execute_step_with_skills(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute orchestrator step using appropriate skills
        
        Args:
            step: Orchestrator step
            context: Execution context
        
        Returns:
            Step execution result
        """
        # Analyze step to determine required skills
        required_skills = await self._analyze_step(step, context)
        
        # Select best skills
        selected_skills = await self._select_skills(required_skills, context)
        
        if not selected_skills:
            return {
                'status': 'error',
                'message': 'No suitable skills found',
                'step': step
            }
        
        # Execute skills in sequence
        result = await self._execute_skills(selected_skills, step, context)
        
        # Log execution
        await self._log_execution(step, selected_skills, result)
        
        return result
    
    async def _analyze_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Analyze step to determine required skills"""
        step_type = step.get('type', 'unknown')
        step_description = step.get('description', '')
        
        # Map step types to skills
        skill_map = {
            'code_generation': ['cpcg', 'code_generator', 'template_engine'],
            'code_review': ['mvp', 'code_reviewer', 'quality_checker'],
            'testing': ['test_generator', 'test_runner', 'coverage_analyzer'],
            'deployment': ['deployer', 'docker_builder', 'ci_cd_runner'],
            'documentation': ['doc_generator', 'markdown_writer'],
            'analysis': ['analyzer', 'pattern_detector', 'complexity_analyzer'],
            'optimization': ['optimizer', 'ccf', 'performance_tuner'],
            'security': ['security_scanner', 'egfv', 'vulnerability_checker'],
            'debugging': ['debugger', 'error_analyzer', 'log_parser'],
            'search': ['search_engine', 'semantic_search', 'rag_retriever']
        }
        
        return skill_map.get(step_type, ['generic_executor'])
    
    async def _select_skills(
        self,
        required_skills: List[str],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Select best skills based on performance history"""
        selected = []
        
        for skill_name in required_skills:
            # Get skill from system
            skill = await self.skills.get_skill(skill_name)
            if not skill:
                continue
            
            # Get performance metrics
            performance = self.skill_performance.get(skill_name, {
                'success_rate': 1.0,
                'avg_time': 0,
                'avg_tokens': 0
            })
            
            # Add performance score
            skill['performance_score'] = performance.get('success_rate', 1.0)
            selected.append(skill)
        
        # Sort by performance
        selected.sort(key=lambda s: s.get('performance_score', 0), reverse=True)
        
        return selected
    
    async def _execute_skills(
        self,
        skills: List[Dict[str, Any]],
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute selected skills"""
        results = []
        combined_output = {}
        total_tokens = 0
        
        for skill in skills:
            try:
                # Prepare skill input
                skill_input = {
                    **step.get('input', {}),
                    **context
                }
                
                # Execute skill
                start_time = datetime.now()
                skill_output = await self.skills.execute_skill(
                    skill.get('id'),
                    skill_input
                )
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Record execution
                execution = SkillExecution(
                    skill_id=skill.get('id'),
                    skill_name=skill.get('name'),
                    input_data=skill_input,
                    output_data=skill_output,
                    execution_time=execution_time,
                    tokens_used=skill_output.get('tokens_used', 0),
                    success=skill_output.get('success', False)
                )
                
                results.append(execution)
                combined_output.update(skill_output.get('data', {}))
                total_tokens += execution.tokens_used
                
                # Update performance metrics
                await self._update_performance(execution)
                
            except Exception as e:
                print(f"❌ Skill execution failed: {e}")
                results.append(SkillExecution(
                    skill_id=skill.get('id'),
                    skill_name=skill.get('name'),
                    input_data=step.get('input', {}),
                    output_data={},
                    execution_time=0,
                    tokens_used=0,
                    success=False,
                    error=str(e)
                ))
        
        return {
            'status': 'success' if any(r.success for r in results) else 'failed',
            'executions': results,
            'combined_output': combined_output,
            'total_tokens': total_tokens,
            'step': step
        }
    
    async def _log_execution(
        self,
        step: Dict[str, Any],
        skills: List[Dict[str, Any]],
        result: Dict[str, Any]
    ):
        """Log skill execution"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step.get('description', 'unknown'),
            'skills_used': [s.get('name') for s in skills],
            'status': result.get('status'),
            'total_tokens': result.get('total_tokens', 0)
        }
        
        self.execution_log.append(log_entry)
        if len(self.execution_log) > 10000:
            self.execution_log = self.execution_log[-10000:]
    
    async def _update_performance(self, execution: SkillExecution):
        """Update skill performance metrics"""
        skill_name = execution.skill_name
        
        if skill_name not in self.skill_performance:
            self.skill_performance[skill_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'total_time': 0,
                'total_tokens': 0,
                'success_rate': 0,
                'avg_time': 0,
                'avg_tokens': 0
            }
        
        perf = self.skill_performance[skill_name]
        perf['total_executions'] += 1
        if execution.success:
            perf['successful_executions'] += 1
        perf['total_time'] += execution.execution_time
        perf['total_tokens'] += execution.tokens_used
        
        # Calculate averages
        perf['success_rate'] = (
            perf['successful_executions'] / perf['total_executions']
        )
        perf['avg_time'] = perf['total_time'] / perf['total_executions']
        perf['avg_tokens'] = perf['total_tokens'] / perf['total_executions']
    
    def get_skill_performance(self) -> Dict[str, Any]:
        """Get all skill performance metrics"""
        return self.skill_performance
    
    def get_execution_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution log"""
        return self.execution_log[-limit:]
    
    async def recommend_skills(
        self,
        task_description: str
    ) -> List[Dict[str, Any]]:
        """Recommend skills for a task"""
        try:
            # Analyze task
            required_skills = await self._analyze_step(
                {'description': task_description},
                {}
            )
            
            # Get skill details
            recommendations = []
            for skill_name in required_skills:
                skill = await self.skills.get_skill(skill_name)
                if skill:
                    perf = self.skill_performance.get(skill_name, {})
                    skill['performance'] = perf
                    recommendations.append(skill)
            
            return recommendations
        except Exception as e:
            print(f"⚠️ Failed to recommend skills: {e}")
            return []


# Integration helper
async def integrate_orchestrator_skills(
    orchestrator,
    skills_system
) -> OrchestratorSkillsBridge:
    """Create and initialize Orchestrator-Skills bridge"""
    bridge = OrchestratorSkillsBridge(orchestrator, skills_system)
    print("✅ Orchestrator ↔ Skills bridge initialized")
    return bridge


# Example usage
if __name__ == "__main__":
    print("Orchestrator ↔ Skills Integration Bridge")
    print("This module connects Orchestrator and Skills systems")
