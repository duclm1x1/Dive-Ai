"""
Dive AI V29.4 - Code Generator for Self-Modification
Generates code fixes and improvements for Dive AI itself

Can generate:
- Bug fixes
- Performance optimizations
- New features
- Refactoring improvements
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import difflib

# Import Dive AI LLM system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "desktop-app" / "backend"))

from llm.connections import get_manager, CLAUDE_OPUS_46_THINKING
from llm.v98_algorithm import CodeGeneratorAlgorithm


@dataclass
class CodeChange:
    """Represents a code modification"""
    file_path: str
    original_code: str
    new_code: str
    description: str
    change_type: str  # 'fix', 'optimize', 'refactor', 'feature'
    diff: str


class DiveCodeGenerator:
    """
    Generates code modifications for Dive AI
    
    Uses Claude 4.6 Opus Thinking for intelligent code generation
    """
    
    def __init__(self, dive_ai_root: str = None):
        self.dive_ai_root = dive_ai_root or Path("D:/Antigravity/Dive AI")
        self.algorithm = CodeGeneratorAlgorithm()
        
    def generate_fix(self, module_path: str, bug_description: str) -> CodeChange:
        """
        Generate a bug fix for Dive AI code
        
        Args:
            module_path: Path to module with bug
            bug_description: Description of the bug
            
        Returns:
            CodeChange with the fix
        """
        # Read current code
        full_path = Path(self.dive_ai_root) / module_path
        with open(full_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Generate fix
        task = f"""Fix this bug in Dive AI module: {module_path}

**Bug Description:**
{bug_description}

**Current Code:**
```python
{original_code}
```

**Task:**
Generate the COMPLETE fixed version of this file.
- Fix the described bug
- Maintain all existing functionality
- Add proper error handling
- Include comments explaining the fix

**Output ONLY the complete fixed code, no explanations outside code comments.**
"""
        
        result = self.algorithm.generate(
            task=task,
            language="python",
            context=f"This is Dive AI V29.4 module: {module_path}"
        )
        
        if result.status != "success":
            raise Exception(f"Fix generation failed: {result.data.get('error')}")
        
        # Extract code from response
        new_code = self._extract_code(result.data['content'])
        
        # Generate diff
        diff = self._generate_diff(original_code, new_code, module_path)
        
        return CodeChange(
            file_path=module_path,
            original_code=original_code,
            new_code=new_code,
            description=f"Bug fix: {bug_description}",
            change_type='fix',
            diff=diff
        )
    
    def optimize_code(self, module_path: str, optimization_goal: str) -> CodeChange:
        """Generate performance optimization"""
        
        full_path = Path(self.dive_ai_root) / module_path
        with open(full_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        task = f"""Optimize this Dive AI module for: {optimization_goal}

**Module:** {module_path}

**Code:**
```python
{original_code}
```

**Optimization Goal:**
{optimization_goal}

**Task:**
Rewrite the code with optimizations while maintaining functionality.
- Improve performance
- Reduce memory usage
- Better algorithms
- Keep all features working

**Output the complete optimized code.**
"""
        
        result = self.algorithm.generate(
            task=task,
            language="python"
        )
        
        if result.status != "success":
            raise Exception(f"Optimization failed: {result.data.get('error')}")
        
        new_code = self._extract_code(result.data['content'])
        diff = self._generate_diff(original_code, new_code, module_path)
        
        return CodeChange(
            file_path=module_path,
            original_code=original_code,
            new_code=new_code,
            description=f"Optimization: {optimization_goal}",
            change_type='optimize',
            diff=diff
        )
    
    def add_feature(self, module_path: str, feature_description: str) -> CodeChange:
        """Add new feature to existing module"""
        
        full_path = Path(self.dive_ai_root) / module_path
        with open(full_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        task = f"""Add this feature to Dive AI module: {module_path}

**Current Code:**
```python
{original_code}
```

**New Feature:**
{feature_description}

**Task:**
Add the new feature while maintaining existing functionality.
- Integrate cleanly with existing code
- Follow existing patterns
- Add proper documentation
- Include error handling

**Output the complete updated code.**
"""
        
        result = self.algorithm.generate(
            task=task,
            language="python"
        )
        
        if result.status != "success":
            raise Exception(f"Feature addition failed: {result.data.get('error')}")
        
        new_code = self._extract_code(result.data['content'])
        diff = self._generate_diff(original_code, new_code, module_path)
        
        return CodeChange(
            file_path=module_path,
            original_code=original_code,
            new_code=new_code,
            description=f"New feature: {feature_description}",
            change_type='feature',
            diff=diff
        )
    
    def _extract_code(self, content: str) -> str:
        """Extract Python code from Claude's response"""
        # Remove markdown code blocks
        if '```python' in content:
            code = content.split('```python')[1].split('```')[0].strip()
        elif '```' in content:
            code = content.split('```')[1].split('```')[0].strip()
        else:
            code = content.strip()
        
        return code
    
    def _generate_diff(self, original: str, new: str, filename: str) -> str:
        """Generate unified diff"""
        original_lines = original.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=''
        )
        
        return ''.join(diff)


# Quick access functions

def fix_dive_bug(module_path: str, bug: str) -> CodeChange:
    """Quick bug fix generation"""
    generator = DiveCodeGenerator()
    return generator.generate_fix(module_path, bug)


def optimize_dive_module(module_path: str, goal: str) -> CodeChange:
    """Quick optimization"""
    generator = DiveCodeGenerator()
    return generator.optimize_code(module_path, goal)


if __name__ == "__main__":
    print("Dive AI Code Generator")
    print("=" * 60)
    
    generator = DiveCodeGenerator()
    
    # Example: Generate a fix
    print("\nGenerating fix for connections.py...")
    print("Bug: Synchronous requests cause slowdowns")
    
    # This would generate the actual fix
    # change = generator.generate_fix(
    #     "desktop-app/backend/llm/connections.py",
    #     "Synchronous HTTP requests in chat() method cause slowdowns"
    # )
    # print(f"\nGenerated fix ({len(change.diff)} chars diff)")
    # print(change.description)
