#!/usr/bin/env python3
"""
Dive Update - Project-Aware Extension
Tracks changes in both Dive AI core and working projects
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dive_core.vision.dive_update_system import DiveUpdateSystem
    from dive_core.engine.dive_dependency_tracker import DiveDependencyTracker
    from dive_core.engine.dive_impact_analyzer import ImpactAnalysis
    from dive_core.vision.dive_update_suggester import UpdatePlan
except ImportError:
    from dive_update_system import DiveUpdateSystem
    from dive_dependency_tracker import DiveDependencyTracker
    from dive_impact_analyzer import ImpactAnalysis
    from dive_update_suggester import UpdatePlan



class DiveUpdateProjectAware(DiveUpdateSystem):
    """
    Project-aware extension of Dive Update System
    
    Features:
    - Tracks changes in Dive AI core
    - Tracks changes in working projects
    - Cross-project impact analysis
    - Project-specific dependency graphs
    """
    
    def __init__(self, root_dir: str = None, project_dir: str = None):
        """
        Initialize project-aware update system
        
        Args:
            root_dir: Dive AI root directory
            project_dir: Current working project directory (if any)
        """
        super().__init__(root_dir)
        
        self.project_dir = project_dir or os.getcwd()
        self.is_working_on_project = self._detect_if_working_on_project()
        
        # Create project-specific tracker if working on a project
        if self.is_working_on_project:
            self.project_tracker = DiveDependencyTracker(self.project_dir)
            self.project_memory_dir = os.path.join(self.project_dir, "memory")
            os.makedirs(self.project_memory_dir, exist_ok=True)
        else:
            self.project_tracker = None
            self.project_memory_dir = None
    
    def _detect_if_working_on_project(self) -> bool:
        """Detect if currently working on a project (not Dive AI itself)"""
        # If project_dir is different from root_dir, we're working on a project
        return os.path.abspath(self.project_dir) != os.path.abspath(self.root_dir)
    
    def analyze_impact_with_project_context(
        self,
        changed_files: List[str],
        new_version: str = None,
        scope: str = "auto"  # "auto", "dive-ai", "project", "both"
    ) -> Dict[str, ImpactAnalysis]:
        """
        Analyze impact with project context
        
        Args:
            changed_files: List of files that were changed
            new_version: New version number
            scope: Analysis scope
                - "auto": Automatically determine scope
                - "dive-ai": Only analyze Dive AI core
                - "project": Only analyze current project
                - "both": Analyze both Dive AI and project
        
        Returns:
            Dictionary with analysis results for each scope
        """
        print("\n" + "="*80)
        print("🔍 DIVE UPDATE - PROJECT-AWARE ANALYSIS")
        print("="*80)
        
        results = {}
        
        # Determine scope
        if scope == "auto":
            scope = self._determine_scope(changed_files)
        
        print(f"   📊 Analysis Scope: {scope.upper()}")
        print(f"   📁 Dive AI Root: {self.root_dir}")
        if self.is_working_on_project:
            print(f"   📁 Project Dir: {self.project_dir}")
        print()
        
        # Analyze Dive AI core if needed
        if scope in ["dive-ai", "both"]:
            print("   🔍 Analyzing Dive AI core...")
            results['dive-ai'] = self.analyze_impact(
                changed_files=changed_files,
                new_version=new_version
            )
        
        # Analyze project if needed
        if scope in ["project", "both"] and self.is_working_on_project:
            print("   🔍 Analyzing current project...")
            results['project'] = self._analyze_project_impact(
                changed_files=changed_files,
                new_version=new_version
            )
        
        # Cross-project analysis if both
        if scope == "both" and self.is_working_on_project:
            print("   🔍 Analyzing cross-project impacts...")
            results['cross-project'] = self._analyze_cross_project_impact(
                changed_files=changed_files,
                results=results
            )
        
        return results
    
    def _determine_scope(self, changed_files: List[str]) -> str:
        """Automatically determine analysis scope based on changed files"""
        dive_ai_files = []
        project_files = []
        
        for file in changed_files:
            abs_path = os.path.abspath(file)
            
            if abs_path.startswith(os.path.abspath(self.root_dir)):
                dive_ai_files.append(file)
            elif self.is_working_on_project and abs_path.startswith(os.path.abspath(self.project_dir)):
                project_files.append(file)
        
        if dive_ai_files and project_files:
            return "both"
        elif dive_ai_files:
            return "dive-ai"
        elif project_files:
            return "project"
        else:
            return "dive-ai"  # Default
    
    def _analyze_project_impact(
        self,
        changed_files: List[str],
        new_version: str
    ) -> ImpactAnalysis:
        """Analyze impact within the current project"""
        # Scan project dependencies
        self.project_tracker.scan_project()
        
        # Find affected files in project
        affected_files = set()
        for changed_file in changed_files:
            # Get relative path within project
            try:
                rel_path = os.path.relpath(changed_file, self.project_dir)
                if rel_path in self.project_tracker.dependencies:
                    dependents = self.project_tracker.get_transitive_dependents(rel_path)
                    affected_files.update(dependents)
            except ValueError:
                # File is outside project directory
                continue
        
        # Remove changed files themselves
        for changed_file in changed_files:
            try:
                rel_path = os.path.relpath(changed_file, self.project_dir)
                affected_files.discard(rel_path)
            except ValueError:
                continue
        
        # Create impact analysis (simplified for now)
        from dive_impact_analyzer import ImpactAnalysis, ImpactItem, ImpactLevel
        
        impacts = []
        for file_path in affected_files:
            impact = ImpactItem(
                file_path=file_path,
                level=ImpactLevel.MEDIUM,
                reason="File depends on changed files in project",
                suggestions=[
                    "Review for compatibility with changes",
                    "Update imports if needed",
                    "Test functionality"
                ]
            )
            impacts.append(impact)
        
        analysis = ImpactAnalysis(
            changed_files=changed_files,
            version_from="unknown",
            version_to=new_version or "unknown",
            impacts=impacts,
            total_affected=len(impacts)
        )
        
        return analysis
    
    def _analyze_cross_project_impact(
        self,
        changed_files: List[str],
        results: Dict[str, ImpactAnalysis]
    ) -> Dict:
        """
        Analyze impacts that cross between Dive AI and project
        
        For example:
        - Changed Dive AI core file that project uses
        - Changed project file that affects how Dive AI processes it
        """
        cross_impacts = {
            'dive_ai_affects_project': [],
            'project_affects_dive_ai': []
        }
        
        # Check if Dive AI changes affect project
        if 'dive-ai' in results:
            dive_ai_analysis = results['dive-ai']
            
            # Check if any affected files are imported by project
            if self.is_working_on_project:
                for impact in dive_ai_analysis.impacts:
                    file_path = impact.file_path
                    
                    # Check if this Dive AI file is used by project
                    if self._is_dive_ai_file_used_by_project(file_path):
                        cross_impacts['dive_ai_affects_project'].append({
                            'dive_ai_file': file_path,
                            'impact_level': impact.level.value,
                            'reason': f"Project uses this Dive AI component: {impact.reason}"
                        })
        
        # Check if project changes affect Dive AI
        if 'project' in results:
            project_analysis = results['project']
            
            # Check if project changes affect how Dive AI processes the project
            for impact in project_analysis.impacts:
                # If project structure changes, Dive AI might need to adapt
                if any(keyword in impact.file_path.lower() for keyword in ['config', 'setup', 'main']):
                    cross_impacts['project_affects_dive_ai'].append({
                        'project_file': impact.file_path,
                        'impact_level': impact.level.value,
                        'reason': "Project structure change may affect Dive AI processing"
                    })
        
        return cross_impacts
    
    def _is_dive_ai_file_used_by_project(self, dive_ai_file: str) -> bool:
        """Check if a Dive AI file is imported/used by the project"""
        if not self.is_working_on_project or not self.project_tracker:
            return False
        
        # Check if any project file imports this Dive AI file
        for file_path, dep in self.project_tracker.dependencies.items():
            for imported_file in dep.imports:
                # Check if import path matches Dive AI file
                if dive_ai_file in imported_file or imported_file in dive_ai_file:
                    return True
        
        return False
    
    def generate_unified_report(
        self,
        analysis_results: Dict[str, ImpactAnalysis]
    ) -> str:
        """Generate unified report across all scopes"""
        lines = []
        lines.append("="*80)
        lines.append("📊 UNIFIED IMPACT REPORT")
        lines.append("="*80)
        lines.append("")
        
        # Summary
        total_affected = sum(
            a.total_affected for a in analysis_results.values() 
            if isinstance(a, ImpactAnalysis)
        )
        lines.append(f"📈 Total Affected Files Across All Scopes: {total_affected}")
        lines.append("")
        
        # Dive AI section
        if 'dive-ai' in analysis_results:
            lines.append("🔧 DIVE AI CORE")
            lines.append("-" * 80)
            analysis = analysis_results['dive-ai']
            lines.append(f"   Affected Files: {analysis.total_affected}")
            if analysis.has_critical_issues():
                lines.append("   ⚠️  CRITICAL ISSUES DETECTED!")
            lines.append("")
        
        # Project section
        if 'project' in analysis_results:
            lines.append("📁 CURRENT PROJECT")
            lines.append("-" * 80)
            analysis = analysis_results['project']
            lines.append(f"   Affected Files: {analysis.total_affected}")
            lines.append("")
        
        # Cross-project section
        if 'cross-project' in analysis_results:
            cross = analysis_results['cross-project']
            lines.append("🔗 CROSS-PROJECT IMPACTS")
            lines.append("-" * 80)
            
            if cross['dive_ai_affects_project']:
                lines.append(f"   Dive AI → Project: {len(cross['dive_ai_affects_project'])} impacts")
                for impact in cross['dive_ai_affects_project'][:3]:
                    lines.append(f"      - {impact['dive_ai_file']}")
            
            if cross['project_affects_dive_ai']:
                lines.append(f"   Project → Dive AI: {len(cross['project_affects_dive_ai'])} impacts")
                for impact in cross['project_affects_dive_ai'][:3]:
                    lines.append(f"      - {impact['project_file']}")
            
            lines.append("")
        
        lines.append("="*80)
        return "\n".join(lines)
    
    def save_project_aware_analysis(
        self,
        analysis_results: Dict,
        output_dir: str = None
    ):
        """Save project-aware analysis results"""
        if output_dir is None:
            output_dir = self.updates_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir,
            f"project_aware_analysis_{timestamp}.json"
        )
        
        # Convert to serializable format
        data = {}
        for scope, result in analysis_results.items():
            if isinstance(result, ImpactAnalysis):
                data[scope] = result.to_dict()
            else:
                data[scope] = result
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"   💾 Project-aware analysis saved: {output_file}")


def main():
    """Test project-aware update system"""
    # Test 1: Analyze Dive AI core change
    print("\n📊 TEST 1: Dive AI Core Change")
    system = DiveUpdateProjectAware()
    
    results = system.analyze_impact_with_project_context(
        changed_files=["core/dive_smart_orchestrator.py"],
        new_version="20.6.0",
        scope="dive-ai"
    )
    
    report = system.generate_unified_report(results)
    print(report)
    
    # Test 2: If working on a project
    if system.is_working_on_project:
        print("\n📊 TEST 2: Project Change")
        results = system.analyze_impact_with_project_context(
            changed_files=["main.py"],
            new_version="1.0.0",
            scope="project"
        )
        
        report = system.generate_unified_report(results)
        print(report)


if __name__ == "__main__":
    main()
