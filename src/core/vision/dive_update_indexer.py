"""
Dive Update Indexer - Index and track code changes for search

Part of Dive Search Engine - enables instant change lookup and breaking change detection.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum


class ChangeType(Enum):
    """Types of changes"""
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    RENAMED = "RENAMED"


class ChangeCategory(Enum):
    """Categories of changes"""
    FEATURE = "FEATURE"
    BUGFIX = "BUGFIX"
    REFACTOR = "REFACTOR"
    BREAKING = "BREAKING"
    PERFORMANCE = "PERFORMANCE"
    DOCUMENTATION = "DOCUMENTATION"
    TEST = "TEST"
    DEPENDENCY = "DEPENDENCY"


class ChangeRecord:
    """Record of a single change"""
    
    def __init__(self, change_id: str):
        self.change_id = change_id
        self.timestamp: datetime = datetime.now()
        self.change_type: ChangeType = ChangeType.MODIFIED
        self.category: ChangeCategory = ChangeCategory.FEATURE
        self.file_path: str = ""
        self.description: str = ""
        self.breaking: bool = False
        self.related_files: List[str] = []
        self.affected_components: List[str] = []
        self.version: Optional[str] = None
        self.author: Optional[str] = None
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "change_id": self.change_id,
            "timestamp": self.timestamp.isoformat(),
            "change_type": self.change_type.value,
            "category": self.category.value,
            "file_path": self.file_path,
            "description": self.description,
            "breaking": self.breaking,
            "related_files": self.related_files,
            "affected_components": self.affected_components,
            "version": self.version,
            "author": self.author,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChangeRecord':
        """Create from dictionary"""
        record = cls(data["change_id"])
        record.timestamp = datetime.fromisoformat(data["timestamp"])
        record.change_type = ChangeType(data["change_type"])
        record.category = ChangeCategory(data["category"])
        record.file_path = data["file_path"]
        record.description = data["description"]
        record.breaking = data["breaking"]
        record.related_files = data["related_files"]
        record.affected_components = data["affected_components"]
        record.version = data.get("version")
        record.author = data.get("author")
        record.metadata = data.get("metadata", {})
        return record


class DiveUpdateIndexer:
    """
    Index and track code changes for search
    
    Features:
    - Track all code changes
    - Categorize changes (feature, bugfix, breaking, etc.)
    - Track affected files and components
    - Search changes by type, category, file, version
    - Detect breaking changes
    - Generate change notifications
    """
    
    def __init__(self, storage_path: str = None):
        self.changes: Dict[str, ChangeRecord] = {}
        self.storage_path = storage_path or "dive_changes.json"
        self.next_change_id = 1
        
        # Load existing changes
        self.load()
    
    def track_change(self, file_path: str, change_type: str, category: str, 
                     description: str, breaking: bool = False, 
                     related_files: List[str] = None, version: str = None) -> ChangeRecord:
        """
        Track a new change
        
        Args:
            file_path: Path to changed file
            change_type: Type of change (ADDED, MODIFIED, DELETED, RENAMED)
            category: Category (FEATURE, BUGFIX, REFACTOR, etc.)
            description: Description of change
            breaking: Whether this is a breaking change
            related_files: List of related files
            version: Version number
            
        Returns:
            ChangeRecord object
        """
        # Generate change ID
        change_id = f"change_{self.next_change_id}"
        self.next_change_id += 1
        
        # Create record
        record = ChangeRecord(change_id)
        record.file_path = file_path
        record.change_type = ChangeType[change_type.upper()]
        record.category = ChangeCategory[category.upper()]
        record.description = description
        record.breaking = breaking
        record.related_files = related_files or []
        record.version = version
        
        # Detect affected components
        record.affected_components = self._detect_affected_components(file_path)
        
        # Store record
        self.changes[change_id] = record
        
        # Save to disk
        self.save()
        
        return record
    
    def _detect_affected_components(self, file_path: str) -> List[str]:
        """Detect which components are affected by file change"""
        components = []
        
        # Map file paths to components
        component_map = {
            'dive_memory': ['memory', 'storage'],
            'dive_orchestrator': ['orchestrator', 'routing', 'task_management'],
            'dive_coder': ['coder', 'code_generation'],
            'dive_update': ['update', 'dependency_tracking'],
            'dive_search': ['search', 'indexing']
        }
        
        file_name = os.path.basename(file_path).lower()
        
        for key, comps in component_map.items():
            if key in file_name:
                components.extend(comps)
        
        return components
    
    def search(self, query: str = None, filters: Dict = None) -> List[ChangeRecord]:
        """
        Search changes
        
        Args:
            query: Search query (searches in description and file path)
            filters: Optional filters (type, category, breaking, version, etc.)
            
        Returns:
            List of matching ChangeRecord objects
        """
        results = []
        
        for change_id, record in self.changes.items():
            # Apply filters
            if filters:
                if 'type' in filters and record.change_type.value != filters['type']:
                    continue
                if 'category' in filters and record.category.value != filters['category']:
                    continue
                if 'breaking' in filters and record.breaking != filters['breaking']:
                    continue
                if 'version' in filters and record.version != filters['version']:
                    continue
                if 'component' in filters and filters['component'] not in record.affected_components:
                    continue
                if 'file' in filters and filters['file'] not in record.file_path:
                    continue
            
            # Apply query
            if query:
                query_lower = query.lower()
                if (query_lower not in record.description.lower() and 
                    query_lower not in record.file_path.lower() and
                    not any(query_lower in comp.lower() for comp in record.affected_components)):
                    continue
            
            results.append(record)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        return results
    
    def get_breaking_changes(self, version: str = None) -> List[ChangeRecord]:
        """Get all breaking changes, optionally filtered by version"""
        filters = {'breaking': True}
        if version:
            filters['version'] = version
        
        return self.search(filters=filters)
    
    def get_changes_for_file(self, file_path: str) -> List[ChangeRecord]:
        """Get all changes for a specific file"""
        return self.search(filters={'file': file_path})
    
    def get_related_changes(self, file_path: str) -> List[ChangeRecord]:
        """Get changes related to a file (including related_files)"""
        results = []
        
        for record in self.changes.values():
            if (record.file_path == file_path or 
                file_path in record.related_files):
                results.append(record)
        
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results
    
    def get_changes_by_component(self, component: str) -> List[ChangeRecord]:
        """Get changes affecting a specific component"""
        return self.search(filters={'component': component})
    
    def get_recent_changes(self, limit: int = 10) -> List[ChangeRecord]:
        """Get most recent changes"""
        all_changes = list(self.changes.values())
        all_changes.sort(key=lambda x: x.timestamp, reverse=True)
        return all_changes[:limit]
    
    def generate_notification(self, change_id: str) -> Dict:
        """
        Generate notification for a change
        
        Args:
            change_id: ID of change
            
        Returns:
            Notification dictionary
        """
        record = self.changes.get(change_id)
        if not record:
            return {}
        
        notification = {
            "type": "CHANGE_NOTIFICATION",
            "change_id": record.change_id,
            "timestamp": record.timestamp.isoformat(),
            "severity": "HIGH" if record.breaking else "NORMAL",
            "title": f"{record.category.value}: {os.path.basename(record.file_path)}",
            "description": record.description,
            "breaking": record.breaking,
            "affected_components": record.affected_components,
            "related_files": record.related_files,
            "action_required": record.breaking
        }
        
        return notification
    
    def get_change_summary(self, version: str = None) -> Dict:
        """
        Get summary of changes
        
        Args:
            version: Optional version to filter by
            
        Returns:
            Summary dictionary
        """
        filters = {}
        if version:
            filters['version'] = version
        
        changes = self.search(filters=filters)
        
        # Count by type
        type_counts = {}
        for record in changes:
            type_counts[record.change_type.value] = type_counts.get(record.change_type.value, 0) + 1
        
        # Count by category
        category_counts = {}
        for record in changes:
            category_counts[record.category.value] = category_counts.get(record.category.value, 0) + 1
        
        # Count breaking changes
        breaking_count = sum(1 for r in changes if r.breaking)
        
        # Affected components
        all_components = set()
        for record in changes:
            all_components.update(record.affected_components)
        
        return {
            "total_changes": len(changes),
            "breaking_changes": breaking_count,
            "type_counts": type_counts,
            "category_counts": category_counts,
            "affected_components": list(all_components),
            "version": version
        }
    
    def save(self) -> None:
        """Save changes to disk"""
        data = {
            "next_change_id": self.next_change_id,
            "changes": {cid: record.to_dict() for cid, record in self.changes.items()}
        }
        
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving changes: {e}")
    
    def load(self) -> None:
        """Load changes from disk"""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.next_change_id = data.get("next_change_id", 1)
            self.changes = {
                cid: ChangeRecord.from_dict(record_data)
                for cid, record_data in data.get("changes", {}).items()
            }
            
            print(f"Loaded {len(self.changes)} changes from {self.storage_path}")
        except Exception as e:
            print(f"Error loading changes: {e}")
    
    def clear(self) -> None:
        """Clear all changes"""
        self.changes = {}
        self.next_change_id = 1
        self.save()
    
    def get_statistics(self) -> Dict:
        """Get statistics about tracked changes"""
        if not self.changes:
            return {}
        
        all_changes = list(self.changes.values())
        
        # Count by type
        type_counts = {}
        for record in all_changes:
            type_counts[record.change_type.value] = type_counts.get(record.change_type.value, 0) + 1
        
        # Count by category
        category_counts = {}
        for record in all_changes:
            category_counts[record.category.value] = category_counts.get(record.category.value, 0) + 1
        
        # Breaking changes
        breaking_count = sum(1 for r in all_changes if r.breaking)
        
        # Versions
        versions = set(r.version for r in all_changes if r.version)
        
        return {
            "total_changes": len(all_changes),
            "breaking_changes": breaking_count,
            "type_counts": type_counts,
            "category_counts": category_counts,
            "versions": list(versions),
            "oldest_change": min(r.timestamp for r in all_changes).isoformat(),
            "newest_change": max(r.timestamp for r in all_changes).isoformat()
        }


if __name__ == "__main__":
    # Test update indexer
    indexer = DiveUpdateIndexer("test_changes.json")
    
    # Clear existing data
    indexer.clear()
    
    # Track some changes
    print("=== Tracking Changes ===")
    
    change1 = indexer.track_change(
        file_path="core/dive_memory_3file_complete.py",
        change_type="MODIFIED",
        category="REFACTOR",
        description="Refactored to 3-file structure",
        breaking=True,
        related_files=["dive_smart_orchestrator.py", "dive_smart_coder.py"],
        version="21.0"
    )
    print(f"Tracked change: {change1.change_id}")
    
    change2 = indexer.track_change(
        file_path="core/dive_smart_orchestrator.py",
        change_type="MODIFIED",
        category="FEATURE",
        description="Added search-driven routing",
        breaking=False,
        version="21.0"
    )
    print(f"Tracked change: {change2.change_id}")
    
    change3 = indexer.track_change(
        file_path="core/dive_search_engine.py",
        change_type="ADDED",
        category="FEATURE",
        description="Added Dive Search Engine",
        breaking=False,
        version="21.0"
    )
    print(f"Tracked change: {change3.change_id}")
    
    # Get statistics
    stats = indexer.get_statistics()
    print("\n=== Statistics ===")
    print(f"Total changes: {stats['total_changes']}")
    print(f"Breaking changes: {stats['breaking_changes']}")
    print(f"Type counts: {stats['type_counts']}")
    print(f"Category counts: {stats['category_counts']}")
    
    # Search for breaking changes
    print("\n=== Breaking Changes ===")
    breaking = indexer.get_breaking_changes()
    for record in breaking:
        print(f"  {record.change_id}: {record.description}")
        print(f"    Affected: {', '.join(record.affected_components)}")
    
    # Get change summary
    print("\n=== Change Summary for v21.0 ===")
    summary = indexer.get_change_summary(version="21.0")
    print(f"Total changes: {summary['total_changes']}")
    print(f"Breaking changes: {summary['breaking_changes']}")
    print(f"Affected components: {', '.join(summary['affected_components'])}")
    
    # Generate notification
    print("\n=== Notification Example ===")
    notification = indexer.generate_notification(change1.change_id)
    print(json.dumps(notification, indent=2))
