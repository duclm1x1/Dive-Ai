#!/usr/bin/env python3
"""
Intelligent Multi-Model Review Agent
Uses complexity analysis to dynamically select optimal AI models for code review
Based on research from GitHub/Reddit and v98store model capabilities
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unified_llm_client import get_unified_client
from complexity_analyzer import get_analyzer, ComplexityScore, ComplexityLevel

@dataclass
class ModelScore:
    """Score for a specific model's review"""
    model_name: str
    specialization_score: float  # 0-10 based on model's strength in this area
    confidence: int  # 0-100
    findings_count: int
    tokens_used: int
    latency_ms: float

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
    consensus: bool  # True if 2+ models agree

@dataclass
class IntelligentReviewReport:
    """Complete intelligent review report"""
    timestamp: str
    complexity_score: int  # 1-10
    complexity_level: str
    selected_models: List[str]
    model_selection_reasoning: str
    total_findings: int
    critical_count: int
    warning_count: int
    info_count: int
    consensus_count: int
    findings: List[ReviewFinding]
    model_scores: List[ModelScore]
    model_summaries: Dict[str, str]
    execution_time_ms: float
    total_tokens_used: int
    estimated_cost_usd: float

class IntelligentMultiModelReviewer:
    """
    Intelligent Multi-Model Review Agent
    Dynamically selects optimal models based on code complexity
    """
    
    # Model pricing (per 1M tokens)
    MODEL_PRICING = {
        "gemini-3-pro": {"input": 2.00, "output": 12.00},
        "deepseek-v3.2": {"input": 2.00, "output": 3.00},
        "deepseek-r1": {"input": 4.00, "output": 16.00},
        "claude-opus-4.5": {"input": 5.00, "output": 25.00},
        "gpt-5.2-pro": {"input": 21.00, "output": 168.00},
    }
    
    # Model specialization scores (1-10) based on research
    MODEL_SPECIALIZATIONS = {
        "gemini-3-pro": {
            "architecture": 10,
            "security": 8,
            "performance": 8,
            "code_quality": 7,
            "best_practices": 7,
            "bugs": 8,
            "algorithm": 10,
            "api_design": 9,
        },
        "deepseek-v3.2": {
            "architecture": 9,
            "security": 7,
            "performance": 8,
            "code_quality": 8,
            "best_practices": 7,
            "bugs": 8,
            "algorithm": 9,
            "api_design": 10,
        },
        "deepseek-r1": {
            "architecture": 10,
            "security": 8,
            "performance": 9,
            "code_quality": 8,
            "best_practices": 7,
            "bugs": 9,
            "algorithm": 10,
            "api_design": 9,
        },
        "claude-opus-4.5": {
            "architecture": 9,
            "security": 9,
            "performance": 9,
            "code_quality": 10,
            "best_practices": 10,
            "bugs": 10,
            "algorithm": 8,
            "api_design": 9,
        },
        "gpt-5.2-pro": {
            "architecture": 9,
            "security": 10,
            "performance": 9,
            "code_quality": 9,
            "best_practices": 9,
            "bugs": 9,
            "algorithm": 9,
            "api_design": 9,
        },
    }
    
    def __init__(self):
        self.llm_client = get_unified_client()
        self.analyzer = get_analyzer()
        
        print("\n" + "="*100)
        print("INTELLIGENT MULTI-MODEL REVIEW AGENT")
        print("="*100)
        print("Features:")
        print("  • Dynamic model selection based on complexity analysis")
        print("  • Research-backed specialization scoring (GitHub/Reddit)")
        print("  • Cost-optimized routing (1-3 models depending on complexity)")
        print("  • Consensus detection across models")
        print("="*100 + "\n")
    
    def review_code(self, code_files: Dict[str, str], context: str = "") -> IntelligentReviewReport:
        """
        Intelligently review code using optimal models
        
        Args:
            code_files: Dict of {filename: code_content}
            context: Project context from Dive-Memory
        
        Returns:
            IntelligentReviewReport with all findings
        """
        
        start_time = datetime.now()
        
        # Step 1: Analyze complexity
        print("[Step 1/4] Analyzing code complexity...\n")
        complexity = self.analyzer.analyze(code_files, context)
        
        print(f"✓ Complexity Score: {complexity.overall_score}/10 ({complexity.level.value.upper()})")
        print(f"  Review Types: {', '.join([rt.value for rt in complexity.review_types])}")
        print(f"  Selected Models: {', '.join(complexity.recommended_models)}")
        print(f"  Reasoning: {complexity.reasoning}\n")
        
        # Step 2: Prepare code for review
        code_text = self._format_code_files(code_files)
        
        # Step 3: Review with selected models
        print(f"[Step 2/4] Running {len(complexity.recommended_models)}-model review...\n")
        
        model_reviews = []
        for i, model_name in enumerate(complexity.recommended_models, 1):
            print(f"[Model {i}/{len(complexity.recommended_models)}] {model_name}...")
            review = self._review_with_model(
                model_name, 
                code_text, 
                context, 
                complexity,
                previous_reviews=model_reviews
            )
            model_reviews.append(review)
            print()
        
        # Step 4: Synthesize findings
        print("[Step 3/4] Synthesizing findings across models...\n")
        report = self._synthesize_reviews(
            complexity,
            model_reviews,
            (datetime.now() - start_time).total_seconds() * 1000
        )
        
        print("[Step 4/4] Review complete!\n")
        
        return report
    
    def _format_code_files(self, code_files: Dict[str, str]) -> str:
        """Format code files for review"""
        formatted = []
        for filename, content in code_files.items():
            formatted.append(f"=== {filename} ===\n{content}\n")
        return "\n".join(formatted)
    
    def _review_with_model(self, model_name: str, code: str, context: str,
                          complexity: ComplexityScore, 
                          previous_reviews: List[Dict]) -> Dict[str, Any]:
        """Review code with a specific model"""
        
        # Get model's specialization scores for this task
        specializations = self.MODEL_SPECIALIZATIONS.get(model_name, {})
        review_types_str = ', '.join([rt.value.replace('_', ' ').title() 
                                      for rt in complexity.review_types])
        
        # Build prompt based on model position
        if len(previous_reviews) == 0:
            # First model: comprehensive review
            prompt = self._build_first_review_prompt(
                model_name, code, context, complexity, specializations
            )
        else:
            # Subsequent models: cross-review and find additional issues
            prompt = self._build_cross_review_prompt(
                model_name, code, context, complexity, 
                specializations, previous_reviews
            )
        
        # Call model
        response = self.llm_client.chat_with_premium_model(
            model_name, prompt, max_tokens=4000
        )
        
        if response.status == "success":
            try:
                # Extract JSON from response
                content = response.content
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                review_data = json.loads(content[json_start:json_end])
                
                findings_key = "findings" if len(previous_reviews) == 0 else "new_findings"
                findings_count = len(review_data.get(findings_key, []))
                
                print(f"✓ {model_name}: {findings_count} findings")
                print(f"  Confidence: {review_data.get('confidence', 0)}%")
                print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms")
                
                return {
                    "model": model_name,
                    "data": review_data,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms,
                    "specialization_score": self._calculate_specialization_score(
                        model_name, complexity.review_types
                    )
                }
            except Exception as e:
                print(f"⚠ {model_name}: JSON parse error - {e}")
                return {
                    "model": model_name,
                    "data": {"summary": response.content, "findings": [], "confidence": 0},
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms,
                    "specialization_score": 0
                }
        else:
            print(f"✗ {model_name}: Review failed - {response.error}")
            return {
                "model": model_name,
                "data": {"summary": "Failed", "findings": [], "confidence": 0},
                "tokens": {"input": 0, "output": 0, "total": 0},
                "latency_ms": 0,
                "specialization_score": 0
            }
    
    def _build_first_review_prompt(self, model_name: str, code: str, 
                                   context: str, complexity: ComplexityScore,
                                   specializations: Dict) -> str:
        """Build prompt for first model (comprehensive review)"""
        
        # Highlight model's strengths
        strengths = []
        for category, score in specializations.items():
            if score >= 9:
                strengths.append(f"{category} (strength: {score}/10)")
        
        strengths_str = ", ".join(strengths) if strengths else "general code review"
        
        return f"""You are a senior code reviewer using {model_name}.

YOUR SPECIALIZATIONS: {strengths_str}

PROJECT CONTEXT:
{context}

CODE COMPLEXITY ANALYSIS:
- Overall Score: {complexity.overall_score}/10 ({complexity.level.value.upper()})
- Review Types Needed: {', '.join([rt.value for rt in complexity.review_types])}
- Lines of Code: {complexity.metrics['lines_of_code']}
- Cyclomatic Complexity: {complexity.metrics['cyclomatic_complexity']:.1f}

CODE TO REVIEW:
{code}

REVIEW FOCUS (based on your strengths):
1. Focus on areas where you excel (9-10/10 scores)
2. Be thorough and critical
3. Provide actionable suggestions
4. Include confidence scores (0-100) for each finding

OUTPUT FORMAT (JSON):
{{
  "summary": "Overall assessment",
  "confidence": 85,
  "findings": [
    {{
      "severity": "CRITICAL|WARNING|INFO",
      "category": "security|performance|bugs|best_practices|architecture|algorithm|api_design",
      "description": "What's wrong",
      "file": "filename",
      "line": 123,
      "suggested_fix": "How to fix it",
      "confidence": 90
    }}
  ]
}}

This is the first review pass. Be comprehensive."""
    
    def _build_cross_review_prompt(self, model_name: str, code: str,
                                   context: str, complexity: ComplexityScore,
                                   specializations: Dict,
                                   previous_reviews: List[Dict]) -> str:
        """Build prompt for subsequent models (cross-review)"""
        
        # Collect all previous findings
        all_previous_findings = []
        for review in previous_reviews:
            findings = review["data"].get("findings", [])
            all_previous_findings.extend(findings)
        
        # Highlight model's strengths
        strengths = []
        for category, score in specializations.items():
            if score >= 9:
                strengths.append(f"{category} (strength: {score}/10)")
        
        strengths_str = ", ".join(strengths) if strengths else "general code review"
        
        previous_models = [r["model"] for r in previous_reviews]
        
        return f"""You are a senior code reviewer using {model_name}.

YOUR SPECIALIZATIONS: {strengths_str}

PROJECT CONTEXT:
{context}

CODE COMPLEXITY ANALYSIS:
- Overall Score: {complexity.overall_score}/10 ({complexity.level.value.upper()})
- Review Types Needed: {', '.join([rt.value for rt in complexity.review_types])}

CODE TO REVIEW:
{code}

PREVIOUS REVIEWS FROM: {', '.join(previous_models)}
Found {len(all_previous_findings)} issues:
{json.dumps(all_previous_findings, indent=2)}

YOUR TASK:
1. Validate previous findings (which ones you confirm)
2. Find ADDITIONAL issues that previous models missed
3. Focus on your specialization areas ({strengths_str})
4. Provide independent assessment

OUTPUT FORMAT (JSON):
{{
  "summary": "Your assessment",
  "confidence": 85,
  "validated_findings": ["Brief description of findings you confirm"],
  "refuted_findings": ["Brief description of findings you disagree with"],
  "new_findings": [
    {{
      "severity": "CRITICAL|WARNING|INFO",
      "category": "security|performance|bugs|best_practices|architecture|algorithm|api_design",
      "description": "What's wrong",
      "file": "filename",
      "line": 123,
      "suggested_fix": "How to fix it",
      "confidence": 90
    }}
  ]
}}

Be independent. Don't just agree with previous reviews."""
    
    def _calculate_specialization_score(self, model_name: str, 
                                       review_types: List) -> float:
        """Calculate model's specialization score for this task"""
        specializations = self.MODEL_SPECIALIZATIONS.get(model_name, {})
        
        if not review_types:
            return 5.0  # Default
        
        scores = []
        for rt in review_types:
            category = rt.value.replace('_', '')  # Remove underscores
            # Map review types to specialization categories
            if 'refactor' in category or 'quality' in category:
                scores.append(specializations.get('code_quality', 5))
            elif 'bug' in category:
                scores.append(specializations.get('bugs', 5))
            elif 'security' in category:
                scores.append(specializations.get('security', 5))
            elif 'performance' in category:
                scores.append(specializations.get('performance', 5))
            elif 'architecture' in category:
                scores.append(specializations.get('architecture', 5))
            elif 'algorithm' in category:
                scores.append(specializations.get('algorithm', 5))
            elif 'api' in category:
                scores.append(specializations.get('api_design', 5))
            else:
                scores.append(specializations.get('best_practices', 5))
        
        return sum(scores) / len(scores) if scores else 5.0
    
    def _synthesize_reviews(self, complexity: ComplexityScore,
                           model_reviews: List[Dict],
                           execution_time_ms: float) -> IntelligentReviewReport:
        """Synthesize all reviews into final report"""
        
        all_findings = []
        model_scores = []
        model_summaries = {}
        total_tokens = 0
        
        # Process each model's review
        for review in model_reviews:
            model_name = review["model"]
            data = review["data"]
            tokens = review["tokens"]
            
            # Extract findings
            if "findings" in data:
                # First model
                for finding in data["findings"]:
                    all_findings.append(ReviewFinding(
                        severity=finding.get("severity", "INFO"),
                        category=finding.get("category", "best_practices"),
                        description=finding.get("description", ""),
                        file=finding.get("file", "unknown"),
                        line=finding.get("line", 0),
                        suggested_fix=finding.get("suggested_fix", ""),
                        found_by=[model_name],
                        confidence=finding.get("confidence", 50),
                        consensus=False
                    ))
            
            if "new_findings" in data:
                # Subsequent models
                for finding in data["new_findings"]:
                    all_findings.append(ReviewFinding(
                        severity=finding.get("severity", "INFO"),
                        category=finding.get("category", "best_practices"),
                        description=finding.get("description", ""),
                        file=finding.get("file", "unknown"),
                        line=finding.get("line", 0),
                        suggested_fix=finding.get("suggested_fix", ""),
                        found_by=[model_name],
                        confidence=finding.get("confidence", 50),
                        consensus=False
                    ))
            
            # Record model score
            model_scores.append(ModelScore(
                model_name=model_name,
                specialization_score=review["specialization_score"],
                confidence=data.get("confidence", 0),
                findings_count=len(data.get("findings", [])) + len(data.get("new_findings", [])),
                tokens_used=tokens["total"],
                latency_ms=review["latency_ms"]
            ))
            
            # Record summary
            model_summaries[model_name] = data.get("summary", "No summary")
            
            # Track tokens
            total_tokens += tokens["total"]
        
        # Detect consensus
        consensus_count = self._detect_consensus(all_findings)
        
        # Count by severity
        critical_count = sum(1 for f in all_findings if f.severity == "CRITICAL")
        warning_count = sum(1 for f in all_findings if f.severity == "WARNING")
        info_count = sum(1 for f in all_findings if f.severity == "INFO")
        
        # Calculate estimated cost
        estimated_cost = self._calculate_cost(model_reviews)
        
        return IntelligentReviewReport(
            timestamp=datetime.now().isoformat(),
            complexity_score=complexity.overall_score,
            complexity_level=complexity.level.value,
            selected_models=complexity.recommended_models,
            model_selection_reasoning=complexity.reasoning,
            total_findings=len(all_findings),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            consensus_count=consensus_count,
            findings=all_findings,
            model_scores=model_scores,
            model_summaries=model_summaries,
            execution_time_ms=execution_time_ms,
            total_tokens_used=total_tokens,
            estimated_cost_usd=estimated_cost
        )
    
    def _detect_consensus(self, findings: List[ReviewFinding]) -> int:
        """Detect consensus findings (2+ models agree)"""
        from collections import defaultdict
        
        groups = defaultdict(list)
        for finding in findings:
            # Group by file + line + category
            key = f"{finding.file}:{finding.line}:{finding.category}"
            groups[key].append(finding)
        
        consensus_count = 0
        for key, group in groups.items():
            if len(group) >= 2:
                consensus_count += 1
                # Mark all findings in this group as consensus
                all_models = []
                for f in group:
                    all_models.extend(f.found_by)
                for f in group:
                    f.found_by = list(set(all_models))
                    f.consensus = True
        
        return consensus_count
    
    def _calculate_cost(self, model_reviews: List[Dict]) -> float:
        """Calculate estimated cost in USD"""
        total_cost = 0.0
        
        for review in model_reviews:
            model_name = review["model"]
            tokens = review["tokens"]
            
            if model_name in self.MODEL_PRICING:
                pricing = self.MODEL_PRICING[model_name]
                input_cost = (tokens["input"] / 1_000_000) * pricing["input"]
                output_cost = (tokens["output"] / 1_000_000) * pricing["output"]
                total_cost += input_cost + output_cost
        
        return total_cost

# Global instance
_reviewer = None

def get_intelligent_reviewer() -> IntelligentMultiModelReviewer:
    """Get or create the intelligent reviewer"""
    global _reviewer
    if _reviewer is None:
        _reviewer = IntelligentMultiModelReviewer()
    return _reviewer

if __name__ == "__main__":
    import json
    
    # Test the intelligent reviewer
    reviewer = get_intelligent_reviewer()
    
    test_code = {
        "auth.py": """
import jwt
import bcrypt
from flask import request

def authenticate_user(username, password):
    # Potential SQL injection vulnerability
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
    
    context = "Authentication API for web application handling user login."
    
    print("\n" + "="*100)
    print("TESTING INTELLIGENT MULTI-MODEL REVIEW SYSTEM")
    print("="*100 + "\n")
    
    report = reviewer.review_code(test_code, context)
    
    print("\n" + "="*100)
    print("INTELLIGENT REVIEW REPORT")
    print("="*100)
    print(f"Complexity: {report.complexity_score}/10 ({report.complexity_level.upper()})")
    print(f"Selected Models: {', '.join(report.selected_models)}")
    print(f"Model Selection Reasoning: {report.model_selection_reasoning}")
    print(f"\nFindings: {report.total_findings} total")
    print(f"  Critical: {report.critical_count}")
    print(f"  Warning: {report.warning_count}")
    print(f"  Info: {report.info_count}")
    print(f"  Consensus: {report.consensus_count}")
    print(f"\nExecution Time: {report.execution_time_ms:.0f}ms")
    print(f"Total Tokens: {report.total_tokens_used:,}")
    print(f"Estimated Cost: ${report.estimated_cost_usd:.4f}")
    
    print("\n" + "="*100 + "\n")
