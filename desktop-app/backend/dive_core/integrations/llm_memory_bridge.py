#!/usr/bin/env python3
"""
LLM ↔ Memory Integration Bridge
Connects LLM Connection with Memory System for seamless context management
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class MemoryContext:
    """Context from memory for LLM"""
    project_id: str
    episodic: List[Dict[str, Any]]  # Recent events
    semantic: List[Dict[str, Any]]  # Knowledge facts
    procedural: List[Dict[str, Any]]  # Skills/processes
    timestamp: str


class LLMMemoryBridge:
    """
    Bridges LLM Connection and Memory System
    Automatically enriches LLM prompts with relevant memory
    """
    
    def __init__(self, llm_client, memory_system):
        """
        Initialize bridge
        
        Args:
            llm_client: LLMClientThreeMode instance
            memory_system: MemorySystem instance
        """
        self.llm = llm_client
        self.memory = memory_system
        self.context_cache = {}
        self.interaction_history = []
    
    async def call_with_memory(
        self,
        prompt: str,
        project_id: str,
        model: Optional[str] = None,
        memory_limit: int = 5000  # tokens
    ) -> Dict[str, Any]:
        """
        Call LLM with automatic memory context injection
        
        Args:
            prompt: User prompt
            project_id: Project identifier
            model: LLM model (auto-select if None)
            memory_limit: Max tokens for memory context
        
        Returns:
            LLM response with memory metadata
        """
        # Retrieve relevant memory context
        memory_context = await self._get_memory_context(
            project_id,
            prompt,
            memory_limit
        )
        
        # Enrich prompt with memory
        enriched_prompt = self._enrich_prompt(prompt, memory_context)
        
        # Call LLM
        response = await self.llm.call(
            enriched_prompt,
            model=model,
            metadata={
                'project_id': project_id,
                'memory_context': memory_context.dict() if memory_context else None
            }
        )
        
        # Store interaction in memory
        await self._store_interaction(
            project_id,
            prompt,
            response,
            memory_context
        )
        
        return response
    
    async def _get_memory_context(
        self,
        project_id: str,
        prompt: str,
        token_limit: int
    ) -> Optional[MemoryContext]:
        """Retrieve relevant memory context for prompt"""
        try:
            # Get episodic memory (recent events)
            episodic = await self.memory.recall_episodic(
                project_id,
                limit=3,
                token_limit=int(token_limit * 0.3)
            )
            
            # Get semantic memory (knowledge)
            semantic = await self.memory.recall_semantic(
                project_id,
                query=prompt,
                limit=5,
                token_limit=int(token_limit * 0.4)
            )
            
            # Get procedural memory (skills)
            procedural = await self.memory.recall_procedural(
                project_id,
                query=prompt,
                limit=3,
                token_limit=int(token_limit * 0.3)
            )
            
            return MemoryContext(
                project_id=project_id,
                episodic=episodic,
                semantic=semantic,
                procedural=procedural,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"⚠️ Memory retrieval failed: {e}")
            return None
    
    def _enrich_prompt(
        self,
        prompt: str,
        context: Optional[MemoryContext]
    ) -> str:
        """Enrich prompt with memory context"""
        if not context:
            return prompt
        
        enriched = prompt
        
        # Add episodic context
        if context.episodic:
            episodic_str = "\n".join([
                f"- {e.get('description', str(e))}"
                for e in context.episodic
            ])
            enriched += f"\n\n## Recent Events:\n{episodic_str}"
        
        # Add semantic context
        if context.semantic:
            semantic_str = "\n".join([
                f"- {s.get('fact', str(s))}"
                for s in context.semantic
            ])
            enriched += f"\n\n## Known Facts:\n{semantic_str}"
        
        # Add procedural context
        if context.procedural:
            procedural_str = "\n".join([
                f"- {p.get('skill', str(p))}"
                for p in context.procedural
            ])
            enriched += f"\n\n## Available Skills:\n{procedural_str}"
        
        return enriched
    
    async def _store_interaction(
        self,
        project_id: str,
        prompt: str,
        response: Dict[str, Any],
        context: Optional[MemoryContext]
    ):
        """Store LLM interaction in memory"""
        try:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'response': response.get('response', ''),
                'model': response.get('model', 'unknown'),
                'tokens_used': response.get('tokens_used', 0),
                'memory_context_used': context is not None
            }
            
            # Store as episodic memory
            await self.memory.store_episodic(
                project_id,
                description=f"LLM call: {prompt[:50]}...",
                metadata=interaction
            )
            
            # Update interaction history
            self.interaction_history.append(interaction)
            if len(self.interaction_history) > 1000:
                self.interaction_history = self.interaction_history[-1000:]
        
        except Exception as e:
            print(f"⚠️ Failed to store interaction: {e}")
    
    async def batch_call_with_memory(
        self,
        prompts: List[str],
        project_id: str,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Call LLM multiple times with memory context
        
        Args:
            prompts: List of prompts
            project_id: Project identifier
            model: LLM model
        
        Returns:
            List of responses
        """
        responses = []
        for prompt in prompts:
            response = await self.call_with_memory(
                prompt,
                project_id,
                model
            )
            responses.append(response)
        
        return responses
    
    def get_interaction_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent interaction history"""
        return self.interaction_history[-limit:]
    
    async def clear_project_memory(self, project_id: str):
        """Clear all memory for a project"""
        try:
            await self.memory.clear_project(project_id)
            print(f"✅ Cleared memory for project: {project_id}")
        except Exception as e:
            print(f"❌ Failed to clear memory: {e}")


# Integration helper
async def integrate_llm_memory(llm_client, memory_system) -> LLMMemoryBridge:
    """Create and initialize LLM-Memory bridge"""
    bridge = LLMMemoryBridge(llm_client, memory_system)
    print("✅ LLM ↔ Memory bridge initialized")
    return bridge


# Example usage
if __name__ == "__main__":
    print("LLM ↔ Memory Integration Bridge")
    print("This module connects LLM and Memory systems")
