"""
Self-Modification Package for Dive AI V29.4

Allows Dive AI to analyze and modify its own code safely.
"""

from .code_analyzer import (
    SelfAwareCodeAnalyzer,
    CodeAnalysisResult,
    analyze_dive_module,
    find_bugs_in_dive
)

from .code_generator import (
    DiveCodeGenerator,
    CodeChange,
    fix_dive_bug,
    optimize_dive_module
)

from .self_modification_engine import (
    SelfModificationEngine,
    ModificationResult,
    dive_fix_bug,
    dive_optimize
)

__all__ = [
    # Analyzer
    'SelfAwareCodeAnalyzer',
    'CodeAnalysisResult',
    'analyze_dive_module',
    'find_bugs_in_dive',
    
    # Generator
    'DiveCodeGenerator',
    'CodeChange',
    'fix_dive_bug',
    'optimize_dive_module',
    
    # Engine
    'SelfModificationEngine',
    'ModificationResult',
    'dive_fix_bug',
    'dive_optimize',
]
