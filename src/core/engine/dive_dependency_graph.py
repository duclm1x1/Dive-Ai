"""
Dive Dependency Graph - Graph-based dependency tracking for instant lookups

Part of Dive Search Engine - enables instant dependency queries instead of file scanning.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import json


class DependencyNode:
    """Represents a file node in the dependency graph"""
    
    def __init__(self, file_path: str, file_type: str = "python"):
        self.file_path = file_path
        self.file_type = file_type
        self.imports: Set[str] = set()
        self.imported_by: Set[str] = set()
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.last_modified: Optional[datetime] = None
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "imports": list(self.imports),
            "imported_by": list(self.imported_by),
            "functions": self.functions,
            "classes": self.classes,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DependencyNode':
        """Create from dictionary"""
        node = cls(data["file_path"], data["file_type"])
        node.imports = set(data["imports"])
        node.imported_by = set(data["imported_by"])
        node.functions = data["functions"]
        node.classes = data["classes"]
        if data["last_modified"]:
            node.last_modified = datetime.fromisoformat(data["last_modified"])
        node.metadata = data["metadata"]
        return node


class DiveDependencyGraph:
    """
    Graph-based dependency tracking for instant lookups
    
    Features:
    - Build dependency graph from Python files
    - Instant dependency/dependent lookups
    - Detect circular dependencies
    - Track file relationships
    - Export/import graph for persistence
    """
    
    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
        self.project_root: Optional[str] = None
    
    def build_graph(self, project_path: str) -> None:
        """
        Build dependency graph from project
        
        Args:
            project_path: Root path of project to analyze
        """
        self.project_root = project_path
        project_path_obj = Path(project_path)
        
        # Find all Python files
        python_files = list(project_path_obj.rglob("*.py"))
        
        print(f"Building dependency graph for {len(python_files)} Python files...")
        
        # First pass: Create nodes
        for py_file in python_files:
            self._create_node(str(py_file))
        
        # Second pass: Build edges
        for py_file in python_files:
            self._analyze_dependencies(str(py_file))
        
        print(f"Dependency graph built: {len(self.nodes)} nodes")
    
    def _create_node(self, file_path: str) -> DependencyNode:
        """Create node for file"""
        if file_path in self.nodes:
            return self.nodes[file_path]
        
        node = DependencyNode(file_path, "python")
        
        # Get file metadata
        try:
            stat = os.stat(file_path)
            node.last_modified = datetime.fromtimestamp(stat.st_mtime)
        except:
            pass
        
        self.nodes[file_path] = node
        return node
    
    def _analyze_dependencies(self, file_path: str) -> None:
        """Analyze dependencies of a file"""
        node = self.nodes.get(file_path)
        if not node:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST
            tree = ast.parse(content)
            
            # Extract imports
            for item in ast.walk(tree):
                if isinstance(item, ast.Import):
                    for alias in item.names:
                        node.imports.add(alias.name)
                        self._add_import_edge(file_path, alias.name)
                
                elif isinstance(item, ast.ImportFrom):
                    if item.module:
                        node.imports.add(item.module)
                        self._add_import_edge(file_path, item.module)
                
                elif isinstance(item, ast.FunctionDef):
                    node.functions.append(item.name)
                
                elif isinstance(item, ast.ClassDef):
                    node.classes.append(item.name)
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _add_import_edge(self, importer: str, imported_module: str) -> None:
        """Add edge between importer and imported"""
        # Try to resolve module to file path
        imported_file = self._resolve_module_to_file(imported_module)
        
        if imported_file and imported_file in self.nodes:
            # Add bidirectional edge
            self.nodes[importer].imports.add(imported_file)
            self.nodes[imported_file].imported_by.add(importer)
    
    def _resolve_module_to_file(self, module_name: str) -> Optional[str]:
        """Resolve module name to file path"""
        if not self.project_root:
            return None
        
        # Convert module name to file path
        # e.g., "core.dive_memory" -> "core/dive_memory.py"
        module_path = module_name.replace('.', os.sep) + '.py'
        full_path = os.path.join(self.project_root, module_path)
        
        if os.path.exists(full_path):
            return full_path
        
        # Try __init__.py
        init_path = os.path.join(self.project_root, module_name.replace('.', os.sep), '__init__.py')
        if os.path.exists(init_path):
            return init_path
        
        return None
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """
        Get files that this file depends on
        
        Args:
            file_path: Path to file
            
        Returns:
            List of file paths this file imports
        """
        node = self.nodes.get(file_path)
        if not node:
            return []
        
        return list(node.imports)
    
    def get_dependents(self, file_path: str) -> List[str]:
        """
        Get files that depend on this file
        
        Args:
            file_path: Path to file
            
        Returns:
            List of file paths that import this file
        """
        node = self.nodes.get(file_path)
        if not node:
            return []
        
        return list(node.imported_by)
    
    def get_transitive_dependencies(self, file_path: str, max_depth: int = 10) -> Set[str]:
        """
        Get all transitive dependencies (dependencies of dependencies)
        
        Args:
            file_path: Path to file
            max_depth: Maximum depth to traverse
            
        Returns:
            Set of all transitive dependencies
        """
        visited = set()
        to_visit = [(file_path, 0)]
        
        while to_visit:
            current, depth = to_visit.pop(0)
            
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            
            # Add dependencies to visit
            deps = self.get_dependencies(current)
            for dep in deps:
                if dep not in visited:
                    to_visit.append((dep, depth + 1))
        
        visited.discard(file_path)  # Remove self
        return visited
    
    def get_transitive_dependents(self, file_path: str, max_depth: int = 10) -> Set[str]:
        """
        Get all transitive dependents (dependents of dependents)
        
        Args:
            file_path: Path to file
            max_depth: Maximum depth to traverse
            
        Returns:
            Set of all transitive dependents
        """
        visited = set()
        to_visit = [(file_path, 0)]
        
        while to_visit:
            current, depth = to_visit.pop(0)
            
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            
            # Add dependents to visit
            deps = self.get_dependents(current)
            for dep in deps:
                if dep not in visited:
                    to_visit.append((dep, depth + 1))
        
        visited.discard(file_path)  # Remove self
        return visited
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the graph
        
        Returns:
            List of circular dependency chains
        """
        circles = []
        visited = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in path:
                # Found circle
                circle_start = path.index(node)
                circle = path[circle_start:] + [node]
                circles.append(circle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            # Visit dependencies
            deps = self.get_dependencies(node)
            for dep in deps:
                dfs(dep, path.copy())
        
        # Check each node
        for node in self.nodes:
            dfs(node, [])
        
        return circles
    
    def get_node_info(self, file_path: str) -> Optional[Dict]:
        """Get information about a node"""
        node = self.nodes.get(file_path)
        if not node:
            return None
        
        return {
            "file_path": node.file_path,
            "file_type": node.file_type,
            "functions": node.functions,
            "classes": node.classes,
            "imports_count": len(node.imports),
            "imported_by_count": len(node.imported_by),
            "last_modified": node.last_modified.isoformat() if node.last_modified else None
        }
    
    def search_by_function(self, function_name: str) -> List[str]:
        """Find files that define a function"""
        results = []
        for file_path, node in self.nodes.items():
            if function_name in node.functions:
                results.append(file_path)
        return results
    
    def search_by_class(self, class_name: str) -> List[str]:
        """Find files that define a class"""
        results = []
        for file_path, node in self.nodes.items():
            if class_name in node.classes:
                results.append(file_path)
        return results
    
    def export_graph(self, output_path: str) -> None:
        """Export graph to JSON file"""
        data = {
            "project_root": self.project_root,
            "nodes": {path: node.to_dict() for path, node in self.nodes.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Graph exported to {output_path}")
    
    def import_graph(self, input_path: str) -> None:
        """Import graph from JSON file"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.project_root = data["project_root"]
        self.nodes = {
            path: DependencyNode.from_dict(node_data)
            for path, node_data in data["nodes"].items()
        }
        
        print(f"Graph imported from {input_path}: {len(self.nodes)} nodes")
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        if not self.nodes:
            return {}
        
        total_imports = sum(len(node.imports) for node in self.nodes.values())
        total_functions = sum(len(node.functions) for node in self.nodes.values())
        total_classes = sum(len(node.classes) for node in self.nodes.values())
        
        # Find most imported files
        most_imported = sorted(
            self.nodes.items(),
            key=lambda x: len(x[1].imported_by),
            reverse=True
        )[:5]
        
        # Find files with most imports
        most_imports = sorted(
            self.nodes.items(),
            key=lambda x: len(x[1].imports),
            reverse=True
        )[:5]
        
        return {
            "total_files": len(self.nodes),
            "total_imports": total_imports,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "avg_imports_per_file": total_imports / len(self.nodes) if self.nodes else 0,
            "most_imported_files": [
                {"file": os.path.basename(path), "imported_by": len(node.imported_by)}
                for path, node in most_imported
            ],
            "files_with_most_imports": [
                {"file": os.path.basename(path), "imports": len(node.imports)}
                for path, node in most_imports
            ]
        }


if __name__ == "__main__":
    # Test dependency graph
    graph = DiveDependencyGraph()
    
    # Build graph for Dive AI
    project_path = "/home/ubuntu/dive-ai-messenger/Dive-Ai"
    graph.build_graph(project_path)
    
    # Get statistics
    stats = graph.get_statistics()
    print("\n=== Dependency Graph Statistics ===")
    print(f"Total files: {stats['total_files']}")
    print(f"Total imports: {stats['total_imports']}")
    print(f"Total functions: {stats['total_functions']}")
    print(f"Total classes: {stats['total_classes']}")
    print(f"Avg imports per file: {stats['avg_imports_per_file']:.2f}")
    
    print("\nMost imported files:")
    for item in stats['most_imported_files']:
        print(f"  {item['file']}: {item['imported_by']} imports")
    
    # Test dependency lookup
    test_file = os.path.join(project_path, "core/dive_memory_3file_complete.py")
    if os.path.exists(test_file):
        print(f"\n=== Testing with {os.path.basename(test_file)} ===")
        
        deps = graph.get_dependencies(test_file)
        print(f"Dependencies: {len(deps)}")
        for dep in deps[:5]:
            print(f"  - {os.path.basename(dep)}")
        
        dependents = graph.get_dependents(test_file)
        print(f"\nDependents: {len(dependents)}")
        for dep in dependents[:5]:
            print(f"  - {os.path.basename(dep)}")
    
    # Export graph
    graph.export_graph(os.path.join(project_path, "dependency_graph.json"))
