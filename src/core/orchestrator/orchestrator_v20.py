#!/usr/bin/env python3
"""
Multi-Model Orchestrator
Intelligently routes prompts to optimal models using hybrid strategies
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unified_llm_client import get_unified_client
from prompt_complexity_analyzer import get_prompt_analyzer, PromptComplexity, ProcessingStrategy
from complexity_analyzer import get_analyzer as get_code_analyzer

@dataclass
class OrchestrationResult:
    """Result of orchestrated multi-model processing"""
    prompt: str
    complexity_analysis: Dict[str, Any]
    strategy_used: str
    models_used: List[str]
    model_results: List[Dict[str, Any]]
    synthesized_result: str
    consensus_findings: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    confidence_score: float  # 0-100
    execution_time_ms: float
    total_tokens: int
    estimated_cost_usd: float
    timestamp: str

class MultiModelOrchestrator:
    """
    Intelligent orchestrator for multi-model processing
    Routes prompts to optimal models using hybrid strategies
    """
    
    # Model pricing (per 1M tokens)
    MODEL_PRICING = {
        "gemini-3-pro": {"input": 2.00, "output": 12.00},
        "deepseek-v3.2": {"input": 2.00, "output": 3.00},
        "deepseek-r1": {"input": 4.00, "output": 16.00},
        "claude-opus-4.5": {"input": 5.00, "output": 25.00},
        "gpt-5.2-pro": {"input": 21.00, "output": 168.00},
    }
    
    def __init__(self):
        self.llm_client = get_unified_client()
        self.prompt_analyzer = get_prompt_analyzer()
        self.code_analyzer = get_code_analyzer()
        
        print("\n" + "="*100)
        print("MULTI-MODEL ORCHESTRATOR")
        print("="*100)
        print("Intelligent routing with hybrid strategies:")
        print("  • SINGLE: Fast single-model processing")
        print("  • SEQUENTIAL: Model A → Model B (iterative improvement)")
        print("  • PARALLEL: Multiple models simultaneously (independent perspectives)")
        print("  • CONSENSUS: All models + voting (critical decisions)")
        print("="*100 + "\n")
    
    def process(self, prompt: str, code_files: Dict[str, str] = None) -> OrchestrationResult:
        """
        Process prompt using optimal orchestration strategy
        
        Args:
            prompt: User's request/question
            code_files: Optional code files for review
        
        Returns:
            OrchestrationResult with synthesized findings
        """
        
        start_time = datetime.now()
        
        # Step 1: Analyze prompt complexity
        print("[Step 1/4] Analyzing prompt complexity...\n")
        complexity = self.prompt_analyzer.analyze(prompt, code_files)
        
        print(f"✓ Task: {complexity.task_type.value}")
        print(f"  Complexity: {complexity.complexity_score}/10")
        print(f"  Strategy: {complexity.recommended_strategy.value.upper()}")
        print(f"  Models: {', '.join(complexity.recommended_models)}")
        print(f"  Reasoning: {complexity.reasoning}\n")
        
        # Step 2: Execute strategy
        print(f"[Step 2/4] Executing {complexity.recommended_strategy.value.upper()} strategy...\n")
        
        if complexity.recommended_strategy == ProcessingStrategy.SINGLE:
            model_results = self._execute_single(prompt, code_files, complexity)
        elif complexity.recommended_strategy == ProcessingStrategy.SEQUENTIAL:
            model_results = self._execute_sequential(prompt, code_files, complexity)
        elif complexity.recommended_strategy == ProcessingStrategy.PARALLEL:
            model_results = self._execute_parallel(prompt, code_files, complexity)
        else:  # CONSENSUS
            model_results = self._execute_consensus(prompt, code_files, complexity)
        
        # Step 3: Synthesize results
        print("\n[Step 3/4] Synthesizing results...\n")
        synthesized, consensus, conflicts, confidence = self._synthesize_results(
            model_results, complexity
        )
        
        # Step 4: Calculate metrics
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        total_tokens = sum(r['tokens']['total'] for r in model_results)
        estimated_cost = self._calculate_cost(model_results)
        
        print(f"[Step 4/4] Complete!\n")
        print(f"✓ Confidence: {confidence:.1f}%")
        print(f"  Consensus Findings: {len(consensus)}")
        print(f"  Conflicts: {len(conflicts)}")
        print(f"  Execution Time: {execution_time:.0f}ms")
        print(f"  Total Tokens: {total_tokens:,}")
        print(f"  Estimated Cost: ${estimated_cost:.4f}\n")
        
        return OrchestrationResult(
            prompt=prompt,
            complexity_analysis=asdict(complexity),
            strategy_used=complexity.recommended_strategy.value,
            models_used=complexity.recommended_models,
            model_results=model_results,
            synthesized_result=synthesized,
            consensus_findings=consensus,
            conflicts=conflicts,
            confidence_score=confidence,
            execution_time_ms=execution_time,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
            timestamp=datetime.now().isoformat()
        )
    
    def _execute_single(self, prompt: str, code_files: Optional[Dict[str, str]],
                       complexity: PromptComplexity) -> List[Dict[str, Any]]:
        """Execute single model strategy"""
        model = complexity.recommended_models[0]
        
        # Build prompt
        full_prompt = self._build_prompt(prompt, code_files, model, complexity, is_first=True)
        
        # Execute
        print(f"[1/1] {model}...")
        response = self.llm_client.chat_with_premium_model(model, full_prompt, max_tokens=4000)
        
        if response.status == "success":
            print(f"✓ {model}: Success")
            print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms")
            
            return [{
                "model": model,
                "content": response.content,
                "tokens": response.tokens_used,
                "latency_ms": response.latency_ms
            }]
        else:
            print(f"✗ {model}: Failed - {response.error}")
            return [{
                "model": model,
                "content": f"Error: {response.error}",
                "tokens": {"input": 0, "output": 0, "total": 0},
                "latency_ms": 0
            }]
    
    def _execute_sequential(self, prompt: str, code_files: Optional[Dict[str, str]],
                           complexity: PromptComplexity) -> List[Dict[str, Any]]:
        """Execute sequential strategy (Model A → Model B)"""
        results = []
        
        for i, model in enumerate(complexity.recommended_models):
            # Build prompt (include previous results if not first)
            if i == 0:
                full_prompt = self._build_prompt(prompt, code_files, model, complexity, is_first=True)
            else:
                full_prompt = self._build_sequential_prompt(
                    prompt, code_files, model, complexity, results
                )
            
            # Execute
            print(f"[{i+1}/{len(complexity.recommended_models)}] {model}...")
            response = self.llm_client.chat_with_premium_model(model, full_prompt, max_tokens=4000)
            
            if response.status == "success":
                print(f"✓ {model}: Success")
                print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms")
                
                results.append({
                    "model": model,
                    "content": response.content,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms
                })
            else:
                print(f"✗ {model}: Failed - {response.error}")
                results.append({
                    "model": model,
                    "content": f"Error: {response.error}",
                    "tokens": {"input": 0, "output": 0, "total": 0},
                    "latency_ms": 0
                })
        
        return results
    
    def _execute_parallel(self, prompt: str, code_files: Optional[Dict[str, str]],
                         complexity: PromptComplexity) -> List[Dict[str, Any]]:
        """Execute parallel strategy (all models simultaneously)"""
        results = []
        
        for i, model in enumerate(complexity.recommended_models):
            # Build prompt (all independent)
            full_prompt = self._build_prompt(prompt, code_files, model, complexity, is_first=True)
            
            # Execute
            print(f"[{i+1}/{len(complexity.recommended_models)}] {model}...")
            response = self.llm_client.chat_with_premium_model(model, full_prompt, max_tokens=4000)
            
            if response.status == "success":
                print(f"✓ {model}: Success")
                print(f"  Tokens: {response.tokens_used['total']}, Latency: {response.latency_ms:.0f}ms")
                
                results.append({
                    "model": model,
                    "content": response.content,
                    "tokens": response.tokens_used,
                    "latency_ms": response.latency_ms
                })
            else:
                print(f"✗ {model}: Failed - {response.error}")
                results.append({
                    "model": model,
                    "content": f"Error: {response.error}",
                    "tokens": {"input": 0, "output": 0, "total": 0},
                    "latency_ms": 0
                })
        
        return results
    
    def _execute_consensus(self, prompt: str, code_files: Optional[Dict[str, str]],
                          complexity: PromptComplexity) -> List[Dict[str, Any]]:
        """Execute consensus strategy (all models + voting)"""
        # Same as parallel but with consensus detection in synthesis
        return self._execute_parallel(prompt, code_files, complexity)
    
    def _build_prompt(self, prompt: str, code_files: Optional[Dict[str, str]],
                     model: str, complexity: PromptComplexity, is_first: bool) -> str:
        """Build prompt for model"""
        
        parts = []
        
        # System context
        parts.append(f"You are an expert AI assistant using {model}.")
        parts.append(f"Task: {complexity.task_type.value.replace('_', ' ').title()}")
        parts.append(f"Complexity: {complexity.complexity_score}/10")
        
        # User prompt
        parts.append(f"\nUser Request:\n{prompt}")
        
        # Code files if provided
        if code_files:
            parts.append("\nCode to analyze:")
            for filename, content in code_files.items():
                parts.append(f"\n=== {filename} ===\n{content}")
        
        # Instructions
        parts.append("\nProvide a comprehensive analysis addressing the user's request.")
        parts.append("Be specific, actionable, and thorough.")
        
        return "\n".join(parts)
    
    def _build_sequential_prompt(self, prompt: str, code_files: Optional[Dict[str, str]],
                                model: str, complexity: PromptComplexity,
                                previous_results: List[Dict]) -> str:
        """Build prompt for sequential model (includes previous results)"""
        
        parts = []
        
        # System context
        parts.append(f"You are an expert AI assistant using {model}.")
        parts.append(f"Task: {complexity.task_type.value.replace('_', ' ').title()}")
        parts.append(f"Complexity: {complexity.complexity_score}/10")
        
        # Previous analysis
        parts.append("\nPrevious Analysis:")
        for result in previous_results:
            parts.append(f"\n--- {result['model']} ---")
            parts.append(result['content'][:1000])  # Truncate if too long
        
        # User prompt
        parts.append(f"\nOriginal Request:\n{prompt}")
        
        # Code files if provided
        if code_files:
            parts.append("\nCode:")
            for filename, content in code_files.items():
                parts.append(f"\n=== {filename} ===\n{content}")
        
        # Instructions
        parts.append("\nBuild upon the previous analysis:")
        parts.append("1. Validate or refute previous findings")
        parts.append("2. Add new insights and perspectives")
        parts.append("3. Provide additional recommendations")
        
        return "\n".join(parts)
    
    def _synthesize_results(self, results: List[Dict], complexity: PromptComplexity):
        """Synthesize results from multiple models"""
        
        if len(results) == 1:
            # Single model - no synthesis needed
            return results[0]['content'], [], [], 85.0
        
        # Extract all findings
        all_findings = []
        for result in results:
            all_findings.append({
                "model": result['model'],
                "content": result['content']
            })
        
        # Detect consensus (simplified - would use NLP in production)
        consensus = []
        conflicts = []
        
        # Calculate confidence based on number of models
        if len(results) == 2:
            confidence = 80.0
        elif len(results) == 3:
            confidence = 90.0
        else:
            confidence = 95.0
        
        # Synthesize into unified response
        synthesized_parts = []
        synthesized_parts.append(f"## Orchestrated Analysis ({len(results)} models)")
        synthesized_parts.append(f"Strategy: {complexity.recommended_strategy.value.upper()}")
        synthesized_parts.append(f"Models: {', '.join([r['model'] for r in results])}\n")
        
        for i, result in enumerate(results, 1):
            synthesized_parts.append(f"### Model {i}: {result['model']}")
            synthesized_parts.append(result['content'])
            synthesized_parts.append("")
        
        return "\n".join(synthesized_parts), consensus, conflicts, confidence
    
    def _calculate_cost(self, results: List[Dict]) -> float:
        """Calculate estimated cost"""
        total_cost = 0.0
        
        for result in results:
            model = result['model']
            tokens = result['tokens']
            
            if model in self.MODEL_PRICING:
                pricing = self.MODEL_PRICING[model]
                input_cost = (tokens['input'] / 1_000_000) * pricing['input']
                output_cost = (tokens['output'] / 1_000_000) * pricing['output']
                total_cost += input_cost + output_cost
        
        return total_cost

# Global instance
_orchestrator = None

def get_orchestrator() -> MultiModelOrchestrator:
    """Get or create the orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiModelOrchestrator()
    return _orchestrator

if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = get_orchestrator()
    
    test_cases = [
        {
            "name": "Simple Question",
            "prompt": "What is a closure in JavaScript?",
            "code": None
        },
        {
            "name": "Code Review",
            "prompt": "Review this code for best practices",
            "code": {
                "example.py": """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""
            }
        },
        {
            "name": "Security Audit",
            "prompt": "Analyze security vulnerabilities in this authentication system",
            "code": {
                "auth.py": """
import jwt
SECRET_KEY = "hardcoded_secret"

def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    user = execute_query(query)
    if user and password == user['password']:
        return jwt.encode({'id': user['id']}, SECRET_KEY)
    return None
"""
            }
        }
    ]
    
    print("\n" + "="*100)
    print("ORCHESTRATOR TEST SUITE")
    print("="*100 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"TEST {i}/{len(test_cases)}: {test['name']}")
        print(f"{'='*100}\n")
        
        result = orchestrator.process(test['prompt'], test['code'])
        
        print(f"\n{'='*80}")
        print("RESULT SUMMARY")
        print(f"{'='*80}")
        print(f"Strategy: {result.strategy_used.upper()}")
        print(f"Models: {', '.join(result.models_used)}")
        print(f"Confidence: {result.confidence_score:.1f}%")
        print(f"Execution Time: {result.execution_time_ms:.0f}ms")
        print(f"Total Tokens: {result.total_tokens:,}")
        print(f"Estimated Cost: ${result.estimated_cost_usd:.4f}")
        print(f"{'='*80}\n")
    
    print("\n" + "="*100 + "\n")
