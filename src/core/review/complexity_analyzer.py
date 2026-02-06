#!/usr/bin/env python3
"""
Code Complexity Analyzer for Intelligent Model Selection
Analyzes code to determine optimal AI models for review
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ComplexityLevel(Enum):
    """Complexity levels for code review"""
    SIMPLE = "simple"           # 1-3: Simple refactoring, style fixes
    MODERATE = "moderate"       # 4-6: Standard features, bug fixes
    COMPLEX = "complex"         # 7-8: Architecture, algorithms, security
    CRITICAL = "critical"       # 9-10: Mission-critical, high-risk changes

class ReviewType(Enum):
    """Types of code review tasks"""
    REFACTORING = "refactoring"
    BUG_FIX = "bug_fix"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ALGORITHM = "algorithm"
    API_DESIGN = "api_design"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"

@dataclass
class ComplexityScore:
    """Complexity analysis result"""
    overall_score: int  # 1-10
    level: ComplexityLevel
    review_types: List[ReviewType]
    metrics: Dict[str, float]
    recommended_models: List[str]
    reasoning: str

class ComplexityAnalyzer:
    """
    Analyzes code complexity to determine optimal review models
    """
    
    def __init__(self):
        self.metrics = {}
    
    def analyze(self, code_files: Dict[str, str], context: str = "") -> ComplexityScore:
        """
        Analyze code complexity and recommend models
        
        Args:
            code_files: Dict of {filename: code_content}
            context: Project context from Dive-Memory
        
        Returns:
            ComplexityScore with recommendations
        """
        
        # Calculate individual metrics
        metrics = {
            "lines_of_code": self._count_lines(code_files),
            "file_count": len(code_files),
            "cyclomatic_complexity": self._estimate_cyclomatic_complexity(code_files),
            "nesting_depth": self._calculate_nesting_depth(code_files),
            "function_count": self._count_functions(code_files),
            "class_count": self._count_classes(code_files),
            "import_count": self._count_imports(code_files),
            "comment_ratio": self._calculate_comment_ratio(code_files),
            "security_indicators": self._detect_security_patterns(code_files),
            "algorithm_complexity": self._detect_algorithm_complexity(code_files),
            "api_patterns": self._detect_api_patterns(code_files),
            "architectural_patterns": self._detect_architectural_patterns(code_files),
        }
        
        # Determine review types needed
        review_types = self._determine_review_types(metrics, context)
        
        # Calculate overall complexity score (1-10)
        overall_score = self._calculate_overall_score(metrics, review_types)
        
        # Determine complexity level
        level = self._determine_complexity_level(overall_score)
        
        # Recommend models based on complexity and review types
        recommended_models = self._recommend_models(overall_score, review_types, metrics)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(metrics, review_types, recommended_models)
        
        return ComplexityScore(
            overall_score=overall_score,
            level=level,
            review_types=review_types,
            metrics=metrics,
            recommended_models=recommended_models,
            reasoning=reasoning
        )
    
    def _count_lines(self, code_files: Dict[str, str]) -> int:
        """Count total lines of code"""
        total = 0
        for content in code_files.values():
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            total += len(lines)
        return total
    
    def _estimate_cyclomatic_complexity(self, code_files: Dict[str, str]) -> float:
        """Estimate cyclomatic complexity"""
        total_complexity = 0
        total_functions = 0
        
        for content in code_files.values():
            # Count decision points (if, for, while, except, and, or, etc.)
            decision_keywords = ['if ', 'elif ', 'for ', 'while ', 'except ', ' and ', ' or ', 'case ']
            for keyword in decision_keywords:
                total_complexity += content.count(keyword)
            
            # Count functions
            total_functions += content.count('def ') + content.count('function ') + content.count('const ')
        
        if total_functions == 0:
            return 1.0
        
        return total_complexity / max(total_functions, 1)
    
    def _calculate_nesting_depth(self, code_files: Dict[str, str]) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        
        for content in code_files.values():
            current_depth = 0
            for line in content.split('\n'):
                # Count leading spaces/tabs
                stripped = line.lstrip()
                if stripped:
                    indent = len(line) - len(stripped)
                    current_depth = indent // 4  # Assume 4-space indentation
                    max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def _count_functions(self, code_files: Dict[str, str]) -> int:
        """Count total functions"""
        total = 0
        for content in code_files.values():
            total += content.count('def ') + content.count('function ') + content.count('const ')
        return total
    
    def _count_classes(self, code_files: Dict[str, str]) -> int:
        """Count total classes"""
        total = 0
        for content in code_files.values():
            total += content.count('class ') + content.count('interface ')
        return total
    
    def _count_imports(self, code_files: Dict[str, str]) -> int:
        """Count import statements"""
        total = 0
        for content in code_files.values():
            total += content.count('import ') + content.count('from ') + content.count('require(')
        return total
    
    def _calculate_comment_ratio(self, code_files: Dict[str, str]) -> float:
        """Calculate ratio of comments to code"""
        total_lines = 0
        comment_lines = 0
        
        for content in code_files.values():
            lines = content.split('\n')
            total_lines += len(lines)
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                    comment_lines += 1
        
        return comment_lines / max(total_lines, 1)
    
    def _detect_security_patterns(self, code_files: Dict[str, str]) -> float:
        """Detect security-sensitive patterns"""
        security_keywords = [
            'password', 'token', 'secret', 'api_key', 'auth', 'encrypt', 'decrypt',
            'sql', 'query', 'execute', 'eval', 'exec', 'subprocess', 'shell',
            'pickle', 'yaml.load', 'json.loads', 'input(', 'raw_input(',
            'os.system', 'os.popen', 'requests.', 'urllib', 'socket'
        ]
        
        # High-risk patterns (worth more points)
        high_risk_patterns = [
            r'f".*SELECT.*FROM.*{',  # SQL injection with f-strings
            r'f\'.*SELECT.*FROM.*{',
            r'hardcoded.*secret',
            r'hardcoded.*password',
            r'SECRET.*=.*["\']',
            r'PASSWORD.*=.*["\']',
            r'eval\(',
            r'exec\(',
            r'os\.system',
            r'subprocess\.call',
        ]
        
        score = 0
        for content in code_files.values():
            content_lower = content.lower()
            
            # Count regular security keywords (1 point each)
            for keyword in security_keywords:
                score += content_lower.count(keyword)
            
            # Count high-risk patterns (5 points each)
            for pattern in high_risk_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                score += len(matches) * 5
        
        return min(score / 5, 10)  # Normalize to 0-10 (adjusted divisor)
    
    def _detect_algorithm_complexity(self, code_files: Dict[str, str]) -> float:
        """Detect algorithmic complexity indicators"""
        algorithm_patterns = [
            r'for.*for',  # Nested loops
            r'while.*while',
            r'recursive',
            r'dynamic.?programming',
            r'memoiz',
            r'cache',
            r'sort',
            r'search',
            r'graph',
            r'tree',
            r'heap',
            r'queue',
            r'stack',
            r'O\(n',  # Big-O notation
        ]
        
        # Advanced algorithm names (worth more points)
        advanced_algorithms = [
            r'dijkstra',
            r'floyd.?warshall',
            r'bellman.?ford',
            r'a.?star',
            r'kruskal',
            r'prim',
            r'topological.?sort',
            r'binary.?search.?tree',
            r'red.?black.?tree',
            r'avl.?tree',
            r'b.?tree',
            r'quicksort',
            r'mergesort',
            r'heapsort',
        ]
        
        score = 0
        for content in code_files.values():
            # Count regular patterns (1 point each)
            for pattern in algorithm_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                score += len(matches)
            
            # Count advanced algorithms (3 points each)
            for pattern in advanced_algorithms:
                matches = re.findall(pattern, content, re.IGNORECASE)
                score += len(matches) * 3
        
        return min(score / 3, 10)  # Normalize to 0-10 (adjusted divisor)
    
    def _detect_api_patterns(self, code_files: Dict[str, str]) -> float:
        """Detect API design patterns"""
        api_patterns = [
            r'@app\.',  # Flask/FastAPI routes
            r'@router\.',
            r'@api\.',
            r'@route',
            r'@get|@post|@put|@delete|@patch',
            r'router\.',
            r'endpoint',
            r'swagger',
            r'openapi',
            r'graphql',
            r'rest',
            r'api',
        ]
        
        score = 0
        for content in code_files.values():
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                score += len(matches)
        
        return min(score / 5, 10)  # Normalize to 0-10
    
    def _detect_architectural_patterns(self, code_files: Dict[str, str]) -> float:
        """Detect architectural complexity"""
        arch_indicators = [
            'singleton', 'factory', 'observer', 'strategy', 'decorator',
            'adapter', 'facade', 'proxy', 'chain', 'command',
            'mvc', 'mvvm', 'repository', 'service', 'controller',
            'middleware', 'pipeline', 'event', 'message', 'queue'
        ]
        
        # Microservices/distributed system indicators (worth more)
        distributed_patterns = [
            r'microservice',
            r'api.?gateway',
            r'service.?mesh',
            r'circuit.?breaker',
            r'rate.?limit',
            r'load.?balanc',
            r'redis',
            r'kafka',
            r'rabbitmq',
            r'grpc',
            r'graphql',
        ]
        
        score = 0
        for content in code_files.values():
            content_lower = content.lower()
            
            # Count regular patterns (1 point each)
            for indicator in arch_indicators:
                score += content_lower.count(indicator)
            
            # Count distributed patterns (3 points each)
            for pattern in distributed_patterns:
                matches = re.findall(pattern, content_lower)
                score += len(matches) * 3
        
        # Bonus for multiple files (indicates architecture)
        if len(code_files) > 5:
            score += 10
        elif len(code_files) > 3:
            score += 5
        elif len(code_files) > 1:
            score += 2
        
        return min(score / 3, 10)  # Normalize to 0-10 (adjusted divisor)
    
    def _determine_review_types(self, metrics: Dict, context: str) -> List[ReviewType]:
        """Determine what types of review are needed"""
        review_types = []
        
        # Always include code quality
        review_types.append(ReviewType.CODE_QUALITY)
        
        # Security review if security patterns detected (LOWERED threshold)
        if metrics["security_indicators"] > 2:  # Changed from 3 to 2
            review_types.append(ReviewType.SECURITY)
        
        # Algorithm review if complex algorithms detected
        if metrics["algorithm_complexity"] > 5:
            review_types.append(ReviewType.ALGORITHM)
        
        # API design review if API patterns detected
        if metrics["api_patterns"] > 5:
            review_types.append(ReviewType.API_DESIGN)
        
        # Architecture review if architectural patterns detected
        if metrics["architectural_patterns"] > 5 or metrics["file_count"] > 5:
            review_types.append(ReviewType.ARCHITECTURE)
        
        # Performance review if high complexity
        if metrics["cyclomatic_complexity"] > 10 or metrics["nesting_depth"] > 4:
            review_types.append(ReviewType.PERFORMANCE)
        
        # Best practices if low comment ratio or high complexity
        if metrics["comment_ratio"] < 0.1 or metrics["cyclomatic_complexity"] > 8:
            review_types.append(ReviewType.BEST_PRACTICES)
        
        # Check context for keywords
        context_lower = context.lower()
        if 'refactor' in context_lower:
            review_types.append(ReviewType.REFACTORING)
        if 'bug' in context_lower or 'fix' in context_lower:
            review_types.append(ReviewType.BUG_FIX)
        if 'payment' in context_lower or 'transaction' in context_lower:
            # Payment processing is always security-sensitive
            if ReviewType.SECURITY not in review_types:
                review_types.append(ReviewType.SECURITY)
        
        return list(set(review_types))  # Remove duplicates
    
    def _calculate_overall_score(self, metrics: Dict, review_types: List[ReviewType]) -> int:
        """Calculate overall complexity score (1-10)"""
        
        # Base score from metrics
        score = 0.0
        
        # Lines of code (0-1.5 points) - reduced weight
        loc = metrics["lines_of_code"]
        if loc < 50:
            score += 0.5
        elif loc < 200:
            score += 1.0
        else:
            score += 1.5
        
        # Cyclomatic complexity (0-2 points)
        cc = metrics["cyclomatic_complexity"]
        if cc < 5:
            score += 0.5
        elif cc < 10:
            score += 1.0
        elif cc < 20:
            score += 1.5
        else:
            score += 2.0
        
        # Nesting depth (0-1.5 points) - increased weight
        if metrics["nesting_depth"] > 4:
            score += 1.5
        elif metrics["nesting_depth"] > 3:
            score += 1.0
        elif metrics["nesting_depth"] > 2:
            score += 0.5
        
        # File count (0-2 points) - increased weight for architecture
        if metrics["file_count"] > 10:
            score += 2.0
        elif metrics["file_count"] > 5:
            score += 1.5
        elif metrics["file_count"] > 2:
            score += 1.0
        elif metrics["file_count"] > 1:
            score += 0.5
        
        # Security indicators (0-3 points) - INCREASED weight
        security_score = metrics["security_indicators"]
        if security_score > 7:
            score += 3.5  # Increased from 3.0
        elif security_score > 5:  # New tier
            score += 2.5
        elif security_score > 3:
            score += 2.0
        elif security_score > 1:
            score += 1.0
        elif security_score > 0:
            score += 0.5
        
        # Algorithm complexity (0-2 points) - INCREASED weight
        algo_score = metrics["algorithm_complexity"]
        if algo_score > 7:
            score += 2.0
        elif algo_score > 4:
            score += 1.5
        elif algo_score > 2:
            score += 1.0
        elif algo_score > 0:
            score += 0.5
        
        # Architectural patterns (0-2 points) - INCREASED weight
        arch_score = metrics["architectural_patterns"]
        if arch_score > 7:
            score += 2.0
        elif arch_score > 4:
            score += 1.5
        elif arch_score > 2:
            score += 1.0
        elif arch_score > 0:
            score += 0.5
        
        # Review types count (more types = more complex)
        score += len(review_types) * 0.4  # Increased from 0.3
        
        # Bonus for specific high-risk combinations
        if ReviewType.SECURITY in review_types and ReviewType.BUG_FIX in review_types:
            score += 1.0  # Security bugs are critical
        if ReviewType.SECURITY in review_types and security_score > 5:
            score += 1.5  # Multiple security issues
        
        # Normalize to 1-10
        return max(1, min(10, int(round(score))))
    
    def _determine_complexity_level(self, score: int) -> ComplexityLevel:
        """Determine complexity level from score"""
        if score <= 3:
            return ComplexityLevel.SIMPLE
        elif score <= 6:
            return ComplexityLevel.MODERATE
        elif score <= 8:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.CRITICAL
    
    def _recommend_models(self, score: int, review_types: List[ReviewType], 
                         metrics: Dict) -> List[str]:
        """
        Recommend models based on complexity and review types
        
        Model Selection Strategy:
        - Simple (1-3): 1 model (Claude Opus 4.5 for speed)
        - Moderate (4-6): 2 models (Claude + DeepSeek V3.2 for cost)
        - Complex (7-8): 3 models (Gemini + Claude + DeepSeek)
        - Critical (9-10): 3-4 models (All models including R1)
        """
        
        models = []
        
        # Simple tasks: Claude only (fastest, most reliable)
        if score <= 3:
            models.append("claude-opus-4.5")
            return models
        
        # Moderate tasks: Claude + DeepSeek V3.2
        if score <= 6:
            models.append("claude-opus-4.5")  # Best code quality
            models.append("deepseek-v3.2")    # Cost-effective cross-check
            return models
        
        # Complex tasks: Choose 3 models based on review types
        if score <= 8:
            # Always include Claude for code quality
            models.append("claude-opus-4.5")
            
            # Add Gemini if architecture/algorithm/multimodal needed
            if (ReviewType.ARCHITECTURE in review_types or 
                ReviewType.ALGORITHM in review_types or
                metrics["architectural_patterns"] > 5):
                models.append("gemini-3-pro")
            
            # Add DeepSeek V3.2 if API design needed
            if ReviewType.API_DESIGN in review_types:
                models.append("deepseek-v3.2")
            
            # Add DeepSeek R1 if algorithm complexity high
            if metrics["algorithm_complexity"] > 7:
                if "deepseek-v3.2" in models:
                    models.remove("deepseek-v3.2")
                models.append("deepseek-r1")
            
            # Ensure we have 3 models
            if len(models) < 3:
                if "gemini-3-pro" not in models:
                    models.append("gemini-3-pro")
                elif "deepseek-v3.2" not in models:
                    models.append("deepseek-v3.2")
            
            return models
        
        # Critical tasks (9-10): All models
        models = ["gemini-3-pro", "claude-opus-4.5", "deepseek-r1"]
        
        # Add GPT-5.2 Pro for truly critical tasks (score 10)
        if score == 10 and metrics["security_indicators"] > 8:
            models.append("gpt-5.2-pro")
        
        return models
    
    def _generate_reasoning(self, metrics: Dict, review_types: List[ReviewType], 
                           models: List[str]) -> str:
        """Generate human-readable reasoning for model selection"""
        
        reasons = []
        
        # Explain complexity
        loc = metrics["lines_of_code"]
        cc = metrics["cyclomatic_complexity"]
        
        reasons.append(f"Code size: {loc} lines across {metrics['file_count']} files")
        reasons.append(f"Cyclomatic complexity: {cc:.1f} (avg per function)")
        
        if metrics["nesting_depth"] > 4:
            reasons.append(f"High nesting depth ({metrics['nesting_depth']}) detected")
        
        if metrics["security_indicators"] > 3:
            reasons.append(f"Security-sensitive code detected ({metrics['security_indicators']:.0f} indicators)")
        
        if metrics["algorithm_complexity"] > 5:
            reasons.append(f"Complex algorithms detected ({metrics['algorithm_complexity']:.0f} patterns)")
        
        if metrics["api_patterns"] > 5:
            reasons.append(f"API design patterns detected ({metrics['api_patterns']:.0f} patterns)")
        
        if metrics["architectural_patterns"] > 5:
            reasons.append(f"Architectural complexity detected ({metrics['architectural_patterns']:.0f} patterns)")
        
        # Explain review types
        review_names = [rt.value.replace('_', ' ').title() for rt in review_types]
        reasons.append(f"Review types: {', '.join(review_names)}")
        
        # Explain model selection
        model_reasons = []
        if "claude-opus-4.5" in models:
            model_reasons.append("Claude Opus 4.5 (best code quality & bug detection)")
        if "gemini-3-pro" in models:
            model_reasons.append("Gemini 3 Pro (abstract reasoning & architecture)")
        if "deepseek-v3.2" in models:
            model_reasons.append("DeepSeek V3.2 (API design & cost-effective)")
        if "deepseek-r1" in models:
            model_reasons.append("DeepSeek R1 (deep reasoning & algorithms)")
        if "gpt-5.2-pro" in models:
            model_reasons.append("GPT-5.2 Pro (critical decision support)")
        
        reasons.append(f"Selected models: {', '.join(model_reasons)}")
        
        return " | ".join(reasons)

# Global instance
_analyzer = None

def get_analyzer() -> ComplexityAnalyzer:
    """Get or create the complexity analyzer"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ComplexityAnalyzer()
    return _analyzer

if __name__ == "__main__":
    # Test the analyzer
    analyzer = get_analyzer()
    
    test_cases = [
        {
            "name": "Simple Refactoring",
            "files": {
                "utils.py": """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""
            },
            "context": "Simple refactoring task"
        },
        {
            "name": "Security-Critical API",
            "files": {
                "auth.py": """
import jwt
import bcrypt
from flask import request

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
            },
            "context": "Authentication API with potential SQL injection"
        },
        {
            "name": "Complex Algorithm",
            "files": {
                "graph.py": """
def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    visited = set()
    
    while len(visited) < len(graph):
        current = min((node for node in graph if node not in visited),
                     key=lambda n: distances[n])
        visited.add(current)
        
        for neighbor, weight in graph[current].items():
            distance = distances[current] + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
    
    return distances

def floyd_warshall(graph):
    dist = [[float('inf')] * len(graph) for _ in range(len(graph))]
    
    for i in range(len(graph)):
        dist[i][i] = 0
    
    for u in graph:
        for v, w in graph[u].items():
            dist[u][v] = w
    
    for k in range(len(graph)):
        for i in range(len(graph)):
            for j in range(len(graph)):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    
    return dist
"""
            },
            "context": "Graph algorithms for route optimization"
        }
    ]
    
    print("\n" + "="*100)
    print("COMPLEXITY ANALYZER TEST")
    print("="*100 + "\n")
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"Test Case: {test['name']}")
        print(f"{'='*80}\n")
        
        result = analyzer.analyze(test['files'], test['context'])
        
        print(f"Overall Score: {result.overall_score}/10")
        print(f"Complexity Level: {result.level.value.upper()}")
        print(f"Review Types: {', '.join([rt.value for rt in result.review_types])}")
        print(f"\nRecommended Models: {', '.join(result.recommended_models)}")
        print(f"\nReasoning: {result.reasoning}")
        print(f"\nMetrics:")
        for key, value in result.metrics.items():
            print(f"  {key}: {value}")
    
    print("\n" + "="*100 + "\n")
