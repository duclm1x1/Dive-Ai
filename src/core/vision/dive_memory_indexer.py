"""
Dive Memory Indexer - Index memory files (FULL.md, CRITERIA.md, CHANGELOG.md) for fast search

Part of Dive Search Engine - enables instant memory queries instead of reading entire files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import hashlib


class MemorySection:
    """Represents a section in memory file"""
    
    def __init__(self, title: str, level: int, content: str, line_start: int, line_end: int):
        self.title = title
        self.level = level  # Header level (1-6)
        self.content = content
        self.line_start = line_start
        self.line_end = line_end
        self.keywords: Set[str] = set()
        self.code_blocks: List[str] = []
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "level": self.level,
            "content": self.content,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "keywords": list(self.keywords),
            "code_blocks": self.code_blocks,
            "metadata": self.metadata
        }


class MemoryIndex:
    """Index for a memory file"""
    
    def __init__(self, file_path: str, file_type: str):
        self.file_path = file_path
        self.file_type = file_type  # FULL, CRITERIA, CHANGELOG
        self.project_name: Optional[str] = None
        self.version: Optional[str] = None
        self.last_modified: Optional[datetime] = None
        self.content_hash: Optional[str] = None
        self.sections: List[MemorySection] = []
        self.total_lines: int = 0
        self.features: List[str] = []
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "project_name": self.project_name,
            "version": self.version,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "content_hash": self.content_hash,
            "sections": [s.to_dict() for s in self.sections],
            "total_lines": self.total_lines,
            "features": self.features,
            "metadata": self.metadata
        }


class DiveMemoryIndexer:
    """
    Index memory files for fast search
    
    Features:
    - Parse Markdown structure (headers, sections)
    - Extract code blocks
    - Extract features and keywords
    - Support search by section, feature, keyword
    - Track file changes
    """
    
    def __init__(self):
        self.indexes: Dict[str, MemoryIndex] = {}
        self.memory_dir: Optional[str] = None
    
    def index_memory_dir(self, memory_dir: str) -> None:
        """
        Index all memory files in directory
        
        Args:
            memory_dir: Path to memory directory
        """
        self.memory_dir = memory_dir
        memory_path = Path(memory_dir)
        
        if not memory_path.exists():
            print(f"Memory directory not found: {memory_dir}")
            return
        
        # Find all memory files
        memory_files = []
        for pattern in ['*_FULL.md', '*_CRITERIA.md', '*_CHANGELOG.md']:
            memory_files.extend(memory_path.glob(pattern))
        
        print(f"Indexing {len(memory_files)} memory files...")
        
        for file_path in memory_files:
            self.index_memory_file(str(file_path))
        
        print(f"Memory indexing complete: {len(self.indexes)} files indexed")
    
    def index_memory_file(self, file_path: str) -> MemoryIndex:
        """
        Index a single memory file
        
        Args:
            file_path: Path to memory file
            
        Returns:
            MemoryIndex object
        """
        # Determine file type
        file_name = os.path.basename(file_path)
        if '_FULL.md' in file_name:
            file_type = 'FULL'
        elif '_CRITERIA.md' in file_name:
            file_type = 'CRITERIA'
        elif '_CHANGELOG.md' in file_name:
            file_type = 'CHANGELOG'
        else:
            file_type = 'UNKNOWN'
        
        # Create index
        index = MemoryIndex(file_path, file_type)
        
        # Extract project name from filename
        # e.g., "DIVE_AI_V21_FULL.md" -> "dive-ai-v21"
        project_match = re.match(r'(.+?)_(FULL|CRITERIA|CHANGELOG)\.md', file_name)
        if project_match:
            index.project_name = project_match.group(1).lower().replace('_', '-')
        
        # Get file metadata
        try:
            stat = os.stat(file_path)
            index.last_modified = datetime.fromtimestamp(stat.st_mtime)
        except:
            pass
        
        # Read and parse file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate content hash
            index.content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Count lines
            index.total_lines = content.count('\n') + 1
            
            # Parse based on file type
            if file_type == 'FULL':
                self._parse_full_file(index, content)
            elif file_type == 'CRITERIA':
                self._parse_criteria_file(index, content)
            elif file_type == 'CHANGELOG':
                self._parse_changelog_file(index, content)
            
            # Store index
            self.indexes[file_path] = index
            
        except Exception as e:
            print(f"Error indexing memory file {file_path}: {e}")
        
        return index
    
    def _parse_full_file(self, index: MemoryIndex, content: str) -> None:
        """Parse FULL.md file"""
        self._parse_markdown_sections(index, content)
        
        # Extract version
        version_match = re.search(r'Version:?\s*(\d+\.\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if version_match:
            index.version = version_match.group(1)
        
        # Extract features (look for "Features" section)
        for section in index.sections:
            if 'feature' in section.title.lower():
                # Extract bullet points as features
                features = re.findall(r'[-*]\s+(.+)', section.content)
                index.features.extend(features)
    
    def _parse_criteria_file(self, index: MemoryIndex, content: str) -> None:
        """Parse CRITERIA.md file"""
        self._parse_markdown_sections(index, content)
    
    def _parse_changelog_file(self, index: MemoryIndex, content: str) -> None:
        """Parse CHANGELOG.md file"""
        self._parse_markdown_sections(index, content)
        
        # Extract version entries
        versions = re.findall(r'##\s+(?:Version\s+)?(\d+\.\d+(?:\.\d+)?)', content)
        if versions:
            index.version = versions[0]  # Latest version
            index.metadata['all_versions'] = versions
    
    def _parse_markdown_sections(self, index: MemoryIndex, content: str) -> None:
        """Parse Markdown content into sections"""
        lines = content.split('\n')
        current_section = None
        section_content = []
        section_start = 0
        
        for i, line in enumerate(lines, 1):
            # Check for header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(section_content)
                    current_section.line_end = i - 1
                    self._extract_section_metadata(current_section)
                    index.sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = MemorySection(title, level, "", i, i)
                section_content = []
                section_start = i
            
            else:
                # Add to current section
                if current_section:
                    section_content.append(line)
        
        # Save last section
        if current_section:
            current_section.content = '\n'.join(section_content)
            current_section.line_end = len(lines)
            self._extract_section_metadata(current_section)
            index.sections.append(current_section)
    
    def _extract_section_metadata(self, section: MemorySection) -> None:
        """Extract metadata from section content"""
        # Extract code blocks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', section.content, re.DOTALL)
        section.code_blocks = code_blocks
        
        # Extract keywords (words longer than 3 chars, excluding common words)
        common_words = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'will', 'your', 'can', 'are', 'not', 'but', 'all', 'were', 'when', 'there', 'been', 'has', 'had', 'more', 'than', 'into', 'could', 'would', 'should'}
        
        words = re.findall(r'\b[a-zA-Z]{4,}\b', section.content.lower())
        section.keywords = {w for w in words if w not in common_words}
    
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        Search memory files
        
        Args:
            query: Search query
            filters: Optional filters (file_type, project, version, etc.)
            
        Returns:
            List of matching results with context
        """
        query_lower = query.lower()
        results = []
        
        for file_path, index in self.indexes.items():
            # Apply filters
            if filters:
                if 'file_type' in filters and index.file_type != filters['file_type']:
                    continue
                if 'project' in filters and index.project_name != filters['project']:
                    continue
                if 'version' in filters and index.version != filters['version']:
                    continue
            
            # Search in sections
            for section in index.sections:
                score = 0
                
                # Title match
                if query_lower in section.title.lower():
                    score += 10
                
                # Content match
                if query_lower in section.content.lower():
                    score += 5
                
                # Keyword match
                for keyword in section.keywords:
                    if query_lower in keyword:
                        score += 2
                
                if score > 0:
                    results.append({
                        "file_path": file_path,
                        "file_type": index.file_type,
                        "project": index.project_name,
                        "version": index.version,
                        "section_title": section.title,
                        "section_level": section.level,
                        "line_start": section.line_start,
                        "line_end": section.line_end,
                        "content": section.content[:500],  # First 500 chars
                        "score": score
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def search_by_feature(self, feature: str) -> List[Dict]:
        """Search for a specific feature"""
        results = []
        
        for file_path, index in self.indexes.items():
            if index.file_type != 'FULL':
                continue
            
            for feat in index.features:
                if feature.lower() in feat.lower():
                    results.append({
                        "file_path": file_path,
                        "project": index.project_name,
                        "version": index.version,
                        "feature": feat
                    })
        
        return results
    
    def get_section(self, file_path: str, section_title: str) -> Optional[Dict]:
        """Get a specific section from memory file"""
        index = self.indexes.get(file_path)
        if not index:
            return None
        
        for section in index.sections:
            if section_title.lower() in section.title.lower():
                return section.to_dict()
        
        return None
    
    def get_relevant_context(self, query: str, max_sections: int = 5) -> str:
        """
        Get relevant context for a query
        
        Args:
            query: Query string
            max_sections: Maximum number of sections to return
            
        Returns:
            Combined context from relevant sections
        """
        results = self.search(query)[:max_sections]
        
        context_parts = []
        for result in results:
            context_parts.append(f"## {result['section_title']}\n{result['content']}\n")
        
        return '\n'.join(context_parts)
    
    def get_statistics(self) -> Dict:
        """Get indexing statistics"""
        if not self.indexes:
            return {}
        
        total_sections = sum(len(idx.sections) for idx in self.indexes.values())
        total_lines = sum(idx.total_lines for idx in self.indexes.values())
        total_features = sum(len(idx.features) for idx in self.indexes.values())
        
        # Count by file type
        type_counts = {}
        for index in self.indexes.values():
            type_counts[index.file_type] = type_counts.get(index.file_type, 0) + 1
        
        # Count projects
        projects = set(idx.project_name for idx in self.indexes.values() if idx.project_name)
        
        return {
            "total_files": len(self.indexes),
            "total_sections": total_sections,
            "total_lines": total_lines,
            "total_features": total_features,
            "file_types": type_counts,
            "projects": list(projects),
            "avg_sections_per_file": total_sections / len(self.indexes) if self.indexes else 0
        }


if __name__ == "__main__":
    # Test memory indexer
    indexer = DiveMemoryIndexer()
    
    # Index memory directory
    memory_dir = "/home/ubuntu/dive-ai-messenger/Dive-Ai/memory"
    if os.path.exists(memory_dir):
        indexer.index_memory_dir(memory_dir)
        
        # Get statistics
        stats = indexer.get_statistics()
        print("\n=== Memory Indexer Statistics ===")
        print(f"Total files: {stats['total_files']}")
        print(f"Total sections: {stats['total_sections']}")
        print(f"Total lines: {stats['total_lines']}")
        print(f"Total features: {stats['total_features']}")
        print(f"File types: {stats['file_types']}")
        print(f"Projects: {stats['projects']}")
        print(f"Avg sections per file: {stats['avg_sections_per_file']:.2f}")
        
        # Test search
        print("\n=== Testing Search ===")
        results = indexer.search("orchestrator")
        print(f"Search 'orchestrator': {len(results)} results")
        for result in results[:3]:
            print(f"\n  File: {result['file_type']}")
            print(f"  Section: {result['section_title']}")
            print(f"  Score: {result['score']}")
            print(f"  Content preview: {result['content'][:100]}...")
        
        # Test context retrieval
        print("\n=== Testing Context Retrieval ===")
        context = indexer.get_relevant_context("memory system", max_sections=2)
        print(f"Context length: {len(context)} chars")
        print(f"Preview:\n{context[:300]}...")
    else:
        print(f"Memory directory not found: {memory_dir}")
