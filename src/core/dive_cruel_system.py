#!/usr/bin/env python3
"""
Dive CRUEL System - V23 Component

Code Review with Understanding, Evidence, and Learning.
7-dimensional code analysis with intelligent debate mechanism.

Based on V15.3 CRUEL system with enhancements for Dive AI.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class Severity(Enum):
    """Warning severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Dimension(Enum):
    """Seven dimensions of code analysis"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    LOGIC = "logic"
    QUALITY = "quality"
    MAINTAINABILITY = "maintainability"
    ARCHITECTURE = "architecture"
    PATTERNS = "patterns"


@dataclass
class Issue:
    """Code issue found by CRUEL"""
    dimension: Dimension
    severity: Severity
    line: int
    message: str
    alternatives: List[str]
    confidence: float


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    file_path: str
    issues: List[Issue]
    score: float
    summary: Dict[Dimension, int]


class DiveCRUELSystem:
    """
    Code Review with Understanding, Evidence, and Learning.
    
    Features:
    - 7-dimensional analysis
    - Pattern-based detection
    - Confidence scoring
    - Alternative suggestions
    - Debate mechanism
    """
    
    def __init__(self):
        self.knowledge_base = self._init_knowledge_base()
        self.stats = {
            'files_analyzed': 0,
            'issues_found': 0,
            'by_severity': {s.value: 0 for s in Severity}
        }
    
    def _init_knowledge_base(self) -> Dict:
        """Initialize knowledge base with rules"""
        return {
            Dimension.SECURITY: [
                {
                    'pattern': r'(password|api_key|secret|token)\s*=\s*["\'][^"\']*["\']',
                    'severity': Severity.CRITICAL,
                    'message': 'Hardcoded secrets detected',
                    'alternatives': [
                        'Use environment variables',
                        'Use configuration files (not in repo)',
                        'Use secrets management service'
                    ],
                    'confidence': 0.95
                },
                {
                    'pattern': r'eval\s*\(',
                    'severity': Severity.CRITICAL,
                    'message': 'Dangerous eval() usage',
                    'alternatives': [
                        'Use ast.literal_eval() for literals',
                        'Use safe parsing libraries',
                        'Avoid dynamic code execution'
                    ],
                    'confidence': 0.9
                }
            ],
            Dimension.PERFORMANCE: [
                {
                    'pattern': r'for\s+\w+\s+in\s+.*:\s*.*\.append\(',
                    'severity': Severity.MEDIUM,
                    'message': 'Loop could use list comprehension',
                    'alternatives': [
                        'Use list comprehension for better performance',
                        'Use map() or filter()',
                        'Use generator expression'
                    ],
                    'confidence': 0.7
                },
                {
                    'pattern': r'for\s+\w+\s+in\s+range\(len\(',
                    'severity': Severity.LOW,
                    'message': 'Unpythonic iteration',
                    'alternatives': [
                        'Use enumerate() for index+value',
                        'Iterate directly over collection',
                        'Use zip() for parallel iteration'
                    ],
                    'confidence': 0.8
                }
            ],
            Dimension.LOGIC: [
                {
                    'pattern': r'def\s+\w+\([^)]*=\s*[\[\{]',
                    'severity': Severity.HIGH,
                    'message': 'Mutable default argument',
                    'alternatives': [
                        'Use None as default, create new object in function',
                        'Use immutable defaults (tuple, frozenset)',
                        'Use factory function'
                    ],
                    'confidence': 0.95
                },
                {
                    'pattern': r'except\s*:',
                    'severity': Severity.MEDIUM,
                    'message': 'Bare except clause',
                    'alternatives': [
                        'Catch specific exceptions',
                        'Use except Exception:',
                        'Add proper error handling'
                    ],
                    'confidence': 0.9
                }
            ],
            Dimension.QUALITY: [
                {
                    'pattern': r'(^|\s)(x|y|z|a|b|c|tmp|temp|data|obj|val)\s*=',
                    'severity': Severity.MEDIUM,
                    'message': 'Unclear variable name',
                    'alternatives': [
                        'Use descriptive names',
                        'Use domain-specific terminology',
                        'Add explanatory comments'
                    ],
                    'confidence': 0.6
                }
            ],
            Dimension.ARCHITECTURE: [
                {
                    'pattern': r'class\s+\w+.*:\s*$',
                    'severity': Severity.MEDIUM,
                    'message': 'Class without docstring',
                    'alternatives': [
                        'Add class docstring',
                        'Document class purpose',
                        'Add usage examples'
                    ],
                    'confidence': 0.85
                },
                {
                    'pattern': r'from\s+\*\s+import',
                    'severity': Severity.HIGH,
                    'message': 'Wildcard import detected',
                    'alternatives': [
                        'Import specific names',
                        'Use qualified imports',
                        'Avoid namespace pollution'
                    ],
                    'confidence': 0.95
                }
            ],
            Dimension.PATTERNS: [
                {
                    'pattern': r'if\s+\w+\s*==\s*True',
                    'severity': Severity.LOW,
                    'message': 'Redundant comparison to True',
                    'alternatives': [
                        'Use if variable: directly',
                        'Simplify boolean logic',
                        'Follow PEP 8 guidelines'
                    ],
                    'confidence': 0.9
                },
                {
                    'pattern': r'if\s+len\([^)]+\)\s*>\s*0',
                    'severity': Severity.LOW,
                    'message': 'Unpythonic length check',
                    'alternatives': [
                        'Use if collection: directly',
                        'Check truthiness instead of length',
                        'More idiomatic Python'
                    ],
                    'confidence': 0.85
                }
            ],
            Dimension.MAINTAINABILITY: [
                {
                    'pattern': r'#\s*TODO',
                    'severity': Severity.LOW,
                    'message': 'TODO comment found',
                    'alternatives': [
                        'Create issue/ticket',
                        'Complete the TODO',
                        'Remove if not needed'
                    ],
                    'confidence': 1.0
                },
                {
                    'pattern': r'#\s*FIXME',
                    'severity': Severity.MEDIUM,
                    'message': 'FIXME comment found',
                    'alternatives': [
                        'Create issue/ticket',
                        'Fix the issue',
                        'Document why it needs fixing'
                    ],
                    'confidence': 1.0
                },
                {
                    'pattern': r'#\s*HACK',
                    'severity': Severity.HIGH,
                    'message': 'HACK comment found',
                    'alternatives': [
                        'Refactor to proper solution',
                        'Document why hack is needed',
                        'Plan for proper fix'
                    ],
                    'confidence': 1.0
                }
            ]
        }
    
    def analyze_file(self, file_path: str, code: str) -> AnalysisResult:
        """
        Analyze a file for issues across all dimensions.
        
        Args:
            file_path: Path to file
            code: File content
            
        Returns:
            AnalysisResult with all issues found
        """
        issues: List[Issue] = []
        lines = code.split('\n')
        
        # Analyze each dimension
        for dimension, rules in self.knowledge_base.items():
            for rule in rules:
                pattern = rule['pattern']
                
                # Check each line
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        issues.append(Issue(
                            dimension=dimension,
                            severity=rule['severity'],
                            line=line_num,
                            message=rule['message'],
                            alternatives=rule['alternatives'],
                            confidence=rule['confidence']
                        ))
        
        # Calculate score (100 - penalty)
        penalty = sum(self._get_penalty(issue.severity) for issue in issues)
        score = max(0, 100 - penalty)
        
        # Summarize by dimension
        summary = {dim: 0 for dim in Dimension}
        for issue in issues:
            summary[issue.dimension] += 1
        
        # Update stats
        self.stats['files_analyzed'] += 1
        self.stats['issues_found'] += len(issues)
        for issue in issues:
            self.stats['by_severity'][issue.severity.value] += 1
        
        return AnalysisResult(
            file_path=file_path,
            issues=issues,
            score=score,
            summary=summary
        )
    
    def _get_penalty(self, severity: Severity) -> int:
        """Get penalty points for severity"""
        penalties = {
            Severity.CRITICAL: 20,
            Severity.HIGH: 10,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 1
        }
        return penalties[severity]
    
    def debate(self, decision: str, context: Optional[Dict] = None) -> Dict:
        """
        Debate a code decision.
        
        Args:
            decision: Code decision to debate
            context: Optional context
            
        Returns:
            Debate result with arguments and alternatives
        """
        return {
            'decision': decision,
            'challenges': [
                'Have you considered performance implications?',
                'Is this the most maintainable approach?',
                'Are there security concerns?'
            ],
            'alternatives': [
                'Consider using established patterns',
                'Look for existing solutions',
                'Simplify the approach'
            ],
            'recommendation': 'Proceed with caution and add tests'
        }
    
    def get_stats(self) -> Dict:
        """Get CRUEL system statistics"""
        return self.stats.copy()


def main():
    """Test CRUEL system"""
    print("=== Dive CRUEL System Test ===\n")
    
    cruel = DiveCRUELSystem()
    
    # Test code
    test_code = '''
import os

# TODO: Implement this
password = "hardcoded_password"
api_key = "sk-1234567890"

def process_data(items=[]):
    for i in range(len(items)):
        result.append(items[i])
    
    try:
        eval(user_input)
    except:
        pass

x = 5
y = 10
'''
    
    # Analyze
    result = cruel.analyze_file("test.py", test_code)
    
    print(f"File: {result.file_path}")
    print(f"Score: {result.score:.1f}/100")
    print(f"Issues found: {len(result.issues)}\n")
    
    # Group by severity
    by_severity = {}
    for issue in result.issues:
        if issue.severity not in by_severity:
            by_severity[issue.severity] = []
        by_severity[issue.severity].append(issue)
    
    # Print issues
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        if severity in by_severity:
            print(f"\n{severity.value} Issues:")
            for issue in by_severity[severity]:
                print(f"  Line {issue.line}: {issue.message}")
                print(f"    Dimension: {issue.dimension.value}")
                print(f"    Confidence: {issue.confidence:.0%}")
                print(f"    Alternatives:")
                for alt in issue.alternatives:
                    print(f"      - {alt}")
    
    # Summary
    print(f"\n\nSummary by Dimension:")
    for dim, count in result.summary.items():
        if count > 0:
            print(f"  {dim.value}: {count} issues")
    
    # Stats
    print(f"\n\nCRUEL Stats: {cruel.get_stats()}")


if __name__ == "__main__":
    main()
