"""
Dive AI V29 - Algorithm Suggestion System
AI-powered algorithm selection via scoring

Features:
- Algorithm catalog with 3 tiers (Strategy, Tactic, Operation)
- Scoring formula: f(A) = base + domain_match + trigger_match + complexity_match - g_cost
- Historical learning from execution data
- Top-N suggestions for AI selection
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.memory_v2 import get_memory_v2, AlgorithmRecord
except ImportError:
    from memory_v2 import get_memory_v2, AlgorithmRecord


@dataclass
class AlgorithmSuggestion:
    """A suggested algorithm with score and reasoning"""
    algorithm: str
    tier: str
    score: float
    reasoning: str
    connections: List[str] = field(default_factory=list)
    sub_algorithms: List[str] = field(default_factory=list)
    confidence: float = 1.0


# ==========================================
# ALGORITHM CATALOG
# ==========================================

ALGORITHM_CATALOG = {
    # ============================================
    # TIER 1: STRATEGY (High-Level Meta-Algorithms)
    # ============================================
    "DevelopWebApp": {
        "tier": "strategy",
        "domains": ["web", "frontend", "backend", "website", "app"],
        "triggers": ["build app", "create website", "develop", "web application", "make a site"],
        "complexity_range": (7, 10),
        "base_score": 0.8,
        "description": "Full web application development workflow",
        "sub_algorithms": ["ScaffoldProject", "DesignSchema", "WriteComponent", "AddTests", "Deploy"],
        "connections": ["task_decomposition", "code_generator", "test_generator", "auto_doc_generator"],
        "workflow_states": ["scaffolding", "schema_design", "implementation", "testing", "deployment"]
    },
    
    "AnalyzeLargeDataset": {
        "tier": "strategy",
        "domains": ["data", "analysis", "ml", "dataset", "statistics"],
        "triggers": ["analyze data", "dataset", "statistics", "insights", "analyze csv", "data analysis"],
        "complexity_range": (6, 10),
        "base_score": 0.75,
        "description": "Large dataset analysis and insights extraction",
        "sub_algorithms": ["LoadData", "CleanData", "Analyze", "Visualize", "Report"],
        "connections": ["rag_engine", "vision_analysis", "auto_doc_generator"],
        "workflow_states": ["data_loading", "cleaning", "analysis", "visualization", "reporting"]
    },
    
    "ConductResearch": {
        "tier": "strategy",
        "domains": ["research", "investigation", "study", "learn"],
        "triggers": ["research", "investigate", "find out", "learn about", "study", "deep dive"],
        "complexity_range": (5, 9),
        "base_score": 0.7,
        "description": "Conduct in-depth research on a topic",
        "sub_algorithms": ["WebSearch", "Gather", "Synthesize", "Summarize", "Document"],
        "connections": ["advanced_search", "skill_seekers", "auto_doc_generator", "rag_engine"],
        "workflow_states": ["search", "gathering", "synthesis", "documentation"]
    },
    
    "RefactorCodebase": {
        "tier": "strategy",
        "domains": ["refactoring", "cleanup", "optimization", "improve"],
        "triggers": ["refactor", "clean up", "optimize code", "improve code", "restructure"],
        "complexity_range": (6, 9),
        "base_score": 0.75,
        "description": "Systematic codebase refactoring",
        "sub_algorithms": ["AnalyzeCode", "PlanRefactor", "ExecuteRefactor", "Test", "Verify"],
        "connections": ["complexity_analyzer", "code_generator", "test_generator", "exhaustive_verification"],
        "workflow_states": ["analysis", "planning", "execution", "testing", "verification"]
    },
    
    "BuildAPIBackend": {
        "tier": "strategy",
        "domains": ["api", "backend", "server", "rest", "graphql"],
        "triggers": ["build api", "create backend", "rest api", "server", "endpoints"],
        "complexity_range": (6, 10),
        "base_score": 0.78,
        "description": "Build complete API backend",
        "sub_algorithms": ["DesignAPI", "CreateEndpoints", "AddAuth", "AddTests", "Document"],
        "connections": ["code_generator", "test_generator", "auto_doc_generator", "security_guardrail"],
        "workflow_states": ["design", "implementation", "auth", "testing", "documentation"]
    },
    
    # ============================================
    # TIER 2: TACTIC (Mid-Level Algorithms)
    # ============================================
    "WritePythonCode": {
        "tier": "tactic",
        "domains": ["code", "python", "programming", "function"],
        "triggers": ["write python", "create function", "implement", "code", "python script"],
        "complexity_range": (3, 7),
        "base_score": 0.85,
        "description": "Write Python code with best practices",
        "sub_operations": ["code_generator", "test_generator"],
        "connections": ["code_generator", "test_generator", "llm_query"]
    },
    
    "WriteJavaScript": {
        "tier": "tactic",
        "domains": ["javascript", "js", "node", "react", "frontend"],
        "triggers": ["write js", "javascript", "react component", "node script"],
        "complexity_range": (3, 7),
        "base_score": 0.82,
        "description": "Write JavaScript/TypeScript code",
        "sub_operations": ["code_generator", "test_generator"],
        "connections": ["code_generator", "llm_query"]
    },
    
    "DebugAndFix": {
        "tier": "tactic",
        "domains": ["debug", "fix", "error", "bug", "issue"],
        "triggers": ["fix bug", "debug", "error", "not working", "broken", "issue"],
        "complexity_range": (4, 8),
        "base_score": 0.9,
        "description": "Debug and fix code issues",
        "sub_operations": ["auto_error_handler", "evidence_collector", "recovery_handler"],
        "connections": ["auto_error_handler", "recovery_handler", "evidence_collector"]
    },
    
    "SearchAndSynthesize": {
        "tier": "tactic",
        "domains": ["search", "find", "information", "lookup"],
        "triggers": ["find", "search for", "look up", "where is", "what is", "how to"],
        "complexity_range": (2, 5),
        "base_score": 0.85,
        "description": "Search for information and synthesize results",
        "sub_operations": ["advanced_search", "rag_engine", "response_ranker"],
        "connections": ["advanced_search", "rag_engine", "skill_seekers"]
    },
    
    "AnalyzeFile": {
        "tier": "tactic",
        "domains": ["analysis", "file", "read", "understand"],
        "triggers": ["analyze", "read file", "what is in", "understand", "explain file"],
        "complexity_range": (2, 6),
        "base_score": 0.8,
        "description": "Analyze and understand file contents",
        "sub_operations": ["vision_analysis", "complexity_analyzer", "context_compression"],
        "connections": ["vision_analysis", "complexity_analyzer", "llm_query"]
    },
    
    "AutomateTask": {
        "tier": "tactic",
        "domains": ["automation", "repeat", "workflow", "batch"],
        "triggers": ["automate", "repeat", "batch", "for each", "run multiple"],
        "complexity_range": (4, 8),
        "base_score": 0.75,
        "description": "Automate repetitive tasks",
        "sub_operations": ["workflow_engine", "dag_executor", "task_orchestrator"],
        "connections": ["workflow_engine", "dag_executor", "task_orchestrator"]
    },
    
    "ControlComputer": {
        "tier": "tactic",
        "domains": ["ui", "desktop", "automation", "click", "mouse"],
        "triggers": ["click", "open app", "control", "mouse", "keyboard", "ui automation"],
        "complexity_range": (3, 7),
        "base_score": 0.8,
        "description": "Control computer UI elements",
        "sub_operations": ["computer_operator", "uitars_algorithm", "vision_analysis"],
        "connections": ["computer_operator", "uitars_algorithm", "vision_analysis"]
    },
    
    "WriteTests": {
        "tier": "tactic",
        "domains": ["testing", "test", "unittest", "pytest"],
        "triggers": ["write test", "create tests", "unit test", "test case"],
        "complexity_range": (3, 6),
        "base_score": 0.85,
        "description": "Write comprehensive tests",
        "sub_operations": ["test_generator", "exhaustive_verification"],
        "connections": ["test_generator", "code_generator"]
    },
    
    "DocumentCode": {
        "tier": "tactic",
        "domains": ["documentation", "docs", "readme", "docstring"],
        "triggers": ["document", "create docs", "readme", "add comments", "docstring"],
        "complexity_range": (2, 5),
        "base_score": 0.8,
        "description": "Generate code documentation",
        "sub_operations": ["auto_doc_generator", "llm_query"],
        "connections": ["auto_doc_generator", "llm_query"]
    },
    
    "ReviewCode": {
        "tier": "tactic",
        "domains": ["review", "check", "quality", "audit"],
        "triggers": ["review code", "check code", "code quality", "audit", "pr review"],
        "complexity_range": (3, 7),
        "base_score": 0.82,
        "description": "Review code for quality and issues",
        "sub_operations": ["complexity_analyzer", "security_guardrail", "cruel_evaluator"],
        "connections": ["complexity_analyzer", "security_guardrail", "quality_gate"]
    },
    
    # ============================================
    # TIER 3: OPERATION (Low-Level Atomic Actions)
    # ============================================
    "CodeGenerator": {
        "tier": "operation",
        "domains": ["code", "generate"],
        "triggers": ["generate code", "write code"],
        "complexity_range": (1, 4),
        "base_score": 0.95,
        "description": "Generate code from requirements",
        "atomic": True,
        "connections": ["llm_query"]
    },
    
    "TestGenerator": {
        "tier": "operation",
        "domains": ["testing", "test"],
        "triggers": ["generate test", "write test"],
        "complexity_range": (1, 4),
        "base_score": 0.9,
        "description": "Generate test cases",
        "atomic": True,
        "connections": ["code_generator", "llm_query"]
    },
    
    "AdvancedSearch": {
        "tier": "operation",
        "domains": ["search", "find"],
        "triggers": ["search", "find in code", "grep"],
        "complexity_range": (1, 3),
        "base_score": 0.95,
        "description": "Advanced code and file search",
        "atomic": True,
        "connections": ["rag_engine"]
    },
    
    "LLMQuery": {
        "tier": "operation",
        "domains": ["llm", "ai", "query"],
        "triggers": ["ask", "query", "generate", "ai"],
        "complexity_range": (1, 3),
        "base_score": 0.9,
        "description": "Query LLM for generation/analysis",
        "atomic": True,
        "connections": ["v98_connection", "aicoding_connection"]
    },
    
    "VisionAnalysis": {
        "tier": "operation",
        "domains": ["image", "screenshot", "visual"],
        "triggers": ["analyze image", "screenshot", "see", "visual"],
        "complexity_range": (1, 4),
        "base_score": 0.85,
        "description": "Analyze images and screenshots",
        "atomic": True,
        "connections": ["llm_query", "uitars_algorithm"]
    },
    
    "FileOperation": {
        "tier": "operation",
        "domains": ["file", "read", "write"],
        "triggers": ["read file", "write file", "create file", "delete file"],
        "complexity_range": (1, 2),
        "base_score": 0.98,
        "description": "File system operations",
        "atomic": True,
        "connections": []
    },
    
    "CommandExecution": {
        "tier": "operation",
        "domains": ["command", "terminal", "shell"],
        "triggers": ["run command", "execute", "terminal", "shell"],
        "complexity_range": (1, 3),
        "base_score": 0.95,
        "description": "Execute system commands",
        "atomic": True,
        "connections": ["autonomous_executor"]
    },
    
    "APIRequest": {
        "tier": "operation",
        "domains": ["api", "http", "request"],
        "triggers": ["call api", "http request", "fetch", "post"],
        "complexity_range": (1, 3),
        "base_score": 0.9,
        "description": "Make HTTP API requests",
        "atomic": True,
        "connections": ["v98_connection", "aicoding_connection"]
    }
}


class AlgorithmSuggester:
    """
    AI-Powered Algorithm Suggestion System
    
    Suggests best algorithms for a task based on:
    - Domain matching
    - Trigger keyword matching
    - Task complexity
    - Historical performance (g(A))
    """
    
    def __init__(self, memory_db_path: str = "data/dive_ai_v29.db"):
        """Initialize suggester with memory"""
        self.memory = get_memory_v2(memory_db_path)
        self.catalog = ALGORITHM_CATALOG
        
        # Register all catalog algorithms to memory
        self._register_catalog_to_memory()
        
        print("🎯 Algorithm Suggester initialized")
        print(f"   Catalog size: {len(self.catalog)} algorithms")
    
    def _register_catalog_to_memory(self):
        """Register catalog algorithms to memory for tracking"""
        for algo_name, spec in self.catalog.items():
            record = AlgorithmRecord(
                algorithm_id=algo_name,
                name=algo_name,
                tier=spec["tier"],
                category=spec.get("domains", ["general"])[0],
                description=spec.get("description", ""),
                tags=spec.get("domains", []) + spec.get("triggers", [])[:3],
                base_score=spec.get("base_score", 0.5)
            )
            self.memory.register_algorithm(record)
    
    def suggest(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        top_n: int = 5,
        tier_filter: Optional[str] = None
    ) -> List[AlgorithmSuggestion]:
        """
        Suggest top-N algorithms for user request
        
        Args:
            user_request: Natural language request
            context: Additional context
            top_n: Number of suggestions to return
            tier_filter: Optional filter by tier (strategy/tactic/operation)
        
        Returns:
            List of AlgorithmSuggestion sorted by score
        """
        # 1. Estimate task complexity
        complexity = self._estimate_complexity(user_request)
        
        # 2. Score all algorithms
        suggestions = []
        
        for algo_name, spec in self.catalog.items():
            # Apply tier filter if specified
            if tier_filter and spec["tier"] != tier_filter:
                continue
            
            # Calculate score
            score, reasoning = self._calculate_score(
                algo_name,
                spec,
                user_request,
                complexity
            )
            
            suggestion = AlgorithmSuggestion(
                algorithm=algo_name,
                tier=spec["tier"],
                score=score,
                reasoning=reasoning,
                connections=spec.get("connections", []),
                sub_algorithms=spec.get("sub_algorithms", spec.get("sub_operations", [])),
                confidence=min(score + 0.1, 1.0)
            )
            
            suggestions.append(suggestion)
        
        # 3. Sort by score descending
        suggestions.sort(key=lambda x: x.score, reverse=True)
        
        # 4. Return top-N
        return suggestions[:top_n]
    
    def _estimate_complexity(self, request: str) -> int:
        """
        Estimate task complexity (1-10)
        
        Higher complexity for:
        - Longer requests
        - Complex keywords
        - Multiple requirements
        """
        # Word count base
        words = request.split()
        word_count = len(words)
        
        # Complex keyword indicators
        complex_keywords = [
            "full", "complete", "comprehensive", "entire", "all",
            "production", "deploy", "scale", "optimize", "refactor"
        ]
        complex_count = sum(1 for w in words if w.lower() in complex_keywords)
        
        # Multi-step indicators
        multi_keywords = ["and", "then", "also", "after", "with"]
        multi_count = sum(1 for w in words if w.lower() in multi_keywords)
        
        # Calculate complexity
        base = min(word_count // 8 + 1, 5)
        complexity = base + complex_count + (multi_count // 2)
        
        return min(max(complexity, 1), 10)
    
    def _calculate_score(
        self,
        algo_name: str,
        spec: Dict,
        request: str,
        complexity: int
    ) -> Tuple[float, str]:
        """
        Calculate algorithm score using formula:
        f(A) = base + domain_match + trigger_match + complexity_match - g_cost
        
        Returns:
            (score, reasoning)
        """
        request_lower = request.lower()
        reasons = []
        
        # 1. Base score
        base = spec.get("base_score", 0.5)
        reasons.append(f"base={base:.2f}")
        
        # 2. Domain match (+0.1 per match)
        domain_match = 0.0
        matched_domains = []
        for domain in spec.get("domains", []):
            if domain.lower() in request_lower:
                domain_match += 0.1
                matched_domains.append(domain)
        domain_match = min(domain_match, 0.3)
        if matched_domains:
            reasons.append(f"domains={matched_domains}")
        
        # 3. Trigger match (+0.15 per match)
        trigger_match = 0.0
        matched_triggers = []
        for trigger in spec.get("triggers", []):
            if trigger.lower() in request_lower:
                trigger_match += 0.15
                matched_triggers.append(trigger)
        trigger_match = min(trigger_match, 0.4)
        if matched_triggers:
            reasons.append(f"triggers={matched_triggers}")
        
        # 4. Complexity match
        min_c, max_c = spec.get("complexity_range", (1, 10))
        if min_c <= complexity <= max_c:
            complexity_match = 0.1
            reasons.append(f"complexity_fit={complexity}")
        else:
            complexity_match = -0.15
            reasons.append(f"complexity_mismatch={complexity}")
        
        # 5. Historical cost g(A)
        g_cost = self.memory.calculate_historical_cost(algo_name)
        if g_cost != 0.5:  # Not default
            reasons.append(f"g_cost={g_cost:.2f}")
        
        # 6. Calculate final score
        score = base + domain_match + trigger_match + complexity_match - (g_cost * 0.3)
        score = min(max(score, 0.0), 1.0)
        
        reasoning = f"Score {score:.2f}: " + ", ".join(reasons)
        
        return score, reasoning
    
    def get_strategy_for_request(self, user_request: str) -> Optional[AlgorithmSuggestion]:
        """Get recommended strategy (high-level) for request"""
        strategies = self.suggest(user_request, tier_filter="strategy", top_n=1)
        return strategies[0] if strategies else None
    
    def get_tactics_for_strategy(self, strategy_name: str) -> List[AlgorithmSuggestion]:
        """Get tactics connected to a strategy"""
        if strategy_name not in self.catalog:
            return []
        
        strategy = self.catalog[strategy_name]
        connections = strategy.get("connections", [])
        
        tactics = []
        for algo_name, spec in self.catalog.items():
            if spec["tier"] == "tactic":
                # Check if connected
                algo_connections = spec.get("connections", [])
                if any(c in connections for c in algo_connections) or algo_name.lower() in str(connections).lower():
                    suggestion = AlgorithmSuggestion(
                        algorithm=algo_name,
                        tier="tactic",
                        score=spec.get("base_score", 0.5),
                        reasoning=f"Connected to {strategy_name}",
                        connections=algo_connections
                    )
                    tactics.append(suggestion)
        
        return tactics
    
    def explain_suggestion(self, suggestion: AlgorithmSuggestion) -> str:
        """Generate human-readable explanation"""
        spec = self.catalog.get(suggestion.algorithm, {})
        
        explanation = f"""
🎯 Algorithm: {suggestion.algorithm}
   Tier: {suggestion.tier.upper()}
   Score: {suggestion.score:.2f}
   
📝 Description:
   {spec.get('description', 'No description')}

🔗 Connections:
   {', '.join(suggestion.connections) if suggestion.connections else 'None'}

📊 Reasoning:
   {suggestion.reasoning}
"""
        
        if suggestion.sub_algorithms:
            explanation += f"""
📋 Sub-algorithms:
   {' → '.join(suggestion.sub_algorithms)}
"""
        
        return explanation
    
    def print_suggestions(self, suggestions: List[AlgorithmSuggestion]):
        """Print suggestions in readable format"""
        print("\n🎯 Algorithm Suggestions")
        print("=" * 50)
        
        for i, s in enumerate(suggestions, 1):
            tier_emoji = {"strategy": "🏛️", "tactic": "⚔️", "operation": "⚙️"}.get(s.tier, "📌")
            print(f"\n{i}. {tier_emoji} [{s.tier.upper()}] {s.algorithm}")
            print(f"   Score: {s.score:.2f} | Confidence: {s.confidence:.2f}")
            print(f"   {s.reasoning}")
            if s.connections:
                print(f"   🔗 {', '.join(s.connections[:3])}")
        
        print("\n" + "=" * 50)


# Singleton
_suggester_instance = None

def get_algorithm_suggester(db_path: str = "data/dive_ai_v29.db") -> AlgorithmSuggester:
    """Get or create Algorithm Suggester singleton"""
    global _suggester_instance
    if _suggester_instance is None:
        _suggester_instance = AlgorithmSuggester(db_path)
    return _suggester_instance


# Test
if __name__ == "__main__":
    suggester = get_algorithm_suggester("data/test_suggester.db")
    
    # Test various requests
    test_requests = [
        "Build a complete web application with React and Firebase",
        "Fix the bug in my Python code",
        "Search for information about machine learning",
        "Write unit tests for the user service",
        "Analyze this CSV file and create visualizations",
        "Click the submit button on the webpage"
    ]
    
    for request in test_requests:
        print(f"\n{'='*60}")
        print(f"📝 Request: {request}")
        print(f"   Complexity: {suggester._estimate_complexity(request)}")
        
        suggestions = suggester.suggest(request, top_n=3)
        suggester.print_suggestions(suggestions)
