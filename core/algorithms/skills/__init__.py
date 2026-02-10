"""
Skills Package - Import and register all V27.2 advanced skills
FIXED: Now properly registers all 15 skill algorithms
"""

# Import all skill algorithm classes
from .semantic_routing import SemanticRoutingAlgorithm
from .skills_batch import (
    FormalVerificationAlgorithm,
    AutoErrorHandlingAlgorithm,
    DynamicNeuralArchitectureAlgorithm,
    DynamicCapacityAllocationAlgorithm,
    HybridDenseSparseAlgorithm,
    ContinuousLearningAlgorithm,
    UserFeedbackLearningAlgorithm,
    FederatedExpertLearningAlgorithm,
    CrossExpertKnowledgeAlgorithm,
    GradientAwareRoutingAlgorithm,
    ContextAwareCompressionAlgorithm,
    TemporalAttentionAlgorithm,
    InferenceTimeScalingAlgorithm,
    HierarchicalExpertsAlgorithm
)

# Export all classes
__all__ = [
    'SemanticRoutingAlgorithm',
    'FormalVerificationAlgorithm',
    'AutoErrorHandlingAlgorithm',
    'DynamicNeuralArchitectureAlgorithm',
    'DynamicCapacityAllocationAlgorithm',
    'HybridDenseSparseAlgorithm',
    'ContinuousLearningAlgorithm',
    'UserFeedbackLearningAlgorithm',
    'FederatedExpertLearningAlgorithm',
    'CrossExpertKnowledgeAlgorithm',
    'GradientAwareRoutingAlgorithm',
    'ContextAwareCompressionAlgorithm',
    'TemporalAttentionAlgorithm',
    'InferenceTimeScalingAlgorithm',
    'HierarchicalExpertsAlgorithm'
]


def register_all_skills(algorithm_manager):
    """Register all 15 skill algorithms"""
    
    skill_classes = [
        SemanticRoutingAlgorithm,
        FormalVerificationAlgorithm,
        AutoErrorHandlingAlgorithm,
        DynamicNeuralArchitectureAlgorithm,
        DynamicCapacityAllocationAlgorithm,
        HybridDenseSparseAlgorithm,
        ContinuousLearningAlgorithm,
        UserFeedbackLearningAlgorithm,
        FederatedExpertLearningAlgorithm,
        CrossExpertKnowledgeAlgorithm,
        GradientAwareRoutingAlgorithm,
        ContextAwareCompressionAlgorithm,
        TemporalAttentionAlgorithm,
        InferenceTimeScalingAlgorithm,
        HierarchicalExpertsAlgorithm
    ]
    
    for skill_class in skill_classes:
        try:
            algo = skill_class()
            algorithm_manager.register(algo.spec.algorithm_id, algo)
            print(f"✅ {algo.spec.algorithm_id} Algorithm registered")
        except Exception as e:
            print(f"❌ Failed to register {skill_class.__name__}: {e}")


# Auto-register when imported by algorithm manager
def register(algorithm_manager):
    """Called by algorithm manager auto-discovery"""
    register_all_skills(algorithm_manager)
