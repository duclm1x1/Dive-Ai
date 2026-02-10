#!/usr/bin/env python3
"""
Dive Memory - 2-File System

Simplified memory structure: Each project has exactly 2 files:
1. {PROJECT}_FULL.md - All knowledge about the project
2. {PROJECT}_CRITERIA.md - How to work with it (tools, actions, best practices)

Auto-detects project and maintains separate 2-file sets.
"""

import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import re


class DiveMemory2FileSystem:
    """
    2-File Memory System for Projects
    
    Each project gets exactly 2 files:
    - {PROJECT}_FULL.md: Complete knowledge
    - {PROJECT}_CRITERIA.md: Execution guidelines
    """
    
    def __init__(self, memory_root: Optional[Path] = None):
        """
        Initialize 2-file system
        
        Args:
            memory_root: Root directory for memory files
        """
        if memory_root is None:
            memory_root = Path(__file__).parent.parent / "memory"
        
        self.memory_root = Path(memory_root)
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        # Current project context
        self.current_project = None
        self.loaded_projects = {}
    
    def detect_project(self, context: str) -> str:
        """
        Auto-detect project from context
        
        Args:
            context: User request or task description
            
        Returns:
            Project name (normalized)
        """
        # Common project patterns
        patterns = [
            r"(?:working on|project|building|developing)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:project|app|system)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                return self._normalize_project_name(project_name)
        
        # Default to current working directory name or "default"
        cwd = Path.cwd().name
        if cwd and cwd != "Dive-Ai":
            return self._normalize_project_name(cwd)
        
        return "dive-ai"  # Default project
    
    def _normalize_project_name(self, name: str) -> str:
        """Normalize project name to kebab-case"""
        # Convert to lowercase and replace spaces with hyphens
        normalized = name.lower().strip()
        normalized = re.sub(r'\s+', '-', normalized)
        normalized = re.sub(r'[^a-z0-9-]', '', normalized)
        return normalized
    
    def get_project_files(self, project: str) -> Dict[str, Path]:
        """
        Get the 2 files for a project
        
        Args:
            project: Project name
            
        Returns:
            Dict with 'full' and 'criteria' file paths
        """
        project_upper = project.upper().replace('-', '_')
        
        return {
            'full': self.memory_root / f"{project_upper}_FULL.md",
            'criteria': self.memory_root / f"{project_upper}_CRITERIA.md"
        }
    
    def load_project(self, project: str) -> Dict[str, str]:
        """
        Load both files for a project
        
        Args:
            project: Project name
            
        Returns:
            Dict with 'full' and 'criteria' content
        """
        files = self.get_project_files(project)
        
        content = {
            'full': '',
            'criteria': ''
        }
        
        # Load FULL file
        if files['full'].exists():
            content['full'] = files['full'].read_text()
            print(f"   📄 Loaded {files['full'].name} ({len(content['full'])} chars)")
        else:
            print(f"   ⚠️  {files['full'].name} not found (will be created)")
        
        # Load CRITERIA file
        if files['criteria'].exists():
            content['criteria'] = files['criteria'].read_text()
            print(f"   📋 Loaded {files['criteria'].name} ({len(content['criteria'])} chars)")
        else:
            print(f"   ⚠️  {files['criteria'].name} not found (will be created)")
        
        # Cache loaded content
        self.loaded_projects[project] = content
        self.current_project = project
        
        return content
    
    def save_full_knowledge(self, project: str, content: str, append: bool = False):
        """
        Save to FULL file (complete knowledge)
        
        Args:
            project: Project name
            content: Content to save
            append: Whether to append or overwrite
        """
        files = self.get_project_files(project)
        full_file = files['full']
        
        if append and full_file.exists():
            existing = full_file.read_text()
            content = f"{existing}\n\n---\n\n{content}"
        
        full_file.write_text(content)
        print(f"   💾 Saved to {full_file.name}")
        
        # Update cache
        if project in self.loaded_projects:
            self.loaded_projects[project]['full'] = content
    
    def save_criteria(self, project: str, content: str, append: bool = False):
        """
        Save to CRITERIA file (execution guidelines)
        
        Args:
            project: Project name
            content: Content to save
            append: Whether to append or overwrite
        """
        files = self.get_project_files(project)
        criteria_file = files['criteria']
        
        if append and criteria_file.exists():
            existing = criteria_file.read_text()
            content = f"{existing}\n\n---\n\n{content}"
        
        criteria_file.write_text(content)
        print(f"   💾 Saved to {criteria_file.name}")
        
        # Update cache
        if project in self.loaded_projects:
            self.loaded_projects[project]['criteria'] = content
    
    def create_project_full_template(self, project: str, description: str = "") -> str:
        """
        Create template for FULL file
        
        Args:
            project: Project name
            description: Project description
            
        Returns:
            Template content
        """
        project_title = project.replace('-', ' ').title()
        
        template = f"""# {project_title} - Complete Knowledge

**Project**: {project_title}  
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Type**: Full Documentation

---

## Overview

{description if description else f"Complete knowledge base for {project_title} project."}

---

## What It Is

[Describe what this project is]

---

## How It Works

[Describe how the project works]

### Architecture

[System architecture]

### Components

[Key components]

### Data Flow

[How data flows through the system]

---

## Features

[List of features]

---

## Technical Details

### Technology Stack

[Technologies used]

### Dependencies

[Key dependencies]

### Configuration

[Configuration details]

---

## History

### Decisions Made

[Key decisions and rationale]

### Changes

[Major changes and updates]

---

## Research & Context

[Research findings, references, related work]

---

## Notes

[Additional notes and observations]

---

*Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return template
    
    def create_project_criteria_template(self, project: str) -> str:
        """
        Create template for CRITERIA file
        
        Args:
            project: Project name
            
        Returns:
            Template content
        """
        project_title = project.replace('-', ' ').title()
        
        template = f"""# {project_title} - Execution Guidelines

**Project**: {project_title}  
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Type**: Criteria & Best Practices

---

## Acceptance Criteria

### Must Have
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Should Have
- [ ] Criterion 4
- [ ] Criterion 5

### Nice to Have
- [ ] Criterion 6

---

## Tools & Technologies

### Required Tools
1. **Tool 1**: Purpose and usage
2. **Tool 2**: Purpose and usage
3. **Tool 3**: Purpose and usage

### Recommended Tools
1. **Tool A**: When to use
2. **Tool B**: When to use

---

## Best Practices

### Code Quality
- Practice 1
- Practice 2
- Practice 3

### Testing
- Test approach 1
- Test approach 2

### Documentation
- Documentation standard 1
- Documentation standard 2

---

## Workflows

### Development Workflow
1. Step 1
2. Step 2
3. Step 3

### Deployment Workflow
1. Step 1
2. Step 2
3. Step 3

---

## Right Actions

### When Starting
- Action 1
- Action 2
- Action 3

### When Implementing
- Action 1
- Action 2
- Action 3

### When Testing
- Action 1
- Action 2
- Action 3

### When Deploying
- Action 1
- Action 2
- Action 3

---

## Common Pitfalls

### Avoid
- Pitfall 1: Why and how to avoid
- Pitfall 2: Why and how to avoid
- Pitfall 3: Why and how to avoid

---

## Checklists

### Pre-Development Checklist
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

### Pre-Deployment Checklist
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

---

## References

### Documentation
- Link 1
- Link 2

### Examples
- Example 1
- Example 2

---

*Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return template
    
    def initialize_project(self, project: str, description: str = ""):
        """
        Initialize a new project with 2 template files
        
        Args:
            project: Project name
            description: Project description
        """
        print(f"\n🆕 Initializing project: {project}")
        
        files = self.get_project_files(project)
        
        # Create FULL file if not exists
        if not files['full'].exists():
            template = self.create_project_full_template(project, description)
            files['full'].write_text(template)
            print(f"   ✅ Created {files['full'].name}")
        else:
            print(f"   ℹ️  {files['full'].name} already exists")
        
        # Create CRITERIA file if not exists
        if not files['criteria'].exists():
            template = self.create_project_criteria_template(project)
            files['criteria'].write_text(template)
            print(f"   ✅ Created {files['criteria'].name}")
        else:
            print(f"   ℹ️  {files['criteria'].name} already exists")
        
        # Load the project
        self.load_project(project)
    
    def list_projects(self) -> List[str]:
        """
        List all projects in memory
        
        Returns:
            List of project names
        """
        projects = set()
        
        for file in self.memory_root.glob("*_FULL.md"):
            project = file.stem.replace('_FULL', '').lower().replace('_', '-')
            projects.add(project)
        
        return sorted(list(projects))
    
    def get_context_for_task(self, task: str, project: Optional[str] = None) -> str:
        """
        Get relevant context for a task
        
        Args:
            task: Task description
            project: Project name (auto-detected if not provided)
            
        Returns:
            Combined context from both files
        """
        if project is None:
            project = self.detect_project(task)
        
        print(f"\n🔍 Getting context for task in project: {project}")
        
        # Load project if not already loaded
        if project not in self.loaded_projects:
            self.load_project(project)
        
        content = self.loaded_projects.get(project, {'full': '', 'criteria': ''})
        
        context = f"""# Context for: {task}

## Project: {project.replace('-', ' ').title()}

---

## FULL KNOWLEDGE

{content['full']}

---

## EXECUTION GUIDELINES

{content['criteria']}

---

*Context compiled: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        return context


def main():
    """Demo: 2-File System"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  📁 Dive Memory - 2-File System Demo                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    memory = DiveMemory2FileSystem()
    
    # Initialize Dive AI project
    print("\n" + "="*80)
    memory.initialize_project("dive-ai", "AI development platform with unified brain")
    
    # Initialize Calo Track project
    print("\n" + "="*80)
    memory.initialize_project("calo-track", "Calorie tracking application")
    
    # List all projects
    print("\n" + "="*80)
    print("📂 All Projects:")
    projects = memory.list_projects()
    for i, proj in enumerate(projects, 1):
        print(f"   {i}. {proj}")
    
    # Auto-detect project from task
    print("\n" + "="*80)
    task = "Working on Calo Track: Implement meal logging feature"
    detected = memory.detect_project(task)
    print(f"🔍 Task: {task}")
    print(f"   Detected project: {detected}")
    
    # Get context for task
    print("\n" + "="*80)
    context = memory.get_context_for_task(task)
    print(f"📊 Context length: {len(context)} characters")
    print(f"   Includes: FULL knowledge + CRITERIA guidelines")
    
    print("\n" + "="*80)
    print("✅ 2-File System Demo Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
