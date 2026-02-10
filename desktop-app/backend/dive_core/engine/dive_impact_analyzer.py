#!/usr/bin/env python3
"""
Dive Impact Analyzer
Analyzes the impact of code changes on related files
"""

import os
import json
import difflib
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from dive_core.engine.dive_dependency_tracker import DiveDependencyTracker, FileDependency
except ImportError:
    from dive_dependency_tracker import DiveDependencyTracker, FileDependency



class ImpactLevel(Enum):
    """Impact severity levels"""
    CRITICAL = "CRITICAL"  # Breaking changes, API changes
    HIGH = "HIGH"          # Function signature changes
    MEDIUM = "MEDIUM"      # New features, refactoring
    LOW = "LOW"            # Documentation, comments


@dataclass
class ImpactItem:
    """Represents an impact on a single file"""
    file_path: str
    level: ImpactLevel
    reason: str
    suggestions: List[str]
    
    def to_dict(self):
        data = asdict(self)
        data['level'] = self.level.value
        return data


@dataclass
class ImpactAnalysis:
    """Complete impact analysis result"""
    changed_files: List[str]
    version_from: str
    version_to: str
    impacts: List[ImpactItem]
    total_affected: int
    
    def to_dict(self):
        return {
            'changed_files': self.changed_files,
            'version_from': self.version_from,
            'version_to': self.version_to,
            'impacts': [impact.to_dict() for impact in self.impacts],
            'total_affected': self.total_affected
        }
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical impacts"""
        return any(impact.level == ImpactLevel.CRITICAL for impact in self.impacts)
    
    def get_by_level(self, level: ImpactLevel) -> List[ImpactItem]:
        """Get all impacts of a specific level"""
        return [impact for impact in self.impacts if impact.level == level]
    
    def report(self) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("="*80)
        lines.append(f"📊 IMPACT ANALYSIS: {self.version_from} → {self.version_to}")
        lines.append("="*80)
        lines.append(f"\n📝 Changed Files: {', '.join(self.changed_files)}")
        lines.append(f"📈 Total Affected Files: {self.total_affected}")
        lines.append("")
        
        # Group by level
        for level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH, ImpactLevel.MEDIUM, ImpactLevel.LOW]:
            items = self.get_by_level(level)
            if items:
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[level.value]
                lines.append(f"{icon} {level.value} ({len(items)} files):")
                for item in items:
                    lines.append(f"   - {item.file_path}")
                    lines.append(f"     Reason: {item.reason}")
                    if item.suggestions:
                        lines.append(f"     Suggestions:")
                        for suggestion in item.suggestions:
                            lines.append(f"       • {suggestion}")
                lines.append("")
        
        lines.append("="*80)
        return "\n".join(lines)


class DiveImpactAnalyzer:
    """
    Analyzes impact of code changes on related files
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getcwd()
        self.tracker = DiveDependencyTracker(root_dir)
        
    def analyze_impact(
        self, 
        changed_files: List[str],
        version_from: str = "unknown",
        version_to: str = "unknown"
    ) -> ImpactAnalysis:
        """
        Analyze impact of changes to given files
        
        Args:
            changed_files: List of files that were changed
            version_from: Previous version
            version_to: New version
            
        Returns:
            ImpactAnalysis object with all impacts
        """
        print(f"\n🔍 Analyzing impact of changes...")
        print(f"   Changed files: {', '.join(changed_files)}")
        
        # Scan project for dependencies
        self.tracker.scan_project()
        
        # Find all affected files
        affected_files = set()
        for changed_file in changed_files:
            # Get all files that depend on this file
            dependents = self.tracker.get_transitive_dependents(changed_file)
            affected_files.update(dependents)
        
        # Remove the changed files themselves
        for changed_file in changed_files:
            affected_files.discard(changed_file)
        
        print(f"   Found {len(affected_files)} potentially affected files")
        
        # Analyze each affected file
        impacts = []
        for file_path in affected_files:
            impact = self._analyze_file_impact(file_path, changed_files, version_to)
            if impact:
                impacts.append(impact)
        
        # Sort by impact level
        level_order = {
            ImpactLevel.CRITICAL: 0,
            ImpactLevel.HIGH: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.LOW: 3
        }
        impacts.sort(key=lambda x: level_order[x.level])
        
        analysis = ImpactAnalysis(
            changed_files=changed_files,
            version_from=version_from,
            version_to=version_to,
            impacts=impacts,
            total_affected=len(impacts)
        )
        
        print(f"   ✅ Impact analysis complete")
        
        return analysis
    
    def _analyze_file_impact(
        self, 
        file_path: str, 
        changed_files: List[str],
        new_version: str
    ) -> ImpactItem:
        """Analyze impact on a single file"""
        
        # Get file dependency info
        if file_path not in self.tracker.dependencies:
            return None
        
        dep = self.tracker.dependencies[file_path]
        
        # Determine impact level and reason
        level, reason, suggestions = self._determine_impact(
            file_path, dep, changed_files, new_version
        )
        
        if level is None:
            return None
        
        return ImpactItem(
            file_path=file_path,
            level=level,
            reason=reason,
            suggestions=suggestions
        )
    
    def _determine_impact(
        self,
        file_path: str,
        dep: FileDependency,
        changed_files: List[str],
        new_version: str
    ) -> Tuple[ImpactLevel, str, List[str]]:
        """Determine impact level, reason, and suggestions"""
        
        suggestions = []
        
        # Check for version mismatches
        if dep.version != "unknown" and dep.version != new_version:
            # Check if file directly imports changed files
            direct_import = any(cf in dep.imports for cf in changed_files)
            
            if direct_import:
                level = ImpactLevel.CRITICAL
                reason = f"Version mismatch: file uses v{dep.version} but changed files are v{new_version}"
                suggestions = [
                    f"Update version references from {dep.version} to {new_version}",
                    "Review imports and ensure compatibility with new version",
                    "Update any hardcoded version strings"
                ]
            else:
                level = ImpactLevel.HIGH
                reason = f"Indirect dependency on changed files with version mismatch"
                suggestions = [
                    "Check if transitive dependencies are compatible",
                    f"Consider updating to v{new_version}"
                ]
            
            return level, reason, suggestions
        
        # Check file type for specific patterns
        file_type = self._get_file_type(file_path)
        
        # Installation/setup scripts are critical
        if file_type in ['script', 'setup']:
            level = ImpactLevel.CRITICAL
            reason = "Installation/setup script may reference old code paths or versions"
            suggestions = [
                "Update version strings and references",
                "Verify all file paths are correct",
                "Test installation flow with new changes"
            ]
            return level, reason, suggestions
        
        # Documentation files
        if file_type == 'docs':
            level = ImpactLevel.MEDIUM
            reason = "Documentation may need updates to reflect changes"
            suggestions = [
                "Update version numbers",
                "Review code examples and ensure they're current",
                "Update changelog if applicable"
            ]
            return level, reason, suggestions
        
        # Test files
        if file_type == 'test':
            level = ImpactLevel.HIGH
            reason = "Test file may need updates to test new changes"
            suggestions = [
                "Review test cases for compatibility",
                "Add tests for new functionality",
                "Update mocked data if needed"
            ]
            return level, reason, suggestions
        
        # Core files that import changed files
        if file_type == 'core' and any(cf in dep.imports for cf in changed_files):
            level = ImpactLevel.HIGH
            reason = "Core file directly imports changed files"
            suggestions = [
                "Review function calls to changed files",
                "Check for API compatibility",
                "Update error handling if needed"
            ]
            return level, reason, suggestions
        
        # Default: medium impact for any file that depends on changes
        level = ImpactLevel.MEDIUM
        reason = "File has indirect dependency on changed files"
        suggestions = [
            "Review for potential compatibility issues",
            "Test functionality after changes"
        ]
        
        return level, reason, suggestions
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on path and name"""
        if file_path.endswith('.sh') or 'install' in file_path.lower() or 'setup' in file_path.lower():
            return 'script'
        elif file_path.startswith('core/'):
            return 'core'
        elif file_path.startswith('test') or 'test' in file_path.lower():
            return 'test'
        elif 'README' in file_path or 'CHANGELOG' in file_path or file_path.endswith('.md'):
            return 'docs'
        elif file_path.startswith('integration/'):
            return 'integration'
        else:
            return 'other'
    
    def save_analysis(self, analysis: ImpactAnalysis, output_path: str):
        """Save impact analysis to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis.to_dict(), f, indent=2)
        
        print(f"   💾 Impact analysis saved: {output_path}")


def main():
    """Test impact analyzer"""
    analyzer = DiveImpactAnalyzer()
    
    # Test: Analyze impact of changing first_run_complete.py
    changed_files = ["first_run_complete.py"]
    
    analysis = analyzer.analyze_impact(
        changed_files=changed_files,
        version_from="20.4.0",
        version_to="21.0.0"
    )
    
    # Print report
    print(analysis.report())
    
    # Save analysis
    analyzer.save_analysis(
        analysis, 
        "memory/updates/impact_analysis_v21.0.0.json"
    )


if __name__ == "__main__":
    main()
