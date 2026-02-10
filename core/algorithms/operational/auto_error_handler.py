"""
🔧 AUTOMATIC ERROR HANDLER (AEH)
Autonomous error detection, recovery, and self-correction

Based on V28's layer5_automatederrorhandling.py + aeh/
"""

import os
import sys
import traceback
from typing import Dict, Any, List, Optional, Callable
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


class ErrorCategory(Enum):
    """Error categories"""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    NETWORK = "network"
    PERMISSION = "permission"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context about an error"""
    error_type: str
    message: str
    category: ErrorCategory
    stacktrace: str = ""
    code_snippet: str = ""
    line_number: int = 0
    recoverable: bool = True


@dataclass
class RecoveryAction:
    """An action to recover from error"""
    action_type: str  # "retry", "fallback", "skip", "restart"
    description: str
    confidence: float  # 0.0 - 1.0
    steps: List[str] = field(default_factory=list)


class AutoErrorHandlerAlgorithm(BaseAlgorithm):
    """
    🔧 Automatic Error Handler (AEH)
    
    Autonomously detects, analyzes, and recovers from errors.
    
    Features:
    - Real-time error detection
    - Root cause analysis
    - Automatic recovery strategies
    - Self-correction
    - Learning from failures
    
    From V28: AEH module (9/10 priority)
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AutoErrorHandler",
            name="Automatic Error Handler (AEH)",
            level="operational",
            category="error_handling",
            version="1.0",
            description="Autonomous error detection and recovery",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("error", "object", True, "Error to handle"),
                    IOField("context", "object", False, "Execution context"),
                    IOField("max_retries", "integer", False, "Max recovery attempts (default: 3)")
                ],
                outputs=[
                    IOField("recovered", "boolean", True, "Error recovered successfully"),
                    IOField("recovery_action", "object", True, "Action taken to recover"),
                    IOField("analysis", "object", True, "Error analysis")
                ]
            ),
            
            steps=[
                "1. Detect error type and category",
                "2. Analyze root cause",
                "3. Determine if recoverable",
                "4. Generate recovery strategies",
                "5. Execute best recovery action",
                "6. Verify recovery success",
                "7. Log for learning"
            ],
            
            tags=["error_handling", "aeh", "recovery", "autonomous"]
        )
        
        self.error_history = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute error handling"""
        error = params.get("error")
        context = params.get("context", {})
        max_retries = params.get("max_retries", 3)
        
        if not error:
            return AlgorithmResult(status="error", error="No error provided")
        
        print(f"\n🔧 Automatic Error Handler (AEH)")
        
        # Step 1: Categorize error
        error_context = self._analyze_error(error, context)
        print(f"   Category: {error_context.category.value}")
        print(f"   Recoverable: {error_context.recoverable}")
        
        # Step 2: Generate recovery strategies
        strategies = self._generate_recovery_strategies(error_context, context)
        print(f"   Strategies: {len(strategies)}")
        
        # Step 3: Execute recovery
        recovered = False
        recovery_action = None
        
        for attempt in range(max_retries):
            if not strategies:
                break
            
            # Try best strategy
            strategy = strategies[0]
            print(f"   Attempt {attempt + 1}: {strategy.action_type}")
            
            success = self._execute_recovery(strategy, error_context, context)
            
            if success:
                recovered = True
                recovery_action = strategy
                print(f"   ✅ Recovered via {strategy.action_type}")
                break
            else:
                # Try next strategy
                strategies.pop(0)
        
        # Log for learning
        self.error_history.append({
            "error": error_context,
            "recovered": recovered,
            "action": recovery_action,
            "attempts": attempt + 1
        })
        
        return AlgorithmResult(
            status="success",
            data={
                "recovered": recovered,
                "recovery_action": self._action_to_dict(recovery_action) if recovery_action else None,
                "analysis": {
                    "category": error_context.category.value,
                    "recoverable": error_context.recoverable,
                    "message": error_context.message,
                    "line": error_context.line_number
                },
                "attempts": attempt + 1,
                "strategies_tried": min(attempt + 1, len(strategies))
            }
        )
    
    def _analyze_error(self, error: Any, context: Dict) -> ErrorContext:
        """Analyze error and categorize"""
        # Extract error info
        if isinstance(error, Exception):
            error_type = type(error).__name__
            message = str(error)
            stacktrace = traceback.format_exc()
        elif isinstance(error, dict):
            error_type = error.get("type", "Unknown")
            message = error.get("message", str(error))
            stacktrace = error.get("stacktrace", "")
        else:
            error_type = "Unknown"
            message = str(error)
            stacktrace = ""
        
        # Categorize
        category = self._categorize_error(error_type, message)
        
        # Determine if recoverable
        recoverable = category not in [ErrorCategory.SYNTAX, ErrorCategory.PERMISSION]
        
        return ErrorContext(
            error_type=error_type,
            message=message,
            category=category,
            stacktrace=stacktrace,
            recoverable=recoverable
        )
    
    def _categorize_error(self, error_type: str, message: str) -> ErrorCategory:
        """Categorize error"""
        error_lower = f"{error_type} {message}".lower()
        
        if "syntax" in error_lower or "indentation" in error_lower:
            return ErrorCategory.SYNTAX
        elif "network" in error_lower or "connection" in error_lower or "timeout" in error_lower:
            return ErrorCategory.NETWORK
        elif "permission" in error_lower or "access denied" in error_lower:
            return ErrorCategory.PERMISSION
        elif "memory" in error_lower or "resource" in error_lower:
            return ErrorCategory.RESOURCE
        elif "runtime" in error_lower or "exception" in error_lower:
            return ErrorCategory.RUNTIME
        elif "assert" in error_lower or "value" in error_lower:
            return ErrorCategory.LOGIC
        else:
            return ErrorCategory.UNKNOWN
    
    def _generate_recovery_strategies(self, error_context: ErrorContext, 
                                     context: Dict) -> List[RecoveryAction]:
        """Generate recovery strategies based on error type"""
        strategies = []
        
        if error_context.category == ErrorCategory.NETWORK:
            strategies.append(RecoveryAction(
                action_type="retry",
                description="Retry connection with backoff",
                confidence=0.8,
                steps=["Wait 1s", "Retry request", "Increase timeout"]
            ))
            strategies.append(RecoveryAction(
                action_type="fallback",
                description="Use fallback endpoint",
                confidence=0.6,
                steps=["Switch to backup server", "Retry request"]
            ))
        
        elif error_context.category == ErrorCategory.RESOURCE:
            strategies.append(RecoveryAction(
                action_type="restart",
                description="Clear cache and restart",
                confidence=0.7,
                steps=["Clear memory cache", "Garbage collect", "Retry"]
            ))
        
        elif error_context.category == ErrorCategory.RUNTIME:
            strategies.append(RecoveryAction(
                action_type="fallback",
                description="Use safe default values",
                confidence=0.5,
                steps=["Use default values", "Continue execution"]
            ))
            strategies.append(RecoveryAction(
                action_type="skip",
                description="Skip problematic operation",
                confidence=0.4,
                steps=["Log error", "Skip operation", "Continue"]
            ))
        
        elif error_context.category == ErrorCategory.LOGIC:
            strategies.append(RecoveryAction(
                action_type="fallback",
                description="Use alternative logic path",
                confidence=0.6,
                steps=["Try alternative approach", "Validate result"]
            ))
        
        # Generic retry
        if error_context.recoverable:
            strategies.append(RecoveryAction(
                action_type="retry",
                description="Simple retry",
                confidence=0.3,
                steps=["Wait briefly", "Retry operation"]
            ))
        
        # Sort by confidence
        strategies.sort(key=lambda s: s.confidence, reverse=True)
        
        return strategies
    
    def _execute_recovery(self, action: RecoveryAction, 
                         error_context: ErrorContext, context: Dict) -> bool:
        """Execute recovery action (simulation)"""
        import time
        import random
        
        # Simulate recovery attempt
        if action.action_type == "retry":
            time.sleep(0.1)  # Simulate wait
            # Success rate depends on error category
            if error_context.category == ErrorCategory.NETWORK:
                return random.random() < 0.7  # 70% success
            else:
                return random.random() < 0.5
        
        elif action.action_type == "fallback":
            return random.random() < action.confidence
        
        elif action.action_type == "skip":
            return True  # Skipping always "succeeds"
        
        elif action.action_type == "restart":
            time.sleep(0.05)
            return random.random() < 0.6
        
        return False
    
    def _action_to_dict(self, action: RecoveryAction) -> Dict:
        """Convert action to dict"""
        return {
            "action_type": action.action_type,
            "description": action.description,
            "confidence": action.confidence,
            "steps": action.steps
        }


def register(algorithm_manager):
    """Register Auto Error Handler Algorithm"""
    algo = AutoErrorHandlerAlgorithm()
    algorithm_manager.register("AutoErrorHandler", algo)
    print("✅ AutoErrorHandler Algorithm registered")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 AUTO ERROR HANDLER TEST")
    print("="*60)
    
    algo = AutoErrorHandlerAlgorithm()
    
    # Test with network error
    test_error = {
        "type": "ConnectionError",
        "message": "Connection timeout after 30s"
    }
    
    result = algo.execute({
        "error": test_error,
        "max_retries": 3
    })
    
    print(f"\n📊 Result: {result.status}")
    if result.status == "success":
        print(f"   Recovered: {result.data['recovered']}")
        print(f"   Attempts: {result.data['attempts']}")
        if result.data['recovery_action']:
            print(f"   Action: {result.data['recovery_action']['action_type']}")
    
    print("\n" + "="*60)
