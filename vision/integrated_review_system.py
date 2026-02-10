#!/usr/bin/env python3
"""
Integrated Multi-Model Review System
Combines Orchestrator with Intelligent Multi-Model Reviewer for optimal code review
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestrator import get_orchestrator
from intelligent_multi_model_reviewer import get_intelligent_reviewer
from prompt_complexity_analyzer import get_prompt_analyzer, TaskType

@dataclass
class IntegratedReviewResult:
    """Complete review result from integrated system"""
    request_type: str  # "code_review" or "general_query"
    prompt: str
    code_files: Optional[Dict[str, str]]
    orchestration_result: Optional[Dict]
    review_report: Optional[Dict]
    final_summary: str
    confidence_score: float
    execution_time_ms: float
    total_cost_usd: float
    timestamp: str

class IntegratedReviewSystem:
    """
    Integrated system combining:
    - Orchestrator: For general queries and prompt routing
    - Intelligent Multi-Model Reviewer: For specialized code review
    """
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.reviewer = get_intelligent_reviewer()
        self.prompt_analyzer = get_prompt_analyzer()
        
        print("\n" + "="*100)
        print("INTEGRATED MULTI-MODEL REVIEW SYSTEM")
        print("="*100)
        print("Unified system combining:")
        print("  • Orchestrator: General queries + intelligent routing")
        print("  • Intelligent Reviewer: Specialized code review with complexity analysis")
        print("  • Prompt Analyzer: Task detection + model selection")
        print("="*100 + "\n")
    
    def process(self, prompt: str, code_files: Dict[str, str] = None) -> IntegratedReviewResult:
        """
        Process request using optimal system component
        
        Args:
            prompt: User's request
            code_files: Optional code files for review
        
        Returns:
            IntegratedReviewResult with complete analysis
        """
        
        start_time = datetime.now()
        
        # Analyze prompt to determine routing
        print("[Routing] Analyzing request...\n")
        complexity = self.prompt_analyzer.analyze(prompt, code_files)
        
        # Decide: Orchestrator vs Intelligent Reviewer
        if self._should_use_code_reviewer(complexity, code_files):
            print("→ Routing to: INTELLIGENT MULTI-MODEL REVIEWER\n")
            result = self._process_with_reviewer(prompt, code_files, start_time)
        else:
            print("→ Routing to: ORCHESTRATOR\n")
            result = self._process_with_orchestrator(prompt, code_files, start_time)
        
        return result
    
    def _should_use_code_reviewer(self, complexity, code_files: Optional[Dict]) -> bool:
        """Determine if should use specialized code reviewer"""
        
        # Use code reviewer if:
        # 1. Code files are provided
        # 2. Task is code-related
        # 3. Complexity is moderate or higher
        
        if not code_files:
            return False
        
        code_related_tasks = [
            TaskType.CODE_REVIEW,
            TaskType.ARCHITECTURE,
            TaskType.SECURITY,
            TaskType.PERFORMANCE,
            TaskType.ALGORITHM,
            TaskType.BUG_FIX,
            TaskType.REFACTORING,
            TaskType.API_DESIGN,
            TaskType.BEST_PRACTICES
        ]
        
        if complexity.task_type in code_related_tasks:
            return True
        
        return False
    
    def _process_with_reviewer(self, prompt: str, code_files: Dict[str, str],
                               start_time: datetime) -> IntegratedReviewResult:
        """Process using Intelligent Multi-Model Reviewer"""
        
        # Use the intelligent reviewer
        report = self.reviewer.review_code(code_files, prompt)
        
        # Generate summary
        summary_parts = []
        summary_parts.append(f"# Code Review Report")
        summary_parts.append(f"Complexity: {report.complexity_score}/10 ({report.complexity_level.upper()})")
        summary_parts.append(f"Models Used: {', '.join(report.selected_models)}")
        summary_parts.append(f"\n## Summary")
        summary_parts.append(f"Total Findings: {report.total_findings}")
        summary_parts.append(f"- Critical: {report.critical_count}")
        summary_parts.append(f"- Warning: {report.warning_count}")
        summary_parts.append(f"- Info: {report.info_count}")
        summary_parts.append(f"- Consensus: {report.consensus_count}")
        
        summary_parts.append(f"\n## Model Assessments")
        for model_name, summary in report.model_summaries.items():
            summary_parts.append(f"\n### {model_name}")
            summary_parts.append(summary)
        
        if report.findings:
            summary_parts.append(f"\n## Key Findings")
            for i, finding in enumerate(report.findings[:10], 1):  # Top 10
                consensus_mark = "🔥" if finding.consensus else ""
                summary_parts.append(f"\n{i}. [{finding.severity}] {consensus_mark} {finding.category.upper()}")
                summary_parts.append(f"   {finding.description}")
                summary_parts.append(f"   Found by: {', '.join(finding.found_by)}")
                summary_parts.append(f"   Confidence: {finding.confidence}%")
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return IntegratedReviewResult(
            request_type="code_review",
            prompt=prompt,
            code_files=code_files,
            orchestration_result=None,
            review_report={
                "complexity_score": report.complexity_score,
                "complexity_level": report.complexity_level,
                "models": report.selected_models,
                "total_findings": report.total_findings,
                "critical": report.critical_count,
                "warning": report.warning_count,
                "info": report.info_count,
                "consensus": report.consensus_count,
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "description": f.description,
                        "file": f.file,
                        "line": f.line,
                        "confidence": f.confidence,
                        "consensus": f.consensus
                    }
                    for f in report.findings
                ]
            },
            final_summary="\n".join(summary_parts),
            confidence_score=sum(f.confidence for f in report.findings) / max(len(report.findings), 1),
            execution_time_ms=execution_time,
            total_cost_usd=report.estimated_cost_usd,
            timestamp=datetime.now().isoformat()
        )
    
    def _process_with_orchestrator(self, prompt: str, code_files: Optional[Dict[str, str]],
                                   start_time: datetime) -> IntegratedReviewResult:
        """Process using Orchestrator"""
        
        # Use the orchestrator
        result = self.orchestrator.process(prompt, code_files)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return IntegratedReviewResult(
            request_type="general_query",
            prompt=prompt,
            code_files=code_files,
            orchestration_result={
                "strategy": result.strategy_used,
                "models": result.models_used,
                "complexity": result.complexity_analysis,
                "consensus_findings": result.consensus_findings,
                "conflicts": result.conflicts
            },
            review_report=None,
            final_summary=result.synthesized_result,
            confidence_score=result.confidence_score,
            execution_time_ms=execution_time,
            total_cost_usd=result.estimated_cost_usd,
            timestamp=datetime.now().isoformat()
        )

# Global instance
_system = None

def get_integrated_system() -> IntegratedReviewSystem:
    """Get or create the integrated system"""
    global _system
    if _system is None:
        _system = IntegratedReviewSystem()
    return _system

if __name__ == "__main__":
    # Test the integrated system
    system = get_integrated_system()
    
    test_cases = [
        {
            "name": "General Question (Orchestrator)",
            "prompt": "What are the key principles of clean code?",
            "code": None
        },
        {
            "name": "Simple Code Review (Intelligent Reviewer)",
            "prompt": "Review this code for improvements",
            "code": {
                "utils.py": """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""
            }
        },
        {
            "name": "Complex Security Audit (Intelligent Reviewer)",
            "prompt": "Comprehensive security analysis of this authentication system",
            "code": {
                "auth.py": """
import jwt
import bcrypt
from flask import request

SECRET_KEY = "hardcoded_secret"

def authenticate_user(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    user = execute_query(query)
    
    if user and bcrypt.checkpw(password, user['password_hash']):
        token = jwt.encode({'user_id': user['id']}, SECRET_KEY)
        return token
    return None

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    token = authenticate_user(data['username'], data['password'])
    return {'token': token}
"""
            }
        }
    ]
    
    print("\n" + "="*100)
    print("INTEGRATED SYSTEM TEST SUITE")
    print("="*100 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"TEST {i}/{len(test_cases)}: {test['name']}")
        print(f"{'='*100}\n")
        
        result = system.process(test['prompt'], test['code'])
        
        print(f"\n{'='*80}")
        print("FINAL RESULT")
        print(f"{'='*80}")
        print(f"Request Type: {result.request_type.upper()}")
        print(f"Confidence: {result.confidence_score:.1f}%")
        print(f"Execution Time: {result.execution_time_ms:.0f}ms")
        print(f"Total Cost: ${result.total_cost_usd:.4f}")
        print(f"\nSummary:\n{result.final_summary[:500]}...")
        print(f"{'='*80}\n")
    
    print("\n" + "="*100 + "\n")
