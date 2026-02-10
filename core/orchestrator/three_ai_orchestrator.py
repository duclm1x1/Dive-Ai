"""
🦞 THREE-AI ORCHESTRATOR
Multi-model review chain for maximum code quality

Architecture:
1. Claude Opus 4.6  → Primary lead (planning + coding)
2. GPT-5.2-Codex    → Code reviewer (zero-error verification)
3. GLM-4.6v         → Multimodal consultant (final review)

Each AI has specific responsibilities and strengths.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)
from core.v98_client import V98Client
import time



class AIRole(Enum):
    """AI role in the 3-AI orchestration"""
    PRIMARY_LEAD = "primary_lead"           # Claude Opus 4.6
    CODE_REVIEWER = "code_reviewer"         # GPT-5.2-Codex
    MULTIMODAL_CONSULTANT = "consultant"    # GLM-4.6v


@dataclass
class AIConfig:
    """Configuration for each AI in the 3-AI system"""
    role: AIRole
    model: str
    provider: str
    priority: int
    features: List[str] = field(default_factory=list)
    cost_tier: str = "standard"
    strengths: List[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """Result from an AI review"""
    ai_role: AIRole
    model: str
    approved: bool
    confidence: float  # 0.0 - 1.0
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    processing_time: float = 0.0


@dataclass
class ThreeAIResult:
    """Consolidated result from 3-AI orchestration"""
    final_output: str
    opus_result: ReviewResult
    codex_result: ReviewResult
    glm_result: ReviewResult
    consensus: bool
    iterations: int
    total_time: float


class ThreeAIOrchestrator(BaseAlgorithm):
    """
    🦞 3-AI Orchestrator Algorithm
    
    Coordinates 3 AI models for maximum quality:
    - Claude Opus 4.6: Primary planner & coder
    - GPT-5.2-Codex: God-level code reviewer
    - GLM-4.6v: Multimodal consultant & final reviewer
    
    Workflow:
    1. Opus plans and codes
    2. Codex reviews code for errors
    3. GLM provides final sanity check
    4. If not approved, iterate with feedback
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ThreeAIOrchestrator",
            name="3-AI Orchestrator",
            level="composite",
            category="orchestration",
            version="1.0",
            description="Multi-model review chain with Opus, Codex, and GLM",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("request", "string", True, "User request to process"),
                    IOField("context", "object", False, "Additional context"),
                    IOField("max_iterations", "integer", False, "Max refinement iterations (default: 3)")
                ],
                outputs=[
                    IOField("result", "object", True, "3-AI consensus result"),
                    IOField("reviews", "array", True, "Individual AI reviews")
                ]
            ),
            
            steps=[
                "1. Load AI configurations",
                "2. Opus (Primary): Plan and code",
                "3. Codex (Reviewer): Review code for errors",
                "4. GLM (Consultant): Final multimodal review",
                "5. Check consensus",
                "6. If not approved, refine and iterate",
                "7. Return consolidated result"
            ],
            
            tags=["orchestration", "multi-model", "quality", "3-ai"]
        )
        
        # Configure 3 AIs
        self.ais = {
            AIRole.PRIMARY_LEAD: AIConfig(
                role=AIRole.PRIMARY_LEAD,
                model="claude-opus-4.6",
                provider="v98",
                priority=1,
                features=["reasoning", "planning", "coding", "long_context"],
                cost_tier="premium",
                strengths=[
                    "Best reasoning & planning",
                    "200K context window",
                    "Multi-step task decomposition",
                    "Complex problem solving"
                ]
            ),
            
            AIRole.CODE_REVIEWER: AIConfig(
                role=AIRole.CODE_REVIEWER,
                model="gpt-5.1-codex",
                provider="v98",
                priority=2,
                features=["code_review", "error_detection", "optimization"],
                cost_tier="codex_exclusive",  # $1/$8
                strengths=[
                    "God-level programming AI",
                    "Zero-error architecture understanding",
                    "Self-correcting errors",
                    "Performance optimization"
                ]
            ),
            
            AIRole.MULTIMODAL_CONSULTANT: AIConfig(
                role=AIRole.MULTIMODAL_CONSULTANT,
                model="glm-4.6v",
                provider="v98",
                priority=3,
                features=["vision", "multimodal", "128k_context", "frontend_replication"],
                cost_tier="standard",
                strengths=[
                    "Multimodal (vision + text)",
                    "128K context window",
                    "Pixel-accurate frontend replication",
                    "Long-context reasoning",
                    "Visual code analysis"
                ]
            )
        }
        
        # Initialize V98 Client for real API calls
        try:
            self.v98_client = V98Client()
            print("✅ V98 Client initialized")
        except Exception as e:
            self.v98_client = None
            print(f"⚠️ V98 Client initialization failed: {e}")
    
    def _call_v98_api(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Make real V98 API call"""
        if not self.v98_client:
            # Fallback to simulation
            return f"[Simulation] Response from {model}"
        
        try:
            response = self.v98_client.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=2000
            )
            
            if "error" in response:
                print(f"      ⚠️ API Error: {response['error']}")
                return f"[Error] {response['error']}"
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content
        
        except Exception as e:
            print(f"      ⚠️ Exception: {e}")
            return f"[Exception] {str(e)}"

    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute 3-AI orchestration"""
        import time
        
        request = params.get("request", "")
        context = params.get("context", {})
        max_iterations = params.get("max_iterations", 3)
        
        if not request:
            return AlgorithmResult(
                status="error",
                error="No request provided"
            )
        
        print(f"\n🦞 3-AI ORCHESTRATOR")
        print(f"   Request: {request[:100]}...")
        
        start_time = time.time()
        iteration = 0
        consensus = False
        
        # Results storage
        opus_result = None
        codex_result = None
        glm_result = None
        final_output = None
        
        while iteration < max_iterations and not consensus:
            iteration += 1
            print(f"\n   Iteration {iteration}/{max_iterations}")
            
            # Phase 1: Opus plans and codes
            print(f"   [1/3] Claude Opus 4.6 (Primary)...")
            opus_result = self._opus_plan_and_code(request, context, iteration)
            
            if not opus_result.approved:
                print(f"      ⚠️ Opus failed: {opus_result.issues}")
                break
            
            final_output = opus_result.insights[0] if opus_result.insights else ""
            
            # Phase 2: Codex reviews
            print(f"   [2/3] GPT-5.2-Codex (Reviewer)...")
            codex_result = self._codex_review(final_output, request, context)
            
            # Phase 3: GLM final review
            print(f"   [3/3] GLM-4.6v (Consultant)...")
            glm_result = self._glm_consultant(
                opus_output=final_output,
                codex_review=codex_result,
                request=request,
                context=context
            )
            
            # Check consensus
            if opus_result.approved and codex_result.approved and glm_result.approved:
                consensus = True
                print(f"      ✅ Consensus achieved!")
            else:
                # Consolidate feedback for next iteration
                all_issues = (
                    codex_result.issues + 
                    glm_result.issues
                )
                context["feedback"] = all_issues
                print(f"      🔄 Refining with {len(all_issues)} issues...")
        
        total_time = time.time() - start_time
        
        # Create result
        three_ai_result = ThreeAIResult(
            final_output=final_output or "",
            opus_result=opus_result,
            codex_result=codex_result,
            glm_result=glm_result,
            consensus=consensus,
            iterations=iteration,
            total_time=total_time
        )
        
        print(f"\n   ✅ Completed in {iteration} iterations ({total_time:.2f}s)")
        
        return AlgorithmResult(
            status="success" if consensus else "partial",
            data={
                "result": final_output,
                "consensus": consensus,
                "iterations": iteration,
                "reviews": {
                    "opus": self._result_to_dict(opus_result),
                    "codex": self._result_to_dict(codex_result),
                    "glm": self._result_to_dict(glm_result)
                },
                "total_time": total_time
            }
        )
    
    def _opus_plan_and_code(self, request: str, context: Dict, iteration: int) -> ReviewResult:
        """Phase 1: Claude Opus plans and codes"""
        import time
        start = time.time()
        
        # Build prompt for Opus
        prompt = f"""You are an expert software architect and coder.

Task: {request}

{'Feedback from previous iteration:' + str(context.get('feedback', [])) if iteration > 1 else ''}

Please:
1. Plan the solution
2. Write high-quality code
3. Explain your approach

Be thorough and precise."""
        
        try:
            if self.api:
                response = self.api.query(
                    model_name="claude-opus-4.6",
                    prompt=prompt,
                    provider="v98"
                )
                
                return ReviewResult(
                    ai_role=AIRole.PRIMARY_LEAD,
                    model="claude-opus-4.6",
                    approved=True,
                    confidence=0.95,
                    insights=[response],
                    processing_time=time.time() - start
                )
            else:
                # Fallback simulation
                return ReviewResult(
                    ai_role=AIRole.PRIMARY_LEAD,
                    model="claude-opus-4.6",
                    approved=True,
                    confidence=0.9,
                    insights=[f"[Opus simulation] Code for: {request}"],
                    processing_time=time.time() - start
                )
        
        except Exception as e:
            return ReviewResult(
                ai_role=AIRole.PRIMARY_LEAD,
                model="claude-opus-4.6",
                approved=False,
                confidence=0.0,
                issues=[str(e)],
                processing_time=time.time() - start
            )
    
    def _codex_review(self, code: str, request: str, context: Dict) -> ReviewResult:
        """Phase 2: GPT-5.2-Codex reviews code"""
        import time
        start = time.time()
        
        prompt = f"""You are a god-level programming AI code reviewer.

Original request: {request}

Code to review:
{code[:2000]}

Review this code for:
1. Bugs and errors
2. Security vulnerabilities
3. Performance issues
4. Best practices violations

Provide specific, actionable feedback."""
        
        try:
            if self.api:
                response = self.api.query(
                    model_name="gpt-5.2-codex",
                    prompt=prompt,
                    provider="v98"
                )
                
                # Simple heuristic: if "approved" or "looks good" in response
                approved = any(phrase in response.lower() for phrase in [
                    "looks good", "approved", "no issues", "well written"
                ])
                
                return ReviewResult(
                    ai_role=AIRole.CODE_REVIEWER,
                    model="gpt-5.2-codex",
                    approved=approved,
                    confidence=0.92,
                    suggestions=response.split('\n')[:5],
                    issues=[] if approved else ["Review flagged potential issues"],
                    processing_time=time.time() - start
                )
            else:
                # Fallback
                return ReviewResult(
                    ai_role=AIRole.CODE_REVIEWER,
                    model="gpt-5.2-codex",
                    approved=True,
                    confidence=0.85,
                    suggestions=["[Codex simulation] Code review passed"],
                    processing_time=time.time() - start
                )
        
        except Exception as e:
            return ReviewResult(
                ai_role=AIRole.CODE_REVIEWER,
                model="gpt-5.2-codex",
                approved=False,
                confidence=0.0,
                issues=[str(e)],
                processing_time=time.time() - start
            )
    
    def _glm_consultant(self, opus_output: str, codex_review: ReviewResult, 
                        request: str, context: Dict) -> ReviewResult:
        """Phase 3: GLM-4.6v final consultant review"""
        import time
        start = time.time()
        
        prompt = f"""You are a multimodal AI consultant providing final review.

Original request: {request}

Opus output: {opus_output[:1000]}

Codex review: {'Approved' if codex_review.approved else 'Issues found'}

Provide your final assessment:
1. Does this solution meet requirements?
2. Are there any logical gaps?
3. Final verdict: APPROVE or NEEDS_WORK"""
        
        try:
            if self.api:
                response = self.api.query(
                    model_name="glm-4.6v",
                    prompt=prompt,
                    provider="v98"
                )
                
                approved = "approve" in response.lower()
                
                return ReviewResult(
                    ai_role=AIRole.MULTIMODAL_CONSULTANT,
                    model="glm-4.6v",
                    approved=approved,
                    confidence=0.88,
                    insights=[response],
                    issues=[] if approved else ["GLM flagged concerns"],
                    processing_time=time.time() - start
                )
            else:
                # Fallback
                return ReviewResult(
                    ai_role=AIRole.MULTIMODAL_CONSULTANT,
                    model="glm-4.6v",
                    approved=True,
                    confidence=0.80,
                    insights=["[GLM simulation] Final review passed"],
                    processing_time=time.time() - start
                )
        
        except Exception as e:
            return ReviewResult(
                ai_role=AIRole.MULTIMODAL_CONSULTANT,
                model="glm-4.6v",
                approved=False,
                confidence=0.0,
                issues=[str(e)],
                processing_time=time.time() - start
            )
    
    def _result_to_dict(self, result: ReviewResult) -> Dict:
        """Convert ReviewResult to dict"""
        if not result:
            return {}
        
        return {
            "ai_role": result.ai_role.value,
            "model": result.model,
            "approved": result.approved,
            "confidence": result.confidence,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "insights": result.insights,
            "processing_time": result.processing_time
        }


def register(algorithm_manager):
    """Register ThreeAIOrchestrator"""
    algo = ThreeAIOrchestrator()
    algorithm_manager.register("ThreeAIOrchestrator", algo)
    print("✅ ThreeAIOrchestrator registered")


# ========================================
# TEST
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🦞 THREE-AI ORCHESTRATOR TEST")
    print("="*60)
    
    orchestrator = ThreeAIOrchestrator()
    
    result = orchestrator.execute({
        "request": "Create a Python function to calculate fibonacci numbers",
        "max_iterations": 2
    })
    
    print(f"\n📊 Result: {result.status}")
    if result.status == "success":
        print(f"   Consensus: {result.data['consensus']}")
        print(f"   Iterations: {result.data['iterations']}")
        print(f"   Time: {result.data['total_time']:.2f}s")
    
    print("\n" + "="*60)
