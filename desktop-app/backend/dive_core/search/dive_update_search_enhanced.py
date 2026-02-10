"""
Dive Update System - Search-Enhanced Version

Extends Dive Update System with search engine integration for:
- Instant dependency lookup (no file scanning)
- Project-aware tracking (Dive AI core vs working projects)
- Cross-project impact analysis
- Historical change search
"""

import os
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path

try:
    from .dive_update_system import DiveUpdateSystem
    from .dive_search_engine import get_search_engine
    from .dive_update_indexer import DiveUpdateIndexer
except ImportError:
    try:
        from dive_core.search.dive_update_system import DiveUpdateSystem
        from dive_core.search.dive_search_engine import get_search_engine
        from dive_core.search.dive_update_indexer import DiveUpdateIndexer
    except ImportError:
        from dive_update_system import DiveUpdateSystem
        from dive_search_engine import get_search_engine
        from dive_update_indexer import DiveUpdateIndexer




class DiveUpdateSearchEnhanced(DiveUpdateSystem):
    """
    Search-Enhanced Update System
    
    Extends update system with:
    - Search-driven dependency tracking
    - Instant dependency graph lookup
    - Project-aware tracking
    - Cross-project impact analysis
    """
    
    def __init__(self):
        """Initialize search-enhanced update system"""
        # Initialize base update system
        super().__init__()
        
        # Initialize search engine
        project_root = Path(__file__).parent.parent
        self.search_engine = get_search_engine(str(project_root))
        
        # Initialize if not ready
        if not self.search_engine.ready:
            print("🔍 Initializing search engine for update system...")
            self.search_engine.initialize(str(project_root))
        
        # Dive AI core path
        self.dive_ai_root = str(project_root)
    
    def analyze_impact(self, changed_file: str, change_description: str = "") -> Dict:
        """
        Analyze impact with search-driven dependency lookup
        
        Args:
            changed_file: Path to changed file
            change_description: Description of change
            
        Returns:
            Impact analysis dictionary
        """
        print(f"\n🔍 Analyzing impact of {os.path.basename(changed_file)}...")
        
        # Use search engine for instant dependency lookup
        dependents = self.search_engine.search_dependencies(
            changed_file,
            direction='dependents'
        )
        
        dependencies = self.search_engine.search_dependencies(
            changed_file,
            direction='dependencies'
        )
        
        print(f"   Found {len(dependents)} dependents, {len(dependencies)} dependencies")
        
        # Get transitive dependents for full impact
        transitive_dependents = self.search_engine.search_dependencies(
            changed_file,
            direction='dependents',
            transitive=True
        )
        
        # Determine if file is core or project
        is_core = self._is_dive_ai_core(changed_file)
        
        # Get historical changes
        related_changes = self.search_engine.index.update_indexer.get_related_changes(changed_file)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(
            len(dependents),
            len(transitive_dependents),
            is_core,
            related_changes
        )
        
        # Categorize updates
        safe_updates = []
        complex_updates = []
        
        for dependent in dependents:
            # Check if update is safe
            if self._is_safe_update(dependent, changed_file):
                safe_updates.append({
                    'file': dependent,
                    'type': 'SAFE',
                    'reason': 'Simple import update'
                })
            else:
                complex_updates.append({
                    'file': dependent,
                    'type': 'COMPLEX',
                    'reason': 'Requires manual review'
                })
        
        # Determine complexity
        if impact_score < 3:
            complexity = 'LOW'
        elif impact_score < 7:
            complexity = 'MEDIUM'
        else:
            complexity = 'HIGH'
        
        return {
            'file': changed_file,
            'is_core': is_core,
            'dependents': dependents,
            'dependencies': dependencies,
            'transitive_dependents': list(transitive_dependents),
            'impact_score': impact_score,
            'complexity': complexity,
            'safe_updates': safe_updates,
            'complex_updates': complex_updates,
            'related_changes': [c.to_dict() for c in related_changes[:5]],
            'search_driven': True
        }
    
    def _is_dive_ai_core(self, file_path: str) -> bool:
        """Check if file is part of Dive AI core"""
        try:
            rel_path = os.path.relpath(file_path, self.dive_ai_root)
            # Core files are in core/, not in project directories
            return rel_path.startswith('core/') or rel_path.startswith('coder/')
        except:
            return False
    
    def _calculate_impact_score(self, dependents_count: int, transitive_count: int,
                                is_core: bool, related_changes: List) -> int:
        """Calculate impact score"""
        score = 0
        
        # Direct dependents
        score += min(dependents_count, 5)
        
        # Transitive dependents
        score += min(transitive_count // 5, 3)
        
        # Core file bonus
        if is_core:
            score += 2
        
        # Recent changes penalty
        if len(related_changes) > 3:
            score += 1
        
        return score
    
    def _is_safe_update(self, dependent_file: str, changed_file: str) -> bool:
        """Check if update is safe to auto-apply"""
        # Get file info
        file_info = self.search_engine.get_file_info(dependent_file)
        
        if not file_info:
            return False
        
        # Check if it's a simple import
        imports = file_info.get('file_info', {}).get('imports', [])
        changed_module = os.path.splitext(os.path.basename(changed_file))[0]
        
        # Safe if it's just an import, not heavy usage
        return changed_module in imports
    
    def track_change(self, file_path: str, change_type: str, category: str,
                    description: str, breaking: bool = False,
                    version: str = None) -> Dict:
        """
        Track change with project awareness
        
        Args:
            file_path: Path to changed file
            change_type: Type of change
            category: Category of change
            description: Description
            breaking: Whether breaking
            version: Version number
            
        Returns:
            Change record with impact analysis
        """
        # Determine if core or project file
        is_core = self._is_dive_ai_core(file_path)
        
        # Track in update indexer
        record = self.search_engine.index.update_indexer.track_change(
            file_path=file_path,
            change_type=change_type,
            category=category,
            description=description,
            breaking=breaking,
            version=version
        )
        
        # Analyze impact
        impact = self.analyze_impact(file_path, description)
        
        # If core change, check project impact
        if is_core:
            project_impact = self._check_project_impact(file_path, impact)
            impact['project_impact'] = project_impact
        
        return {
            'change_record': record.to_dict(),
            'impact': impact,
            'is_core': is_core
        }
    
    def _check_project_impact(self, core_file: str, impact: Dict) -> Dict:
        """
        Check if core change affects working projects
        
        Args:
            core_file: Path to core file
            impact: Impact analysis
            
        Returns:
            Project impact dictionary
        """
        # Find project files in dependents
        project_files = []
        
        for dependent in impact['transitive_dependents']:
            if not self._is_dive_ai_core(dependent):
                project_files.append(dependent)
        
        return {
            'affected_project_files': project_files,
            'count': len(project_files),
            'requires_project_update': len(project_files) > 0
        }
    
    def search_changes(self, query: str, **filters) -> List[Dict]:
        """
        Search changes with filters
        
        Args:
            query: Search query
            **filters: Additional filters
            
        Returns:
            List of matching changes
        """
        results = self.search_engine.search_updates(query, **filters)
        return [r.data for r in results]
    
    def get_breaking_changes_for_version(self, version: str) -> List[Dict]:
        """Get breaking changes for specific version"""
        return self.search_engine.get_breaking_changes(version)
    
    def get_changes_affecting_file(self, file_path: str) -> List[Dict]:
        """Get all changes that affect a file"""
        # Get direct changes
        direct_changes = self.search_engine.index.update_indexer.get_changes_for_file(file_path)
        
        # Get changes to dependencies
        dependencies = self.search_engine.search_dependencies(file_path, direction='dependencies')
        
        dependency_changes = []
        for dep in dependencies:
            dep_changes = self.search_engine.index.update_indexer.get_changes_for_file(dep)
            dependency_changes.extend(dep_changes)
        
        # Combine and deduplicate
        all_changes = list(direct_changes) + list(dependency_changes)
        seen = set()
        unique_changes = []
        
        for change in all_changes:
            if change.change_id not in seen:
                seen.add(change.change_id)
                unique_changes.append(change.to_dict())
        
        # Sort by timestamp
        unique_changes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return unique_changes
    
    def suggest_updates(self, file_path: str) -> List[Dict]:
        """
        Suggest updates for a file based on changes
        
        Args:
            file_path: Path to file
            
        Returns:
            List of suggested updates
        """
        # Get changes affecting file
        changes = self.get_changes_affecting_file(file_path)
        
        suggestions = []
        
        for change in changes:
            if change['breaking']:
                suggestions.append({
                    'priority': 'HIGH',
                    'type': 'BREAKING_CHANGE',
                    'description': f"Update required due to: {change['description']}",
                    'affected_file': change['file_path'],
                    'change_id': change['change_id']
                })
            elif change['category'] in ['FEATURE', 'REFACTOR']:
                suggestions.append({
                    'priority': 'MEDIUM',
                    'type': 'ENHANCEMENT',
                    'description': f"Consider updating for: {change['description']}",
                    'affected_file': change['file_path'],
                    'change_id': change['change_id']
                })
        
        return suggestions
    
    def get_statistics(self) -> Dict:
        """Get update system statistics"""
        stats = self.search_engine.index.update_indexer.get_statistics()
        
        # Add search-specific stats
        stats['search_driven'] = True
        stats['search_engine_ready'] = self.search_engine.ready
        
        return stats


if __name__ == "__main__":
    # Test search-enhanced update system
    update_system = DiveUpdateSearchEnhanced()
    
    print("\n=== Testing Search-Enhanced Update System ===")
    
    # Test impact analysis
    test_file = os.path.join(update_system.dive_ai_root, "core/dive_memory_3file_complete.py")
    if os.path.exists(test_file):
        print("\n1. Testing Impact Analysis")
        impact = update_system.analyze_impact(test_file, "Refactored memory system")
        print(f"   File: {os.path.basename(impact['file'])}")
        print(f"   Is core: {impact['is_core']}")
        print(f"   Dependents: {len(impact['dependents'])}")
        print(f"   Transitive dependents: {len(impact['transitive_dependents'])}")
        print(f"   Impact score: {impact['impact_score']}")
        print(f"   Complexity: {impact['complexity']}")
        print(f"   Safe updates: {len(impact['safe_updates'])}")
        print(f"   Complex updates: {len(impact['complex_updates'])}")
    
    # Test change tracking
    print("\n2. Testing Change Tracking")
    result = update_system.track_change(
        file_path=test_file,
        change_type="MODIFIED",
        category="REFACTOR",
        description="Added search integration",
        breaking=False,
        version="21.0"
    )
    print(f"   Change tracked: {result['change_record']['change_id']}")
    print(f"   Is core: {result['is_core']}")
    if 'project_impact' in result['impact']:
        print(f"   Project files affected: {result['impact']['project_impact']['count']}")
    
    # Test change search
    print("\n3. Testing Change Search")
    changes = update_system.search_changes("memory", category="REFACTOR")
    print(f"   Found {len(changes)} changes")
    for change in changes[:3]:
        print(f"      - {change['description']}")
    
    # Test update suggestions
    print("\n4. Testing Update Suggestions")
    suggestions = update_system.suggest_updates(test_file)
    print(f"   Found {len(suggestions)} suggestions")
    for sug in suggestions[:3]:
        print(f"      - [{sug['priority']}] {sug['description']}")
    
    # Get statistics
    print("\n=== Update System Statistics ===")
    stats = update_system.get_statistics()
    print(f"Total changes: {stats.get('total_changes', 0)}")
    print(f"Breaking changes: {stats.get('breaking_changes', 0)}")
    print(f"Search driven: {stats['search_driven']}")
    print(f"Search engine ready: {stats['search_engine_ready']}")
