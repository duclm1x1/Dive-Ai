#!/usr/bin/env python3
"""
Multi-Model Review Agent - Updated with V98Store Models
Uses Gemini 3 Pro Preview, DeepSeek V3.2 Thinking, and Claude Opus 4.5
for comprehensive code review
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unified_llm_client import get_unified_client

@dataclass
class ReviewFinding:
    """A single review finding"""
    severity: str  # CRITICAL, WARNING, INFO
    category: str  # security, performance, bugs, best_practices, architecture
    description: str
    file: str
    line: int
    suggested_fix: str
    found_by: List[str]  # Which models found this
    confidence: int  # 0-100

@dataclass
class ReviewReport:
    """Complete review report"""
    timestamp: str
    total_findings: int
    critical_count: int
    warning_count: int
    info_count: int
    findings: List[ReviewFinding]
    model_summaries: Dict[str, str]
    execution_time_ms: float
    tokens_used: Dict[str, int]
    consensus_findings: int  # Findings agreed upon by 2+ models

class MultiModelReviewer:
    """
    Multi-Model Review Agent
    Uses THREE premium models from v98store sequentially
    """
    
    def __init__(self):
        self.llm_client = get_unified_client()
        self.findings = []
        
        print("\n" + "="*100)
        print("MULTI-MODEL REVIEW AGENT (V98Store Models)")
        print("="*100)
        print("Models: Gemini 3 Pro Preview → DeepSeek V3.2 Thinking → Claude Opus 4.5")
        print("Pricing: $2/$12 → $2/$3 → $5/$25 per 1M tokens")
        print("="*100 + "\n")
    
    def review_code(self, code_files: Dict[str, str], context: str = "") -> ReviewReport:
        """
        Review code using three premium models sequentially
        
        Args:
            code_files: Dict of {filename: code_content}
            context: Project context from Dive-Memory
        
        Returns:
            ReviewReport with all findings
        """
        
        start_time = datetime.now()
        
        # Prepare code for review
        code_text = self._format_code_files(code_files)
        
        print("[Phase 1/4] Gemini 3 Pro Preview Review...\n")
        gemini_review = self._review_with_gemini(code_text, context)
        
        print("[Phase 2/4] DeepSeek V3.2 Thinking Cross-Review...\n")
        deepseek_review = self._review_with_deepseek(code_text, context, gemini_review)
        
        print("[Phase 3/4] Claude Opus 4.5 Final Validation...\n")
        claude_review = self._review_with_claude(code_text, context, gemini_review, deepseek_review)
        
        print("[Phase 4/4] Synthesizing Findings...\n")
        report = self._synthesize_reviews(
            gemini_review,
            deepseek_review,
            claude_review,
            (datetime.now() - start_time).total_seconds() * 1000
        )
        
        return report
    
    def _format_code_files(self, code_files: Dict[str, str]) -> str:
        """Format code files for review"""
        formatted = []
        for filename, content in code_files.items():
            formatted.append(f"=== {filename} ===\n{content}\n")
        return "\n".join(formatted)
    
    def _review_with_gemini(self, code: str, context: str) -> Dict[str, Any]:
        """Phase 1: Gemini 3 Pro Preview Review"""
        
        prompt = f"""You are a senior code reviewer using Gemini 3 Pro Preview with advanced reasoning.

PROJECT CONTEXT:
{context}

CODE TO REVIEW:
{code}

REVIEW FOCUS:
1. Architecture and design patterns
2. Security vulnerabilities
3. Performance bottlenecks
4. Best practice violations
5. Code maintainability

OUTPUT FORMAT (JSON):
{{
  "summary": "Overall assessment",
  "confidence": 85,
  "findings": [
    {{
      "severity": "CRITICAL|WARNING|INFO",
      "category": "security|performance|bugs|best_practices|architecture",
      "description": "What's wrong",
      "file": "filename",
      "line": 123,
      "suggested_fix": "How to fix it",
      "confidence": 90
    }}
  ]
}}

Be thorough and critical. This is the first review pass."""

        response = self.llm_client.chat_with_premium_model("gemini-3-pro", prompt, max_tokens=4000)
        
        if response.status == "success":
            try:
                # Extract JSON from response
                content = response.content
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                review_data = json.loads(content[json_start:json_end])
                
                print(f"✓ Gemini Review: {len(review_data.get('findings', []))} findings")
                print(f"  Confidence: {review_data.get('confidence', 0)}%")
                print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms\n")
                
                return {
                    "model": "gemini-3-pro-preview-thinking",
                    "data": review_data,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms
                }
            except Exception as e:
                print(f"⚠ JSON parse error: {e}")
                return {"model": "gemini-3-pro-preview-thinking", "data": {"summary": response.content, "findings": [], "confidence": 0}}
        else:
            print(f"✗ Gemini Review failed: {response.error}\n")
            return {"model": "gemini-3-pro-preview-thinking", "data": {"summary": "Failed", "findings": [], "confidence": 0}}
    
    def _review_with_deepseek(self, code: str, context: str, gemini_review: Dict) -> Dict[str, Any]:
        """Phase 2: DeepSeek V3.2 Thinking Cross-Review"""
        
        gemini_findings = gemini_review.get("data", {}).get("findings", [])
        
        prompt = f"""You are a senior code reviewer using DeepSeek V3.2 with integrated thinking.

PROJECT CONTEXT:
{context}

CODE TO REVIEW:
{code}

GEMINI 3 PRO FOUND ({len(gemini_findings)} issues):
{json.dumps(gemini_findings, indent=2)}

YOUR TASK:
1. Validate Gemini's findings (confirm or refute)
2. Find ADDITIONAL issues Gemini missed
3. Focus on tool integration, API design, and code quality
4. Provide confidence scores for each finding

OUTPUT FORMAT (JSON):
{{
  "summary": "Your assessment",
  "confidence": 85,
  "validated_findings": ["Which Gemini findings you confirm"],
  "refuted_findings": ["Which Gemini findings are wrong"],
  "new_findings": [
    {{
      "severity": "CRITICAL|WARNING|INFO",
      "category": "security|performance|bugs|best_practices|architecture",
      "description": "What's wrong",
      "file": "filename",
      "line": 123,
      "suggested_fix": "How to fix it",
      "confidence": 90
    }}
  ]
}}

Be independent. Don't just agree with Gemini."""

        response = self.llm_client.chat_with_premium_model("deepseek-v3.2", prompt, max_tokens=4000)
        
        if response.status == "success":
            try:
                content = response.content
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                review_data = json.loads(content[json_start:json_end])
                
                print(f"✓ DeepSeek Review: {len(review_data.get('new_findings', []))} new findings")
                print(f"  Validated: {len(review_data.get('validated_findings', []))}, Refuted: {len(review_data.get('refuted_findings', []))}")
                print(f"  Confidence: {review_data.get('confidence', 0)}%")
                print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms\n")
                
                return {
                    "model": "deepseek-v3.2-thinking",
                    "data": review_data,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms
                }
            except Exception as e:
                print(f"⚠ JSON parse error: {e}")
                return {"model": "deepseek-v3.2-thinking", "data": {"summary": response.content, "new_findings": [], "confidence": 0}}
        else:
            print(f"✗ DeepSeek Review failed: {response.error}\n")
            return {"model": "deepseek-v3.2-thinking", "data": {"summary": "Failed", "new_findings": [], "confidence": 0}}
    
    def _review_with_claude(self, code: str, context: str, gemini_review: Dict, deepseek_review: Dict) -> Dict[str, Any]:
        """Phase 3: Claude Opus 4.5 Final Validation"""
        
        gemini_findings = gemini_review.get("data", {}).get("findings", [])
        deepseek_new = deepseek_review.get("data", {}).get("new_findings", [])
        
        prompt = f"""You are a senior code reviewer using Claude Opus 4.5, setting new standards in coding excellence.

PROJECT CONTEXT:
{context}

CODE TO REVIEW:
{code}

PREVIOUS REVIEWS:
Gemini found: {len(gemini_findings)} issues
DeepSeek found: {len(deepseek_new)} additional issues

ALL FINDINGS SO FAR:
{json.dumps(gemini_findings + deepseek_new, indent=2)}

YOUR TASK:
1. Final comprehensive review - find ANY remaining issues
2. Validate all previous findings
3. Focus on coding standards, enterprise patterns, and best practices
4. Confirm code is production-ready or list blockers

OUTPUT FORMAT (JSON):
{{
  "summary": "Final assessment",
  "confidence": 85,
  "additional_findings": [
    {{
      "severity": "CRITICAL|WARNING|INFO",
      "category": "security|performance|bugs|best_practices|architecture",
      "description": "What's wrong",
      "file": "filename",
      "line": 123,
      "suggested_fix": "How to fix it",
      "confidence": 90
    }}
  ],
  "production_ready": true|false,
  "blockers": ["List of must-fix issues before deployment"]
}}

This is the final review. Be thorough and set high standards."""

        response = self.llm_client.chat_with_premium_model("claude-opus-4.5", prompt, max_tokens=4000)
        
        if response.status == "success":
            try:
                content = response.content
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                review_data = json.loads(content[json_start:json_end])
                
                print(f"✓ Claude Review: {len(review_data.get('additional_findings', []))} additional findings")
                print(f"  Production Ready: {review_data.get('production_ready', False)}")
                print(f"  Blockers: {len(review_data.get('blockers', []))}")
                print(f"  Confidence: {review_data.get('confidence', 0)}%")
                print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms\n")
                
                return {
                    "model": "claude-opus-4-5-20251101",
                    "data": review_data,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms
                }
            except Exception as e:
                print(f"⚠ JSON parse error: {e}")
                return {"model": "claude-opus-4-5-20251101", "data": {"summary": response.content, "additional_findings": [], "confidence": 0}}
        else:
            print(f"✗ Claude Review failed: {response.error}\n")
            return {"model": "claude-opus-4-5-20251101", "data": {"summary": "Failed", "additional_findings": [], "confidence": 0}}
    
    def _synthesize_reviews(self, gemini_review: Dict, deepseek_review: Dict, 
                           claude_review: Dict, execution_time_ms: float) -> ReviewReport:
        """Synthesize all reviews into final report"""
        
        all_findings = []
        
        # Process Gemini findings
        for finding in gemini_review.get("data", {}).get("findings", []):
            all_findings.append(ReviewFinding(
                severity=finding.get("severity", "INFO"),
                category=finding.get("category", "best_practices"),
                description=finding.get("description", ""),
                file=finding.get("file", "unknown"),
                line=finding.get("line", 0),
                suggested_fix=finding.get("suggested_fix", ""),
                found_by=["gemini-3-pro"],
                confidence=finding.get("confidence", 50)
            ))
        
        # Process DeepSeek findings
        for finding in deepseek_review.get("data", {}).get("new_findings", []):
            all_findings.append(ReviewFinding(
                severity=finding.get("severity", "INFO"),
                category=finding.get("category", "best_practices"),
                description=finding.get("description", ""),
                file=finding.get("file", "unknown"),
                line=finding.get("line", 0),
                suggested_fix=finding.get("suggested_fix", ""),
                found_by=["deepseek-v3.2"],
                confidence=finding.get("confidence", 50)
            ))
        
        # Process Claude findings
        for finding in claude_review.get("data", {}).get("additional_findings", []):
            all_findings.append(ReviewFinding(
                severity=finding.get("severity", "INFO"),
                category=finding.get("category", "best_practices"),
                description=finding.get("description", ""),
                file=finding.get("file", "unknown"),
                line=finding.get("line", 0),
                suggested_fix=finding.get("suggested_fix", ""),
                found_by=["claude-opus-4.5"],
                confidence=finding.get("confidence", 50)
            ))
        
        # Detect consensus (2+ models agree on similar issues)
        consensus_count = self._detect_consensus(all_findings)
        
        # Count by severity
        critical_count = sum(1 for f in all_findings if f.severity == "CRITICAL")
        warning_count = sum(1 for f in all_findings if f.severity == "WARNING")
        info_count = sum(1 for f in all_findings if f.severity == "INFO")
        
        # Calculate total tokens
        total_tokens = {
            "input": sum([
                gemini_review.get("tokens", {}).get("input", 0),
                deepseek_review.get("tokens", {}).get("input", 0),
                claude_review.get("tokens", {}).get("input", 0)
            ]),
            "output": sum([
                gemini_review.get("tokens", {}).get("output", 0),
                deepseek_review.get("tokens", {}).get("output", 0),
                claude_review.get("tokens", {}).get("output", 0)
            ])
        }
        total_tokens["total"] = total_tokens["input"] + total_tokens["output"]
        
        # Model summaries
        model_summaries = {
            "gemini-3-pro": gemini_review.get("data", {}).get("summary", "No summary"),
            "deepseek-v3.2": deepseek_review.get("data", {}).get("summary", "No summary"),
            "claude-opus-4.5": claude_review.get("data", {}).get("summary", "No summary")
        }
        
        return ReviewReport(
            timestamp=datetime.now().isoformat(),
            total_findings=len(all_findings),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            findings=all_findings,
            model_summaries=model_summaries,
            execution_time_ms=execution_time_ms,
            tokens_used=total_tokens,
            consensus_findings=consensus_count
        )
    
    def _detect_consensus(self, findings: List[ReviewFinding]) -> int:
        """Detect how many findings have consensus (2+ models agree)"""
        # Simple heuristic: group by file + line + category
        from collections import defaultdict
        
        groups = defaultdict(list)
        for finding in findings:
            key = f"{finding.file}:{finding.line}:{finding.category}"
            groups[key].append(finding)
        
        consensus_count = 0
        for key, group in groups.items():
            if len(group) >= 2:
                # Merge findings from multiple models
                consensus_count += 1
                # Update found_by for all findings in this group
                all_models = []
                for f in group:
                    all_models.extend(f.found_by)
                for f in group:
                    f.found_by = list(set(all_models))
        
        return consensus_count

# Global instance
_reviewer = None

def get_reviewer() -> MultiModelReviewer:
    """Get or create the multi-model reviewer"""
    global _reviewer
    if _reviewer is None:
        _reviewer = MultiModelReviewer()
    return _reviewer

if __name__ == "__main__":
    import json
    
    # Test the reviewer
    reviewer = get_reviewer()
    
    test_code = {
        "example.py": """
def process_user_input(user_input):
    # Potential SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return execute_query(query)

def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']  # Could use sum()
    return total
"""
    }
    
    context = "This is a web application handling user authentication and payments."
    
    print("\n" + "="*100)
    print("TESTING MULTI-MODEL REVIEW SYSTEM")
    print("="*100 + "\n")
    
    report = reviewer.review_code(test_code, context)
    
    print("\n" + "="*100)
    print("REVIEW REPORT")
    print("="*100)
    print(f"Total Findings: {report.total_findings}")
    print(f"  Critical: {report.critical_count}")
    print(f"  Warning: {report.warning_count}")
    print(f"  Info: {report.info_count}")
    print(f"Consensus Findings: {report.consensus_findings}")
    print(f"Execution Time: {report.execution_time_ms:.0f}ms")
    print(f"Tokens Used: {report.tokens_used['total']} ({report.tokens_used['input']} input + {report.tokens_used['output']} output)")
    print("\nModel Summaries:")
    for model, summary in report.model_summaries.items():
        print(f"  {model}: {summary[:100]}...")
    print("\nFindings:")
    for i, finding in enumerate(report.findings, 1):
        print(f"\n{i}. [{finding.severity}] {finding.category}")
        print(f"   File: {finding.file}:{finding.line}")
        print(f"   Found by: {', '.join(finding.found_by)}")
        print(f"   Confidence: {finding.confidence}%")
        print(f"   Description: {finding.description}")
        print(f"   Fix: {finding.suggested_fix}")
    
    print("\n" + "="*100 + "\n")
