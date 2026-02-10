"""
Dive AI V29.4 - Self-Aware Code Analyzer
Analyzes Dive AI's own codebase for understanding and improvement

Can analyze:
- Module purposes and dependencies
- Potential bugs and issues
- Performance bottlenecks
- Code quality and improvements
"""

import os
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import Dive AI LLM system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "desktop-app" / "backend"))

from llm.connections import get_manager, CLAUDE_OPUS_46_THINKING
from llm.v98_algorithm import V98Algorithm


@dataclass
class CodeAnalysisResult:
    """Result from code analysis"""
    module_path: str
    purpose: str
    dependencies: List[str]
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    complexity_score: float
    understanding: str


class SelfAwareCodeAnalyzer:
    """
    Dive AI analyzes its own code
    
    Uses Claude 4.6 Opus Thinking for deep code understanding
    """
    
    def __init__(self, dive_ai_root: str = None):
        self.dive_ai_root = dive_ai_root or Path("D:/Antigravity/Dive AI")
        self.algorithm = V98Algorithm(name="CodeAnalyzer")
        self.analyzed_modules = {}
        
    def analyze_module(self, module_path: str) -> CodeAnalysisResult:
        """
        Analyze a Dive AI Python module
        
        Args:
            module_path: Relative path from Dive AI root
            
        Returns:
            CodeAnalysisResult with full understanding
        """
        full_path = Path(self.dive_ai_root) / module_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Module not found: {full_path}")
        
        # Read the code
        with open(full_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse with AST for structure
        try:
            tree = ast.parse(code)
            structure = self._extract_structure(tree)
        except SyntaxError as e:
            structure = {"error": str(e)}
        
        # Use Claude 4.6 to understand
        prompt = f"""Analyze this Dive AI V29.4 module: {module_path}

```python
{code}
```

Structure:
{structure}

Provide detailed analysis:

1. **Purpose**: What does this module do? What's its role in Dive AI?

2. **Dependencies**: What other modules/libraries does it depend on?

3. **Issues**: Identify potential bugs, code smells, or problems:
   - Syntax errors
   - Logic issues
   - Performance problems
   - Security vulnerabilities
   - Missing error handling

4. **Suggestions**: How can this code be improved?
   - Better patterns
   - Optimizations
   - Refactoring opportunities
   - Missing features

5. **Complexity**: Rate code complexity (1-10) and explain why.

Format as JSON:
{{
    "purpose": "...",
    "dependencies": ["mod1", "mod2"],
    "issues": [
        {{"type": "bug", "line": 42, "description": "...", "severity": "high"}},
        ...
    ],
    "suggestions": ["suggestion 1", "suggestion 2"],
    "complexity_score": 7.5,
    "understanding": "Deep explanation..."
}}
"""
        
        # Execute analysis
        result = self.algorithm.execute(
            prompt=prompt,
            model=CLAUDE_OPUS_46_THINKING,
            max_tokens=8192
        )
        
        if result.status != "success":
            raise Exception(f"Analysis failed: {result.data.get('error')}")
        
        # Parse JSON response
        import json
        try:
            analysis = json.loads(result.data['content'])
        except json.JSONDecodeError:
            # Fallback: extract from markdown if needed
            content = result.data['content']
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
                analysis = json.loads(json_str)
            else:
                analysis = {
                    "purpose": "Analysis parsing failed",
                    "dependencies": [],
                    "issues": [],
                    "suggestions": [],
                    "complexity_score": 0,
                    "understanding": content
                }
        
        # Create result
        result_obj = CodeAnalysisResult(
            module_path=module_path,
            purpose=analysis.get('purpose', ''),
            dependencies=analysis.get('dependencies', []),
            issues=analysis.get('issues', []),
            suggestions=analysis.get('suggestions', []),
            complexity_score=analysis.get('complexity_score', 0),
            understanding=analysis.get('understanding', '')
        )
        
        # Cache result
        self.analyzed_modules[module_path] = result_obj
        
        return result_obj
    
    def _extract_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract code structure from AST"""
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'bases': [b.id for b in node.bases if isinstance(b, ast.Name)],
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                })
            elif isinstance(node, ast.FunctionDef):
                if not any(node.name in c['methods'] for c in classes):
                    functions.append({
                        'name': node.name,
                        'args': [a.arg for a in node.args.args]
                    })
            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}" if node.module else "")
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': list(set(imports))
        }
    
    def find_bugs(self, module_path: str) -> List[Dict[str, Any]]:
        """Quick bug detection in module"""
        analysis = self.analyze_module(module_path)
        return [issue for issue in analysis.issues if issue.get('type') == 'bug']
    
    def suggest_improvements(self, module_path: str) -> List[str]:
        """Get improvement suggestions"""
        analysis = self.analyze_module(module_path)
        return analysis.suggestions
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> Dict[str, CodeAnalysisResult]:
        """Analyze all Python files in directory"""
        dir_path = Path(self.dive_ai_root) / directory
        results = {}
        
        for py_file in dir_path.rglob(pattern):
            rel_path = py_file.relative_to(self.dive_ai_root)
            try:
                results[str(rel_path)] = self.analyze_module(str(rel_path))
            except Exception as e:
                print(f"Failed to analyze {rel_path}: {e}")
        
        return results


# Quick access functions

def analyze_dive_module(module_path: str) -> CodeAnalysisResult:
    """Quick analysis of a Dive AI module"""
    analyzer = SelfAwareCodeAnalyzer()
    return analyzer.analyze_module(module_path)


def find_bugs_in_dive(module_path: str) -> List[Dict[str, Any]]:
    """Find bugs in Dive AI module"""
    analyzer = SelfAwareCodeAnalyzer()
    return analyzer.find_bugs(module_path)


if __name__ == "__main__":
    # Test self-awareness
    print("Dive AI Self-Aware Code Analyzer")
    print("=" * 60)
    
    analyzer = SelfAwareCodeAnalyzer()
    
    # Analyze the connections module
    print("\nAnalyzing: desktop-app/backend/llm/connections.py")
    result = analyzer.analyze_module("desktop-app/backend/llm/connections.py")
    
    print(f"\nPurpose: {result.purpose}")
    print(f"\nComplexity: {result.complexity_score}/10")
    print(f"\nIssues found: {len(result.issues)}")
    for issue in result.issues[:3]:  # Show first 3
        print(f"  - [{issue.get('severity')}] Line {issue.get('line')}: {issue.get('description')}")
    
    print(f"\nSuggestions: {len(result.suggestions)}")
    for i, suggestion in enumerate(result.suggestions[:3], 1):
        print(f"  {i}. {suggestion}")
