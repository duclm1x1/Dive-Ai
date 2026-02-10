"""
Dive Search Engine - Main search engine interface

The core component that powers the entire Dive AI system with unified search.
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from .dive_search_index import DiveSearchIndex, SearchResult
    from .dive_search_processor import DiveSearchProcessor
except ImportError:
    from dive_search_index import DiveSearchIndex, SearchResult
    from dive_search_processor import DiveSearchProcessor


class DiveSearchEngine:
    """
    Main search engine for Dive AI
    
    Provides unified search across:
    - Python files (AST-based)
    - Memory files (FULL/CRITERIA/CHANGELOG)
    - Change tracking (updates)
    - Dependencies (graph-based)
    
    Features:
    - Natural language queries
    - Structured queries with filters
    - Semantic understanding
    - Query expansion
    - Result ranking
    - Context retrieval
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root
        self.index = DiveSearchIndex(project_root)
        self.processor = DiveSearchProcessor()
        self.ready = False
    
    def initialize(self, project_path: str) -> None:
        """
        Initialize search engine with project
        
        Args:
            project_path: Root path of project to index
        """
        self.project_root = project_path
        self.index.index_project(project_path)
        self.ready = True
        print("✓ Search engine initialized and ready")
    
    def search(self, query: str, sources: List[str] = None, 
               filters: Dict = None, limit: int = 20, 
               semantic: bool = False) -> List[SearchResult]:
        """
        Main search method
        
        Args:
            query: Search query (natural language or structured)
            sources: List of sources to search (file, memory, update, dependency)
            filters: Optional filters
            limit: Maximum number of results
            semantic: Enable semantic understanding
            
        Returns:
            List of SearchResult objects
        """
        if not self.ready:
            print("Warning: Search engine not initialized")
            return []
        
        # Process query
        if not filters and not sources:
            # Auto-parse query
            params = self.processor.build_search_params(query)
            query = params['query']
            sources = params['sources']
            filters = params['filters']
            semantic = semantic or params['semantic']
        
        # Search
        results = self.index.search(query, sources, filters, limit)
        
        return results
    
    def search_files(self, query: str, file_type: str = None, 
                     has_class: str = None, has_function: str = None,
                     imports: str = None) -> List[SearchResult]:
        """
        Search files specifically
        
        Args:
            query: Search query
            file_type: Filter by file type (python, markdown, etc.)
            has_class: Filter by class name
            has_function: Filter by function name
            imports: Filter by import
            
        Returns:
            List of SearchResult objects
        """
        filters = {'file': {}}
        
        if file_type:
            filters['file']['file_type'] = file_type
        if has_class:
            filters['file']['has_class'] = has_class
        if has_function:
            filters['file']['has_function'] = has_function
        if imports:
            filters['file']['imports'] = imports
        
        return self.search(query, sources=['file'], filters=filters)
    
    def search_memory(self, query: str, file_type: str = None, 
                      project: str = None, version: str = None) -> List[SearchResult]:
        """
        Search memory specifically
        
        Args:
            query: Search query
            file_type: Filter by memory file type (FULL, CRITERIA, CHANGELOG)
            project: Filter by project name
            version: Filter by version
            
        Returns:
            List of SearchResult objects
        """
        filters = {'memory': {}}
        
        if file_type:
            filters['memory']['file_type'] = file_type
        if project:
            filters['memory']['project'] = project
        if version:
            filters['memory']['version'] = version
        
        return self.search(query, sources=['memory'], filters=filters)
    
    def search_updates(self, query: str = None, change_type: str = None,
                       category: str = None, breaking: bool = None,
                       version: str = None) -> List[SearchResult]:
        """
        Search updates/changes specifically
        
        Args:
            query: Search query
            change_type: Filter by change type (ADDED, MODIFIED, DELETED)
            category: Filter by category (FEATURE, BUGFIX, BREAKING, etc.)
            breaking: Filter breaking changes
            version: Filter by version
            
        Returns:
            List of SearchResult objects
        """
        filters = {'update': {}}
        
        if change_type:
            filters['update']['type'] = change_type
        if category:
            filters['update']['category'] = category
        if breaking is not None:
            filters['update']['breaking'] = breaking
        if version:
            filters['update']['version'] = version
        
        return self.search(query or "", sources=['update'], filters=filters)
    
    def search_dependencies(self, file_path: str, direction: str = 'dependents',
                           transitive: bool = False) -> List[str]:
        """
        Search dependencies
        
        Args:
            file_path: Path to file
            direction: 'dependents' (who imports this) or 'dependencies' (what this imports)
            transitive: Include transitive dependencies
            
        Returns:
            List of file paths
        """
        if transitive:
            if direction == 'dependents':
                return list(self.index.dependency_graph.get_transitive_dependents(file_path))
            else:
                return list(self.index.dependency_graph.get_transitive_dependencies(file_path))
        else:
            return self.index.search_dependencies(file_path, direction)
    
    def search_related_to(self, file_path: str) -> Dict[str, Any]:
        """
        Find everything related to a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with all related information
        """
        return self.index.search_related_to(file_path)
    
    def get_relevant_context(self, task_description: str, max_sections: int = 5) -> str:
        """
        Get relevant context from memory for a task
        
        This replaces reading entire memory files!
        
        Args:
            task_description: Description of task
            max_sections: Maximum number of sections to return
            
        Returns:
            Relevant context string
        """
        return self.index.get_relevant_context(task_description, max_sections)
    
    def get_breaking_changes(self, version: str = None) -> List[Dict]:
        """
        Get breaking changes
        
        Args:
            version: Optional version filter
            
        Returns:
            List of breaking changes
        """
        return self.index.get_breaking_changes(version)
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Get complete information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info, dependencies, changes
        """
        return self.index.get_file_info(file_path)
    
    def understand_query(self, query: str) -> Dict:
        """
        Understand query intent and provide suggestions
        
        Args:
            query: Search query
            
        Returns:
            Understanding dictionary
        """
        return self.processor.understand_query(query)
    
    def suggest_filters(self, query: str) -> List[Dict]:
        """
        Suggest filters for query
        
        Args:
            query: Search query
            
        Returns:
            List of filter suggestions
        """
        return self.processor.suggest_filters(query)
    
    def get_statistics(self) -> Dict:
        """Get statistics from all indexes"""
        return self.index.get_statistics()
    
    def export_indexes(self, output_dir: str) -> None:
        """Export all indexes"""
        self.index.export_indexes(output_dir)
    
    def import_indexes(self, input_dir: str) -> None:
        """Import indexes"""
        self.index.import_indexes(input_dir)
        self.ready = True


# Singleton instance
_search_engine_instance = None


def get_search_engine(project_root: str = None) -> DiveSearchEngine:
    """
    Get singleton search engine instance
    
    Args:
        project_root: Optional project root (only used on first call)
        
    Returns:
        DiveSearchEngine instance
    """
    global _search_engine_instance
    
    if _search_engine_instance is None:
        _search_engine_instance = DiveSearchEngine(project_root)
    
    return _search_engine_instance


if __name__ == "__main__":
    # Test search engine
    engine = DiveSearchEngine()
    
    # Initialize with Dive AI project
    project_path = "/home/ubuntu/dive-ai-messenger/Dive-Ai"
    engine.initialize(project_path)
    
    # Get statistics
    print("\n=== Search Engine Statistics ===")
    stats = engine.get_statistics()
    print(f"Files indexed: {stats['file_index']['total_files']}")
    print(f"Memory files indexed: {stats['memory_index']['total_files']}")
    print(f"Changes tracked: {stats['update_index'].get('total_changes', 0)}")
    print(f"Dependency nodes: {stats['dependency_graph']['total_files']}")
    
    # Test natural language search
    print("\n=== Testing Natural Language Search ===")
    results = engine.search("orchestrator routing logic")
    print(f"Query: 'orchestrator routing logic'")
    print(f"Results: {len(results)}")
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. Source: {result.source}, Type: {result.result_type}, Score: {result.score}")
        if result.source == 'file':
            print(f"   File: {os.path.basename(result.data['file_path'])}")
            print(f"   Classes: {', '.join(result.data['classes'][:3])}")
        elif result.source == 'memory':
            print(f"   Section: {result.data['section_title']}")
            print(f"   Content: {result.data['content'][:100]}...")
    
    # Test file search
    print("\n=== Testing File Search ===")
    results = engine.search_files("DiveMemory", has_class="DiveMemory")
    print(f"Files with class 'DiveMemory': {len(results)}")
    for result in results[:3]:
        print(f"  - {os.path.basename(result.data['file_path'])}")
    
    # Test dependency search
    test_file = os.path.join(project_path, "core/dive_memory_3file_complete.py")
    if os.path.exists(test_file):
        print(f"\n=== Testing Dependency Search ===")
        print(f"File: {os.path.basename(test_file)}")
        
        dependents = engine.search_dependencies(test_file, direction='dependents')
        print(f"Dependents: {len(dependents)}")
        for dep in dependents[:3]:
            print(f"  - {os.path.basename(dep)}")
    
    # Test context retrieval
    print("\n=== Testing Context Retrieval ===")
    context = engine.get_relevant_context("memory system architecture", max_sections=2)
    print(f"Context length: {len(context)} chars")
    print(f"Preview:\n{context[:200]}...")
    
    # Test breaking changes
    print("\n=== Testing Breaking Changes ===")
    breaking = engine.get_breaking_changes()
    print(f"Breaking changes: {len(breaking)}")
    for change in breaking[:3]:
        print(f"  - {change['description']}")
    
    # Test query understanding
    print("\n=== Testing Query Understanding ===")
    understanding = engine.understand_query("find files affected by memory change")
    print(f"Query: 'find files affected by memory change'")
    print(f"Intent: {understanding['parsed']['intent']}")
    print(f"Sources: {understanding['parsed']['sources']}")
    print(f"Suggestions: {understanding['suggestions']}")
