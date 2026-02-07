#!/usr/bin/env python3
"""
Dive Dependency Tracker
Tracks relationships between files in the Dive AI system
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FileDependency:
    """Represents a file and its dependencies"""
    file_path: str
    imports: List[str]
    imported_by: List[str]
    functions_defined: List[str]
    functions_used: Dict[str, List[str]]
    version: str
    last_modified: float
    
    def to_dict(self):
        return asdict(self)


class DiveDependencyTracker:
    """
    Tracks dependencies between Python files
    Builds relationship graph for impact analysis
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getcwd()
        self.dependencies: Dict[str, FileDependency] = {}
        self.graph = {"nodes": [], "edges": []}
        
    def scan_project(self, exclude_dirs: List[str] = None) -> Dict[str, FileDependency]:
        """
        Scan entire project for dependencies
        
        Args:
            exclude_dirs: Directories to exclude from scanning
            
        Returns:
            Dictionary of file paths to FileDependency objects
        """
        exclude_dirs = exclude_dirs or [
            "__pycache__", ".git", "venv", "env", 
            "node_modules", ".pytest_cache", "memory"
        ]
        
        print("🔍 Scanning project for dependencies...")
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    python_files.append(rel_path)
        
        print(f"   Found {len(python_files)} Python files")
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        # Build reverse dependencies (imported_by)
        self._build_reverse_dependencies()
        
        # Build graph
        self._build_graph()
        
        print(f"   ✅ Dependency analysis complete")
        print(f"   📊 {len(self.dependencies)} files analyzed")
        
        return self.dependencies
    
    def _analyze_file(self, file_path: str):
        """Analyze a single Python file for dependencies"""
        full_path = os.path.join(self.root_dir, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=file_path)
            
            # Extract imports
            imports = self._extract_imports(tree, file_path)
            
            # Extract function definitions
            functions_defined = self._extract_functions(tree)
            
            # Extract version (if defined)
            version = self._extract_version(content)
            
            # Get last modified time
            last_modified = os.path.getmtime(full_path)
            
            # Create dependency object
            dep = FileDependency(
                file_path=file_path,
                imports=imports,
                imported_by=[],  # Will be filled later
                functions_defined=functions_defined,
                functions_used={},  # TODO: Implement function call tracking
                version=version,
                last_modified=last_modified
            )
            
            self.dependencies[file_path] = dep
            
        except Exception as e:
            print(f"   ⚠️  Error analyzing {file_path}: {e}")
    
    def _extract_imports(self, tree: ast.AST, current_file: str) -> List[str]:
        """Extract import statements from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Convert module names to file paths
        file_imports = []
        for imp in imports:
            # Convert module path to file path
            # e.g., "core.dive_memory" -> "core/dive_memory.py"
            file_path = imp.replace('.', '/') + '.py'
            
            # Check if file exists in project
            full_path = os.path.join(self.root_dir, file_path)
            if os.path.exists(full_path):
                file_imports.append(file_path)
            else:
                # Try as package
                package_path = imp.replace('.', '/') + '/__init__.py'
                full_package_path = os.path.join(self.root_dir, package_path)
                if os.path.exists(full_package_path):
                    file_imports.append(package_path)
        
        return file_imports
    
    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract function definitions from AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return functions
    
    def _extract_version(self, content: str) -> str:
        """Extract version string from file content"""
        # Look for VERSION = "x.x.x" or __version__ = "x.x.x"
        patterns = [
            r'VERSION\s*=\s*["\']([0-9.]+)["\']',
            r'__version__\s*=\s*["\']([0-9.]+)["\']',
            r'version\s*=\s*["\']([0-9.]+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _build_reverse_dependencies(self):
        """Build reverse dependency mapping (imported_by)"""
        for file_path, dep in self.dependencies.items():
            for imported_file in dep.imports:
                if imported_file in self.dependencies:
                    self.dependencies[imported_file].imported_by.append(file_path)
    
    def _build_graph(self):
        """Build graph representation of dependencies"""
        # Add nodes
        for file_path, dep in self.dependencies.items():
            self.graph["nodes"].append({
                "id": file_path,
                "type": self._get_file_type(file_path),
                "version": dep.version,
                "functions": len(dep.functions_defined)
            })
        
        # Add edges
        for file_path, dep in self.dependencies.items():
            for imported_file in dep.imports:
                self.graph["edges"].append({
                    "from": file_path,
                    "to": imported_file,
                    "type": "imports"
                })
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on path"""
        if file_path.startswith('core/'):
            return 'core'
        elif file_path.startswith('integration/'):
            return 'integration'
        elif file_path.startswith('test'):
            return 'test'
        elif file_path.endswith('.sh'):
            return 'script'
        else:
            return 'other'
    
    def get_dependents(self, file_path: str) -> List[str]:
        """Get all files that depend on the given file"""
        if file_path not in self.dependencies:
            return []
        
        return self.dependencies[file_path].imported_by
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get all files that the given file depends on"""
        if file_path not in self.dependencies:
            return []
        
        return self.dependencies[file_path].imports
    
    def get_transitive_dependents(self, file_path: str, visited: Set[str] = None) -> Set[str]:
        """
        Get all files that transitively depend on the given file
        (i.e., files that depend on this file, and files that depend on those, etc.)
        """
        if visited is None:
            visited = set()
        
        if file_path in visited:
            return visited
        
        visited.add(file_path)
        
        dependents = self.get_dependents(file_path)
        for dependent in dependents:
            self.get_transitive_dependents(dependent, visited)
        
        return visited
    
    def save_graph(self, output_path: str):
        """Save dependency graph to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=2)
        
        print(f"   💾 Dependency graph saved: {output_path}")
    
    def save_dependencies(self, output_path: str):
        """Save full dependency data to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = {
            file_path: dep.to_dict()
            for file_path, dep in self.dependencies.items()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"   💾 Dependencies saved: {output_path}")
    
    def print_summary(self):
        """Print summary of dependencies"""
        print("\n" + "="*80)
        print("📊 DEPENDENCY SUMMARY")
        print("="*80)
        
        # Count file types
        type_counts = {}
        for dep in self.dependencies.values():
            file_type = self._get_file_type(dep.file_path)
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        print("\n📁 Files by Type:")
        for file_type, count in sorted(type_counts.items()):
            print(f"   {file_type}: {count}")
        
        # Find most imported files
        most_imported = sorted(
            self.dependencies.items(),
            key=lambda x: len(x[1].imported_by),
            reverse=True
        )[:5]
        
        print("\n🔗 Most Imported Files:")
        for file_path, dep in most_imported:
            print(f"   {file_path}: {len(dep.imported_by)} dependents")
        
        # Find files with most imports
        most_imports = sorted(
            self.dependencies.items(),
            key=lambda x: len(x[1].imports),
            reverse=True
        )[:5]
        
        print("\n📥 Files with Most Imports:")
        for file_path, dep in most_imports:
            print(f"   {file_path}: {len(dep.imports)} imports")
        
        print("\n" + "="*80)


def main():
    """Test dependency tracker"""
    tracker = DiveDependencyTracker()
    
    # Scan project
    dependencies = tracker.scan_project()
    
    # Print summary
    tracker.print_summary()
    
    # Save outputs
    tracker.save_graph("memory/file_tracking/dependency_graph.json")
    tracker.save_dependencies("memory/file_tracking/file_dependencies.json")
    
    # Test: Find dependents of a core file
    test_file = "core/dive_memory_3file_complete.py"
    if test_file in dependencies:
        print(f"\n🔍 Testing: Files that depend on {test_file}")
        dependents = tracker.get_transitive_dependents(test_file)
        dependents.remove(test_file)  # Remove self
        print(f"   Found {len(dependents)} dependent files:")
        for dep in sorted(dependents)[:10]:
            print(f"   - {dep}")


if __name__ == "__main__":
    main()
