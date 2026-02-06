"""
Dive-Memory v2 - AI Persistent Project Memory
Base Skill for Dive AI V20

This skill provides persistent project memory through:
- Context injection from PROJECT.memory.md
- Knowledge management with .known.md files
- Skill auto-discovery based on intent
- Task management with acceptance criteria
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class DiveMemorySkill:
    """
    Dive-Memory v2 Base Skill
    
    Always-active skill that provides persistent project memory
    and context injection for AI agents.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize Dive-Memory skill
        
        Args:
            project_path: Path to project root (defaults to current directory)
        """
        self.project_path = Path(project_path or os.getcwd())
        self.memory_file = self.project_path / "PROJECT.memory.md"
        self.knowns_dir = self.project_path / "knowns"
        self.tasks_dir = self.project_path / "tasks"
        
    def is_active(self) -> bool:
        """
        Check if this skill should be active for the current project
        
        Returns:
            True if PROJECT.memory.md exists, False otherwise
        """
        return self.memory_file.exists()
    
    def load_memory(self) -> Optional[Dict[str, Any]]:
        """
        Load and parse PROJECT.memory.md
        
        Returns:
            Parsed memory dictionary or None if file doesn't exist
        """
        if not self.is_active():
            return None
        
        try:
            content = self.memory_file.read_text(encoding='utf-8')
            memory, markdown_body = self._parse_memory_file(content)
            return memory
        except Exception as e:
            print(f"[Dive-Memory] Error loading memory: {e}")
            return None
    
    def _parse_memory_file(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse PROJECT.memory.md with YAML front-matter
        
        Args:
            content: File content
            
        Returns:
            Tuple of (memory dict, markdown body)
        """
        # Extract YAML front-matter
        if not content.startswith('---'):
            raise ValueError("PROJECT.memory.md must start with YAML front-matter")
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError("Invalid PROJECT.memory.md format")
        
        yaml_content = parts[1].strip()
        markdown_body = parts[2].strip()
        
        # Parse YAML
        parsed = yaml.safe_load(yaml_content)
        
        # Normalize field names (support both snake_case and camelCase)
        memory = {
            'project_goal': parsed.get('project_goal') or parsed.get('projectGoal', ''),
            'persona': parsed.get('persona', ''),
            'always_on_skills': parsed.get('always_on_skills') or parsed.get('alwaysOnSkills', []),
            'behavioral_rules': parsed.get('behavioral_rules') or parsed.get('behavioralRules', []),
            'skill_triggers': parsed.get('skill_triggers') or parsed.get('skillTriggers', []),
            'dynamic_state': parsed.get('dynamic_state') or parsed.get('dynamicState', {}),
        }
        
        return memory, markdown_body
    
    def generate_meta_prompt(self, memory: Dict[str, Any]) -> str:
        """
        Generate meta-prompt from project memory
        
        Args:
            memory: Parsed memory dictionary
            
        Returns:
            Meta-prompt string for context injection
        """
        sections = []
        
        sections.append("[BEGIN PROJECT CONSTITUTION]")
        sections.append("")
        
        # Project Goal
        if memory.get('project_goal'):
            sections.append(f"Project Goal: {memory['project_goal']}")
            sections.append("")
        
        # AI Persona
        if memory.get('persona'):
            sections.append(f"AI Persona: {memory['persona']}")
            sections.append("")
        
        # Always-On Skills
        if memory.get('always_on_skills'):
            sections.append("Available Skills (Always Consider):")
            for skill in memory['always_on_skills']:
                name = skill.get('name', '')
                desc = skill.get('description', '')
                sections.append(f"  - {name}: {desc}")
            sections.append("")
        
        # Behavioral Rules
        if memory.get('behavioral_rules'):
            sections.append("Behavioral Rules (MUST Follow):")
            for idx, rule in enumerate(memory['behavioral_rules'], 1):
                sections.append(f"  {idx}. {rule}")
            sections.append("")
        
        # Dynamic State
        if memory.get('dynamic_state'):
            sections.append("Current Context:")
            for key, value in memory['dynamic_state'].items():
                sections.append(f"  - {key}: {value}")
            sections.append("")
        
        sections.append("[END PROJECT CONSTITUTION]")
        sections.append("")
        
        return "\n".join(sections)
    
    def match_skill_triggers(
        self, 
        user_prompt: str, 
        triggers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match user prompt against skill triggers
        
        Args:
            user_prompt: User's input prompt
            triggers: List of skill trigger configurations
            
        Returns:
            List of matched triggers with relevance scores
        """
        lower_prompt = user_prompt.lower()
        matches = []
        
        for trigger in triggers:
            relevance = 0
            intents = trigger.get('intent', [])
            
            for intent in intents:
                if intent.lower() in lower_prompt:
                    relevance += 1
            
            if relevance > 0:
                matches.append({
                    **trigger,
                    'relevance': relevance
                })
        
        # Sort by relevance (highest first)
        matches.sort(key=lambda x: x['relevance'], reverse=True)
        
        return matches
    
    def inject_context(self, user_prompt: str) -> Dict[str, Any]:
        """
        Inject project context into user prompt
        
        Args:
            user_prompt: Original user prompt
            
        Returns:
            Dictionary with:
                - final_prompt: Full prompt with context
                - meta_prompt: Generated meta-prompt
                - matched_triggers: List of matched skill triggers
                - suggestions: List of skill suggestions
        """
        memory = self.load_memory()
        
        if not memory:
            return {
                'final_prompt': user_prompt,
                'meta_prompt': '',
                'matched_triggers': [],
                'suggestions': []
            }
        
        # Generate meta-prompt
        meta_prompt = self.generate_meta_prompt(memory)
        
        # Match skill triggers
        triggers = memory.get('skill_triggers', [])
        matched_triggers = self.match_skill_triggers(user_prompt, triggers)
        
        # Generate suggestions
        suggestions = []
        for match in matched_triggers:
            skill = match.get('skill_to_suggest') or match.get('skill', '')
            prompt_template = match.get('suggestion_prompt') or match.get('promptTemplate', '')
            if skill and prompt_template:
                suggestions.append(f"[Skill Suggestion] {skill}: {prompt_template}")
        
        # Build final prompt
        final_sections = [meta_prompt]
        
        if suggestions:
            final_sections.append("[SKILL SUGGESTIONS]")
            final_sections.extend(suggestions)
            final_sections.append("")
        
        final_sections.append("[BEGIN USER REQUEST]")
        final_sections.append(user_prompt)
        final_sections.append("[END USER REQUEST]")
        
        final_prompt = "\n".join(final_sections)
        
        return {
            'final_prompt': final_prompt,
            'meta_prompt': meta_prompt,
            'matched_triggers': matched_triggers,
            'suggestions': suggestions
        }
    
    def update_dynamic_state(self, updates: Dict[str, Any]) -> bool:
        """
        Update dynamic state in PROJECT.memory.md
        
        Args:
            updates: Dictionary of state updates
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_active():
            return False
        
        try:
            content = self.memory_file.read_text(encoding='utf-8')
            memory, markdown_body = self._parse_memory_file(content)
            
            # Update dynamic state
            current_state = memory.get('dynamic_state', {})
            current_state.update(updates)
            memory['dynamic_state'] = current_state
            
            # Serialize back to file
            serialized = self._serialize_memory_file(memory, markdown_body)
            self.memory_file.write_text(serialized, encoding='utf-8')
            
            return True
        except Exception as e:
            print(f"[Dive-Memory] Error updating state: {e}")
            return False
    
    def _serialize_memory_file(self, memory: Dict[str, Any], markdown_body: str) -> str:
        """
        Serialize memory back to PROJECT.memory.md format
        
        Args:
            memory: Memory dictionary
            markdown_body: Markdown content
            
        Returns:
            Serialized file content
        """
        yaml_data = {
            'project_goal': memory.get('project_goal', ''),
            'persona': memory.get('persona', ''),
            'always_on_skills': memory.get('always_on_skills', []),
            'behavioral_rules': memory.get('behavioral_rules', []),
            'skill_triggers': memory.get('skill_triggers', []),
            'dynamic_state': memory.get('dynamic_state', {}),
        }
        
        yaml_string = yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True)
        
        return f"---\n{yaml_string}---\n\n{markdown_body}"
    
    def list_knowledge_docs(self) -> List[Dict[str, Any]]:
        """
        List all knowledge documents in the project
        
        Returns:
            List of knowledge document metadata
        """
        if not self.knowns_dir.exists():
            return []
        
        docs = []
        for file in self.knowns_dir.glob("*.known.md"):
            try:
                content = file.read_text(encoding='utf-8')
                metadata = self._extract_known_metadata(content)
                metadata['filename'] = file.name
                metadata['path'] = str(file)
                docs.append(metadata)
            except Exception as e:
                print(f"[Dive-Memory] Error reading {file}: {e}")
        
        return docs
    
    def _extract_known_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from .known.md file
        
        Args:
            content: File content
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'title': 'Untitled',
            'category': 'General',
            'tags': [],
        }
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                try:
                    parsed = yaml.safe_load(parts[1])
                    metadata.update(parsed)
                except:
                    pass
        
        return metadata
    
    def get_skill_info(self) -> Dict[str, Any]:
        """
        Get skill information for registry
        
        Returns:
            Skill metadata dictionary
        """
        return {
            'name': 'dive-memory-v2',
            'type': 'base',
            'always_active': True,
            'priority': 1,
            'capabilities': [
                'context_injection',
                'knowledge_management',
                'skill_discovery',
                'task_management'
            ],
            'description': 'Persistent project memory and context injection for AI agents',
            'version': '2.0.0'
        }


# Export for easy import
__all__ = ['DiveMemorySkill']


# CLI interface for testing
if __name__ == '__main__':
    import sys
    
    skill = DiveMemorySkill()
    
    if len(sys.argv) < 2:
        print("Usage: python skill.py <command> [args]")
        print("Commands:")
        print("  test - Test context injection")
        print("  info - Show skill info")
        print("  list - List knowledge documents")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'test':
        if not skill.is_active():
            print("PROJECT.memory.md not found in current directory")
            sys.exit(1)
        
        test_prompt = "I need to implement user authentication"
        result = skill.inject_context(test_prompt)
        
        print("=== Context Injection Test ===\n")
        print(result['final_prompt'])
        print("\n=== Matched Triggers ===")
        print(json.dumps(result['matched_triggers'], indent=2))
        
    elif command == 'info':
        info = skill.get_skill_info()
        print(json.dumps(info, indent=2))
        
    elif command == 'list':
        docs = skill.list_knowledge_docs()
        print(f"Found {len(docs)} knowledge documents:\n")
        for doc in docs:
            print(f"- {doc['title']} [{doc['category']}]")
            print(f"  {doc['filename']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
