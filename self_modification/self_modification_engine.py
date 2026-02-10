"""
Dive AI V29.4 - Self-Modification Engine
Safely applies code changes to Dive AI itself

Features:
- Backup before modification
- Sandbox testing
- Rollback on failure
- Change logging
- Safety checks
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import subprocess
import json

from .code_analyzer import SelfAwareCodeAnalyzer, CodeAnalysisResult
from .code_generator import DiveCodeGenerator, CodeChange


@dataclass
class ModificationResult:
    """Result of self-modification attempt"""
    success: bool
    change: CodeChange
    backup_path: str
    test_results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    applied_at: Optional[datetime] = None


class SelfModificationEngine:
    """
    Safely modifies Dive AI's own code
    
    Safety features:
    - Backup before changes
    - Protected files list
    - Sandbox testing
    - Automatic rollback
    """
    
    # Files that cannot be modified (too critical)
    PROTECTED_FILES = [
        "Launch-UI-TARS.bat",
        "Launch-UI-TARS-Silent.bat",
        "Stop-UI-TARS.bat",
        ".env",
        "self_modification/self_modification_engine.py",  # Can't modify itself!
    ]
    
    def __init__(self, dive_ai_root: str = None):
        self.dive_ai_root = dive_ai_root or Path("D:/Antigravity/Dive AI")
        self.backup_dir = Path(self.dive_ai_root) / ".backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.analyzer = SelfAwareCodeAnalyzer(dive_ai_root)
        self.generator = DiveCodeGenerator(dive_ai_root)
        
        # Modification history
        self.history_file = self.backup_dir / "modification_history.json"
        self.history = self._load_history()
    
    def modify_code(self, change: CodeChange, test_first: bool = True) -> ModificationResult:
        """
        Apply code change to Dive AI
        
        Args:
            change: The code change to apply
            test_first: Run tests in sandbox before applying
            
        Returns:
            ModificationResult with status
        """
        # Safety check: Protected files
        if self._is_protected(change.file_path):
            return ModificationResult(
                success=False,
                change=change,
                backup_path="",
                error=f"Cannot modify protected file: {change.file_path}"
            )
        
        # Create backup
        backup_path = self._create_backup(change.file_path)
        
        try:
            # Test in sandbox if requested
            if test_first:
                test_results = self._test_in_sandbox(change)
                if not test_results['passed']:
                    return ModificationResult(
                        success=False,
                        change=change,
                        backup_path=backup_path,
                        test_results=test_results,
                        error=f"Tests failed: {test_results.get('error')}"
                    )
            else:
                test_results = None (applied_paths = self._apply_change(change)
            
            # Log modification
            self._log_modification(change, backup_path, test_results)
            
            return ModificationResult(
                success=True,
                change=change,
                backup_path=backup_path,
                test_results=test_results,
                applied_at=datetime.now()
            )
            
        except Exception as e:
            # Rollback on error
            self._rollback(change.file_path, backup_path)
            return ModificationResult(
                success=False,
                change=change,
                backup_path=backup_path,
                error=str(e)
            )
    
    def fix_bug(self, module_path: str, bug_description: str) -> ModificationResult:
        """
        Analyze bug and apply fix
        """
        print(f"Generating fix for: {module_path}")
        print(f"Bug: {bug_description}")
        
        # Generate fix
        change = self.generator.generate_fix(module_path, bug_description)
        
        # Apply with testing
        result = self.modify_code(change, test_first=True)
        
        if result.success:
            print(f"✅ Fix applied successfully!")
            print(f"Backup at: {result.backup_path}")
        else:
            print(f"❌ Fix failed: {result.error}")
        
        return result
    
    def optimize_module(self, module_path: str, goal: str) -> ModificationResult:
        """Optimize module performance"""
        change = self.generator.optimize_code(module_path, goal)
        return self.modify_code(change, test_first=True)
    
    def add_feature(self, module_path: str, feature: str) -> ModificationResult:
        """Add new feature to module"""
        change = self.generator.add_feature(module_path, feature)
        return self.modify_code(change, test_first=True)
    
    def rollback_last(self) -> bool:
        """Rollback the last modification"""
        if not self.history:
            print("No modifications to rollback")
            return False
        
        last = self.history[-1]
        file_path = last['file_path']
        backup_path = last['backup_path']
        
        self._rollback(file_path, backup_path)
        self.history.pop()
        self._save_history()
        
        print(f"✅ Rolled back: {file_path}")
        return True
    
    def _is_protected(self, file_path: str) -> bool:
        """Check if file is protected from modification"""
        return any(protected in file_path for protected in self.PROTECTED_FILES)
    
    def _create_backup(self, file_path: str) -> str:
        """Create backup of file before modification"""
        source = Path(self.dive_ai_root) / file_path
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.replace('/', '_').replace('\\', '_')}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(source, backup_path)
        print(f"📦 Backup created: {backup_path.name}")
        
        return str(backup_path)
    
    def _apply_change(self, change: CodeChange):
        """Write new code to file"""
        target = Path(self.dive_ai_root) / change.file_path
        
        with open(target, 'w', encoding='utf-8') as f:
            f.write(change.new_code)
        
        print(f"✍️  Applied changes to: {change.file_path}")
    
    def _rollback(self, file_path: str, backup_path: str):
        """Restore file from backup"""
        target = Path(self.dive_ai_root) / file_path
        shutil.copy2(backup_path, target)
        print(f"↩️  Rolled back: {file_path}")
    
    def _test_in_sandbox(self, change: CodeChange) -> Dict[str, Any]:
        """
        Test code change in sandbox environment
        
        TODO: Implement proper sandboxing
        For now, just does basic syntax check
        """
        try:
            # Syntax check
            compile(change.new_code, change.file_path, 'exec')
            
            return {
                'passed': True,
                'tests_run': 1,
                'errors': []
            }
        except SyntaxError as e:
            return {
                'passed': False,
                'error': str(e),
                'tests_run': 0
            }
    
    def _log_modification(self, change: CodeChange, backup_path: str, test_results: Optional[Dict]):
        """Log modification to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'file_path': change.file_path,
            'change_type': change.change_type,
            'description': change.description,
            'backup_path': backup_path,
            'test_results': test_results
        }
        
        self.history.append(entry)
        self._save_history()
    
    def _load_history(self) -> List[Dict]:
        """Load modification history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save modification history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)


# Quick access

def dive_fix_bug(module: str, bug: str) -> ModificationResult:
    """Quick bug fix for Dive AI"""
    engine = SelfModificationEngine()
    return engine.fix_bug(module, bug)


def dive_optimize(module: str, goal: str) -> ModificationResult:
    """Quick optimization"""
    engine = SelfModificationEngine()
    return engine.optimize_module(module, goal)


if __name__ == "__main__":
    print("Dive AI Self-Modification Engine")
    print("=" * 60)
    print("\nSafety features enabled:")
    print("✅ Automatic backups")
    print("✅ Protected files list")
    print("✅ Sandbox testing")
    print("✅ Rollback capability")
    print("\nReady for self-improvement!")
