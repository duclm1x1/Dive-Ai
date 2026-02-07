#!/usr/bin/env python3
"""
Dive Update Suggester
Generates actionable update suggestions for affected files
"""

import os
import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

from dive_impact_analyzer import ImpactAnalysis, ImpactItem, ImpactLevel


@dataclass
class UpdateSuggestion:
    """Represents a suggested update for a file"""
    file_path: str
    impact_level: ImpactLevel
    update_type: str  # version_bump, import_update, code_refactor, docs_update
    description: str
    old_code: str
    new_code: str
    auto_apply: bool  # Whether this can be safely auto-applied
    
    def to_dict(self):
        data = asdict(self)
        data['impact_level'] = self.impact_level.value
        return data


@dataclass
class UpdatePlan:
    """Complete update plan with all suggestions"""
    version_from: str
    version_to: str
    suggestions: List[UpdateSuggestion]
    auto_applicable: int
    manual_review: int
    
    def to_dict(self):
        return {
            'version_from': self.version_from,
            'version_to': self.version_to,
            'suggestions': [s.to_dict() for s in self.suggestions],
            'auto_applicable': self.auto_applicable,
            'manual_review': self.manual_review
        }
    
    def report(self) -> str:
        """Generate human-readable update plan"""
        lines = []
        lines.append("="*80)
        lines.append(f"📝 UPDATE PLAN: {self.version_from} → {self.version_to}")
        lines.append("="*80)
        lines.append(f"\n📊 Summary:")
        lines.append(f"   Total Updates: {len(self.suggestions)}")
        lines.append(f"   ✅ Auto-applicable: {self.auto_applicable}")
        lines.append(f"   👁️  Manual Review: {self.manual_review}")
        lines.append("")
        
        # Group by file
        by_file = {}
        for suggestion in self.suggestions:
            if suggestion.file_path not in by_file:
                by_file[suggestion.file_path] = []
            by_file[suggestion.file_path].append(suggestion)
        
        for file_path, suggestions in sorted(by_file.items()):
            # Get highest impact level
            max_level = max(s.impact_level for s in suggestions)
            icon = {
                ImpactLevel.CRITICAL: "🔴",
                ImpactLevel.HIGH: "🟠",
                ImpactLevel.MEDIUM: "🟡",
                ImpactLevel.LOW: "🟢"
            }[max_level]
            
            lines.append(f"{icon} {file_path} ({max_level.value})")
            lines.append("")
            
            for i, suggestion in enumerate(suggestions, 1):
                auto_marker = "✅ AUTO" if suggestion.auto_apply else "👁️  MANUAL"
                lines.append(f"   Update {i}: {suggestion.update_type} [{auto_marker}]")
                lines.append(f"   Description: {suggestion.description}")
                
                if suggestion.old_code and suggestion.new_code:
                    lines.append(f"   ")
                    lines.append(f"   OLD:")
                    for line in suggestion.old_code.split('\n'):
                        lines.append(f"   - {line}")
                    lines.append(f"   ")
                    lines.append(f"   NEW:")
                    for line in suggestion.new_code.split('\n'):
                        lines.append(f"   + {line}")
                
                lines.append("")
        
        lines.append("="*80)
        return "\n".join(lines)


class DiveUpdateSuggester:
    """
    Generates actionable update suggestions based on impact analysis
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.getcwd()
    
    def generate_update_plan(
        self, 
        impact_analysis: ImpactAnalysis
    ) -> UpdatePlan:
        """
        Generate update plan from impact analysis
        
        Args:
            impact_analysis: Impact analysis result
            
        Returns:
            UpdatePlan with all suggestions
        """
        print(f"\n📝 Generating update plan...")
        
        suggestions = []
        
        for impact in impact_analysis.impacts:
            file_suggestions = self._generate_file_suggestions(
                impact, 
                impact_analysis.version_to
            )
            suggestions.extend(file_suggestions)
        
        # Count auto-applicable vs manual review
        auto_applicable = sum(1 for s in suggestions if s.auto_apply)
        manual_review = len(suggestions) - auto_applicable
        
        plan = UpdatePlan(
            version_from=impact_analysis.version_from,
            version_to=impact_analysis.version_to,
            suggestions=suggestions,
            auto_applicable=auto_applicable,
            manual_review=manual_review
        )
        
        print(f"   ✅ Update plan generated")
        print(f"   📊 {len(suggestions)} updates suggested")
        print(f"   ✅ {auto_applicable} auto-applicable")
        print(f"   👁️  {manual_review} need manual review")
        
        return plan
    
    def _generate_file_suggestions(
        self, 
        impact: ImpactItem,
        new_version: str
    ) -> List[UpdateSuggestion]:
        """Generate suggestions for a single file"""
        suggestions = []
        
        file_path = impact.file_path
        full_path = os.path.join(self.root_dir, file_path)
        
        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"   ⚠️  Could not read {file_path}: {e}")
            return suggestions
        
        # Generate suggestions based on file type
        file_type = self._get_file_type(file_path)
        
        if file_type == 'script':
            suggestions.extend(self._suggest_script_updates(
                file_path, content, new_version, impact.level
            ))
        elif file_type == 'docs':
            suggestions.extend(self._suggest_docs_updates(
                file_path, content, new_version, impact.level
            ))
        elif file_type in ['core', 'integration']:
            suggestions.extend(self._suggest_code_updates(
                file_path, content, new_version, impact.level
            ))
        
        # Always check for version string updates
        version_suggestion = self._suggest_version_update(
            file_path, content, new_version, impact.level
        )
        if version_suggestion:
            suggestions.append(version_suggestion)
        
        return suggestions
    
    def _suggest_script_updates(
        self, 
        file_path: str, 
        content: str,
        new_version: str,
        impact_level: ImpactLevel
    ) -> List[UpdateSuggestion]:
        """Generate suggestions for shell scripts"""
        suggestions = []
        
        # Find version references in echo statements
        pattern = r'echo.*[Vv](\d+\.\d+\.\d+)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            old_version = match.group(1)
            if old_version != new_version:
                old_line = match.group(0)
                new_line = old_line.replace(old_version, new_version)
                
                suggestions.append(UpdateSuggestion(
                    file_path=file_path,
                    impact_level=impact_level,
                    update_type="version_bump",
                    description=f"Update version string from {old_version} to {new_version}",
                    old_code=old_line,
                    new_code=new_line,
                    auto_apply=True
                ))
        
        return suggestions
    
    def _suggest_docs_updates(
        self,
        file_path: str,
        content: str,
        new_version: str,
        impact_level: ImpactLevel
    ) -> List[UpdateSuggestion]:
        """Generate suggestions for documentation files"""
        suggestions = []
        
        # Find version references (e.g., V20.4.0, v20.4.0, 20.4.0)
        pattern = r'[Vv]?(\d+\.\d+\.\d+)'
        matches = re.finditer(pattern, content)
        
        seen_versions = set()
        for match in matches:
            old_version = match.group(1)
            if old_version != new_version and old_version not in seen_versions:
                seen_versions.add(old_version)
                
                # Get context (line containing the version)
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]
                
                suggestions.append(UpdateSuggestion(
                    file_path=file_path,
                    impact_level=ImpactLevel.LOW,
                    update_type="docs_update",
                    description=f"Update version reference from {old_version} to {new_version}",
                    old_code=f"...{old_version}...",
                    new_code=f"...{new_version}...",
                    auto_apply=True
                ))
        
        return suggestions
    
    def _suggest_code_updates(
        self,
        file_path: str,
        content: str,
        new_version: str,
        impact_level: ImpactLevel
    ) -> List[UpdateSuggestion]:
        """Generate suggestions for Python code files"""
        suggestions = []
        
        # Check for version constants
        version_patterns = [
            (r'VERSION\s*=\s*["\']([0-9.]+)["\']', 'VERSION = "{}"'),
            (r'__version__\s*=\s*["\']([0-9.]+)["\']', '__version__ = "{}"'),
        ]
        
        for pattern, template in version_patterns:
            match = re.search(pattern, content)
            if match:
                old_version = match.group(1)
                if old_version != new_version:
                    old_code = match.group(0)
                    new_code = template.format(new_version)
                    
                    suggestions.append(UpdateSuggestion(
                        file_path=file_path,
                        impact_level=impact_level,
                        update_type="version_bump",
                        description=f"Update version constant from {old_version} to {new_version}",
                        old_code=old_code,
                        new_code=new_code,
                        auto_apply=True
                    ))
        
        return suggestions
    
    def _suggest_version_update(
        self,
        file_path: str,
        content: str,
        new_version: str,
        impact_level: ImpactLevel
    ) -> UpdateSuggestion:
        """Generate version update suggestion if needed"""
        
        # Special handling for VERSION file
        if file_path == "VERSION":
            old_version = content.strip()
            if old_version != new_version:
                return UpdateSuggestion(
                    file_path=file_path,
                    impact_level=ImpactLevel.CRITICAL,
                    update_type="version_bump",
                    description=f"Update VERSION file from {old_version} to {new_version}",
                    old_code=old_version,
                    new_code=new_version,
                    auto_apply=True
                )
        
        return None
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type"""
        if file_path.endswith('.sh') or 'install' in file_path.lower():
            return 'script'
        elif 'README' in file_path or 'CHANGELOG' in file_path or file_path.endswith('.md'):
            return 'docs'
        elif file_path.startswith('core/'):
            return 'core'
        elif file_path.startswith('integration/'):
            return 'integration'
        else:
            return 'other'
    
    def save_plan(self, plan: UpdatePlan, output_path: str):
        """Save update plan to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2)
        
        print(f"   💾 Update plan saved: {output_path}")


def main():
    """Test update suggester"""
    from dive_impact_analyzer import DiveImpactAnalyzer
    
    # First, run impact analysis
    analyzer = DiveImpactAnalyzer()
    analysis = analyzer.analyze_impact(
        changed_files=["first_run_complete.py"],
        version_from="20.4.0",
        version_to="21.0.0"
    )
    
    # Generate update plan
    suggester = DiveUpdateSuggester()
    plan = suggester.generate_update_plan(analysis)
    
    # Print report
    print(plan.report())
    
    # Save plan
    suggester.save_plan(
        plan,
        "memory/updates/update_plan_v21.0.0.json"
    )


if __name__ == "__main__":
    main()
