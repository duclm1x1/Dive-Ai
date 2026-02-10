"""
V98 Algorithm Wrapper - Uses ConnectionV98Algorithm pattern

Wraps the V98 connection with algorithm-based execution flow,
supporting all 5 Claude models with proper step tracking.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .connections import (
    V98Client, V98ConnectionManager, get_manager,
    ALL_MODELS, CLAUDE_OPUS_46_THINKING, CLAUDE_SONNET_45,
    V98Model, LLMResponse
)


@dataclass
class AlgorithmStep:
    """Single execution step"""
    id: str
    title: str
    status: str = "pending"  # pending, running, success, failed
    start_time: float = 0
    end_time: float = 0
    result: Any = None
    error: str = None


@dataclass
class AlgorithmResult:
    """Result from algorithm execution"""
    status: str  # success, failure
    data: Dict[str, Any] = field(default_factory=dict)
    steps: List[AlgorithmStep] = field(default_factory=list)
    total_time_ms: float = 0
    tokens_used: int = 0
    model_used: str = None


class V98Algorithm:
    """
    V98 Algorithm with step-based execution
    
    Follows the ConnectionV98Algorithm pattern with:
    - Step tracking
    - Automatic model selection
    - Fallback on failure
    - Token tracking
    """
    
    def __init__(self, name: str = "V98Algorithm"):
        self.name = name
        self.manager = get_manager()
        self.steps: List[AlgorithmStep] = []
        self.current_step: AlgorithmStep = None
    
    def _start_step(self, step_id: str, title: str) -> AlgorithmStep:
        """Start a new step"""
        step = AlgorithmStep(
            id=step_id,
            title=title,
            status="running",
            start_time=time.time()
        )
        self.steps.append(step)
        self.current_step = step
        return step
    
    def _end_step(self, success: bool, result: Any = None, error: str = None):
        """End current step"""
        if self.current_step:
            self.current_step.end_time = time.time()
            self.current_step.status = "success" if success else "failed"
            self.current_step.result = result
            self.current_step.error = error
    
    def execute(self, 
                prompt: str,
                system: str = None,
                model: V98Model = None,
                max_tokens: int = 4096) -> AlgorithmResult:
        """
        Execute algorithm with prompt
        
        Steps:
        1. Initialize - Validate inputs
        2. Select Model - Choose best model
        3. Call API - Send to V98
        4. Parse Response - Extract content
        5. Finalize - Return result
        """
        start_time = time.time()
        total_tokens = 0
        model_used = None
        
        try:
            # Step 1: Initialize
            self._start_step("init", "Initialize")
            if not prompt:
                self._end_step(False, error="Empty prompt")
                return AlgorithmResult(
                    status="failure",
                    data={"error": "Empty prompt"},
                    steps=self.steps
                )
            self._end_step(True)
            
            # Step 2: Select Model
            self._start_step("select_model", "Select Model")
            selected_model = model or CLAUDE_OPUS_46_THINKING
            model_used = selected_model.name
            self._end_step(True, result=selected_model.model)
            
            # Step 3: Call API
            self._start_step("call_api", f"Call V98 ({selected_model.name})")
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = self.manager.client.chat(
                messages, 
                model=selected_model,
                max_tokens=max_tokens
            )
            
            if not response.success:
                # Try fallback
                self._end_step(False, error=response.error)
                
                self._start_step("fallback", "Fallback to other model")
                response = self.manager.client.chat_with_fallback(
                    messages,
                    max_tokens=max_tokens
                )
                
                if not response.success:
                    self._end_step(False, error=response.error)
                    return AlgorithmResult(
                        status="failure",
                        data={"error": response.error},
                        steps=self.steps
                    )
                
                model_used = response.model
                self._end_step(True)
            else:
                self._end_step(True)
            
            total_tokens = response.tokens_used
            
            # Step 4: Parse Response
            self._start_step("parse", "Parse Response")
            content = response.content
            self._end_step(True, result=f"{len(content)} chars")
            
            # Step 5: Finalize
            self._start_step("finalize", "Finalize")
            total_time = (time.time() - start_time) * 1000
            self._end_step(True)
            
            return AlgorithmResult(
                status="success",
                data={
                    "content": content,
                    "thinking": response.thinking,
                    "latency_ms": response.latency_ms
                },
                steps=self.steps,
                total_time_ms=total_time,
                tokens_used=total_tokens,
                model_used=model_used
            )
            
        except Exception as e:
            self._end_step(False, error=str(e))
            return AlgorithmResult(
                status="failure",
                data={"error": str(e)},
                steps=self.steps
            )


class CodeGeneratorAlgorithm(V98Algorithm):
    """Specialized algorithm for code generation"""
    
    def __init__(self):
        super().__init__("CodeGenerator")
    
    def generate(self,
                 task: str,
                 language: str = "python",
                 context: str = None) -> AlgorithmResult:
        """Generate code for a task"""
        
        system = f"""You are an expert {language} developer. 
Generate production-ready code only.
Include proper error handling and documentation.
Do not include explanations outside of code comments."""
        
        prompt = task
        if context:
            prompt = f"Context:\n{context}\n\nTask:\n{task}"
        
        return self.execute(
            prompt=prompt,
            system=system,
            model=CLAUDE_OPUS_46_THINKING,
            max_tokens=8192
        )


class ReviewAlgorithm(V98Algorithm):
    """Specialized algorithm for code review"""
    
    def __init__(self):
        super().__init__("CodeReview")
    
    def review(self, code: str, language: str = "python") -> AlgorithmResult:
        """Review code and suggest improvements"""
        
        system = """You are a senior code reviewer.
Analyze the code for:
1. Bugs and potential issues
2. Performance problems
3. Security vulnerabilities
4. Code style improvements
5. Best practices violations

Provide specific, actionable feedback."""
        
        prompt = f"Review this {language} code:\n\n```{language}\n{code}\n```"
        
        return self.execute(
            prompt=prompt,
            system=system,
            model=CLAUDE_SONNET_45,  # Faster for reviews
            max_tokens=4096
        )


# Quick access functions
def generate_code(task: str, language: str = "python") -> str:
    """Quick code generation"""
    algo = CodeGeneratorAlgorithm()
    result = algo.generate(task, language)
    return result.data.get("content", "") if result.status == "success" else ""


def review_code(code: str, language: str = "python") -> str:
    """Quick code review"""
    algo = ReviewAlgorithm()
    result = algo.review(code, language)
    return result.data.get("content", "") if result.status == "success" else ""
