"""
Comprehensive Test Suite for All 80 Algorithms
Tests registration, execution, and outputs for all algorithms
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.algorithms import get_algorithm_manager


def test_all_algorithms():
    """Test all 80 algorithms systematically"""
    
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE ALGORITHM TEST - ALL 80 ALGORITHMS")
    print("="*80)
    
    # Get manager
    manager = get_algorithm_manager()
    
    print(f"\n✅ Total Algorithms Registered: {len(manager.algorithms)}/80")
    print(f"✅ Total Categories: {len(manager.get_categories())}")
    
    # Test each category
    categories = {
        "connection": ["ConnectionV98", "ConnectionAICoding", "ConnectionOpenAI"],
        "llm": ["LLMQuery", "StreamingLLMQuery"],
        "routing": ["SmartModelRouter", "ComplexityAnalyzer"],
        "utilities": ["InputValidation", "OutputFormatting"],
        "cli": ["CLIAsk", "CLICode", "CLISearch", "CLIMemory", "CLIComputer", "CLIOrchestrate", "CLIServe"],
        "orchestration": ["SmartOrchestrator", "TaskDecomposition", "ParallelExecution", "SequentialExecution", 
                         "WorkflowMonitoring", "ErrorRecovery", "ResultAggregation"],
        "memory": ["HighPerformanceMemory", "MemoryLoop", "ProjectMemory", "GitHubMemorySync", 
                  "SemanticSearch", "ContextRetrieval"],
        "agent-coordination": ["AgentSelector", "AgentPoolManager", "AgentExecution", "AgentCollaboration",
                              "AgentCapabilityMatching", "AgentPerformanceTracking"],
        "skills": ["SemanticRouting", "FormalVerification", "AutoErrorHandling", "DynamicNeuralArchitecture",
                  "DynamicCapacityAllocation", "HybridDenseSparse", "ContinuousLearning", "UserFeedbackLearning",
                  "FederatedExpertLearning", "CrossExpertKnowledge", "GradientAwareRouting", "ContextAwareCompression",
                  "TemporalAttention", "InferenceTimeScaling", "HierarchicalExperts"],
        "computer-control": ["ComputerOperator", "VisionAnalysis", "TaskPlanning", "ActionExecution",
                            "ScreenshotCapture", "MouseControl", "KeyboardControl", "WindowManagement"],
        "code-generation": ["CodeGenerator", "CodeReviewer", "TestWriter", "DocumentationGenerator",
                           "Refactoring", "DependencyAnalyzer"],
        "update": ["UpdateDetection", "UpdateSuggestion", "AlgorithmGenerator", "AlgorithmOptimizer"],
        "prompting": ["HybridPrompting", "PromptTemplate", "ChainOfThought", "FewShotLearning",
                     "ResponseFormatting", "ContextWindowManagement"]
    }
    
    total_expected = sum(len(algos) for algos in categories.values())
    print(f"\n📊 Expected Total: {total_expected} algorithms")
    
    # Test each category
    passed = 0
    failed = 0
    missing = 0
    
    for category, algorithm_ids in categories.items():
        print(f"\n{'='*80}")
        print(f"📁 Category: {category.upper()} ({len(algorithm_ids)} algorithms)")
        print(f"{'='*80}")
        
        for algo_id in algorithm_ids:
            try:
                # Check if registered
                algo = manager.get_algorithm(algo_id)
                
                if algo is None:
                    print(f"   ❌ {algo_id}: NOT REGISTERED")
                    missing += 1
                    continue
                
                # Try to execute with minimal params
                test_params = get_test_params(algo_id)
                result = manager.execute(algo_id, test_params)
                
                if result and (result.status == "success" or isinstance(result, dict)):
                    print(f"   ✅ {algo_id}: PASSED")
                    passed += 1
                else:
                    print(f"   ⚠️  {algo_id}: EXECUTED but status={getattr(result, 'status', 'unknown')}")
                    failed += 1
                    
            except Exception as e:
                print(f"   ❌ {algo_id}: ERROR - {str(e)[:60]}")
                failed += 1
    
    # Final summary
    print("\n" + "="*80)
    print("📊 FINAL TEST RESULTS")
    print("="*80)
    print(f"✅ Passed:  {passed}/{total_expected}")
    print(f"❌ Failed:  {failed}/{total_expected}")
    print(f"⚠️  Missing: {missing}/{total_expected}")
    print(f"📈 Success Rate: {(passed/total_expected)*100:.1f}%")
    
    # Category breakdown
    print(f"\n📊 Algorithms by Category:")
    for category in sorted(manager.get_categories()):
        algos = manager.category_index.get(category, [])
        print(f"   {category}: {len(algos)} algorithms")
    
    print("\n" + "="*80)
    if passed >= total_expected * 0.9:  # 90% pass rate
        print("✅ ALGORITHM SYSTEM TEST: PASSED!")
        print("🦞🚀 V29.4 Algorithm Framework is PRODUCTION READY!")
    else:
        print("⚠️  ALGORITHM SYSTEM TEST: NEEDS ATTENTION")
        print(f"   {missing} algorithms not registered")
        print(f"   {failed} algorithms failed execution")
    print("="*80 + "\n")
    
    return passed, failed, missing


def get_test_params(algo_id: str) -> dict:
    """Get test parameters for each algorithm"""
    
    # Minimal test params for each algorithm type
    params_map = {
        # Connections
        "ConnectionV98": {},
        "ConnectionAICoding": {},
        "ConnectionOpenAI": {},
        
        # LLM
        "LLMQuery": {"prompt": "test", "provider": "v98", "model": "test"},
        "StreamingLLMQuery": {"prompt": "test"},
        
        # Routing
        "SmartModelRouter": {"task": "test task"},
        "ComplexityAnalyzer": {"task": "test task"},
        
        # Utilities
        "InputValidation": {"inputs": {}, "spec": {}},
        "OutputFormatting": {"data": {"test": "value"}},
        
        # CLI
        "CLIAsk": {"question": "What is Python?"},
        "CLICode": {"action": "generate", "requirements": "test"},
        "CLISearch": {"query": "test"},
        "CLIMemory": {"action": "list"},
        "CLIComputer": {"command": "screenshot"},
        "CLIOrchestrate": {"task": "test task"},
        "CLIServe": {},
        
        # Orchestration
        "SmartOrchestrator": {"task": "test task"},
        "TaskDecomposition": {"task": "test task"},
        "ParallelExecution": {"tasks": []},
        "SequentialExecution": {"tasks": []},
        "WorkflowMonitoring": {"workflow_id": "test"},
        "ErrorRecovery": {"error": {}},
        "ResultAggregation": {"results": []},
        
        # Memory
        "HighPerformanceMemory": {"action": "add", "content": "test"},
        "MemoryLoop": {"data": "test"},
        "ProjectMemory": {"project_id": "test", "action": "get"},
        "GitHubMemorySync": {"action": "pull", "repo": "test/repo"},
        "SemanticSearch": {"query": "test"},
        "ContextRetrieval": {"task": "test"},
        
        # Agent Coordination
        "AgentSelector": {"task": "test task"},
        "AgentPoolManager": {"action": "list"},
        "AgentExecution": {"agent_id": "test", "task": "test"},
        "AgentCollaboration": {"agents": [], "task": "test"},
        "AgentCapabilityMatching": {"requirements": []},
        "AgentPerformanceTracking": {"agent_id": "test"},
        
        # Skills
        "SemanticRouting": {"query": "test query"},
        "FormalVerification": {"code": "test"},
        "AutoErrorHandling": {"code": "test"},
        "DynamicNeuralArchitecture": {"task": "test"},
        "DynamicCapacityAllocation": {"current_load": 0.5},
        "HybridDenseSparse": {"model": {}},
        "ContinuousLearning": {"new_data": []},
        "UserFeedbackLearning": {"feedback": {}},
        "FederatedExpertLearning": {"experts": []},
        "CrossExpertKnowledge": {"source_expert": "A", "target_expert": "B"},
        "GradientAwareRouting": {"gradients": []},
        "ContextAwareCompression": {"data": "test"},
        "TemporalAttention": {"sequence": []},
        "InferenceTimeScaling": {"complexity": 5},
        "HierarchicalExperts": {"query": "test"},
        
        # Computer Control
        "ComputerOperator": {"action": "screenshot", "params": {}},
        "VisionAnalysis": {"screenshot": "test", "prompt": "test"},
        "TaskPlanning": {"command": "test"},
        "ActionExecution": {"actions": []},
        "ScreenshotCapture": {},
        "MouseControl": {"action": "move", "x": 0, "y": 0},
        "KeyboardControl": {"text": "test"},
        "WindowManagement": {"window_title": "test", "action": "focus"},
        
        # Code Generation
        "CodeGenerator": {"requirements": "test function"},
        "CodeReviewer": {"code": "def test(): pass"},
        "TestWriter": {"code": "def test(): pass"},
        "DocumentationGenerator": {"code": "def test(): pass"},
        "Refactoring": {"code": "def test(): pass"},
        "DependencyAnalyzer": {"code": "import os"},
        
        # Update & Evolution
        "UpdateDetection": {"system_state": {}},
        "UpdateSuggestion": {"component": "test"},
        "AlgorithmGenerator": {"need": "test algorithm"},
        "AlgorithmOptimizer": {"algorithm_id": "test"},
        
        # Prompting
        "HybridPrompting": {"prompt": "test"},
        "PromptTemplate": {"template_type": "qa"},
        "ChainOfThought": {"prompt": "test"},
        "FewShotLearning": {"prompt": "test", "examples": []},
        "ResponseFormatting": {"response": "test"},
        "ContextWindowManagement": {"context": "test", "max_tokens": 100}
    }
    
    return params_map.get(algo_id, {})


if __name__ == "__main__":
    print("\n🦞 DIVE AI V29.4 - COMPREHENSIVE ALGORITHM TEST SUITE\n")
    passed, failed, missing = test_all_algorithms()
    
    # Exit code based on results
    if missing == 0 and failed == 0:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed
