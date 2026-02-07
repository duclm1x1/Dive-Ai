#!/usr/bin/env python3
"""
Prompt Complexity Analyzer
Analyzes prompts to determine optimal model routing strategy
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    """Types of tasks the system can handle"""
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ALGORITHM = "algorithm"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    API_DESIGN = "api_design"
    BEST_PRACTICES = "best_practices"
    GENERAL = "general"

class ProcessingStrategy(Enum):
    """Processing strategies for orchestration"""
    SINGLE = "single"          # One model only
    SEQUENTIAL = "sequential"  # Model A → Model B
    PARALLEL = "parallel"      # Multiple models simultaneously
    CONSENSUS = "consensus"    # All models + voting

@dataclass
class PromptComplexity:
    """Result of prompt complexity analysis"""
    task_type: TaskType
    complexity_score: int  # 1-10
    required_capabilities: Set[str]
    estimated_tokens: int
    domain_specificity: float  # 0-1
    ambiguity_level: float  # 0-1
    recommended_strategy: ProcessingStrategy
    recommended_models: List[str]
    reasoning: str

class PromptComplexityAnalyzer:
    """
    Analyzes prompts to determine complexity and optimal routing
    """
    
    # Task type keywords
    TASK_KEYWORDS = {
        TaskType.CODE_REVIEW: [
            'review', 'check', 'analyze', 'assess', 'evaluate', 'critique',
            'code quality', 'best practices', 'improvements'
        ],
        TaskType.ARCHITECTURE: [
            'architecture', 'design', 'structure', 'pattern', 'system design',
            'microservice', 'scalability', 'modularity', 'component'
        ],
        TaskType.SECURITY: [
            'security', 'vulnerability', 'exploit', 'injection', 'xss', 'csrf',
            'authentication', 'authorization', 'encryption', 'secure'
        ],
        TaskType.PERFORMANCE: [
            'performance', 'optimize', 'speed', 'efficiency', 'latency',
            'throughput', 'bottleneck', 'profiling', 'memory'
        ],
        TaskType.ALGORITHM: [
            'algorithm', 'complexity', 'big-o', 'optimization', 'data structure',
            'graph', 'tree', 'sorting', 'searching', 'dynamic programming'
        ],
        TaskType.BUG_FIX: [
            'bug', 'fix', 'error', 'issue', 'problem', 'crash', 'exception',
            'debugging', 'troubleshoot', 'not working'
        ],
        TaskType.REFACTORING: [
            'refactor', 'cleanup', 'simplify', 'reorganize', 'restructure',
            'improve readability', 'reduce complexity', 'clean code'
        ],
        TaskType.API_DESIGN: [
            'api', 'endpoint', 'rest', 'graphql', 'interface', 'contract',
            'route', 'handler', 'request', 'response'
        ],
        TaskType.BEST_PRACTICES: [
            'best practice', 'convention', 'standard', 'guideline', 'style',
            'naming', 'formatting', 'documentation'
        ]
    }
    
    # Capability requirements by task type
    CAPABILITY_MAP = {
        TaskType.CODE_REVIEW: {'code_quality', 'best_practices', 'bug_detection'},
        TaskType.ARCHITECTURE: {'abstract_reasoning', 'system_design', 'patterns'},
        TaskType.SECURITY: {'security_expertise', 'vulnerability_detection'},
        TaskType.PERFORMANCE: {'optimization', 'profiling', 'algorithm_analysis'},
        TaskType.ALGORITHM: {'algorithm_knowledge', 'complexity_analysis', 'math'},
        TaskType.BUG_FIX: {'debugging', 'error_analysis', 'code_quality'},
        TaskType.REFACTORING: {'code_quality', 'design_patterns', 'best_practices'},
        TaskType.API_DESIGN: {'api_design', 'interface_design', 'tool_use'},
        TaskType.BEST_PRACTICES: {'code_quality', 'conventions', 'standards'},
        TaskType.GENERAL: {'general_reasoning'}
    }
    
    def __init__(self):
        pass
    
    def analyze(self, prompt: str, code_files: Dict[str, str] = None) -> PromptComplexity:
        """
        Analyze prompt complexity and recommend routing strategy
        
        Args:
            prompt: User's request/question
            code_files: Optional code files being reviewed
        
        Returns:
            PromptComplexity with routing recommendations
        """
        
        # Detect task type
        task_type = self._detect_task_type(prompt)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(prompt, code_files)
        
        # Identify required capabilities
        capabilities = self._identify_capabilities(task_type, prompt)
        
        # Estimate token usage
        estimated_tokens = self._estimate_tokens(prompt, code_files)
        
        # Calculate domain specificity
        domain_specificity = self._calculate_domain_specificity(prompt)
        
        # Calculate ambiguity level
        ambiguity_level = self._calculate_ambiguity(prompt)
        
        # Recommend strategy and models
        strategy = self._recommend_strategy(complexity_score, task_type, ambiguity_level)
        models = self._recommend_models(complexity_score, task_type, capabilities)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            task_type, complexity_score, capabilities, strategy, models
        )
        
        return PromptComplexity(
            task_type=task_type,
            complexity_score=complexity_score,
            required_capabilities=capabilities,
            estimated_tokens=estimated_tokens,
            domain_specificity=domain_specificity,
            ambiguity_level=ambiguity_level,
            recommended_strategy=strategy,
            recommended_models=models,
            reasoning=reasoning
        )
    
    def _detect_task_type(self, prompt: str) -> TaskType:
        """Detect the primary task type from prompt"""
        prompt_lower = prompt.lower()
        
        # Score each task type
        scores = {}
        for task_type, keywords in self.TASK_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                scores[task_type] = score
        
        # Return highest scoring task type
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return TaskType.GENERAL
    
    def _calculate_complexity(self, prompt: str, code_files: Dict[str, str] = None) -> int:
        """Calculate complexity score (1-10)"""
        score = 0.0
        
        # Prompt length (0-2 points)
        prompt_length = len(prompt)
        if prompt_length < 30:
            score += 0.5
        elif prompt_length < 100:
            score += 1.0
        elif prompt_length < 300:
            score += 1.5
        else:
            score += 2.0
        
        # Code presence baseline (0-2 points)
        if code_files:
            score += 1.5  # Having code to review adds baseline complexity
            
            total_lines = sum(len(code.split('\n')) for code in code_files.values())
            file_count = len(code_files)
            
            # Code size (0-3 points)
            if total_lines < 20:
                score += 1.0
            elif total_lines < 100:
                score += 1.5
            elif total_lines < 300:
                score += 2.0
            elif total_lines < 1000:
                score += 2.5
            else:
                score += 3.0
            
            # Multi-file bonus (0-1.5 points)
            if file_count > 5:
                score += 1.5
            elif file_count > 2:
                score += 1.0
            elif file_count > 1:
                score += 0.5
        
        # Technical depth (0-3 points) - INCREASED
        technical_keywords = [
            'algorithm', 'architecture', 'security', 'performance', 'optimization',
            'design pattern', 'microservice', 'distributed', 'concurrent', 'async',
            'vulnerability', 'authentication', 'scalability'
        ]
        tech_count = sum(1 for kw in technical_keywords if kw in prompt.lower())
        score += min(tech_count * 0.8, 3.0)  # Increased from 0.5 to 0.8
        
        # Multiple concerns (0-2.5 points) - INCREASED
        concerns = [
            'security', 'performance', 'scalability', 'maintainability',
            'testability', 'reliability', 'usability', 'best practices'
        ]
        concern_count = sum(1 for c in concerns if c in prompt.lower())
        score += min(concern_count * 0.8, 2.5)  # Increased from 0.5 to 0.8
        
        # Comprehensive analysis bonus (0-2 points) - INCREASED
        if any(word in prompt.lower() for word in ['comprehensive', 'thorough', 'detailed', 'complete']):
            score += 2.0  # Increased from 1.0
        elif any(word in prompt.lower() for word in ['analyze', 'review', 'assess']):
            score += 1.0
        
        # Critical keywords (0-1.5 points)
        if any(word in prompt.lower() for word in ['critical', 'production', 'mission-critical']):
            score += 1.5
        
        return max(1, min(10, int(round(score))))
    
    def _identify_capabilities(self, task_type: TaskType, prompt: str) -> Set[str]:
        """Identify required capabilities"""
        capabilities = set(self.CAPABILITY_MAP.get(task_type, set()))
        
        # Add additional capabilities based on prompt keywords
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['security', 'vulnerability', 'exploit']):
            capabilities.add('security_expertise')
        
        if any(word in prompt_lower for word in ['algorithm', 'complexity', 'optimization']):
            capabilities.add('algorithm_knowledge')
        
        if any(word in prompt_lower for word in ['architecture', 'design', 'pattern']):
            capabilities.add('abstract_reasoning')
        
        if any(word in prompt_lower for word in ['api', 'endpoint', 'interface']):
            capabilities.add('api_design')
        
        return capabilities
    
    def _estimate_tokens(self, prompt: str, code_files: Dict[str, str] = None) -> int:
        """Estimate total token usage"""
        # Rough estimation: 1 token ≈ 4 characters
        tokens = len(prompt) // 4
        
        if code_files:
            code_length = sum(len(code) for code in code_files.values())
            tokens += code_length // 4
        
        return tokens
    
    def _calculate_domain_specificity(self, prompt: str) -> float:
        """Calculate how domain-specific the prompt is (0-1)"""
        # Domain-specific keywords
        domain_keywords = [
            'blockchain', 'machine learning', 'neural network', 'kubernetes',
            'microservice', 'distributed system', 'real-time', 'embedded',
            'cryptography', 'compiler', 'database', 'networking'
        ]
        
        prompt_lower = prompt.lower()
        matches = sum(1 for kw in domain_keywords if kw in prompt_lower)
        
        return min(matches * 0.2, 1.0)
    
    def _calculate_ambiguity(self, prompt: str) -> float:
        """Calculate ambiguity level (0-1, higher = more ambiguous)"""
        ambiguity = 0.0
        prompt_lower = prompt.lower()
        
        # Vague words increase ambiguity
        vague_words = ['somehow', 'maybe', 'possibly', 'might', 'could', 'should']
        ambiguity += sum(0.1 for word in vague_words if word in prompt_lower)
        
        # Questions without specifics increase ambiguity
        if '?' in prompt and len(prompt) < 100:
            ambiguity += 0.2
        
        # Lack of concrete details
        if not any(word in prompt_lower for word in ['file', 'function', 'class', 'line', 'code']):
            ambiguity += 0.2
        
        return min(ambiguity, 1.0)
    
    def _recommend_strategy(self, complexity: int, task_type: TaskType, 
                           ambiguity: float) -> ProcessingStrategy:
        """Recommend processing strategy"""
        
        # Critical complexity always uses consensus
        if complexity >= 9:
            return ProcessingStrategy.CONSENSUS
        
        # High ambiguity benefits from consensus
        if ambiguity > 0.6 and complexity >= 7:
            return ProcessingStrategy.CONSENSUS
        
        # Complex tasks use parallel
        if complexity >= 7:
            return ProcessingStrategy.PARALLEL
        
        # Sequential for iterative tasks
        if task_type in [TaskType.REFACTORING, TaskType.API_DESIGN] and complexity >= 5:
            return ProcessingStrategy.SEQUENTIAL
        
        # Moderate complexity uses sequential
        if complexity >= 5:
            return ProcessingStrategy.SEQUENTIAL
        
        # Simple tasks use single model
        return ProcessingStrategy.SINGLE
    
    def _recommend_models(self, complexity: int, task_type: TaskType,
                         capabilities: Set[str]) -> List[str]:
        """Recommend models based on complexity and task type"""
        
        # Model specializations (from research)
        TASK_SPECIALISTS = {
            TaskType.CODE_REVIEW: "claude-opus-4.5",
            TaskType.ARCHITECTURE: "gemini-3-pro",
            TaskType.SECURITY: "claude-opus-4.5",
            TaskType.PERFORMANCE: "gemini-3-pro",
            TaskType.ALGORITHM: "gemini-3-pro",
            TaskType.BUG_FIX: "claude-opus-4.5",
            TaskType.REFACTORING: "claude-opus-4.5",
            TaskType.API_DESIGN: "deepseek-v3.2",
            TaskType.BEST_PRACTICES: "claude-opus-4.5",
            TaskType.GENERAL: "claude-opus-4.5"
        }
        
        models = []
        
        # Simple: 1 model
        if complexity <= 4:
            models.append(TASK_SPECIALISTS.get(task_type, "claude-opus-4.5"))
            return models
        
        # Moderate: 2 models
        if complexity <= 6:
            primary = TASK_SPECIALISTS.get(task_type, "claude-opus-4.5")
            models.append(primary)
            
            # Add complementary model
            if task_type in [TaskType.ARCHITECTURE, TaskType.ALGORITHM]:
                models.append("deepseek-r1")
            else:
                models.append("deepseek-v3.2")
            
            return models
        
        # Complex: 3 models
        if complexity <= 8:
            # Always include Claude for code quality
            models.append("claude-opus-4.5")
            
            # Add Gemini for architecture/algorithms
            if task_type in [TaskType.ARCHITECTURE, TaskType.ALGORITHM, TaskType.PERFORMANCE]:
                models.append("gemini-3-pro")
                models.append("deepseek-r1")
            else:
                models.append("gemini-3-pro")
                models.append("deepseek-v3.2")
            
            return models
        
        # Critical: All models
        models = ["gemini-3-pro", "claude-opus-4.5", "deepseek-r1"]
        
        # Add GPT-5.2 Pro for critical security
        if task_type == TaskType.SECURITY and complexity == 10:
            models.append("gpt-5.2-pro")
        
        return models
    
    def _generate_reasoning(self, task_type: TaskType, complexity: int,
                           capabilities: Set[str], strategy: ProcessingStrategy,
                           models: List[str]) -> str:
        """Generate human-readable reasoning"""
        
        parts = []
        
        # Task type
        parts.append(f"Task: {task_type.value.replace('_', ' ').title()}")
        
        # Complexity
        if complexity <= 2:
            parts.append(f"Complexity: {complexity}/10 (Trivial)")
        elif complexity <= 4:
            parts.append(f"Complexity: {complexity}/10 (Simple)")
        elif complexity <= 6:
            parts.append(f"Complexity: {complexity}/10 (Moderate)")
        elif complexity <= 8:
            parts.append(f"Complexity: {complexity}/10 (Complex)")
        else:
            parts.append(f"Complexity: {complexity}/10 (Critical)")
        
        # Capabilities
        if capabilities:
            cap_str = ', '.join(sorted(capabilities))
            parts.append(f"Required: {cap_str}")
        
        # Strategy
        parts.append(f"Strategy: {strategy.value.title()}")
        
        # Models
        parts.append(f"Models: {', '.join(models)}")
        
        return " | ".join(parts)

# Global instance
_analyzer = None

def get_prompt_analyzer() -> PromptComplexityAnalyzer:
    """Get or create the prompt analyzer"""
    global _analyzer
    if _analyzer is None:
        _analyzer = PromptComplexityAnalyzer()
    return _analyzer

if __name__ == "__main__":
    # Test the analyzer
    analyzer = get_prompt_analyzer()
    
    test_prompts = [
        {
            "prompt": "Fix the typo in line 5",
            "code": None,
            "expected": "SINGLE, complexity 1-2"
        },
        {
            "prompt": "Review this code for best practices",
            "code": {"main.py": "def hello():\n    print('hello')\n"},
            "expected": "SINGLE, complexity 3-4"
        },
        {
            "prompt": "Analyze the security vulnerabilities in this authentication system",
            "code": {"auth.py": "# 100 lines of auth code..."},
            "expected": "SEQUENTIAL/PARALLEL, complexity 5-7"
        },
        {
            "prompt": "Comprehensive architecture review of this microservices system with focus on security, performance, and scalability",
            "code": {
                "gateway.py": "# API gateway code...",
                "auth.py": "# Auth service...",
                "db.py": "# Database layer..."
            },
            "expected": "CONSENSUS, complexity 8-10"
        }
    ]
    
    print("\n" + "="*100)
    print("PROMPT COMPLEXITY ANALYZER TEST")
    print("="*100 + "\n")
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['prompt'][:60]}...")
        print(f"{'='*80}\n")
        
        result = analyzer.analyze(test['prompt'], test['code'])
        
        print(f"Task Type: {result.task_type.value}")
        print(f"Complexity: {result.complexity_score}/10")
        print(f"Strategy: {result.recommended_strategy.value.upper()}")
        print(f"Models: {', '.join(result.recommended_models)}")
        print(f"Capabilities: {', '.join(sorted(result.required_capabilities))}")
        print(f"Estimated Tokens: {result.estimated_tokens}")
        print(f"Domain Specificity: {result.domain_specificity:.2f}")
        print(f"Ambiguity: {result.ambiguity_level:.2f}")
        print(f"\nReasoning: {result.reasoning}")
        print(f"Expected: {test['expected']}")
    
    print("\n" + "="*100 + "\n")
