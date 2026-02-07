"""
Dive File Indexer - AST-based file indexing for search

Part of Dive Search Engine - indexes Python files with structure analysis.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import hashlib


class FileIndex:
    """Index entry for a single file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_type = self._detect_file_type(file_path)
        self.content_hash: Optional[str] = None
        self.last_modified: Optional[datetime] = None
        self.size: int = 0
        
        # Python-specific
        self.imports: Set[str] = set()
        self.classes: List[Dict] = []
        self.functions: List[Dict] = []
        self.variables: List[str] = []
        self.docstring: Optional[str] = None
        
        # General
        self.lines: int = 0
        self.keywords: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from extension"""
        ext = Path(file_path).suffix.lower()
        type_map = {
            '.py': 'python',
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sh': 'shell',
            '.js': 'javascript',
            '.ts': 'typescript'
        }
        return type_map.get(ext, 'unknown')
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "content_hash": self.content_hash,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "size": self.size,
            "imports": list(self.imports),
            "classes": self.classes,
            "functions": self.functions,
            "variables": self.variables,
            "docstring": self.docstring,
            "lines": self.lines,
            "keywords": list(self.keywords),
            "metadata": self.metadata
        }


class DiveFileIndexer:
    """
    AST-based file indexer for search
    
    Features:
    - Index Python files with AST analysis
    - Extract imports, classes, functions
    - Extract docstrings and metadata
    - Track file changes with hashing
    - Support incremental indexing
    """
    
    def __init__(self):
        self.indexes: Dict[str, FileIndex] = {}
        self.project_root: Optional[str] = None
    
    def index_project(self, project_path: str, extensions: List[str] = None) -> None:
        """
        Index all files in project
        
        Args:
            project_path: Root path of project
            extensions: List of file extensions to index (default: ['.py'])
        """
        if extensions is None:
            extensions = ['.py']
        
        self.project_root = project_path
        project_path_obj = Path(project_path)
        
        # Find all files with specified extensions
        files = []
        for ext in extensions:
            files.extend(project_path_obj.rglob(f"*{ext}"))
        
        print(f"Indexing {len(files)} files...")
        
        for file_path in files:
            self.index_file(str(file_path))
        
        print(f"Indexing complete: {len(self.indexes)} files indexed")
    
    def index_file(self, file_path: str) -> FileIndex:
        """
        Index a single file
        
        Args:
            file_path: Path to file
            
        Returns:
            FileIndex object
        """
        # Check if file needs reindexing
        if file_path in self.indexes:
            existing = self.indexes[file_path]
            if not self._needs_reindex(file_path, existing):
                return existing
        
        # Create new index
        index = FileIndex(file_path)
        
        # Get file metadata
        try:
            stat = os.stat(file_path)
            index.last_modified = datetime.fromtimestamp(stat.st_mtime)
            index.size = stat.st_size
        except:
            pass
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate content hash
            index.content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Count lines
            index.lines = content.count('\n') + 1
            
            # Index based on file type
            if index.file_type == 'python':
                self._index_python_file(index, content)
            elif index.file_type == 'markdown':
                self._index_markdown_file(index, content)
            else:
                self._index_text_file(index, content)
            
            # Store index
            self.indexes[file_path] = index
            
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
        
        return index
    
    def _needs_reindex(self, file_path: str, existing: FileIndex) -> bool:
        """Check if file needs reindexing"""
        try:
            stat = os.stat(file_path)
            current_mtime = datetime.fromtimestamp(stat.st_mtime)
            
            if existing.last_modified and current_mtime > existing.last_modified:
                return True
            
            # Check content hash
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            current_hash = hashlib.md5(content.encode()).hexdigest()
            
            return current_hash != existing.content_hash
        except:
            return True
    
    def _index_python_file(self, index: FileIndex, content: str) -> None:
        """Index Python file with AST"""
        try:
            tree = ast.parse(content)
            
            # Extract module docstring
            if ast.get_docstring(tree):
                index.docstring = ast.get_docstring(tree)
            
            # Walk AST
            for node in ast.walk(tree):
                # Imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        index.imports.add(alias.name)
                        index.keywords.add(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        index.imports.add(node.module)
                        index.keywords.add(node.module)
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "lineno": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "methods": [],
                        "bases": [self._get_name(base) for base in node.bases]
                    }
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(item.name)
                    
                    index.classes.append(class_info)
                    index.keywords.add(node.name)
                
                # Functions
                elif isinstance(node, ast.FunctionDef):
                    # Skip methods (already captured in classes)
                    if not any(node.name in cls["methods"] for cls in index.classes):
                        func_info = {
                            "name": node.name,
                            "lineno": node.lineno,
                            "docstring": ast.get_docstring(node),
                            "args": [arg.arg for arg in node.args.args],
                            "returns": self._get_name(node.returns) if node.returns else None
                        }
                        index.functions.append(func_info)
                        index.keywords.add(node.name)
                
                # Variables (module level)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            index.variables.append(target.id)
                            index.keywords.add(target.id)
        
        except Exception as e:
            print(f"Error parsing Python file: {e}")
    
    def _get_name(self, node) -> Optional[str]:
        """Get name from AST node"""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return None
    
    def _index_markdown_file(self, index: FileIndex, content: str) -> None:
        """Index Markdown file"""
        lines = content.split('\n')
        
        # Extract headers as keywords
        for line in lines:
            if line.startswith('#'):
                header = line.lstrip('#').strip()
                index.keywords.add(header)
        
        # Extract code blocks
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
    
    def _index_text_file(self, index: FileIndex, content: str) -> None:
        """Index plain text file"""
        # Extract common words as keywords
        words = content.split()
        common_words = set()
        
        for word in words:
            # Clean word
            word = word.strip('.,!?;:()[]{}"\'-').lower()
            if len(word) > 3:  # Only words longer than 3 chars
                common_words.add(word)
        
        # Keep top keywords
        index.keywords = common_words
    
    def search(self, query: str, filters: Dict = None) -> List[FileIndex]:
        """
        Search indexed files
        
        Args:
            query: Search query
            filters: Optional filters (file_type, has_class, has_function, etc.)
            
        Returns:
            List of matching FileIndex objects
        """
        query_lower = query.lower()
        results = []
        
        for file_path, index in self.indexes.items():
            # Apply filters
            if filters:
                if 'file_type' in filters and index.file_type != filters['file_type']:
                    continue
                if 'has_class' in filters:
                    if not any(filters['has_class'].lower() in cls['name'].lower() for cls in index.classes):
                        continue
                if 'has_function' in filters:
                    if not any(filters['has_function'].lower() in func['name'].lower() for func in index.functions):
                        continue
                if 'imports' in filters:
                    if filters['imports'] not in index.imports:
                        continue
            
            # Search in various fields
            score = 0
            
            # File name match
            if query_lower in os.path.basename(file_path).lower():
                score += 10
            
            # Class name match
            for cls in index.classes:
                if query_lower in cls['name'].lower():
                    score += 5
            
            # Function name match
            for func in index.functions:
                if query_lower in func['name'].lower():
                    score += 5
            
            # Import match
            for imp in index.imports:
                if query_lower in imp.lower():
                    score += 3
            
            # Keyword match
            for keyword in index.keywords:
                if query_lower in keyword.lower():
                    score += 1
            
            # Docstring match
            if index.docstring and query_lower in index.docstring.lower():
                score += 2
            
            if score > 0:
                index.metadata['search_score'] = score
                results.append(index)
        
        # Sort by score
        results.sort(key=lambda x: x.metadata.get('search_score', 0), reverse=True)
        
        return results
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get information about indexed file"""
        index = self.indexes.get(file_path)
        if not index:
            return None
        
        return index.to_dict()
    
    def get_statistics(self) -> Dict:
        """Get indexing statistics"""
        if not self.indexes:
            return {}
        
        total_lines = sum(idx.lines for idx in self.indexes.values())
        total_classes = sum(len(idx.classes) for idx in self.indexes.values())
        total_functions = sum(len(idx.functions) for idx in self.indexes.values())
        total_imports = sum(len(idx.imports) for idx in self.indexes.values())
        
        return {
            "total_files": len(self.indexes),
            "total_lines": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "total_imports": total_imports,
            "avg_lines_per_file": total_lines / len(self.indexes) if self.indexes else 0,
            "file_types": self._count_file_types()
        }
    
    def _count_file_types(self) -> Dict[str, int]:
        """Count files by type"""
        types = {}
        for index in self.indexes.values():
            types[index.file_type] = types.get(index.file_type, 0) + 1
        return types


if __name__ == "__main__":
    # Test file indexer
    indexer = DiveFileIndexer()
    
    # Index Dive AI project
    project_path = "/home/ubuntu/dive-ai-messenger/Dive-Ai"
    indexer.index_project(project_path)
    
    # Get statistics
    stats = indexer.get_statistics()
    print("\n=== File Indexer Statistics ===")
    print(f"Total files: {stats['total_files']}")
    print(f"Total lines: {stats['total_lines']}")
    print(f"Total classes: {stats['total_classes']}")
    print(f"Total functions: {stats['total_functions']}")
    print(f"Total imports: {stats['total_imports']}")
    print(f"Avg lines per file: {stats['avg_lines_per_file']:.2f}")
    print(f"\nFile types: {stats['file_types']}")
    
    # Test search
    print("\n=== Testing Search ===")
    results = indexer.search("DiveMemory")
    print(f"Search 'DiveMemory': {len(results)} results")
    for result in results[:5]:
        print(f"  - {os.path.basename(result.file_path)} (score: {result.metadata.get('search_score', 0)})")
    
    # Test with filters
    results = indexer.search("", filters={"has_class": "DiveMemory"})
    print(f"\nFiles with class 'DiveMemory': {len(results)} results")
    for result in results[:5]:
        print(f"  - {os.path.basename(result.file_path)}")
