from __future__ import annotations
import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Optional

class DependencyAnalyzer:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.graph: Dict[str, Set[str]] = {}
        self.reverse_graph: Dict[str, Set[str]] = {}

    def analyze(self, files: List[str]):
        for f in files:
            p = Path(f).resolve()
            if p.suffix.lower() != '.py':
                continue
            
            rel_path = str(p.relative_to(self.repo_root))
            imports = self._get_imports(p)
            
            if rel_path not in self.graph:
                self.graph[rel_path] = set()
            
            for imp in imports:
                resolved = self._resolve_import(p.parent, imp)
                if resolved:
                    self.graph[rel_path].add(resolved)
                    if resolved not in self.reverse_graph:
                        self.reverse_graph[resolved] = set()
                    self.reverse_graph[resolved].add(rel_path)

    def _get_imports(self, file_path: Path) -> List[str]:
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8', errors='ignore'))
        except Exception:
            return []
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _resolve_import(self, current_dir: Path, import_name: str) -> Optional[str]:
        # Simple resolution: check if it's a local file
        parts = import_name.split('.')
        
        # Try relative to current dir
        potential_path = current_dir.joinpath(*parts).with_suffix('.py')
        if potential_path.exists():
            return str(potential_path.relative_to(self.repo_root))
        
        # Try relative to repo root
        potential_path = self.repo_root.joinpath(*parts).with_suffix('.py')
        if potential_path.exists():
            return str(potential_path.relative_to(self.repo_root))
            
        # Try as a package (__init__.py)
        potential_path = self.repo_root.joinpath(*parts, '__init__.py')
        if potential_path.exists():
            return str(potential_path.relative_to(self.repo_root))
            
        return None

    def get_all_dependencies(self, rel_path: str) -> Set[str]:
        deps = set()
        to_visit = [rel_path]
        while to_visit:
            curr = to_visit.pop()
            if curr in self.graph:
                for d in self.graph[curr]:
                    if d not in deps:
                        deps.add(d)
                        to_visit.append(d)
        return deps

    def get_impacted_files(self, rel_path: str) -> Set[str]:
        impacted = set()
        to_visit = [rel_path]
        while to_visit:
            curr = to_visit.pop()
            if curr in self.reverse_graph:
                for f in self.reverse_graph[curr]:
                    if f not in impacted:
                        impacted.add(f)
                        to_visit.append(f)
        return impacted
