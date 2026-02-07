"""
Dive Memory - Search-Enhanced Version

Extends Dive Memory 3-File System with search engine integration for:
- Fast context retrieval (query instead of read all)
- Change tracking with notifications
- Search-driven memory access
- Integration with Dive Search Engine
"""

import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# Import base memory system
try:
    from .dive_memory_3file_complete import DiveMemory3FileComplete
    from .dive_search_engine import get_search_engine
    from .dive_update_indexer import DiveUpdateIndexer, ChangeType, ChangeCategory
except ImportError:
    from dive_memory_3file_complete import DiveMemory3FileComplete
    from dive_search_engine import get_search_engine
    from dive_update_indexer import DiveUpdateIndexer, ChangeType, ChangeCategory


class DiveMemorySearchEnhanced(DiveMemory3FileComplete):
    """
    Search-Enhanced Memory System
    
    Extends 3-file system with:
    - Search engine integration
    - Fast context retrieval
    - Change tracking
    - Notifications
    """
    
    def __init__(self, memory_root: Optional[Path] = None):
        """Initialize search-enhanced memory"""
        super().__init__(memory_root)
        
        # Initialize search engine
        project_root = Path(__file__).parent.parent
        self.search_engine = get_search_engine(str(project_root))
        
        # Initialize if not already done
        if not self.search_engine.ready:
            print("Initializing search engine for memory...")
            self.search_engine.initialize(str(project_root))
        
        # Initialize update indexer for change tracking
        self.update_indexer = DiveUpdateIndexer(
            str(self.memory_root / "dive_memory_changes.json")
        )
    
    def load_project(self, project: str) -> Dict[str, str]:
        """Load project and index in search engine"""
        # Load with base system
        content = super().load_project(project)
        
        # Re-index memory files in search engine
        print("   🔍 Indexing memory in search engine...")
        self.search_engine.index.memory_indexer.index_memory_dir(str(self.memory_root))
        
        return content
    
    def search_memory(self, query: str, file_type: str = None, 
                     max_results: int = 10) -> List[Dict]:
        """
        Search memory instead of reading all
        
        Args:
            query: Search query
            file_type: Optional filter (FULL, CRITERIA, CHANGELOG)
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        results = self.search_engine.search_memory(
            query=query,
            file_type=file_type,
            project=self.current_project,
            limit=max_results
        )
        
        return [r.data for r in results]
    
    def get_relevant_context(self, task_description: str, max_sections: int = 5) -> str:
        """
        Get only relevant context for task
        
        This replaces reading entire FULL.md!
        
        Args:
            task_description: Description of task
            max_sections: Maximum sections to return
            
        Returns:
            Relevant context string
        """
        context = self.search_engine.get_relevant_context(
            task_description, 
            max_sections
        )
        
        if context:
            print(f"   ✓ Retrieved {len(context)} chars of relevant context (vs {self._get_full_size()} chars total)")
        else:
            print("   ⚠️  No relevant context found, falling back to full memory")
            # Fallback to full memory
            if self.current_project and self.current_project in self.loaded_projects:
                context = self.loaded_projects[self.current_project].get('full', '')
        
        return context
    
    def _get_full_size(self) -> int:
        """Get size of FULL.md"""
        if self.current_project and self.current_project in self.loaded_projects:
            return len(self.loaded_projects[self.current_project].get('full', ''))
        return 0
    
    def save_project(self, project: str, content: Dict[str, str], 
                    track_changes: bool = True) -> None:
        """
        Save project with change tracking
        
        Args:
            project: Project name
            content: Content dictionary
            track_changes: Whether to track changes
        """
        files = self.get_project_files(project)
        
        # Detect changes before saving
        changes = []
        if track_changes:
            changes = self._detect_changes(project, content)
        
        # Save files
        for key, file_path in files.items():
            if key in content:
                file_path.write_text(content[key])
                print(f"   💾 Saved {file_path.name} ({len(content[key])} chars)")
        
        # Track changes
        if track_changes and changes:
            self._track_changes(project, changes)
        
        # Re-index memory
        print("   🔍 Re-indexing memory...")
        self.search_engine.index.memory_indexer.index_memory_dir(str(self.memory_root))
        
        # Update loaded projects
        self.loaded_projects[project] = content
    
    def _detect_changes(self, project: str, new_content: Dict[str, str]) -> List[Dict]:
        """
        Detect changes between old and new content
        
        Args:
            project: Project name
            new_content: New content
            
        Returns:
            List of change dictionaries
        """
        changes = []
        
        # Get old content
        old_content = self.loaded_projects.get(project, {})
        
        for key in ['full', 'criteria', 'changelog']:
            old = old_content.get(key, '')
            new = new_content.get(key, '')
            
            if old != new:
                # Determine change type
                if not old and new:
                    change_type = 'ADDED'
                elif old and not new:
                    change_type = 'DELETED'
                else:
                    change_type = 'MODIFIED'
                
                # Calculate change size
                old_lines = old.count('\n') if old else 0
                new_lines = new.count('\n') if new else 0
                lines_changed = abs(new_lines - old_lines)
                
                changes.append({
                    'file': key,
                    'type': change_type,
                    'old_size': len(old),
                    'new_size': len(new),
                    'lines_changed': lines_changed,
                    'timestamp': datetime.now()
                })
        
        return changes
    
    def _track_changes(self, project: str, changes: List[Dict]) -> None:
        """
        Track changes in update indexer
        
        Args:
            project: Project name
            changes: List of changes
        """
        files = self.get_project_files(project)
        
        for change in changes:
            file_key = change['file']
            file_path = str(files[file_key])
            
            # Determine category
            category = 'DOCUMENTATION'
            if file_key == 'changelog':
                category = 'DOCUMENTATION'
            elif change['lines_changed'] > 100:
                category = 'FEATURE'
            
            # Track in update indexer
            description = f"Memory {change['type'].lower()}: {file_key}.md ({change['lines_changed']} lines)"
            
            self.update_indexer.track_change(
                file_path=file_path,
                change_type=change['type'],
                category=category,
                description=description,
                breaking=False,  # Memory changes are rarely breaking
                version=self._get_current_version(project)
            )
            
            print(f"   📝 Tracked change: {description}")
    
    def _get_current_version(self, project: str) -> Optional[str]:
        """Get current version from memory"""
        if project in self.loaded_projects:
            full_content = self.loaded_projects[project].get('full', '')
            # Try to extract version
            import re
            version_match = re.search(r'Version:?\s*(\d+\.\d+(?:\.\d+)?)', full_content)
            if version_match:
                return version_match.group(1)
        return None
    
    def get_change_history(self, project: str, limit: int = 10) -> List[Dict]:
        """
        Get change history for project
        
        Args:
            project: Project name
            limit: Maximum changes to return
            
        Returns:
            List of changes
        """
        files = self.get_project_files(project)
        all_changes = []
        
        for file_path in files.values():
            changes = self.update_indexer.get_changes_for_file(str(file_path))
            all_changes.extend([c.to_dict() for c in changes])
        
        # Sort by timestamp
        all_changes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_changes[:limit]
    
    def get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Get recent changes across all projects"""
        changes = self.update_indexer.get_recent_changes(limit)
        return [c.to_dict() for c in changes]
    
    def search_features(self, query: str) -> List[str]:
        """
        Search for features in memory
        
        Args:
            query: Search query
            
        Returns:
            List of matching features
        """
        results = self.search_engine.index.memory_indexer.search_by_feature(query)
        return [r['feature'] for r in results]
    
    def get_breaking_changes(self, version: str = None) -> List[Dict]:
        """Get breaking changes"""
        return self.search_engine.get_breaking_changes(version)
    
    def notify_change(self, change_type: str, description: str, 
                     affected_files: List[str] = None) -> Dict:
        """
        Create notification for a change
        
        Args:
            change_type: Type of change (ADDED, MODIFIED, DELETED)
            description: Description of change
            affected_files: List of affected files
            
        Returns:
            Notification dictionary
        """
        notification = {
            "type": "MEMORY_CHANGE",
            "change_type": change_type,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "affected_files": affected_files or [],
            "project": self.current_project
        }
        
        # Append to changelog if current project loaded
        if self.current_project and self.current_project in self.loaded_projects:
            changelog = self.loaded_projects[self.current_project].get('changelog', '')
            
            # Add notification to changelog
            notification_entry = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {change_type}\n"
            notification_entry += f"{description}\n"
            if affected_files:
                notification_entry += f"Affected files: {', '.join(affected_files)}\n"
            
            self.loaded_projects[self.current_project]['changelog'] = changelog + notification_entry
        
        return notification
    
    def get_statistics(self) -> Dict:
        """Get memory statistics including search stats"""
        stats = {
            "projects_loaded": len(self.loaded_projects),
            "current_project": self.current_project,
            "memory_files": len(list(self.memory_root.glob("*.md"))),
            "total_changes_tracked": len(self.update_indexer.changes),
            "search_engine_stats": self.search_engine.get_statistics()
        }
        
        return stats


if __name__ == "__main__":
    # Test search-enhanced memory
    memory = DiveMemorySearchEnhanced()
    
    # Load Dive AI project
    print("\n=== Loading Dive AI Project ===")
    content = memory.load_project("dive-ai")
    
    # Test search
    print("\n=== Testing Memory Search ===")
    results = memory.search_memory("orchestrator", max_results=3)
    print(f"Search 'orchestrator': {len(results)} results")
    for result in results:
        print(f"  - {result['section_title']} (score: {result['score']})")
    
    # Test context retrieval
    print("\n=== Testing Context Retrieval ===")
    context = memory.get_relevant_context("orchestrator routing", max_sections=2)
    print(f"Context length: {len(context)} chars")
    print(f"Preview: {context[:200]}...")
    
    # Test change history
    print("\n=== Testing Change History ===")
    changes = memory.get_change_history("dive-ai", limit=5)
    print(f"Recent changes: {len(changes)}")
    for change in changes[:3]:
        print(f"  - {change['description']}")
    
    # Get statistics
    print("\n=== Memory Statistics ===")
    stats = memory.get_statistics()
    print(f"Projects loaded: {stats['projects_loaded']}")
    print(f"Current project: {stats['current_project']}")
    print(f"Memory files: {stats['memory_files']}")
    print(f"Changes tracked: {stats['total_changes_tracked']}")
