"""
Dive AI V29 - Evaluation Package

Components:
- GPA Scorer: Goal-Plan-Action scoring for individual actions
- Workflow Scorer: Process KPIs for workflow-level evaluation
- Feedback Synthesizer: Combines tactical and strategic feedback
"""

from .gpa_scorer import (
    GPAScorerAlgorithm,
    GPAScore,
    FeedbackSynthesizer,
    EvaluationResult,
    DimensionScore,
    EvaluationDimension,
    ScoreLevel
)

from .workflow_scorer import (
    WorkflowScorer,
    ProcessKPIs,
    WorkflowExecution,
    get_workflow_scorer
)

__all__ = [
    # GPA Scorer
    'GPAScorerAlgorithm',
    'GPAScore',
    'FeedbackSynthesizer',
    'EvaluationResult',
    'DimensionScore',
    'EvaluationDimension',
    'ScoreLevel',
    # Workflow Scorer
    'WorkflowScorer',
    'ProcessKPIs',
    'WorkflowExecution',
    'get_workflow_scorer',
]
