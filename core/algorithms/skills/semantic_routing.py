"""
Semantic Routing Algorithm (SR)
Route queries to specialized models/experts based on semantic understanding

Algorithm = CODE + STEPS
⭐ CRITICAL SKILL from V27.2
"""

import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class SemanticRoutingAlgorithm(BaseAlgorithm):
    """
    Semantic Routing (SR) - Intelligent Query Routing
    
    ⭐ CRITICAL SKILL: Routes queries to optimal expert/model based on semantic analysis
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="SemanticRouting",
            name="Semantic Routing (SR)",
            level="operational",
            category="skills",
            version="1.0",
            description="Route queries to specialized models/experts based on semantic understanding. Analyzes intent, domain, complexity to select optimal handler.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("query", "string", True, "User query"),
                    IOField("available_experts", "list", False, "Available expert models"),
                    IOField("routing_strategy", "string", False, "Strategy: auto/explicit")
                ],
                outputs=[
                    IOField("selected_expert", "string", True, "Selected expert/model"),
                    IOField("confidence", "float", True, "Routing confidence 0-1"),
                    IOField("reasoning", "string", True, "Why this expert was selected"),
                    IOField("fallback_experts", "list", False, "Alternative experts")
                ]
            ),
            
            steps=[
                "Step 1: Analyze query semantics (intent, domain, complexity)",
                "Step 2: Extract key topics and keywords",
                "Step 3: Match to expert specializations",
                "Step 4: Calculate confidence scores",
                "Step 5: Select highest-confidence expert",
                "Step 6: Identify fallback options",
                "Step 7: Return routing decision + reasoning"
            ],
            
            tags=["semantic-routing", "sr", "skill", "routing", "CRITICAL"],
            performance_target={
                "accuracy": "95%+ correct routing",
                "latency": "<100ms"
            }
        )
        
        # Define expert specializations
        self.experts = {
            "code_expert": {
                "domains": ["programming", "coding", "debugging", "algorithm"],
                "keywords": ["code", "function", "class", "bug", "implement", "refactor"],
                "languages": ["python", "javascript", "java", "go", "c++"]
            },
            "data_expert": {
                "domains": ["data-science", "analytics", "statistics", "ml"],
                "keywords": ["data", "analyze", "predict", "model", "train", "dataset"],
                "tools": ["pandas", "numpy", "sklearn", "tensorflow"]
            },
            "system_expert": {
                "domains": ["architecture", "infrastructure", "devops", "deployment"],
                "keywords": ["deploy", "scale", "architecture", "infrastructure", "server"],
                "technologies": ["docker", "kubernetes", "aws", "ci/cd"]
            },
            "qa_expert": {
                "domains": ["general-knowledge", "explanation", "definition"],
                "keywords": ["what", "how", "why", "explain", "define"],
                "scope": ["general"]
            },
            "creative_expert": {
                "domains": ["writing", "content", "creative"],
                "keywords": ["write", "create", "generate", "story", "article"],
                "outputs": ["text", "content", "documentation"]
            }
        }
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute semantic routing"""
        
        query = params.get("query", "")
        available_experts = params.get("available_experts", list(self.experts.keys()))
        routing_strategy = params.get("routing_strategy", "auto")
        
        print(f"\n🎯 Semantic Routing: '{query[:60]}...'")
        
        try:
            # Step 1: Analyze query
            analysis = self._analyze_query(query)
            
            print(f"   📊 Intent: {analysis['intent']}, Domain: {analysis['domain']}")
            
            # Step 2-4: Match and score experts
            expert_scores = {}
            for expert_id in available_experts:
                if expert_id in self.experts:
                    score = self._calculate_expert_score(
                        self.experts[expert_id],
                        analysis
                    )
                    expert_scores[expert_id] = score
            
            # Step 5: Select best expert
            if not expert_scores:
                selected = "qa_expert"  # Default fallback
                confidence = 0.5
            else:
                selected = max(expert_scores, key=expert_scores.get)
                confidence = expert_scores[selected]
            
            # Step 6: Get fallback options
            sorted_experts = sorted(expert_scores.items(), key=lambda x: x[1], reverse=True)
            fallbacks = [exp for exp, _ in sorted_experts[1:3]]  # Top 2 alternatives
            
            # Step 7: Create reasoning
            reasoning = self._create_reasoning(selected, analysis, confidence)
            
            print(f"   ✅ Routed to: {selected} (confidence: {confidence:.2f})")
            
            return AlgorithmResult(
                status="success",
                data={
                    "selected_expert": selected,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "fallback_experts": fallbacks
                },
                metadata={
                    "analysis": analysis,
                    "all_scores": expert_scores
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Semantic routing failed: {str(e)}")
    
    def _analyze_query(self, query: str) -> Dict:
        """Analyze query semantics"""
        
        query_lower = query.lower()
        
        # Detect intent
        if any(kw in query_lower for kw in ["how to", "implement", "create", "build"]):
            intent = "implementation"
        elif any(kw in query_lower for kw in ["what is", "explain", "define"]):
            intent = "explanation"
        elif any(kw in query_lower for kw in ["fix", "debug", "error", "bug"]):
            intent = "debugging"
        elif any(kw in query_lower for kw in ["analyze", "evaluate"]):
            intent = "analysis"
        else:
            intent = "general"
        
        # Detect domain
        if any(kw in query_lower for kw in ["code", "function", "class", "python", "javascript"]):
            domain = "programming"
        elif any(kw in query_lower for kw in ["data", "dataset", "model", "train"]):
            domain = "data-science"
        elif any(kw in query_lower for kw in ["deploy", "server", "infrastructure"]):
            domain = "infrastructure"
        else:
            domain = "general"
        
        # Extract keywords
        words = query_lower.split()
        keywords = [w for w in words if len(w) > 3][:10]
        
        return {
            "intent": intent,
            "domain": domain,
            "keywords": keywords,
            "length": len(query),
            "complexity": "high" if len(words) > 20 else "medium" if len(words) > 10 else "low"
        }
    
    def _calculate_expert_score(self, expert_config: Dict, analysis: Dict) -> float:
        """Calculate match score for expert"""
        
        score = 0.0
        
        # Domain match (40% weight)
        if analysis["domain"] in expert_config.get("domains", []):
            score += 0.4
        
        # Keyword match (40% weight)
        expert_keywords = expert_config.get("keywords", [])
        keyword_matches = sum(1 for kw in analysis["keywords"] if kw in expert_keywords)
        if expert_keywords:
            score += 0.4 * (keyword_matches / len(expert_keywords))
        
        # Scope match (20% weight)
        if expert_config.get("scope") == ["general"] and analysis["domain"] == "general":
            score += 0.2
        
        return min(score, 1.0)
    
    def _create_reasoning(self, expert_id: str, analysis: Dict, confidence: float) -> str:
        """Generate reasoning for routing decision"""
        
        reasons = [
            f"Query intent: {analysis['intent']}",
            f"Domain: {analysis['domain']}",
            f"Selected: {expert_id}",
            f"Confidence: {confidence:.0%}"
        ]
        
        return " | ".join(reasons)


def register(algorithm_manager):
    """Register Semantic Routing Algorithm"""
    try:
        algo = SemanticRoutingAlgorithm()
        algorithm_manager.register("SemanticRouting", algo)
        print("✅ Semantic Routing (SR) Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register SemanticRouting: {e}")

# Auto-register on import
if __name__ != "__main__":
    try:
        from core.algorithms.algorithm_manager import AlgorithmManager
    except ImportError:
        pass
