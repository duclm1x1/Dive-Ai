"""
📂 MULTI-PROJECT SUPPORT
Manage multiple codebases simultaneously with project-specific agent pools
"""

import os
import sys
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class ProjectStatus(Enum):
    """Project status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


@dataclass
class Project:
    """Project configuration"""
    project_id: str
    name: str
    path: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.ACTIVE
    allocated_agents: int = 50  # Default agent allocation
    preferred_models: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    priority: int = 3  # 1-5
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Runtime stats
    tasks_completed: int = 0
    total_cost: float = 0.0
    agent_pool: List[int] = field(default_factory=list)


@dataclass
class CrossProjectContext:
    """Shared context across projects"""
    shared_patterns: Dict[str, str] = field(default_factory=dict)
    common_utilities: Dict[str, str] = field(default_factory=dict)
    learned_solutions: Dict[str, str] = field(default_factory=dict)


class MultiProjectManager:
    """
    📂 Multi-Project Management System
    
    Features:
    - Manage multiple codebases
    - Project-specific agent pools
    - Resource allocation per project
    - Cross-project memory sharing
    - Workspace switching
    """
    
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.current_project: Optional[str] = None
        self.cross_context = CrossProjectContext()
        self.lock = threading.Lock()
        self.total_agents = 512
        
        print("📂 MultiProjectManager initialized")
    
    def add_project(self, name: str, path: str, description: str = "",
                   tech_stack: List[str] = None, priority: int = 3,
                   agent_allocation: int = None) -> Project:
        """Add a new project"""
        with self.lock:
            # Generate project ID
            project_id = f"proj-{len(self.projects) + 1:03d}"
            
            # Calculate agent allocation if not specified
            if agent_allocation is None:
                agent_allocation = self._calculate_allocation(priority)
            
            project = Project(
                project_id=project_id,
                name=name,
                path=path,
                description=description,
                tech_stack=tech_stack or [],
                priority=priority,
                allocated_agents=agent_allocation
            )
            
            # Detect tech stack if not provided
            if not project.tech_stack:
                project.tech_stack = self._detect_tech_stack(path)
            
            # Assign agent pool
            project.agent_pool = self._allocate_agents(agent_allocation)
            
            self.projects[project_id] = project
            
            # Set as current if first project
            if self.current_project is None:
                self.current_project = project_id
            
            print(f"   ✅ Added project: {name} ({agent_allocation} agents)")
            return project
    
    def remove_project(self, project_id: str) -> bool:
        """Remove project and free its agents"""
        with self.lock:
            if project_id in self.projects:
                project = self.projects[project_id]
                
                # Free agents back to pool
                # (In real implementation, reassign to other projects)
                
                del self.projects[project_id]
                
                if self.current_project == project_id:
                    self.current_project = next(iter(self.projects), None)
                
                return True
            return False
    
    def switch_project(self, project_id: str) -> bool:
        """Switch active project"""
        with self.lock:
            if project_id in self.projects:
                if self.current_project:
                    old_project = self.projects[self.current_project]
                    old_project.last_active = datetime.now()
                
                self.current_project = project_id
                self.projects[project_id].last_active = datetime.now()
                
                print(f"   🔄 Switched to: {self.projects[project_id].name}")
                return True
            return False
    
    def get_current_project(self) -> Optional[Project]:
        """Get current active project"""
        if self.current_project:
            return self.projects.get(self.current_project)
        return None
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def list_projects(self) -> List[Project]:
        """List all projects"""
        return list(self.projects.values())
    
    def _calculate_allocation(self, priority: int) -> int:
        """Calculate agent allocation based on priority"""
        # Higher priority = more agents
        base = 50
        priority_bonus = (priority - 1) * 25
        
        # Adjust based on existing projects
        existing_allocation = sum(p.allocated_agents for p in self.projects.values())
        available = self.total_agents - existing_allocation
        
        return min(base + priority_bonus, available)
    
    def _allocate_agents(self, count: int) -> List[int]:
        """Allocate agent IDs to project"""
        # Get already allocated agent IDs
        allocated = set()
        for project in self.projects.values():
            allocated.update(project.agent_pool)
        
        # Find available agents
        available = [i for i in range(1, self.total_agents + 1) if i not in allocated]
        
        return available[:count]
    
    def _detect_tech_stack(self, path: str) -> List[str]:
        """Auto-detect project tech stack"""
        tech_stack = []
        path_obj = Path(path)
        
        if not path_obj.exists():
            return tech_stack
        
        # Check for common files
        indicators = {
            "package.json": ["node", "javascript"],
            "requirements.txt": ["python"],
            "pyproject.toml": ["python"],
            "Cargo.toml": ["rust"],
            "go.mod": ["go"],
            "pom.xml": ["java", "maven"],
            "build.gradle": ["java", "gradle"],
            "Gemfile": ["ruby"],
            "composer.json": ["php"],
            "pubspec.yaml": ["dart", "flutter"],
            "tsconfig.json": ["typescript"],
            "next.config.js": ["nextjs"],
            "vite.config.js": ["vite"],
            "electron.js": ["electron"],
            "Dockerfile": ["docker"],
            ".git": ["git"]
        }
        
        for filename, techs in indicators.items():
            if (path_obj / filename).exists():
                tech_stack.extend(techs)
        
        return list(set(tech_stack))
    
    def reallocate_resources(self):
        """Reallocate agents based on project priorities and activity"""
        with self.lock:
            if not self.projects:
                return
            
            # Calculate total priority weight
            total_weight = sum(p.priority for p in self.projects.values() 
                             if p.status == ProjectStatus.ACTIVE)
            
            if total_weight == 0:
                return
            
            # Reallocate based on priority
            for project in self.projects.values():
                if project.status == ProjectStatus.ACTIVE:
                    new_allocation = int(
                        (project.priority / total_weight) * self.total_agents
                    )
                    project.allocated_agents = new_allocation
                    project.agent_pool = self._allocate_agents(new_allocation)
    
    def share_learning(self, source_project: str, pattern_name: str, 
                      pattern_solution: str):
        """Share learning across projects"""
        self.cross_context.learned_solutions[pattern_name] = pattern_solution
    
    def get_shared_solution(self, pattern_name: str) -> Optional[str]:
        """Get shared solution from cross-project memory"""
        return self.cross_context.learned_solutions.get(pattern_name)
    
    def get_project_stats(self, project_id: str = None) -> Dict[str, Any]:
        """Get project statistics"""
        if project_id:
            project = self.projects.get(project_id)
            if not project:
                return {}
            
            return {
                "project_id": project.project_id,
                "name": project.name,
                "path": project.path,
                "status": project.status.value,
                "allocated_agents": project.allocated_agents,
                "tasks_completed": project.tasks_completed,
                "total_cost": project.total_cost,
                "tech_stack": project.tech_stack,
                "priority": project.priority,
                "last_active": project.last_active.isoformat()
            }
        
        # Overall stats
        return {
            "total_projects": len(self.projects),
            "active_projects": sum(1 for p in self.projects.values() 
                                  if p.status == ProjectStatus.ACTIVE),
            "total_agents_allocated": sum(p.allocated_agents 
                                         for p in self.projects.values()),
            "current_project": self.current_project,
            "shared_solutions": len(self.cross_context.learned_solutions),
            "projects": [self.get_project_stats(p.project_id) 
                        for p in self.projects.values()]
        }
    
    def execute_on_project(self, project_id: str, task: str) -> Dict[str, Any]:
        """Execute task on specific project"""
        project = self.projects.get(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Switch to project temporarily
        old_project = self.current_project
        self.switch_project(project_id)
        
        result = {
            "project_id": project_id,
            "project_name": project.name,
            "task": task,
            "assigned_agents": project.allocated_agents,
            "tech_stack": project.tech_stack,
            "status": "executing"
        }
        
        # Update stats
        project.tasks_completed += 1
        project.last_active = datetime.now()
        
        # Restore previous project
        if old_project:
            self.switch_project(old_project)
        
        return result


# Global instance
_manager: Optional[MultiProjectManager] = None


def get_project_manager() -> MultiProjectManager:
    """Get or create global project manager"""
    global _manager
    if _manager is None:
        _manager = MultiProjectManager()
    return _manager


if __name__ == "__main__":
    print("\n📂 Multi-Project Support Module\n")
    
    manager = get_project_manager()
    
    # Add projects
    manager.add_project(
        name="Dive AI",
        path="D:\\Antigravity\\Dive AI",
        description="Main AI Framework",
        priority=5
    )
    
    manager.add_project(
        name="UI-TARS Desktop",
        path="D:\\Antigravity\\UI-Tars - Desktop",
        description="Desktop Application",
        priority=4
    )
    
    manager.add_project(
        name="VoiceNow",
        path="D:\\Projects\\VoiceNow",
        description="Voice assistant",
        priority=3
    )
    
    # Get stats
    stats = manager.get_project_stats()
    print("\n📊 Project Stats:")
    print(json.dumps(stats, indent=2, default=str))
    
    # Switch project
    print("\n🔄 Switching projects...")
    manager.switch_project("proj-002")
    current = manager.get_current_project()
    print(f"   Current: {current.name if current else 'None'}")
