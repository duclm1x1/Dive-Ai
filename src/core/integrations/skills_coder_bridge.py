#!/usr/bin/env python3
"""
Skills ↔ Coder Integration Bridge
Connects Skills System with Coder for intelligent code generation and skill composition
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CodeGeneration:
    """Code generation record"""
    skill_id: str
    code: str
    language: str
    quality_score: float
    tokens_used: int
    execution_time: float


class SkillsCoderBridge:
    """
    Bridges Skills System and Coder
    Uses skills to enhance code generation and composition
    """
    
    def __init__(self, skills_system, coder):
        """
        Initialize bridge
        
        Args:
            skills_system: Skills system instance
            coder: Coder instance
        """
        self.skills = skills_system
        self.coder = coder
        self.code_cache = {}
        self.generation_history = []
        self.skill_composition_cache = {}
    
    async def generate_code_with_skills(
        self,
        task: str,
        language: str = 'python',
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate code using skills composition
        
        Args:
            task: Code generation task
            language: Programming language
            context: Optional context
        
        Returns:
            Generated code with metadata
        """
        # Find relevant skills
        relevant_skills = await self._find_relevant_skills(task, language)
        
        # Compose skills for code generation
        skill_composition = await self._compose_skills(
            relevant_skills,
            task,
            language
        )
        
        # Generate code using composition
        code_result = await self.coder.generate(
            task,
            language=language,
            skills=skill_composition,
            context=context
        )
        
        # Enhance code with skills
        enhanced_code = await self._enhance_code(
            code_result.get('code', ''),
            relevant_skills,
            language
        )
        
        # Record generation
        generation = CodeGeneration(
            skill_id=','.join([s.get('id') for s in relevant_skills]),
            code=enhanced_code,
            language=language,
            quality_score=code_result.get('quality_score', 0),
            tokens_used=code_result.get('tokens_used', 0),
            execution_time=code_result.get('execution_time', 0)
        )
        
        self.generation_history.append(generation)
        
        return {
            'code': enhanced_code,
            'language': language,
            'quality_score': generation.quality_score,
            'tokens_used': generation.tokens_used,
            'skills_used': [s.get('name') for s in relevant_skills],
            'execution_time': generation.execution_time
        }
    
    async def _find_relevant_skills(
        self,
        task: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Find skills relevant to code generation task"""
        try:
            # Query skills by task and language
            skills = await self.skills.search_skills(
                query=task,
                language=language,
                limit=5
            )
            
            return skills
        except Exception as e:
            print(f"⚠️ Failed to find relevant skills: {e}")
            return []
    
    async def _compose_skills(
        self,
        skills: List[Dict[str, Any]],
        task: str,
        language: str
    ) -> Dict[str, Any]:
        """Compose skills for code generation"""
        composition = {
            'primary_skill': None,
            'supporting_skills': [],
            'skill_chain': []
        }
        
        if not skills:
            return composition
        
        # Primary skill (highest relevance)
        composition['primary_skill'] = skills[0]
        
        # Supporting skills
        composition['supporting_skills'] = skills[1:]
        
        # Build skill chain for execution
        for skill in skills:
            composition['skill_chain'].append({
                'skill_id': skill.get('id'),
                'skill_name': skill.get('name'),
                'input_mapping': skill.get('input_mapping', {}),
                'output_mapping': skill.get('output_mapping', {})
            })
        
        # Cache composition
        cache_key = f"{task}:{language}"
        self.skill_composition_cache[cache_key] = composition
        
        return composition
    
    async def _enhance_code(
        self,
        code: str,
        skills: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Enhance generated code with skills"""
        enhanced = code
        
        for skill in skills:
            try:
                # Apply skill enhancement
                enhancement = await self.skills.apply_enhancement(
                    skill.get('id'),
                    code,
                    language
                )
                
                if enhancement:
                    enhanced = enhancement
            except Exception as e:
                print(f"⚠️ Skill enhancement failed: {e}")
        
        return enhanced
    
    async def review_code_with_skills(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Review code using skills"""
        try:
            # Find review skills
            review_skills = await self.skills.search_skills(
                query='code review',
                language=language,
                limit=3
            )
            
            # Execute reviews
            reviews = []
            for skill in review_skills:
                review = await self.skills.execute_skill(
                    skill.get('id'),
                    {'code': code, 'language': language}
                )
                reviews.append(review)
            
            # Aggregate reviews
            aggregated = {
                'code_quality': 0,
                'issues': [],
                'suggestions': [],
                'security_score': 0,
                'performance_score': 0
            }
            
            for review in reviews:
                if 'quality' in review:
                    aggregated['code_quality'] += review['quality']
                if 'issues' in review:
                    aggregated['issues'].extend(review['issues'])
                if 'suggestions' in review:
                    aggregated['suggestions'].extend(review['suggestions'])
                if 'security_score' in review:
                    aggregated['security_score'] += review['security_score']
                if 'performance_score' in review:
                    aggregated['performance_score'] += review['performance_score']
            
            # Average scores
            if review_skills:
                aggregated['code_quality'] /= len(review_skills)
                aggregated['security_score'] /= len(review_skills)
                aggregated['performance_score'] /= len(review_skills)
            
            return aggregated
        except Exception as e:
            print(f"⚠️ Code review failed: {e}")
            return {}
    
    async def optimize_code_with_skills(
        self,
        code: str,
        language: str,
        optimization_type: str = 'performance'
    ) -> str:
        """Optimize code using skills"""
        try:
            # Find optimization skills
            opt_skills = await self.skills.search_skills(
                query=f'code optimization {optimization_type}',
                language=language,
                limit=3
            )
            
            optimized = code
            
            for skill in opt_skills:
                result = await self.skills.execute_skill(
                    skill.get('id'),
                    {
                        'code': optimized,
                        'language': language,
                        'optimization_type': optimization_type
                    }
                )
                
                if result.get('optimized_code'):
                    optimized = result['optimized_code']
            
            return optimized
        except Exception as e:
            print(f"⚠️ Code optimization failed: {e}")
            return code
    
    def get_generation_history(self, limit: int = 50) -> List[CodeGeneration]:
        """Get recent code generation history"""
        return self.generation_history[-limit:]
    
    def get_skill_composition_cache(self) -> Dict[str, Any]:
        """Get cached skill compositions"""
        return self.skill_composition_cache
    
    async def recommend_skills_for_task(
        self,
        task: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Recommend skills for a code generation task"""
        try:
            skills = await self._find_relevant_skills(task, language)
            
            recommendations = []
            for skill in skills:
                recommendations.append({
                    'id': skill.get('id'),
                    'name': skill.get('name'),
                    'description': skill.get('description'),
                    'relevance_score': skill.get('relevance_score', 0),
                    'language': language
                })
            
            return recommendations
        except Exception as e:
            print(f"⚠️ Failed to recommend skills: {e}")
            return []


# Integration helper
async def integrate_skills_coder(
    skills_system,
    coder
) -> SkillsCoderBridge:
    """Create and initialize Skills-Coder bridge"""
    bridge = SkillsCoderBridge(skills_system, coder)
    print("✅ Skills ↔ Coder bridge initialized")
    return bridge


# Example usage
if __name__ == "__main__":
    print("Skills ↔ Coder Integration Bridge")
    print("This module connects Skills and Coder systems")
