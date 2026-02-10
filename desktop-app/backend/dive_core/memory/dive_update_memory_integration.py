#!/usr/bin/env python3
"""
Dive Update - Memory Integration
Integrates Dive Update System with Dive Memory for persistent tracking
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    from dive_core.memory.dive_memory_3file_complete import DiveMemory3FileComplete
    from dive_core.search.dive_update_system import DiveUpdateSystem
    from dive_core.engine.dive_impact_analyzer import ImpactAnalysis
    from dive_core.search.dive_update_suggester import UpdatePlan
except ImportError:
    from dive_memory_3file_complete import DiveMemory3FileComplete
    from dive_update_system import DiveUpdateSystem
    from dive_impact_analyzer import ImpactAnalysis
    from dive_update_suggester import UpdatePlan



class DiveUpdateMemoryIntegration:
    """
    Integration layer between Dive Update System and Dive Memory
    
    Features:
    - Track file states and versions in memory
    - Record impact analyses and update plans
    - Maintain update history
    - Enable rollback capabilities
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getcwd()
        self.update_system = DiveUpdateSystem(root_dir)
        self.memory = DiveMemory3FileComplete()
        
        # Ensure update tracking project exists
        self.tracking_project = "dive-update-tracking"
        self._init_tracking_project()
    
    def _init_tracking_project(self):
        """Initialize update tracking project in memory"""
        files = self.memory.get_project_files(self.tracking_project)
        
        # Create FULL.md if not exists
        if not files['full'].exists():
            content = self._create_tracking_full_template()
            files['full'].write_text(content)
            print(f"   ✅ Created {files['full'].name}")
        
        # Create CRITERIA.md if not exists
        if not files['criteria'].exists():
            content = self._create_tracking_criteria_template()
            files['criteria'].write_text(content)
            print(f"   ✅ Created {files['criteria'].name}")
        
        # Create CHANGELOG.md if not exists
        if not files['changelog'].exists():
            content = "# Dive Update System - Change Log\n\n"
            files['changelog'].write_text(content)
            print(f"   ✅ Created {files['changelog'].name}")
    
    def _create_tracking_full_template(self) -> str:
        """Create template for tracking FULL.md"""
        return """# Dive Update System - File Tracking

## Overview

This document tracks the state of all files in the Dive AI system, including:
- Current versions
- Dependencies
- Last modifications
- Breaking changes

## File States

### Core Files

#### dive_smart_orchestrator.py
- **Version:** 21.0
- **Last Modified:** {timestamp}
- **Dependencies:** dive_memory_3file_complete.py, dive_smart_coder.py
- **Dependents:** dive_ai_complete_system.py, install.sh
- **Breaking Changes:** None

#### dive_smart_coder.py
- **Version:** 21.0
- **Last Modified:** {timestamp}
- **Dependencies:** dive_memory_3file_complete.py
- **Dependents:** dive_smart_orchestrator.py
- **Breaking Changes:** None

### Integration Files

#### unified_llm_client_config.py
- **Version:** 21.0
- **Last Modified:** {timestamp}
- **Dependencies:** None
- **Dependents:** dive_smart_orchestrator.py, dive_smart_coder.py
- **Breaking Changes:** None

### Setup Scripts

#### install.sh
- **Version:** 20.4.1
- **Last Modified:** {timestamp}
- **Dependencies:** setup_api_keys.py, first_run_complete.py
- **Dependents:** None
- **Breaking Changes:** None

## Version History

### V21.0.0 (2026-02-05)
- Updated memory system to 3-file structure
- Enhanced workflow with knowledge graph
- Breaking change: Memory API changed

### V20.4.1 (2026-02-05)
- Added auto-install system
- Non-interactive API key setup

### V20.4.0 (2026-02-04)
- Complete workflow integration
- Smart Orchestrator and Smart Coder

## Metadata

- **Last Updated:** {timestamp}
- **Total Files Tracked:** 0
- **Total Dependencies:** 0
""".format(timestamp=datetime.now().isoformat())
    
    def _create_tracking_criteria_template(self) -> str:
        """Create template for tracking CRITERIA.md"""
        return """# Dive Update System - Execution Criteria

## When to Run Update Analysis

### Trigger Conditions

1. **Version Breakthrough**
   - Major version change (e.g., 20.x → 21.x)
   - Minor version change with breaking changes
   - Action: Run full impact analysis

2. **Core File Modification**
   - Changes to files in core/ directory
   - Changes to memory system
   - Changes to orchestrator/coder
   - Action: Analyze transitive dependencies

3. **API Changes**
   - Function signature changes
   - New required parameters
   - Removed functions
   - Action: Critical impact analysis

4. **Setup Script Changes**
   - Changes to install.sh
   - Changes to first_run scripts
   - Changes to startup scripts
   - Action: Test installation flow

### Impact Levels

#### CRITICAL
- Breaking API changes
- Version mismatches in setup scripts
- Core system incompatibilities
- **Action:** Must fix before release

#### HIGH
- Function signature changes
- Direct dependency issues
- Test failures
- **Action:** Should fix before release

#### MEDIUM
- New features requiring updates
- Documentation updates
- Refactoring impacts
- **Action:** Fix in next iteration

#### LOW
- Comment changes
- Minor documentation updates
- Non-breaking enhancements
- **Action:** Optional, can defer

## Update Application Rules

### Auto-Apply Criteria

Safe to auto-apply if:
1. Simple version string replacement
2. Documentation updates
3. Comment updates
4. No logic changes

### Manual Review Required

Requires human review if:
1. Code logic changes
2. Function signature changes
3. Complex refactoring
4. Test modifications

## Decision Tree

```
File Changed
    ↓
Is it a core file?
    ↓ Yes
    Run full dependency scan
    Analyze all dependents
    Generate update plan
    Apply auto-updates
    Flag manual reviews
    ↓ No
    Is it a setup script?
        ↓ Yes
        Check version references
        Update related scripts
        Test installation
        ↓ No
        Is it documentation?
            ↓ Yes
            Update version refs
            Check examples
            ↓ No
            Standard update flow
```

## Known Issues

### Issue 1: Version Mismatch Detection
**Problem:** Sometimes version strings in comments are not detected
**Workaround:** Use strict VERSION constant pattern
**Status:** Monitoring

### Issue 2: Circular Dependencies
**Problem:** Circular imports can cause analysis loops
**Workaround:** Track visited files to prevent infinite loops
**Status:** Handled in code

## Examples

### Example 1: Core File Update

```python
# Changed file: core/dive_memory_3file_complete.py
# New version: 21.0.0

# Run analysis
system = DiveUpdateMemoryIntegration()
system.track_change_and_update(
    changed_files=["core/dive_memory_3file_complete.py"],
    new_version="21.0.0",
    breaking=True,
    description="Updated to 3-file memory structure"
)

# Result:
# - 15 files analyzed
# - 5 critical impacts found
# - 3 auto-updates applied
# - 2 manual reviews flagged
```

### Example 2: Version Breakthrough

```python
# Breakthrough from 20.4.1 to 21.0.0

system = DiveUpdateMemoryIntegration()
system.version_breakthrough(
    from_version="20.4.1",
    to_version="21.0.0",
    major_changes=[
        "Memory system restructured",
        "New knowledge graph feature",
        "Enhanced workflow"
    ]
)

# Result:
# - Full project scan
# - Impact analysis on all files
# - Update plan generated
# - Critical updates applied
# - Report saved to memory
```

## Metadata

- **Last Updated:** {timestamp}
- **Version:** 1.0
- **Status:** Active
""".format(timestamp=datetime.now().isoformat())
    
    def track_change_and_update(
        self,
        changed_files: List[str],
        new_version: str,
        breaking: bool = False,
        description: str = "",
        auto_apply: bool = True,
        dry_run: bool = False
    ) -> Dict:
        """
        Track a change and run update workflow
        
        Args:
            changed_files: List of files that were changed
            new_version: New version number
            breaking: Whether this is a breaking change
            description: Description of the change
            auto_apply: Whether to auto-apply safe updates
            dry_run: Don't actually modify files
            
        Returns:
            Dictionary with results
        """
        print("\n" + "="*80)
        print("🔄 DIVE UPDATE - TRACK CHANGE & UPDATE")
        print("="*80)
        print(f"   Changed Files: {', '.join(changed_files)}")
        print(f"   New Version: {new_version}")
        print(f"   Breaking: {breaking}")
        print(f"   Description: {description}")
        
        # Run full analysis and plan
        analysis, plan = self.update_system.full_analysis_and_plan(
            changed_files=changed_files,
            new_version=new_version
        )
        
        # Apply updates if requested
        results = {}
        if auto_apply:
            results = self.update_system.apply_updates(
                plan=plan,
                auto_only=True,
                dry_run=dry_run
            )
        
        # Record in memory
        self._record_change_in_memory(
            changed_files=changed_files,
            new_version=new_version,
            breaking=breaking,
            description=description,
            analysis=analysis,
            plan=plan,
            results=results
        )
        
        return {
            'analysis': analysis,
            'plan': plan,
            'results': results,
            'total_affected': analysis.total_affected,
            'auto_applied': sum(1 for v in results.values() if v),
            'manual_review': plan.manual_review
        }
    
    def version_breakthrough(
        self,
        from_version: str,
        to_version: str,
        major_changes: List[str],
        auto_apply: bool = True,
        dry_run: bool = False
    ) -> Dict:
        """
        Handle version breakthrough with full project analysis
        
        Args:
            from_version: Previous version
            to_version: New version
            major_changes: List of major changes in this version
            auto_apply: Whether to auto-apply safe updates
            dry_run: Don't actually modify files
            
        Returns:
            Dictionary with results
        """
        print("\n" + "="*80)
        print(f"🚀 VERSION BREAKTHROUGH: {from_version} → {to_version}")
        print("="*80)
        
        # Scan project for dependencies
        tracking_info = self.update_system.scan_and_track()
        
        # Find all files that might need updates
        # For version breakthrough, we analyze all core files
        core_files = [
            f for f in self.update_system.tracker.dependencies.keys()
            if f.startswith('core/') or f.startswith('integration/')
        ]
        
        print(f"\n   📊 Analyzing {len(core_files)} core/integration files")
        
        # Run analysis
        analysis, plan = self.update_system.full_analysis_and_plan(
            changed_files=core_files,
            new_version=to_version
        )
        
        # Apply updates if requested
        results = {}
        if auto_apply:
            results = self.update_system.apply_updates(
                plan=plan,
                auto_only=True,
                dry_run=dry_run
            )
        
        # Record breakthrough in memory
        self._record_breakthrough_in_memory(
            from_version=from_version,
            to_version=to_version,
            major_changes=major_changes,
            analysis=analysis,
            plan=plan,
            results=results
        )
        
        return {
            'tracking_info': tracking_info,
            'analysis': analysis,
            'plan': plan,
            'results': results,
            'total_affected': analysis.total_affected,
            'auto_applied': sum(1 for v in results.values() if v),
            'manual_review': plan.manual_review
        }
    
    def _record_change_in_memory(
        self,
        changed_files: List[str],
        new_version: str,
        breaking: bool,
        description: str,
        analysis: ImpactAnalysis,
        plan: UpdatePlan,
        results: Dict[str, bool]
    ):
        """Record change details in memory"""
        files = self.memory.get_project_files(self.tracking_project)
        
        # Update CHANGELOG
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        changelog_entry = f"""
## {timestamp} - Version {new_version}

### Changed Files
{chr(10).join(f'- {f}' for f in changed_files)}

### Description
{description}

### Breaking Change
{'Yes' if breaking else 'No'}

### Impact Analysis
- Total Affected Files: {analysis.total_affected}
- Critical: {len(analysis.get_by_level(analysis.impacts[0].level if analysis.impacts else None))}
- Auto-Applied Updates: {sum(1 for v in results.values() if v)}
- Manual Review Required: {plan.manual_review}

---
"""
        
        # Append to changelog
        current_changelog = files['changelog'].read_text()
        files['changelog'].write_text(current_changelog + changelog_entry)
        
        print(f"   💾 Recorded change in memory: {files['changelog'].name}")
    
    def _record_breakthrough_in_memory(
        self,
        from_version: str,
        to_version: str,
        major_changes: List[str],
        analysis: ImpactAnalysis,
        plan: UpdatePlan,
        results: Dict[str, bool]
    ):
        """Record version breakthrough in memory"""
        files = self.memory.get_project_files(self.tracking_project)
        
        # Update CHANGELOG
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        changelog_entry = f"""
## 🚀 {timestamp} - VERSION BREAKTHROUGH: {from_version} → {to_version}

### Major Changes
{chr(10).join(f'- {change}' for change in major_changes)}

### Impact Analysis
- Total Affected Files: {analysis.total_affected}
- Auto-Applied Updates: {sum(1 for v in results.values() if v)}
- Manual Review Required: {plan.manual_review}

### Files Updated
{chr(10).join(f'- {file}: {"✅" if success else "⚠️"}' for file, success in results.items())}

---
"""
        
        # Append to changelog
        current_changelog = files['changelog'].read_text()
        files['changelog'].write_text(current_changelog + changelog_entry)
        
        print(f"   💾 Recorded breakthrough in memory: {files['changelog'].name}")
    
    def get_update_history(self, limit: int = 10) -> List[Dict]:
        """Get recent update history from memory"""
        files = self.memory.get_project_files(self.tracking_project)
        
        if not files['changelog'].exists():
            return []
        
        changelog = files['changelog'].read_text()
        
        # Parse changelog entries (simple parsing)
        entries = []
        current_entry = {}
        
        for line in changelog.split('\n'):
            if line.startswith('## '):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {'title': line[3:].strip()}
            elif line.strip() and current_entry:
                if 'content' not in current_entry:
                    current_entry['content'] = []
                current_entry['content'].append(line)
        
        if current_entry:
            entries.append(current_entry)
        
        return entries[:limit]


def main():
    """Test Dive Update Memory Integration"""
    integration = DiveUpdateMemoryIntegration()
    
    # Test 1: Track a change
    print("\n📊 TEST 1: Track Change and Update")
    result = integration.track_change_and_update(
        changed_files=["first_run_complete.py"],
        new_version="21.0.0",
        breaking=True,
        description="Updated to use new 3-file memory structure",
        auto_apply=True,
        dry_run=True  # Don't actually modify files
    )
    
    print(f"\n✅ Test 1 Results:")
    print(f"   Total Affected: {result['total_affected']}")
    print(f"   Auto Applied: {result['auto_applied']}")
    print(f"   Manual Review: {result['manual_review']}")
    
    # Test 2: Get update history
    print("\n📊 TEST 2: Get Update History")
    history = integration.get_update_history(limit=5)
    print(f"   Found {len(history)} recent updates")
    for entry in history:
        print(f"   - {entry.get('title', 'Unknown')}")


if __name__ == "__main__":
    main()
