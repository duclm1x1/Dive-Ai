"""
Dive Search Index - Unified index combining all data sources

Part of Dive Search Engine - provides unified interface for all indexes.
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from .dive_file_indexer import DiveFileIndexer
    from .dive_memory_indexer import DiveMemoryIndexer
    from .dive_update_indexer import DiveUpdateIndexer
except ImportError:
    try:
        from dive_core.search.dive_file_indexer import DiveFileIndexer
        from dive_core.search.dive_memory_indexer import DiveMemoryIndexer
        from dive_core.search.dive_update_indexer import DiveUpdateIndexer
    except ImportError:
        from dive_file_indexer import DiveFileIndexer
        from dive_memory_indexer import DiveMemoryIndexer
        from dive_update_indexer import DiveUpdateIndexer

# dive_dependency_graph is in engine/, not search/
try:
    from dive_core.engine.dive_dependency_graph import DiveDependencyGraph
except ImportError:
    try:
        from dive_dependency_graph import DiveDependencyGraph
    except ImportError:
        DiveDependencyGraph = None





class SearchResult:
    """Unified search result"""
    
    def __init__(self, source: str, result_type: str, data: Dict):
        self.source = source  # file, memory, update, dependency
        self.result_type = result_type  # class, function, section, change, etc.
        self.data = data
        self.score: float = 0.0
        self.relevance: str = "NORMAL"  # HIGH, NORMAL, LOW
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "source": self.source,
            "result_type": self.result_type,
            "data": self.data,
            "score": self.score,
            "relevance": self.relevance
        }


class DiveSearchIndex:
    """
    Unified index for all Dive AI data sources
    
    Combines:
    - File Index (Python files with AST)
    - Memory Index (FULL/CRITERIA/CHANGELOG)
    - Update Index (Change tracking)
    - Dependency Graph (File relationships)
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root
        
        # Initialize all indexers
        self.file_indexer = DiveFileIndexer()
        self.memory_indexer = DiveMemoryIndexer()
        self.update_indexer = DiveUpdateIndexer()
        self.dependency_graph = DiveDependencyGraph()
        
        self.indexed = False
    
    def index_project(self, project_path: str) -> None:
        """
        Index entire project
        
        Args:
            project_path: Root path of project
        """
        self.project_root = project_path
        
        print(f"=== Indexing Dive AI Project: {project_path} ===\n")
        
        # Index files
        print("1. Indexing Python files...")
        self.file_indexer.index_project(project_path, extensions=['.py'])
        file_stats = self.file_indexer.get_statistics()
        print(f"   ✓ {file_stats['total_files']} files indexed\n")
        
        # Index memory
        memory_dir = os.path.join(project_path, "memory")
        if os.path.exists(memory_dir):
            print("2. Indexing memory files...")
            self.memory_indexer.index_memory_dir(memory_dir)
            memory_stats = self.memory_indexer.get_statistics()
            print(f"   ✓ {memory_stats['total_files']} memory files indexed\n")
        else:
            print("2. Memory directory not found, skipping...\n")
        
        # Build dependency graph
        print("3. Building dependency graph...")
        self.dependency_graph.build_graph(project_path)
        dep_stats = self.dependency_graph.get_statistics()
        print(f"   ✓ {dep_stats['total_files']} files in graph\n")
        
        # Update indexer is always ready (loads from disk)
        update_stats = self.update_indexer.get_statistics()
        print(f"4. Update indexer ready")
        print(f"   ✓ {update_stats.get('total_changes', 0)} changes tracked\n")
        
        self.indexed = True
        print("=== Indexing Complete ===\n")
    
    def search(self, query: str, sources: List[str] = None, 
               filters: Dict = None, limit: int = 20) -> List[SearchResult]:
        """
        Unified search across all sources
        
        Args:
            query: Search query
            sources: List of sources to search (file, memory, update, dependency)
                    If None, searches all sources
            filters: Optional filters specific to each source
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        if not self.indexed:
            print("Warning: Project not indexed. Call index_project() first.")
            return []
        
        if sources is None:
            sources = ['file', 'memory', 'update']
        
        all_results = []
        
        # Search files
        if 'file' in sources:
            file_results = self._search_files(query, filters)
            all_results.extend(file_results)
        
        # Search memory
        if 'memory' in sources:
            memory_results = self._search_memory(query, filters)
            all_results.extend(memory_results)
        
        # Search updates
        if 'update' in sources:
            update_results = self._search_updates(query, filters)
            all_results.extend(update_results)
        
        # Sort by score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        return all_results[:limit]
    
    def _search_files(self, query: str, filters: Dict = None) -> List[SearchResult]:
        """Search in file index"""
        file_filters = filters.get('file', {}) if filters else {}
        file_indexes = self.file_indexer.search(query, file_filters)
        
        results = []
        for file_index in file_indexes:
            result = SearchResult(
                source='file',
                result_type='file',
                data={
                    'file_path': file_index.file_path,
                    'file_type': file_index.file_type,
                    'classes': [c['name'] for c in file_index.classes],
                    'functions': [f['name'] for f in file_index.functions],
                    'imports': list(file_index.imports),
                    'docstring': file_index.docstring
                }
            )
            result.score = file_index.metadata.get('search_score', 0)
            results.append(result)
        
        return results
    
    def _search_memory(self, query: str, filters: Dict = None) -> List[SearchResult]:
        """Search in memory index"""
        memory_filters = filters.get('memory', {}) if filters else {}
        memory_results = self.memory_indexer.search(query, memory_filters)
        
        results = []
        for mem_result in memory_results:
            result = SearchResult(
                source='memory',
                result_type='section',
                data=mem_result
            )
            result.score = mem_result.get('score', 0)
            results.append(result)
        
        return results
    
    def _search_updates(self, query: str, filters: Dict = None) -> List[SearchResult]:
        """Search in update index"""
        update_filters = filters.get('update', {}) if filters else {}
        update_records = self.update_indexer.search(query, update_filters)
        
        results = []
        for record in update_records:
            result = SearchResult(
                source='update',
                result_type='change',
                data=record.to_dict()
            )
            # Score based on recency and breaking status
            result.score = 5 if record.breaking else 3
            results.append(result)
        
        return results
    
    def search_dependencies(self, file_path: str, direction: str = 'dependents') -> List[str]:
        """
        Search dependencies
        
        Args:
            file_path: Path to file
            direction: 'dependents' or 'dependencies'
            
        Returns:
            List of file paths
        """
        if direction == 'dependents':
            return self.dependency_graph.get_dependents(file_path)
        else:
            return self.dependency_graph.get_dependencies(file_path)
    
    def search_related_to(self, file_path: str) -> Dict[str, Any]:
        """
        Find everything related to a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with related files, changes, memory sections
        """
        # Get dependencies
        dependencies = self.dependency_graph.get_dependencies(file_path)
        dependents = self.dependency_graph.get_dependents(file_path)
        
        # Get related changes
        changes = self.update_indexer.get_related_changes(file_path)
        
        # Search memory for mentions
        file_name = os.path.basename(file_path)
        memory_results = self.memory_indexer.search(file_name)
        
        return {
            "file_path": file_path,
            "dependencies": dependencies,
            "dependents": dependents,
            "related_changes": [c.to_dict() for c in changes],
            "memory_mentions": memory_results,
            "total_related": len(dependencies) + len(dependents) + len(changes)
        }
    
    def get_breaking_changes(self, version: str = None) -> List[Dict]:
        """Get breaking changes"""
        changes = self.update_indexer.get_breaking_changes(version)
        return [c.to_dict() for c in changes]
    
    def get_relevant_context(self, query: str, max_sections: int = 5) -> str:
        """Get relevant context from memory"""
        return self.memory_indexer.get_relevant_context(query, max_sections)
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get complete information about a file"""
        # File index info
        file_info = self.file_indexer.get_file_info(file_path)
        
        # Dependency info
        dep_info = self.dependency_graph.get_node_info(file_path)
        
        # Related changes
        changes = self.update_indexer.get_changes_for_file(file_path)
        
        if not file_info and not dep_info:
            return None
        
        return {
            "file_info": file_info,
            "dependency_info": dep_info,
            "recent_changes": [c.to_dict() for c in changes[:5]],
            "total_changes": len(changes)
        }
    
    def get_statistics(self) -> Dict:
        """Get statistics from all indexes"""
        return {
            "file_index": self.file_indexer.get_statistics(),
            "memory_index": self.memory_indexer.get_statistics(),
            "update_index": self.update_indexer.get_statistics(),
            "dependency_graph": self.dependency_graph.get_statistics()
        }
    
    def export_indexes(self, output_dir: str) -> None:
        """Export all indexes to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export dependency graph
        dep_path = os.path.join(output_dir, "dependency_graph.json")
        self.dependency_graph.export_graph(dep_path)
        
        # Update indexer auto-saves to its storage path
        
        print(f"Indexes exported to {output_dir}")
    
    def import_indexes(self, input_dir: str) -> None:
        """Import indexes from files"""
        # Import dependency graph
        dep_path = os.path.join(input_dir, "dependency_graph.json")
        if os.path.exists(dep_path):
            self.dependency_graph.import_graph(dep_path)
        
        # Update indexer auto-loads from its storage path
        
        self.indexed = True
        print(f"Indexes imported from {input_dir}")


if __name__ == "__main__":
    # Test unified search index
    search_index = DiveSearchIndex()
    
    # Index Dive AI project
    project_path = "/home/ubuntu/dive-ai-messenger/Dive-Ai"
    search_index.index_project(project_path)
    
    # Get statistics
    print("\n=== Unified Index Statistics ===")
    stats = search_index.get_statistics()
    
    print("\nFile Index:")
    for key, value in stats['file_index'].items():
        print(f"  {key}: {value}")
    
    print("\nMemory Index:")
    for key, value in stats['memory_index'].items():
        print(f"  {key}: {value}")
    
    print("\nUpdate Index:")
    for key, value in stats['update_index'].items():
        print(f"  {key}: {value}")
    
    print("\nDependency Graph:")
    for key, value in stats['dependency_graph'].items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    
    # Test unified search
    print("\n=== Testing Unified Search ===")
    results = search_index.search("orchestrator", limit=5)
    print(f"Search 'orchestrator': {len(results)} results")
    for result in results:
        print(f"\n  Source: {result.source}")
        print(f"  Type: {result.result_type}")
        print(f"  Score: {result.score}")
        if result.source == 'file':
            print(f"  File: {os.path.basename(result.data['file_path'])}")
        elif result.source == 'memory':
            print(f"  Section: {result.data['section_title']}")
    
    # Test related search
    test_file = os.path.join(project_path, "core/dive_memory_3file_complete.py")
    if os.path.exists(test_file):
        print(f"\n=== Testing Related Search for {os.path.basename(test_file)} ===")
        related = search_index.search_related_to(test_file)
        print(f"Dependencies: {len(related['dependencies'])}")
        print(f"Dependents: {len(related['dependents'])}")
        print(f"Related changes: {len(related['related_changes'])}")
        print(f"Memory mentions: {len(related['memory_mentions'])}")
        print(f"Total related items: {related['total_related']}")
