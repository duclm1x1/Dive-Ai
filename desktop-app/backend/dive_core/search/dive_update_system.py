#!/usr/bin/env python3
"""
Dive Update System
Unified system for detecting, analyzing, and applying updates when code changes
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

try:
    from dive_core.engine.dive_dependency_tracker import DiveDependencyTracker
    from dive_core.engine.dive_impact_analyzer import DiveImpactAnalyzer, ImpactAnalysis
    from dive_core.search.dive_update_suggester import DiveUpdateSuggester, UpdatePlan, UpdateSuggestion
except ImportError:
    from dive_dependency_tracker import DiveDependencyTracker
    from dive_impact_analyzer import DiveImpactAnalyzer, ImpactAnalysis
    from dive_update_suggester import DiveUpdateSuggester, UpdatePlan, UpdateSuggestion



class DiveUpdateSystem:
    """
    Unified system for managing code updates across the project
    
    Features:
    - Automatic dependency tracking
    - Impact analysis for changes
    - Update suggestions generation
    - Auto-apply safe updates
    - Integration with Dive Memory
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getcwd()
        self.tracker = DiveDependencyTracker(root_dir)
        self.analyzer = DiveImpactAnalyzer(root_dir)
        self.suggester = DiveUpdateSuggester(root_dir)
        
        # Create directories
        self.memory_dir = os.path.join(self.root_dir, "memory")
        self.updates_dir = os.path.join(self.memory_dir, "updates")
        self.tracking_dir = os.path.join(self.memory_dir, "file_tracking")
        
        os.makedirs(self.updates_dir, exist_ok=True)
        os.makedirs(self.tracking_dir, exist_ok=True)
    
    def analyze_impact(
        self,
        changed_files: List[str],
        new_version: str = None,
        old_version: str = None
    ) -> ImpactAnalysis:
        """
        Analyze impact of changes to given files
        
        Args:
            changed_files: List of files that were changed
            new_version: New version number (auto-detect from VERSION file if not provided)
            old_version: Old version number (auto-detect if not provided)
            
        Returns:
            ImpactAnalysis object
        """
        print("\n" + "="*80)
        print("🔍 DIVE UPDATE SYSTEM - IMPACT ANALYSIS")
        print("="*80)
        
        # Auto-detect versions if not provided
        if new_version is None:
            new_version = self._read_version()
        
        if old_version is None:
            old_version = self._get_previous_version(new_version)
        
        # Run impact analysis
        analysis = self.analyzer.analyze_impact(
            changed_files=changed_files,
            version_from=old_version,
            version_to=new_version
        )
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = os.path.join(
            self.updates_dir,
            f"impact_analysis_{new_version}_{timestamp}.json"
        )
        self.analyzer.save_analysis(analysis, analysis_file)
        
        return analysis
    
    def generate_update_plan(self, analysis: ImpactAnalysis) -> UpdatePlan:
        """
        Generate update plan from impact analysis
        
        Args:
            analysis: Impact analysis result
            
        Returns:
            UpdatePlan object
        """
        print("\n" + "="*80)
        print("📝 DIVE UPDATE SYSTEM - UPDATE PLAN")
        print("="*80)
        
        # Generate plan
        plan = self.suggester.generate_update_plan(analysis)
        
        # Save plan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = os.path.join(
            self.updates_dir,
            f"update_plan_{analysis.version_to}_{timestamp}.json"
        )
        self.suggester.save_plan(plan, plan_file)
        
        return plan
    
    def apply_updates(
        self,
        plan: UpdatePlan,
        auto_only: bool = True,
        dry_run: bool = False,
        backup: bool = True
    ) -> Dict[str, bool]:
        """
        Apply updates from update plan
        
        Args:
            plan: Update plan to apply
            auto_only: Only apply updates marked as auto_apply
            dry_run: Don't actually modify files, just show what would be done
            backup: Create backups before modifying files
            
        Returns:
            Dictionary mapping file paths to success status
        """
        print("\n" + "="*80)
        print("🔧 DIVE UPDATE SYSTEM - APPLYING UPDATES")
        print("="*80)
        
        if dry_run:
            print("   🔍 DRY RUN MODE - No files will be modified")
        
        results = {}
        
        # Filter suggestions
        suggestions = plan.suggestions
        if auto_only:
            suggestions = [s for s in suggestions if s.auto_apply]
            print(f"   📊 Applying {len(suggestions)} auto-applicable updates")
        else:
            print(f"   📊 Applying {len(suggestions)} updates")
        
        # Group by file
        by_file = {}
        for suggestion in suggestions:
            if suggestion.file_path not in by_file:
                by_file[suggestion.file_path] = []
            by_file[suggestion.file_path].append(suggestion)
        
        # Apply updates file by file
        for file_path, file_suggestions in by_file.items():
            try:
                success = self._apply_file_updates(
                    file_path, 
                    file_suggestions,
                    dry_run=dry_run,
                    backup=backup
                )
                results[file_path] = success
                
                if success:
                    print(f"   ✅ {file_path}: {len(file_suggestions)} updates applied")
                else:
                    print(f"   ⚠️  {file_path}: Updates skipped")
                    
            except Exception as e:
                print(f"   ❌ {file_path}: Error - {e}")
                results[file_path] = False
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        print(f"\n   📊 Summary: {successful}/{len(results)} files updated successfully")
        
        return results
    
    def _apply_file_updates(
        self,
        file_path: str,
        suggestions: List[UpdateSuggestion],
        dry_run: bool = False,
        backup: bool = True
    ) -> bool:
        """Apply updates to a single file"""
        full_path = os.path.join(self.root_dir, file_path)
        
        if not os.path.exists(full_path):
            print(f"      ⚠️  File not found: {file_path}")
            return False
        
        # Read current content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"      ❌ Could not read file: {e}")
            return False
        
        # Create backup if requested
        if backup and not dry_run:
            backup_path = full_path + ".backup"
            shutil.copy2(full_path, backup_path)
        
        # Apply each suggestion
        modified_content = content
        for suggestion in suggestions:
            if suggestion.old_code and suggestion.new_code:
                # Simple string replacement
                if suggestion.old_code in modified_content:
                    modified_content = modified_content.replace(
                        suggestion.old_code,
                        suggestion.new_code,
                        1  # Replace only first occurrence
                    )
                else:
                    print(f"      ⚠️  Could not find old code in file")
        
        # Write updated content
        if not dry_run:
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            except Exception as e:
                print(f"      ❌ Could not write file: {e}")
                # Restore backup
                if backup:
                    shutil.copy2(backup_path, full_path)
                return False
        
        return True
    
    def scan_and_track(self) -> Dict:
        """
        Scan project and build dependency graph
        
        Returns:
            Dictionary with tracking information
        """
        print("\n" + "="*80)
        print("🔍 DIVE UPDATE SYSTEM - DEPENDENCY TRACKING")
        print("="*80)
        
        # Scan project
        dependencies = self.tracker.scan_project()
        
        # Save outputs
        self.tracker.save_graph(
            os.path.join(self.tracking_dir, "dependency_graph.json")
        )
        self.tracker.save_dependencies(
            os.path.join(self.tracking_dir, "file_dependencies.json")
        )
        
        # Print summary
        self.tracker.print_summary()
        
        return {
            'total_files': len(dependencies),
            'graph_nodes': len(self.tracker.graph['nodes']),
            'graph_edges': len(self.tracker.graph['edges'])
        }
    
    def full_analysis_and_plan(
        self,
        changed_files: List[str],
        new_version: str = None
    ) -> tuple[ImpactAnalysis, UpdatePlan]:
        """
        Run complete analysis and generate update plan
        
        Args:
            changed_files: List of files that were changed
            new_version: New version number
            
        Returns:
            Tuple of (ImpactAnalysis, UpdatePlan)
        """
        # Analyze impact
        analysis = self.analyze_impact(changed_files, new_version)
        
        # Print impact report
        print("\n" + analysis.report())
        
        # Generate update plan
        plan = self.generate_update_plan(analysis)
        
        # Print update plan
        print("\n" + plan.report())
        
        return analysis, plan
    
    def auto_update_workflow(
        self,
        changed_files: List[str],
        new_version: str = None,
        dry_run: bool = False
    ) -> bool:
        """
        Complete automatic update workflow
        
        Args:
            changed_files: List of files that were changed
            new_version: New version number
            dry_run: Don't actually modify files
            
        Returns:
            True if all updates successful
        """
        print("\n" + "="*80)
        print("🤖 DIVE UPDATE SYSTEM - AUTO UPDATE WORKFLOW")
        print("="*80)
        
        # Run analysis and generate plan
        analysis, plan = self.full_analysis_and_plan(changed_files, new_version)
        
        # Check for critical issues
        if analysis.has_critical_issues():
            print("\n⚠️  CRITICAL ISSUES DETECTED!")
            print("   Proceeding with auto-updates for safe changes...")
        
        # Apply auto-applicable updates
        results = self.apply_updates(plan, auto_only=True, dry_run=dry_run)
        
        # Check if all succeeded
        all_success = all(results.values())
        
        if all_success:
            print("\n✅ AUTO UPDATE WORKFLOW COMPLETE!")
            print("   All related files have been synchronized.")
        else:
            print("\n⚠️  AUTO UPDATE WORKFLOW COMPLETED WITH WARNINGS")
            print("   Some files may need manual review.")
        
        # Show manual review items
        manual_items = [s for s in plan.suggestions if not s.auto_apply]
        if manual_items:
            print(f"\n👁️  {len(manual_items)} items need manual review:")
            for item in manual_items:
                print(f"   - {item.file_path}: {item.description}")
        
        return all_success
    
    def _read_version(self) -> str:
        """Read current version from VERSION file"""
        version_file = os.path.join(self.root_dir, "VERSION")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        return "unknown"
    
    def _get_previous_version(self, current_version: str) -> str:
        """Get previous version (simple decrement)"""
        try:
            parts = current_version.split('.')
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                if patch > 0:
                    return f"{major}.{minor}.{patch-1}"
                elif minor > 0:
                    return f"{major}.{minor-1}.0"
                elif major > 0:
                    return f"{major-1}.0.0"
        except:
            pass
        return "unknown"


def main():
    """Test Dive Update System"""
    system = DiveUpdateSystem()
    
    # Test 1: Scan and track dependencies
    print("\n📊 TEST 1: Dependency Tracking")
    system.scan_and_track()
    
    # Test 2: Full analysis and plan
    print("\n📊 TEST 2: Impact Analysis & Update Plan")
    changed_files = ["first_run_complete.py"]
    analysis, plan = system.full_analysis_and_plan(
        changed_files=changed_files,
        new_version="21.0.0"
    )
    
    # Test 3: Auto update workflow (dry run)
    print("\n📊 TEST 3: Auto Update Workflow (Dry Run)")
    system.auto_update_workflow(
        changed_files=changed_files,
        new_version="21.0.0",
        dry_run=True
    )


if __name__ == "__main__":
    main()
