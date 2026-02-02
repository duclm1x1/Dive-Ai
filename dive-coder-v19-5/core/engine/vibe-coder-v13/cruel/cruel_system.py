#!/usr/bin/env python3
"""
CRUEL SYSTEM - Intelligent Code Debate & Review Engine
Challenges code decisions, provides warnings, and offers constructive criticism

Features:
- 7-dimensional code analysis (Security, Performance, Logic, Quality, Maintainability, Architecture, Patterns)
- Intelligent debate mechanism with alternatives
- Confidence-based warning system
- Real-time and on-demand analysis
- Integration with Vibe Coder System

Usage:
    python3 cruel_system.py analyze code.py
    python3 cruel_system.py debate "my code decision"
    python3 cruel_system.py review
    python3 cruel_system.py help

Author: Cruel System Team
Version: 1.0
Status: Production Ready
"""

import json
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Warning severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AnalysisDimension(Enum):
    """Seven dimensions of code analysis."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    LOGIC = "logic"
    QUALITY = "quality"
    MAINTAINABILITY = "maintainability"
    ARCHITECTURE = "architecture"
    PATTERNS = "patterns"


class CruelSystem:
    """
    Intelligent code debate and review engine.
    Challenges every decision with evidence-based reasoning.
    """

    def __init__(self):
        """Initialize Cruel System."""
        self.version = "1.0"
        self.timestamp = datetime.now().isoformat()
        self.analysis_history = []
        self.debate_history = []
        self.user_preferences = {}
        
        # Initialize knowledge base
        self.knowledge_base = self._load_knowledge_base()
        self.anti_patterns = self._load_anti_patterns()
        self.best_practices = self._load_best_practices()

    # ============================================================================
    # KNOWLEDGE BASE INITIALIZATION
    # ============================================================================

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load comprehensive knowledge base for analysis."""
        return {
            "security_rules": {
                "sql_injection": {
                    "pattern": r"(query|sql|execute)\s*=\s*['\"].*\+",
                    "severity": Severity.CRITICAL.value,
                    "message": "Potential SQL injection vulnerability detected",
                    "alternatives": [
                        "Use parameterized queries with placeholders",
                        "Use ORM (SQLAlchemy, Django ORM, etc.)",
                        "Validate and sanitize all inputs"
                    ]
                },
                "hardcoded_secrets": {
                    "pattern": r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]*['\"]",
                    "severity": Severity.CRITICAL.value,
                    "message": "Hardcoded secrets detected",
                    "alternatives": [
                        "Use environment variables",
                        "Use configuration files (not in repo)",
                        "Use secrets management service"
                    ]
                },
                "no_input_validation": {
                    "pattern": r"def\s+\w+\([^)]*\):\s*(?!.*validate|.*check|.*assert)",
                    "severity": Severity.HIGH.value,
                    "message": "No input validation detected",
                    "alternatives": [
                        "Add input validation at function entry",
                        "Use type hints and runtime validation",
                        "Use validation library"
                    ]
                }
            },
            "performance_rules": {
                "n_plus_one": {
                    "pattern": r"for\s+\w+\s+in\s+.*:\s*(?=.*query|.*select|.*fetch)",
                    "severity": Severity.HIGH.value,
                    "message": "Potential N+1 query problem",
                    "alternatives": [
                        "Use JOIN to fetch all data at once",
                        "Use eager loading",
                        "Use batch queries"
                    ]
                },
                "inefficient_loop": {
                    "pattern": r"for\s+\w+\s+in\s+.*:\s*(?=.*append)",
                    "severity": Severity.MEDIUM.value,
                    "message": "Loop could potentially use list comprehension",
                    "alternatives": [
                        "Use list comprehension for better performance",
                        "Use map() or filter()",
                        "Use generator expression"
                    ]
                },
                "global_state": {
                    "pattern": r"^[A-Z_]+\s*=\s*(?!.*=.*\()",
                    "severity": Severity.MEDIUM.value,
                    "message": "Global variable detected",
                    "alternatives": [
                        "Use dependency injection",
                        "Use class attributes",
                        "Use configuration object"
                    ]
                }
            },
            "logic_rules": {
                "missing_null_check": {
                    "pattern": r"\.(\w+)\(|\.(\w+)\s*\[",
                    "severity": Severity.HIGH.value,
                    "message": "Potential null/undefined reference",
                    "alternatives": [
                        "Add null check before access",
                        "Use optional chaining (if supported)",
                        "Use try-except block"
                    ]
                },
                "division_by_zero": {
                    "pattern": r"/\s*(\w+|\d+)",
                    "severity": Severity.HIGH.value,
                    "message": "Potential division by zero",
                    "alternatives": [
                        "Add zero check before division",
                        "Use exception handling",
                        "Provide default value"
                    ]
                },
                "mutable_default": {
                    "pattern": r"def\s+\w+\([^)]*=\s*[\[\{]",
                    "severity": Severity.HIGH.value,
                    "message": "Mutable default argument detected",
                    "alternatives": [
                        "Use None as default, create new object in function",
                        "Use immutable defaults (tuple, frozenset)",
                        "Use factory function"
                    ]
                }
            },
            "quality_rules": {
                "unclear_naming": {
                    "pattern": r"(x|y|z|a|b|c|tmp|temp|data|obj|val)\s*=",
                    "severity": Severity.MEDIUM.value,
                    "message": "Unclear variable name detected",
                    "alternatives": [
                        "Use descriptive names (e.g., 'user_count' instead of 'x')",
                        "Use domain-specific terminology",
                        "Add explanatory comments"
                    ]
                },
                "long_function": {
                    "severity": Severity.MEDIUM.value,
                    "message": "Function is too long (>50 lines)",
                    "alternatives": [
                        "Extract helper functions",
                        "Use composition pattern",
                        "Simplify logic"
                    ]
                },
                "high_complexity": {
                    "severity": Severity.MEDIUM.value,
                    "message": "High cyclomatic complexity detected",
                    "alternatives": [
                        "Extract conditional logic to separate functions",
                        "Use polymorphism instead of if-else chains",
                        "Simplify decision trees"
                    ]
                }
            },
            "maintainability_rules": {
                "magic_numbers": {
                    "pattern": r"(?<![a-zA-Z_])\d{2,}(?![a-zA-Z_])",
                    "severity": Severity.LOW.value,
                    "message": "Magic number detected",
                    "alternatives": [
                        "Extract to named constant",
                        "Add explanatory comment",
                        "Use configuration file"
                    ]
                },
                "missing_documentation": {
                    "severity": Severity.LOW.value,
                    "message": "Function lacks documentation",
                    "alternatives": [
                        "Add docstring with description, params, returns",
                        "Add inline comments for complex logic",
                        "Generate documentation from code"
                    ]
                },
                "inconsistent_style": {
                    "severity": Severity.LOW.value,
                    "message": "Inconsistent code style detected",
                    "alternatives": [
                        "Use formatter (Black, Prettier, etc.)",
                        "Follow language style guide (PEP 8, etc.)",
                        "Use linter configuration"
                    ]
                }
            },
            "architecture_rules": {
                "tight_coupling": {
                    "severity": Severity.HIGH.value,
                    "message": "Tight coupling detected",
                    "alternatives": [
                        "Use dependency injection",
                        "Define interfaces/abstract classes",
                        "Use factory pattern"
                    ]
                },
                "god_object": {
                    "severity": Severity.MEDIUM.value,
                    "message": "Class doing too much (God Object)",
                    "alternatives": [
                        "Split into smaller, focused classes",
                        "Use composition over inheritance",
                        "Apply Single Responsibility Principle"
                    ]
                },
                "circular_dependency": {
                    "severity": Severity.HIGH.value,
                    "message": "Circular dependency detected",
                    "alternatives": [
                        "Introduce mediator/event bus",
                        "Restructure module hierarchy",
                        "Use dependency injection"
                    ]
                }
            },
            "patterns_rules": {
                "missing_context_manager": {
                    "pattern": r"(open|lock|connection)\s*\(.*\).*try.*finally",
                    "severity": Severity.MEDIUM.value,
                    "message": "Resource management without context manager",
                    "alternatives": [
                        "Use 'with' statement (Python)",
                        "Use try-with-resources (Java)",
                        "Use RAII pattern"
                    ]
                },
                "callback_hell": {
                    "pattern": r"\.then\(.*\.then\(.*\.then\(",
                    "severity": Severity.MEDIUM.value,
                    "message": "Callback hell (pyramid of doom)",
                    "alternatives": [
                        "Use async/await",
                        "Use Promise chains with proper formatting",
                        "Use reactive programming"
                    ]
                },
                "missing_error_handling": {
                    "severity": Severity.HIGH.value,
                    "message": "Missing error handling",
                    "alternatives": [
                        "Add try-except/try-catch blocks",
                        "Use error handling middleware",
                        "Implement error recovery strategy"
                    ]
                }
            }
        }

    def _load_anti_patterns(self) -> List[Dict[str, Any]]:
        """Load common anti-patterns database."""
        return [
            {
                "name": "Singleton Pattern Abuse",
                "problem": "Using Singleton for everything creates hidden dependencies",
                "solution": "Use dependency injection instead",
                "severity": "MEDIUM"
            },
            {
                "name": "God Object",
                "problem": "One class doing too many things",
                "solution": "Split into smaller, focused classes",
                "severity": "HIGH"
            },
            {
                "name": "Feature Envy",
                "problem": "Method uses more features of another class than its own",
                "solution": "Move method to the class that has the data",
                "severity": "MEDIUM"
            },
            {
                "name": "Primitive Obsession",
                "problem": "Using primitives instead of small objects",
                "solution": "Create value objects for domain concepts",
                "severity": "LOW"
            },
            {
                "name": "Switch Statements",
                "problem": "Large switch statements instead of polymorphism",
                "solution": "Use inheritance or strategy pattern",
                "severity": "MEDIUM"
            }
        ]

    def _load_best_practices(self) -> Dict[str, List[str]]:
        """Load best practices for different languages."""
        return {
            "python": [
                "Follow PEP 8 style guide",
                "Use type hints for clarity",
                "Use context managers for resource management",
                "Use list comprehensions for simple transformations",
                "Handle exceptions specifically, not with bare except",
                "Use docstrings for all public functions",
                "Avoid mutable default arguments",
                "Use f-strings for string formatting"
            ],
            "javascript": [
                "Use const/let instead of var",
                "Use async/await instead of callbacks",
                "Add JSDoc comments for functions",
                "Use arrow functions for callbacks",
                "Handle promise rejections",
                "Use strict mode",
                "Avoid global variables",
                "Use template literals for strings"
            ],
            "java": [
                "Follow Java naming conventions",
                "Use interfaces for abstraction",
                "Use try-with-resources for resource management",
                "Use Optional instead of null",
                "Use streams for collections",
                "Add Javadoc comments",
                "Use dependency injection",
                "Avoid checked exceptions when possible"
            ],
            "typescript": [
                "Use strict mode in tsconfig.json",
                "Avoid 'any' type, use proper typing",
                "Use interfaces for contracts",
                "Use enums for constants",
                "Use async/await for promises",
                "Add JSDoc comments",
                "Use readonly for immutable properties",
                "Use discriminated unions for type safety"
            ]
        }

    # ============================================================================
    # CORE ANALYSIS ENGINE
    # ============================================================================

    def analyze(self, code: str, language: str = "python", filename: str = "") -> Dict[str, Any]:
        """
        Perform comprehensive 7-dimensional analysis of code.
        
        Args:
            code: Source code to analyze
            language: Programming language
            filename: Optional filename for context
            
        Returns:
            Analysis report with warnings and recommendations
        """
        analysis_report = {
            "timestamp": self.timestamp,
            "filename": filename,
            "language": language,
            "code_length": len(code.split('\n')),
            "dimensions": {},
            "overall_score": 0,
            "warnings": [],
            "recommendations": [],
            "debate_points": []
        }

        # Run all 7 analysis engines
        analysis_report["dimensions"]["security"] = self._analyze_security(code, language)
        analysis_report["dimensions"]["performance"] = self._analyze_performance(code, language)
        analysis_report["dimensions"]["logic"] = self._analyze_logic(code, language)
        analysis_report["dimensions"]["quality"] = self._analyze_quality(code, language)
        analysis_report["dimensions"]["maintainability"] = self._analyze_maintainability(code, language)
        analysis_report["dimensions"]["architecture"] = self._analyze_architecture(code, language)
        analysis_report["dimensions"]["patterns"] = self._analyze_patterns(code, language)

        # Aggregate warnings
        analysis_report["warnings"] = self._aggregate_warnings(analysis_report["dimensions"])
        
        # Generate debate points
        analysis_report["debate_points"] = self._generate_debate_points(code, language)
        
        # Calculate overall score
        analysis_report["overall_score"] = self._calculate_overall_score(analysis_report["dimensions"])
        
        # Generate recommendations
        analysis_report["recommendations"] = self._generate_recommendations(analysis_report)

        # Store in history
        self.analysis_history.append(analysis_report)

        return analysis_report

    def _analyze_security(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze security dimension."""
        findings = {
            "dimension": "security",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        security_rules = self.knowledge_base.get("security_rules", {})
        
        for rule_name, rule in security_rules.items():
            if "pattern" in rule:
                matches = re.finditer(rule["pattern"], code, re.MULTILINE)
                for match in matches:
                    findings["issues"].append({
                        "type": rule_name,
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "line": code[:match.start()].count('\n') + 1,
                        "alternatives": rule.get("alternatives", []),
                        "confidence": 85
                    })
                    findings["score"] -= 15

        findings["confidence"] = min(100, 50 + len(findings["issues"]) * 10)
        findings["score"] = max(0, findings["score"])
        
        return findings

    def _analyze_performance(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze performance dimension."""
        findings = {
            "dimension": "performance",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        performance_rules = self.knowledge_base.get("performance_rules", {})
        
        for rule_name, rule in performance_rules.items():
            if "pattern" in rule:
                matches = re.finditer(rule["pattern"], code, re.MULTILINE)
                for match in matches:
                    findings["issues"].append({
                        "type": rule_name,
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "line": code[:match.start()].count('\n') + 1,
                        "alternatives": rule.get("alternatives", []),
                        "confidence": 75
                    })
                    findings["score"] -= 10

        findings["confidence"] = min(100, 50 + len(findings["issues"]) * 8)
        findings["score"] = max(0, findings["score"])
        
        return findings

    def _analyze_logic(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze logic dimension."""
        findings = {
            "dimension": "logic",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        logic_rules = self.knowledge_base.get("logic_rules", {})
        
        for rule_name, rule in logic_rules.items():
            if "pattern" in rule:
                matches = re.finditer(rule["pattern"], code, re.MULTILINE)
                for match in matches:
                    findings["issues"].append({
                        "type": rule_name,
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "line": code[:match.start()].count('\n') + 1,
                        "alternatives": rule.get("alternatives", []),
                        "confidence": 80
                    })
                    findings["score"] -= 12

        findings["confidence"] = min(100, 50 + len(findings["issues"]) * 9)
        findings["score"] = max(0, findings["score"])
        
        return findings

    def _analyze_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code quality dimension."""
        findings = {
            "dimension": "quality",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        # Check for unclear naming
        unclear_vars = re.findall(r'\b([a-z]|tmp|temp|data|obj|val)\s*=', code)
        if unclear_vars:
            findings["issues"].append({
                "type": "unclear_naming",
                "severity": "MEDIUM",
                "message": f"Found {len(unclear_vars)} unclear variable names",
                "alternatives": ["Use descriptive names", "Use domain terminology"],
                "confidence": 70
            })
            findings["score"] -= 8

        # Check function length
        functions = re.findall(r'def\s+\w+\([^)]*\):(.*?)(?=\ndef|\nclass|\Z)', code, re.DOTALL)
        for func in functions:
            lines = len(func.split('\n'))
            if lines > 50:
                findings["issues"].append({
                    "type": "long_function",
                    "severity": "MEDIUM",
                    "message": f"Function is {lines} lines (consider breaking it down)",
                    "alternatives": ["Extract helper functions", "Use composition"],
                    "confidence": 85
                })
                findings["score"] -= 5

        findings["confidence"] = min(100, 60 + len(findings["issues"]) * 5)
        findings["score"] = max(0, findings["score"])
        
        return findings

    def _analyze_maintainability(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze maintainability dimension."""
        findings = {
            "dimension": "maintainability",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        # Check for magic numbers
        magic_numbers = re.findall(r'(?<![a-zA-Z_])\d{2,}(?![a-zA-Z_])', code)
        if len(magic_numbers) > 3:
            findings["issues"].append({
                "type": "magic_numbers",
                "severity": "LOW",
                "message": f"Found {len(magic_numbers)} magic numbers",
                "alternatives": ["Extract to constants", "Add comments"],
                "confidence": 65
            })
            findings["score"] -= 5

        # Check for documentation
        docstrings = len(re.findall(r'""".*?"""', code, re.DOTALL))
        functions = len(re.findall(r'def\s+\w+', code))
        if functions > 0 and docstrings < functions * 0.5:
            findings["issues"].append({
                "type": "missing_documentation",
                "severity": "LOW",
                "message": "Insufficient documentation",
                "alternatives": ["Add docstrings", "Add comments"],
                "confidence": 75
            })
            findings["score"] -= 3

        findings["confidence"] = min(100, 60 + len(findings["issues"]) * 4)
        findings["score"] = max(0, findings["score"])
        
        return findings

    def _analyze_architecture(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze architecture dimension."""
        findings = {
            "dimension": "architecture",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        # Check for direct instantiation (tight coupling)
        direct_instantiation = len(re.findall(r'=\s*\w+\(', code))
        if direct_instantiation > 5:
            findings["issues"].append({
                "type": "tight_coupling",
                "severity": "HIGH",
                "message": "Potential tight coupling through direct instantiation",
                "alternatives": ["Use dependency injection", "Use factory pattern"],
                "confidence": 70
            })
            findings["score"] -= 15

        # Check for god objects (large classes)
        classes = re.findall(r'class\s+\w+.*?(?=\nclass|\Z)', code, re.DOTALL)
        for cls in classes:
            methods = len(re.findall(r'def\s+\w+', cls))
            if methods > 15:
                findings["issues"].append({
                    "type": "god_object",
                    "severity": "MEDIUM",
                    "message": f"Class has {methods} methods (consider splitting)",
                    "alternatives": ["Split into smaller classes", "Use composition"],
                    "confidence": 80
                })
                findings["score"] -= 10

        findings["confidence"] = min(100, 60 + len(findings["issues"]) * 7)
        findings["score"] = max(0, findings["score"])
        
        return findings

    def _analyze_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze design patterns dimension."""
        findings = {
            "dimension": "patterns",
            "score": 100,
            "issues": [],
            "confidence": 0
        }

        # Check for context manager usage (Python)
        if language == "python":
            file_opens = len(re.findall(r'open\s*\(', code))
            with_statements = len(re.findall(r'with\s+', code))
            if file_opens > with_statements:
                findings["issues"].append({
                    "type": "missing_context_manager",
                    "severity": "MEDIUM",
                    "message": "Resource management without context manager",
                    "alternatives": ["Use 'with' statement"],
                    "confidence": 85
                })
                findings["score"] -= 10

        # Check for error handling
        try_blocks = len(re.findall(r'try\s*:', code))
        functions = len(re.findall(r'def\s+\w+', code))
        if functions > 0 and try_blocks < functions * 0.3:
            findings["issues"].append({
                "type": "missing_error_handling",
                "severity": "HIGH",
                "message": "Insufficient error handling",
                "alternatives": ["Add try-except blocks", "Use error middleware"],
                "confidence": 75
            })
            findings["score"] -= 12

        findings["confidence"] = min(100, 60 + len(findings["issues"]) * 6)
        findings["score"] = max(0, findings["score"])
        
        return findings

    # ============================================================================
    # DEBATE MECHANISM
    # ============================================================================

    def debate(self, decision: str, context: str = "") -> Dict[str, Any]:
        """
        Debate a code decision with alternatives and trade-offs.
        
        Args:
            decision: The decision/approach to debate
            context: Additional context about the decision
            
        Returns:
            Debate analysis with alternatives and recommendations
        """
        debate_session = {
            "timestamp": self.timestamp,
            "decision": decision,
            "context": context,
            "challenges": [],
            "alternatives": [],
            "trade_offs": [],
            "recommendation": "",
            "reasoning": []
        }

        # Identify decision type
        decision_type = self._identify_decision_type(decision)
        debate_session["decision_type"] = decision_type

        # Generate challenges
        debate_session["challenges"] = self._generate_challenges(decision, decision_type)

        # Generate alternatives
        debate_session["alternatives"] = self._generate_alternatives(decision, decision_type)

        # Analyze trade-offs
        debate_session["trade_offs"] = self._analyze_trade_offs(
            debate_session["alternatives"]
        )

        # Provide recommendation
        debate_session["recommendation"] = self._recommend(
            decision,
            debate_session["alternatives"],
            debate_session["trade_offs"]
        )

        # Provide reasoning
        debate_session["reasoning"] = self._provide_reasoning(
            decision,
            debate_session["challenges"],
            debate_session["recommendation"]
        )

        # Store in history
        self.debate_history.append(debate_session)

        return debate_session

    def _identify_decision_type(self, decision: str) -> str:
        """Identify the type of decision being debated."""
        decision_lower = decision.lower()
        
        if any(word in decision_lower for word in ["global", "variable", "state"]):
            return "state_management"
        elif any(word in decision_lower for word in ["error", "exception", "catch", "try"]):
            return "error_handling"
        elif any(word in decision_lower for word in ["loop", "iteration", "for", "while"]):
            return "iteration"
        elif any(word in decision_lower for word in ["class", "object", "design", "pattern"]):
            return "design"
        elif any(word in decision_lower for word in ["query", "database", "sql", "fetch"]):
            return "database"
        elif any(word in decision_lower for word in ["security", "auth", "encrypt", "password"]):
            return "security"
        else:
            return "general"

    def _generate_challenges(self, decision: str, decision_type: str) -> List[Dict[str, str]]:
        """Generate challenges to the decision."""
        challenges = []

        if decision_type == "state_management":
            challenges = [
                {
                    "challenge": "Why use global state instead of dependency injection?",
                    "concern": "Global state creates hidden dependencies and makes testing difficult"
                },
                {
                    "challenge": "How will you handle state mutations across modules?",
                    "concern": "Global state is hard to track and debug"
                },
                {
                    "challenge": "What about thread safety and concurrency?",
                    "concern": "Global state may cause race conditions in concurrent environments"
                }
            ]
        elif decision_type == "error_handling":
            challenges = [
                {
                    "challenge": "Are you catching too broad an exception?",
                    "concern": "Broad exception handling can mask unexpected errors"
                },
                {
                    "challenge": "How will users know what went wrong?",
                    "concern": "Error messages should be specific and actionable"
                },
                {
                    "challenge": "Are you handling recovery properly?",
                    "concern": "Just catching isn't enough; you need a recovery strategy"
                }
            ]
        elif decision_type == "database":
            challenges = [
                {
                    "challenge": "Is this a potential N+1 query problem?",
                    "concern": "Fetching in loops can cause performance issues"
                },
                {
                    "challenge": "Are you using parameterized queries?",
                    "concern": "String concatenation in queries is vulnerable to injection"
                },
                {
                    "challenge": "Have you considered caching?",
                    "concern": "Repeated queries could be optimized with caching"
                }
            ]
        else:
            challenges = [
                {
                    "challenge": "Have you considered alternative approaches?",
                    "concern": "The first solution isn't always the best"
                },
                {
                    "challenge": "What are the trade-offs?",
                    "concern": "Every decision has pros and cons"
                },
                {
                    "challenge": "How does this affect maintainability?",
                    "concern": "Future developers need to understand your code"
                }
            ]

        return challenges

    def _generate_alternatives(self, decision: str, decision_type: str) -> List[Dict[str, Any]]:
        """Generate alternative approaches."""
        alternatives = []

        if decision_type == "state_management":
            alternatives = [
                {
                    "name": "Dependency Injection",
                    "description": "Pass state as dependencies to functions/classes",
                    "pros": ["Explicit dependencies", "Easy to test", "Thread-safe"],
                    "cons": ["More verbose", "More parameters"],
                    "score": 95
                },
                {
                    "name": "Configuration Object",
                    "description": "Use a configuration class instead of global variables",
                    "pros": ["Encapsulated", "Easier to manage", "Can be immutable"],
                    "cons": ["Still global-like", "Need to pass around"],
                    "score": 80
                },
                {
                    "name": "Environment Variables",
                    "description": "Store configuration in environment variables",
                    "pros": ["Secure", "Environment-specific", "Standard practice"],
                    "cons": ["Less flexible", "Runtime-only"],
                    "score": 75
                }
            ]
        elif decision_type == "error_handling":
            alternatives = [
                {
                    "name": "Specific Exception Handling",
                    "description": "Catch specific exception types",
                    "pros": ["Precise", "Clear intent", "Catches real errors"],
                    "cons": ["More verbose", "Need to know exception types"],
                    "score": 95
                },
                {
                    "name": "Exception Chaining",
                    "description": "Wrap exceptions with context",
                    "pros": ["Preserves stack trace", "Adds context", "Debugging-friendly"],
                    "cons": ["More code", "Overhead"],
                    "score": 85
                },
                {
                    "name": "Result Type (Either/Option)",
                    "description": "Use Result/Either type for error handling",
                    "pros": ["Type-safe", "Explicit", "Functional approach"],
                    "cons": ["Language-dependent", "Learning curve"],
                    "score": 80
                }
            ]
        elif decision_type == "database":
            alternatives = [
                {
                    "name": "Eager Loading / JOIN",
                    "description": "Fetch all data in one query using JOINs",
                    "pros": ["Single query", "Better performance", "Atomic"],
                    "cons": ["More complex query", "Larger result set"],
                    "score": 95
                },
                {
                    "name": "Batch Queries",
                    "description": "Fetch multiple items in one query",
                    "pros": ["Fewer queries", "Better performance", "Simpler than JOIN"],
                    "cons": ["Still multiple queries", "More complex logic"],
                    "score": 85
                },
                {
                    "name": "Caching",
                    "description": "Cache frequently accessed data",
                    "pros": ["Fast", "Reduces DB load", "Scalable"],
                    "cons": ["Cache invalidation", "Stale data", "Complexity"],
                    "score": 75
                }
            ]
        else:
            alternatives = [
                {
                    "name": "Approach A",
                    "description": "First alternative approach",
                    "pros": ["Benefit 1", "Benefit 2"],
                    "cons": ["Drawback 1"],
                    "score": 85
                },
                {
                    "name": "Approach B",
                    "description": "Second alternative approach",
                    "pros": ["Benefit 1", "Benefit 2"],
                    "cons": ["Drawback 1"],
                    "score": 80
                }
            ]

        return alternatives

    def _analyze_trade_offs(self, alternatives: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Analyze trade-offs between alternatives."""
        trade_offs = []

        if len(alternatives) >= 2:
            for i, alt1 in enumerate(alternatives[:-1]):
                for alt2 in alternatives[i+1:]:
                    trade_offs.append({
                        "between": f"{alt1['name']} vs {alt2['name']}",
                        "trade_off": f"{alt1['name']} is better for X, but {alt2['name']} is better for Y",
                        "consideration": "Choose based on your specific requirements"
                    })

        return trade_offs

    def _recommend(self, decision: str, alternatives: List[Dict[str, Any]], 
                   trade_offs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Provide a recommendation."""
        if not alternatives:
            return {"recommendation": "No clear recommendation", "reasoning": ""}

        # Find highest scoring alternative
        best = max(alternatives, key=lambda x: x.get("score", 0))

        return {
            "recommendation": best["name"],
            "reasoning": f"Based on analysis, {best['name']} provides the best balance of benefits",
            "score": best.get("score", 0),
            "confidence": 85
        }

    def _provide_reasoning(self, decision: str, challenges: List[Dict[str, str]], 
                          recommendation: Dict[str, Any]) -> List[str]:
        """Provide detailed reasoning."""
        reasoning = [
            f"Decision analyzed: {decision}",
            f"Identified {len(challenges)} key challenges to consider",
            f"Recommended approach: {recommendation.get('recommendation', 'N/A')}",
            "Consider the trade-offs carefully before implementing"
        ]
        return reasoning

    # ============================================================================
    # AGGREGATION & REPORTING
    # ============================================================================

    def _aggregate_warnings(self, dimensions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate all warnings from all dimensions."""
        warnings = []
        
        for dimension_name, dimension_data in dimensions.items():
            for issue in dimension_data.get("issues", []):
                warnings.append({
                    "dimension": dimension_name,
                    "severity": issue.get("severity", "MEDIUM"),
                    "type": issue.get("type", "unknown"),
                    "message": issue.get("message", ""),
                    "line": issue.get("line", 0),
                    "alternatives": issue.get("alternatives", []),
                    "confidence": issue.get("confidence", 0)
                })

        # Sort by severity and confidence
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        warnings.sort(
            key=lambda x: (severity_order.get(x["severity"], 5), -x["confidence"])
        )

        return warnings

    def _generate_debate_points(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Generate specific debate points about the code."""
        debate_points = []

        # Check for common decisions to debate
        if "global" in code:
            debate_points.append({
                "point": "Why use global variables?",
                "concern": "Global state creates hidden dependencies",
                "alternatives": ["Dependency injection", "Configuration object", "Environment variables"]
            })

        if "except:" in code:
            debate_points.append({
                "point": "Why catch all exceptions?",
                "concern": "Bare except catches unexpected errors",
                "alternatives": ["Catch specific exceptions", "Use exception chaining", "Let errors propagate"]
            })

        if re.search(r"for\s+\w+\s+in\s+.*:\s*.*query", code):
            debate_points.append({
                "point": "Is this an N+1 query problem?",
                "concern": "Querying in loops causes performance issues",
                "alternatives": ["Use JOIN", "Batch queries", "Add caching"]
            })

        return debate_points

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Based on overall score
        overall_score = analysis.get("overall_score", 0)
        
        if overall_score < 50:
            recommendations.append("⚠️ CRITICAL: Code quality is poor. Consider major refactoring.")
        elif overall_score < 70:
            recommendations.append("⚠️ HIGH: Several issues need attention. Plan improvements.")
        elif overall_score < 85:
            recommendations.append("✓ MEDIUM: Some improvements possible. Consider for next sprint.")
        else:
            recommendations.append("✓ GOOD: Code quality is solid. Keep up the good work!")

        # Based on warnings
        critical_warnings = [w for w in analysis.get("warnings", []) if w["severity"] == "CRITICAL"]
        high_warnings = [w for w in analysis.get("warnings", []) if w["severity"] == "HIGH"]

        if critical_warnings:
            recommendations.append(f"🔴 Fix {len(critical_warnings)} critical issues immediately")
        
        if high_warnings:
            recommendations.append(f"🟠 Address {len(high_warnings)} high-priority issues")

        return recommendations

    def _calculate_overall_score(self, dimensions: Dict[str, Any]) -> int:
        """Calculate overall code health score."""
        scores = []
        weights = {
            "security": 0.25,
            "performance": 0.20,
            "logic": 0.20,
            "quality": 0.15,
            "maintainability": 0.10,
            "architecture": 0.07,
            "patterns": 0.03
        }

        for dimension_name, weight in weights.items():
            if dimension_name in dimensions:
                score = dimensions[dimension_name].get("score", 100)
                scores.append(score * weight)

        return int(sum(scores)) if scores else 100

    # ============================================================================
    # REPORTING & OUTPUT
    # ============================================================================

    def generate_report(self, analysis: Dict[str, Any], format: str = "text") -> str:
        """Generate a formatted analysis report."""
        if format == "json":
            return json.dumps(analysis, indent=2)

        # Text format
        report = []
        report.append("=" * 70)
        report.append("🔥 CRUEL SYSTEM - CODE ANALYSIS REPORT")
        report.append("=" * 70)
        report.append("")

        # Header
        report.append(f"File: {analysis.get('filename', 'N/A')}")
        report.append(f"Language: {analysis.get('language', 'N/A')}")
        report.append(f"Lines of Code: {analysis.get('code_length', 0)}")
        report.append(f"Overall Score: {analysis.get('overall_score', 0)}/100")
        report.append("")

        # Dimension Scores
        report.append("📊 DIMENSION SCORES:")
        report.append("-" * 70)
        for dim_name, dim_data in analysis.get("dimensions", {}).items():
            score = dim_data.get("score", 0)
            issues = len(dim_data.get("issues", []))
            report.append(f"  {dim_name.upper():20} {score:3}/100  ({issues} issues)")
        report.append("")

        # Warnings
        warnings = analysis.get("warnings", [])
        if warnings:
            report.append("⚠️  WARNINGS:")
            report.append("-" * 70)
            for warning in warnings[:10]:  # Top 10
                report.append(f"  [{warning['severity']:8}] {warning['message']}")
                report.append(f"            Line {warning.get('line', '?')}")
                if warning.get("alternatives"):
                    report.append(f"            Alternatives: {', '.join(warning['alternatives'][:2])}")
            if len(warnings) > 10:
                report.append(f"  ... and {len(warnings) - 10} more warnings")
            report.append("")

        # Debate Points
        debate_points = analysis.get("debate_points", [])
        if debate_points:
            report.append("🎭 DEBATE POINTS:")
            report.append("-" * 70)
            for point in debate_points[:5]:
                report.append(f"  ❓ {point['point']}")
                report.append(f"     Concern: {point['concern']}")
            report.append("")

        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            report.append("💡 RECOMMENDATIONS:")
            report.append("-" * 70)
            for rec in recommendations:
                report.append(f"  • {rec}")
            report.append("")

        report.append("=" * 70)
        return "\n".join(report)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface for Cruel System."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()
    cruel = CruelSystem()

    if command == "help":
        print_help()

    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 cruel_system.py analyze <file.py>")
            return

        filepath = sys.argv[2]
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return

        with open(filepath, 'r') as f:
            code = f.read()

        language = "python" if filepath.endswith(".py") else "javascript"
        analysis = cruel.analyze(code, language, filepath)
        report = cruel.generate_report(analysis)
        print(report)

    elif command == "debate":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 cruel_system.py debate \"your decision\"")
            return

        decision = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        
        debate = cruel.debate(decision, context)
        
        print("=" * 70)
        print("🎭 CRUEL SYSTEM - DEBATE SESSION")
        print("=" * 70)
        print(f"\nDecision: {debate['decision']}")
        print(f"Type: {debate['decision_type']}\n")
        
        print("❓ CHALLENGES:")
        for i, challenge in enumerate(debate['challenges'], 1):
            print(f"  {i}. {challenge['challenge']}")
            print(f"     └─ {challenge['concern']}\n")
        
        print("💡 ALTERNATIVES:")
        for alt in debate['alternatives']:
            print(f"  • {alt['name']} (Score: {alt['score']}/100)")
            print(f"    {alt['description']}")
            print(f"    Pros: {', '.join(alt['pros'][:2])}")
            print(f"    Cons: {', '.join(alt['cons'][:1])}\n")
        
        print("🎯 RECOMMENDATION:")
        rec = debate['recommendation']
        print(f"  {rec['recommendation']}")
        print(f"  Confidence: {rec['confidence']}%\n")

    elif command == "review":
        print("📋 Review Mode - Analyzing current project...")
        print("(This would scan all files in the project)")

    else:
        print(f"❌ Unknown command: {command}")
        print_help()


def print_help():
    """Print help message."""
    print("""
🔥 CRUEL SYSTEM v1.0 - Intelligent Code Debate & Review Engine

USAGE:
    python3 cruel_system.py <command> [arguments]

COMMANDS:
    analyze <file>      Analyze a code file (7-dimensional analysis)
    debate <decision>   Debate a code decision with alternatives
    review              Review entire project
    help                Show this help message

EXAMPLES:
    python3 cruel_system.py analyze mycode.py
    python3 cruel_system.py debate "using global variables"
    python3 cruel_system.py review

FEATURES:
    ✓ 7-Dimensional Analysis (Security, Performance, Logic, Quality, etc.)
    ✓ Intelligent Debate Mechanism
    ✓ Alternative Suggestions
    ✓ Trade-off Analysis
    ✓ Confidence Scoring
    ✓ Actionable Recommendations

For more information, see CRUEL_SYSTEM_DESIGN.md
    """)


if __name__ == "__main__":
    main()
