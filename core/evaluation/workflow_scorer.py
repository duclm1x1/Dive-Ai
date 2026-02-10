"""
Dive AI V29 - Workflow Scorer
Process KPIs for Workflow-Level Evaluation

Part of Metacognition Layer for strategic learning

Process KPIs:
- Lead Time: Total execution time
- Wasted Action Ratio: Failed actions / total actions
- Path Complexity: How many decision branches taken
- Final Success Rate: Overall success of workflow
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProcessKPIs:
    """Process KPIs for workflow evaluation"""
    lead_time: float  # Total time in seconds
    wasted_action_ratio: float  # 0-1
    path_complexity: float  # Number of branches
    final_success_rate: float  # 0-1
    overall_score: float  # Weighted average
    
    @staticmethod
    def calculate(
        lead_time: float,
        total_actions: int,
        failed_actions: int,
        branch_count: int,
        successful: bool
    ) -> 'ProcessKPIs':
        """Calculate KPIs from raw metrics"""
        # Wasted action ratio
        wasted_ratio = failed_actions / max(total_actions, 1)
        
        # Normalize lead time (lower is better, max 10 mins = 600s)
        lead_time_score = 1.0 - min(lead_time / 600, 1.0)
        
        # Path complexity (fewer branches is simpler, max 10)
        complexity = min(branch_count / 10, 1.0)
        complexity_score = 1.0 - complexity
        
        # Success rate
        success_score = 1.0 if successful else 0.0
        
        # Overall score
        overall = (
            lead_time_score * 0.2 +
            (1.0 - wasted_ratio) * 0.3 +
            complexity_score * 0.1 +
            success_score * 0.4
        )
        
        return ProcessKPIs(
            lead_time=lead_time,
            wasted_action_ratio=wasted_ratio,
            path_complexity=branch_count,
            final_success_rate=success_score,
            overall_score=overall
        )


@dataclass
class WorkflowExecution:
    """Record of a workflow execution"""
    execution_id: str
    meta_algorithm_id: str
    initial_request: str
    actions: List[Dict[str, Any]]
    start_time: float
    end_time: float = 0
    kpis: Optional[ProcessKPIs] = None
    
    def add_action(self, action: Dict[str, Any]):
        """Add action to execution"""
        self.actions.append({
            **action,
            "timestamp": datetime.now().isoformat()
        })
    
    def complete(self, success: bool = True):
        """Complete execution and calculate KPIs"""
        self.end_time = time.time()
        
        lead_time = self.end_time - self.start_time
        total_actions = len(self.actions)
        failed_actions = sum(1 for a in self.actions if not a.get("success", True))
        branch_count = sum(1 for a in self.actions if a.get("is_branch", False))
        
        self.kpis = ProcessKPIs.calculate(
            lead_time=lead_time,
            total_actions=total_actions,
            failed_actions=failed_actions,
            branch_count=branch_count,
            successful=success
        )
        
        return self.kpis


class WorkflowScorer:
    """
    📊 Workflow Scorer
    
    Evaluates entire workflows using Process KPIs:
    - Tracks all actions in workflow
    - Calculates efficiency metrics
    - Generates strategic feedback for Cognitive Layer
    """
    
    def __init__(self):
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.history: List[WorkflowExecution] = []
    
    def start_execution(
        self,
        execution_id: str,
        meta_algorithm_id: str,
        initial_request: str
    ) -> WorkflowExecution:
        """Start tracking a workflow execution"""
        execution = WorkflowExecution(
            execution_id=execution_id,
            meta_algorithm_id=meta_algorithm_id,
            initial_request=initial_request,
            actions=[],
            start_time=time.time()
        )
        
        self.active_executions[execution_id] = execution
        return execution
    
    def log_action(
        self,
        execution_id: str,
        action_name: str,
        success: bool = True,
        is_branch: bool = False,
        details: Dict = None
    ):
        """Log an action in the workflow"""
        if execution_id not in self.active_executions:
            return
        
        self.active_executions[execution_id].add_action({
            "action": action_name,
            "success": success,
            "is_branch": is_branch,
            "details": details or {}
        })
    
    def complete_execution(
        self,
        execution_id: str,
        success: bool = True
    ) -> Optional[ProcessKPIs]:
        """Complete a workflow execution and get KPIs"""
        if execution_id not in self.active_executions:
            return None
        
        execution = self.active_executions.pop(execution_id)
        kpis = execution.complete(success)
        
        self.history.append(execution)
        
        return kpis
    
    def get_meta_algorithm_stats(self, meta_algorithm_id: str) -> Dict[str, Any]:
        """Get statistics for a meta-algorithm"""
        relevant = [e for e in self.history if e.meta_algorithm_id == meta_algorithm_id]
        
        if not relevant:
            return {"executions": 0}
        
        avg_lead_time = sum(e.kpis.lead_time for e in relevant if e.kpis) / len(relevant)
        avg_wasted = sum(e.kpis.wasted_action_ratio for e in relevant if e.kpis) / len(relevant)
        avg_score = sum(e.kpis.overall_score for e in relevant if e.kpis) / len(relevant)
        success_count = sum(1 for e in relevant if e.kpis and e.kpis.final_success_rate > 0)
        
        return {
            "executions": len(relevant),
            "avg_lead_time": avg_lead_time,
            "avg_wasted_ratio": avg_wasted,
            "avg_score": avg_score,
            "success_rate": success_count / len(relevant)
        }
    
    def generate_strategic_feedback(self, kpis: ProcessKPIs) -> Dict[str, Any]:
        """Generate strategic feedback for Cognitive Layer"""
        feedback = {
            "target": "Cognitive Layer",
            "kpis": {
                "lead_time": kpis.lead_time,
                "wasted_ratio": kpis.wasted_action_ratio,
                "complexity": kpis.path_complexity,
                "success": kpis.final_success_rate,
                "overall": kpis.overall_score
            },
            "recommendations": []
        }
        
        # Analyze KPIs and generate recommendations
        if kpis.wasted_action_ratio > 0.3:
            feedback["recommendations"].append(
                "HIGH wasted actions. Review algorithm selection for this task type."
            )
        
        if kpis.lead_time > 300:  # 5 minutes
            feedback["recommendations"].append(
                "SLOW execution. Consider breaking into smaller workflows."
            )
        
        if kpis.path_complexity > 5:
            feedback["recommendations"].append(
                "COMPLEX path. Simplify decision tree in Meta-Algorithm."
            )
        
        if kpis.final_success_rate < 1.0:
            feedback["recommendations"].append(
                "FAILED workflow. Log pattern for future avoidance."
            )
        
        if kpis.overall_score >= 0.8:
            feedback["recommendations"].append(
                "EXCELLENT execution. Save pattern for reuse."
            )
        
        # Overall assessment
        if kpis.overall_score >= 0.8:
            feedback["assessment"] = "Meta-Algorithm effective. Consider as template."
        elif kpis.overall_score >= 0.6:
            feedback["assessment"] = "Meta-Algorithm adequate. Minor refinements suggested."
        elif kpis.overall_score >= 0.4:
            feedback["assessment"] = "Meta-Algorithm underperforming. Review workflow design."
        else:
            feedback["assessment"] = "Meta-Algorithm failed. Select alternative approach."
        
        return feedback


# Singleton
_workflow_scorer = None

def get_workflow_scorer() -> WorkflowScorer:
    """Get workflow scorer singleton"""
    global _workflow_scorer
    if _workflow_scorer is None:
        _workflow_scorer = WorkflowScorer()
    return _workflow_scorer


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📊 WORKFLOW SCORER TEST")
    print("=" * 60)
    
    scorer = get_workflow_scorer()
    
    # Simulate a workflow
    print("\n📝 Starting workflow execution...")
    scorer.start_execution("test-001", "DevelopWebApp", "Build a calculator app")
    
    # Log actions
    scorer.log_action("test-001", "analyze_request", success=True)
    scorer.log_action("test-001", "select_algorithm", success=True)
    time.sleep(0.1)
    scorer.log_action("test-001", "generate_code", success=True)
    scorer.log_action("test-001", "test_code", success=False, is_branch=True)  # Failed, branched
    scorer.log_action("test-001", "fix_code", success=True)
    scorer.log_action("test-001", "test_code_retry", success=True)
    
    # Complete
    kpis = scorer.complete_execution("test-001", success=True)
    
    print(f"\n📊 Process KPIs:")
    print(f"   Lead Time: {kpis.lead_time:.2f}s")
    print(f"   Wasted Ratio: {kpis.wasted_action_ratio:.0%}")
    print(f"   Path Complexity: {kpis.path_complexity}")
    print(f"   Success: {kpis.final_success_rate:.0%}")
    print(f"   Overall Score: {kpis.overall_score:.2f}")
    
    # Get feedback
    print("\n💡 Strategic Feedback:")
    feedback = scorer.generate_strategic_feedback(kpis)
    print(f"   Assessment: {feedback['assessment']}")
    for rec in feedback['recommendations']:
        print(f"   → {rec}")
    
    # Stats
    print("\n📈 Meta-Algorithm Stats:")
    stats = scorer.get_meta_algorithm_stats("DevelopWebApp")
    print(f"   Executions: {stats['executions']}")
    print(f"   Avg Score: {stats['avg_score']:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ Workflow Scorer test completed!")
