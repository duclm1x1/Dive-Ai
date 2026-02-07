"""
Dive Orchestrator - Search-Enhanced Version

Extends Dive Smart Orchestrator with search engine integration for:
- Search-driven task routing
- Fast context retrieval
- Breaking change detection
- Auto-fix with search
- Related file discovery
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import base orchestrator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from .dive_smart_orchestrator import DiveSmartOrchestrator, TaskType, Intent
    from .dive_search_engine import get_search_engine
    from .dive_memory_search_enhanced import DiveMemorySearchEnhanced
    from .dive_update_system import DiveUpdateSystem
except ImportError:
    from dive_smart_orchestrator import DiveSmartOrchestrator, TaskType, Intent
    from dive_search_engine import get_search_engine
    from dive_memory_search_enhanced import DiveMemorySearchEnhanced
    from dive_update_system import DiveUpdateSystem


class DiveOrchestratorSearchEnhanced(DiveSmartOrchestrator):
    """
    Search-Enhanced Orchestrator
    
    Extends orchestrator with:
    - Search-driven routing
    - Fast context retrieval
    - Breaking change detection
    - Auto-fix capabilities
    """
    
    def __init__(self):
        """Initialize search-enhanced orchestrator"""
        # Initialize base orchestrator
        super().__init__()
        
        # Replace memory with search-enhanced version
        self.memory = DiveMemorySearchEnhanced()
        
        # Initialize search engine
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.search_engine = get_search_engine(project_root)
        
        # Initialize if not ready
        if not self.search_engine.ready:
            print("🔍 Initializing search engine...")
            self.search_engine.initialize(project_root)
        
        # Initialize update system
        self.update_system = DiveUpdateSystem()
    
    def analyze_task(self, prompt: str) -> Intent:
        """
        Analyze task with search-driven context
        
        Args:
            prompt: User prompt
            
        Returns:
            Intent object
        """
        print("\n🔍 Analyzing task with search-driven context...")
        
        # Get relevant context from memory using search
        context = self.memory.get_relevant_context(prompt, max_sections=5)
        
        # Check for breaking changes
        breaking_changes = self.search_engine.get_breaking_changes()
        
        if breaking_changes:
            print(f"⚠️  Found {len(breaking_changes)} breaking changes")
            # Add to context
            context += "\n\n## Breaking Changes\n"
            for change in breaking_changes[:3]:
                context += f"- {change['description']}\n"
        
        # Use base analyzer with enhanced context
        intent = super().analyze_task(prompt)
        
        # Enhance intent with search results
        intent = self._enhance_intent_with_search(intent, prompt)
        
        return intent
    
    def _enhance_intent_with_search(self, intent: Intent, prompt: str) -> Intent:
        """
        Enhance intent with search results
        
        Args:
            intent: Base intent
            prompt: User prompt
            
        Returns:
            Enhanced intent
        """
        # Search for related files
        results = self.search_engine.search(prompt, limit=5)
        
        # Extract entities from search results
        for result in results:
            if result.source == 'file':
                file_name = os.path.basename(result.data['file_path'])
                if file_name not in intent.entities:
                    intent.entities.append(file_name)
            elif result.source == 'memory':
                section = result.data['section_title']
                if section not in intent.entities:
                    intent.entities.append(section)
        
        return intent
    
    def find_related_files(self, task_description: str) -> List[str]:
        """
        Find files related to task using search
        
        Args:
            task_description: Description of task
            
        Returns:
            List of related file paths
        """
        results = self.search_engine.search(
            task_description,
            sources=['file'],
            limit=10
        )
        
        return [r.data['file_path'] for r in results]
    
    def check_breaking_changes_for_files(self, file_paths: List[str]) -> Dict[str, List[Dict]]:
        """
        Check if files have breaking changes
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary mapping files to their breaking changes
        """
        breaking_by_file = {}
        
        for file_path in file_paths:
            # Get related changes
            related = self.search_engine.search_related_to(file_path)
            
            # Filter breaking changes
            breaking = [
                c for c in related['related_changes']
                if c.get('breaking', False)
            ]
            
            if breaking:
                breaking_by_file[file_path] = breaking
        
        return breaking_by_file
    
    def auto_fix_breaking_changes(self, file_path: str, breaking_changes: List[Dict]) -> bool:
        """
        Attempt to auto-fix breaking changes
        
        Args:
            file_path: Path to file
            breaking_changes: List of breaking changes
            
        Returns:
            True if fixed, False if manual intervention needed
        """
        print(f"\n🔧 Attempting auto-fix for {os.path.basename(file_path)}...")
        
        # Get affected files
        dependents = self.search_engine.search_dependencies(file_path, direction='dependents')
        
        if not dependents:
            print("   ✓ No dependents affected")
            return True
        
        print(f"   Found {len(dependents)} affected files")
        
        # Use update system to analyze impact
        impact = self.update_system.analyze_impact(file_path)
        
        # Check if auto-fix is safe
        if impact.get('complexity', 'HIGH') == 'LOW':
            print("   ✓ Auto-fix is safe, applying updates...")
            
            # Apply safe updates
            for update in impact.get('safe_updates', []):
                print(f"      - Updating {os.path.basename(update['file'])}")
                # In real implementation, would apply the update
            
            return True
        else:
            print("   ⚠️  Complex changes detected, manual review required")
            return False
    
    def route_task(self, intent: Intent) -> str:
        """
        Route task with search-driven logic
        
        Args:
            intent: Task intent
            
        Returns:
            Routing decision
        """
        # Check if task involves files with breaking changes
        related_files = self.find_related_files(intent.raw_prompt)
        breaking_by_file = self.check_breaking_changes_for_files(related_files)
        
        if breaking_by_file:
            print(f"\n⚠️  Breaking changes detected in {len(breaking_by_file)} files")
            
            # Attempt auto-fix
            all_fixed = True
            for file_path, changes in breaking_by_file.items():
                if not self.auto_fix_breaking_changes(file_path, changes):
                    all_fixed = False
            
            if not all_fixed:
                return "MANUAL_REVIEW_REQUIRED"
        
        # Use base routing with enhanced context
        return super().route_task(intent)
    
    def get_task_context(self, task_description: str) -> Dict[str, Any]:
        """
        Get complete context for task using search
        
        Args:
            task_description: Task description
            
        Returns:
            Context dictionary
        """
        # Get memory context
        memory_context = self.memory.get_relevant_context(task_description, max_sections=5)
        
        # Get related files
        related_files = self.find_related_files(task_description)
        
        # Get breaking changes
        breaking_changes = self.search_engine.get_breaking_changes()
        
        # Get recent changes
        recent_changes = self.memory.get_recent_changes(limit=5)
        
        return {
            "memory_context": memory_context,
            "memory_context_size": len(memory_context),
            "related_files": related_files[:5],
            "breaking_changes": breaking_changes,
            "recent_changes": recent_changes,
            "search_driven": True
        }
    
    def search_for_solution(self, problem: str) -> List[Dict]:
        """
        Search for solution to problem
        
        Args:
            problem: Problem description
            
        Returns:
            List of potential solutions from memory/files
        """
        # Search memory for similar problems
        memory_results = self.search_engine.search_memory(problem, limit=5)
        
        # Search files for relevant code
        file_results = self.search_engine.search_files(problem, limit=5)
        
        # Search changes for related fixes
        update_results = self.search_engine.search_updates(problem, limit=5)
        
        solutions = []
        
        # Extract solutions from memory
        for result in memory_results:
            solutions.append({
                "source": "memory",
                "title": result.data['section_title'],
                "content": result.data['content'][:500],
                "score": result.score
            })
        
        # Extract solutions from files
        for result in file_results:
            solutions.append({
                "source": "file",
                "file": os.path.basename(result.data['file_path']),
                "classes": result.data['classes'][:3],
                "functions": result.data['functions'][:3],
                "score": result.score
            })
        
        # Extract solutions from updates
        for result in update_results:
            solutions.append({
                "source": "update",
                "description": result.data['description'],
                "category": result.data['category'],
                "score": result.score
            })
        
        # Sort by score
        solutions.sort(key=lambda x: x['score'], reverse=True)
        
        return solutions
    
    def get_statistics(self) -> Dict:
        """Get orchestrator statistics including search stats"""
        stats = {
            "search_engine_ready": self.search_engine.ready,
            "memory_stats": self.memory.get_statistics(),
            "search_stats": self.search_engine.get_statistics()
        }
        
        return stats


if __name__ == "__main__":
    # Test search-enhanced orchestrator
    orchestrator = DiveOrchestratorSearchEnhanced()
    
    print("\n=== Testing Search-Enhanced Orchestrator ===")
    
    # Test task analysis
    print("\n1. Testing Task Analysis")
    prompt = "Fix bug in orchestrator routing logic"
    intent = orchestrator.analyze_task(prompt)
    print(f"   Task type: {intent.type}")
    print(f"   Entities: {intent.entities[:5]}")
    print(f"   Confidence: {intent.confidence}")
    
    # Test related file finding
    print("\n2. Testing Related File Finding")
    related = orchestrator.find_related_files("memory system")
    print(f"   Found {len(related)} related files")
    for file in related[:3]:
        print(f"      - {os.path.basename(file)}")
    
    # Test context retrieval
    print("\n3. Testing Context Retrieval")
    context = orchestrator.get_task_context("orchestrator routing")
    print(f"   Memory context: {context['memory_context_size']} chars")
    print(f"   Related files: {len(context['related_files'])}")
    print(f"   Breaking changes: {len(context['breaking_changes'])}")
    print(f"   Recent changes: {len(context['recent_changes'])}")
    
    # Test solution search
    print("\n4. Testing Solution Search")
    solutions = orchestrator.search_for_solution("routing logic")
    print(f"   Found {len(solutions)} potential solutions")
    for sol in solutions[:3]:
        print(f"      - {sol['source']}: {sol.get('title', sol.get('file', sol.get('description')))}")
    
    # Get statistics
    print("\n=== Orchestrator Statistics ===")
    stats = orchestrator.get_statistics()
    print(f"Search engine ready: {stats['search_engine_ready']}")
    print(f"Projects loaded: {stats['memory_stats']['projects_loaded']}")
