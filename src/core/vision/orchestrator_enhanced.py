"""
Dive Orchestrator v16 - Enhanced with All 12 Features

Integrated Features:
- YAML Workflow Definition (Orchestrator)
- Task History Tracking (Orchestrator)
- Task Type Recommendation (Orchestrator)
- Model Checker & Selection (Orchestrator)
- Model Ranking (Orchestrator)
- Model Version Tracking (Orchestrator)
- Auto-Update System (Orchestrator)
- Task Analysis (Agents)
- GitHub/Reddit Insights (Agents)
- Fallback Model Support (Agents)
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.features.advanced_features import (
    AdvancedFeaturesManager,
    WorkflowManager,
    TaskHistoryTracker,
    TaskAnalyzer,
    TaskTypeRecommender,
    ModelChecker,
    ModelSelector,
    ModelRanker,
    InsightCollector,
    VersionTracker,
    AutoUpdateManager,
    FallbackModelManager,
    TaskHistoryEntry,
    YAMLWorkflow,
    WorkflowStep,
)


logger = logging.getLogger(__name__)


class DiveOrchestratorEnhanced:
    """Enhanced Dive Orchestrator with all 12 features"""
    
    def __init__(self, name: str = "DiveOrchestratorEnhanced", num_agents: int = 8):
        """Initialize enhanced orchestrator"""
        self.name = name
        self.num_agents = num_agents
        self.agents = [f"agent_{i:02d}" for i in range(1, num_agents + 1)]
        
        # Initialize advanced features
        self.features = AdvancedFeaturesManager()
        
        # Orchestrator-level features
        self.workflow_manager: WorkflowManager = self.features.workflow_manager
        self.history_tracker: TaskHistoryTracker = self.features.history_tracker
        self.model_checker: ModelChecker = self.features.model_checker
        self.model_selector: ModelSelector = self.features.model_selector
        self.model_ranker: ModelRanker = self.features.model_ranker
        self.version_tracker: VersionTracker = self.features.version_tracker
        self.auto_update_manager: AutoUpdateManager = self.features.auto_update_manager
        
        # Agent-level features (provided to agents)
        self.task_analyzer: TaskAnalyzer = self.features.task_analyzer
        self.task_recommender: TaskTypeRecommender = self.features.task_recommender
        self.insight_collector: InsightCollector = self.features.insight_collector
        self.fallback_manager: FallbackModelManager = self.features.fallback_manager
        
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.logger.info(f"Enhanced Orchestrator initialized: {self.name}")
    
    # ========================================================================
    # ORCHESTRATOR FEATURES
    # ========================================================================
    
    def create_workflow_from_yaml(self, yaml_content: str) -> Optional[YAMLWorkflow]:
        """Create workflow from YAML"""
        try:
            workflow = YAMLWorkflow.from_yaml(yaml_content)
            self.workflow_manager.workflows[workflow.workflow_id] = workflow
            self.logger.info(f"Workflow created from YAML: {workflow.workflow_id}")
            return workflow
        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            return None
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute YAML workflow"""
        workflow = self.workflow_manager.workflows.get(workflow_id)
        if not workflow:
            self.logger.error(f"Workflow not found: {workflow_id}")
            return {"status": "error", "message": "Workflow not found"}
        
        results = {
            "workflow_id": workflow_id,
            "steps_executed": 0,
            "steps_failed": 0,
            "step_results": []
        }
        
        for step in workflow.steps:
            # Check dependencies
            if step.dependencies:
                self.logger.info(f"Step {step.step_id} has dependencies: {step.dependencies}")
            
            # Select model based on task type
            model = self.model_selector.select_model(step.task_type, step)
            
            # Execute step (simulated)
            step_result = {
                "step_id": step.step_id,
                "model": model,
                "status": "completed"
            }
            results["step_results"].append(step_result)
            results["steps_executed"] += 1
        
        self.logger.info(f"Workflow executed: {workflow_id} ({results['steps_executed']} steps)")
        return results
    
    def record_task_execution(self, task_id: str, agent_id: str, status: str, 
                             execution_time: float, result: Any = None, error: str = None):
        """Record task execution in history"""
        entry = TaskHistoryEntry(
            task_id=task_id,
            timestamp=datetime.now(),
            status=status,
            agent_id=agent_id,
            execution_time=execution_time,
            result=result,
            error=error
        )
        self.history_tracker.record_task(entry)
    
    def get_task_history(self, task_id: str) -> List[TaskHistoryEntry]:
        """Get task history"""
        return self.history_tracker.get_task_history(task_id)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.history_tracker.get_statistics()
    
    def check_models_daily(self) -> Dict[str, bool]:
        """Check all models (daily)"""
        if self.model_checker.should_check():
            self.logger.info("Running daily model check...")
            return self.model_checker.check_all_models()
        else:
            self.logger.info("Model check not needed today")
            return {}
    
    def select_best_model(self, task_type: str, task: Any) -> str:
        """Select best model for task"""
        return self.model_selector.select_model(task_type, task)
    
    def rank_models_for_task(self, task_type: str) -> List[tuple]:
        """Rank models for task type"""
        models = list(self.model_checker.models.values())
        return self.model_ranker.rank_models(task_type, models)
    
    def check_for_model_updates(self, model_id: str, current_version: str) -> Optional[Any]:
        """Check if model update available"""
        return self.version_tracker.check_for_updates(model_id, current_version)
    
    def start_auto_updates(self):
        """Start automatic update checking"""
        self.auto_update_manager.start_auto_update()
    
    # ========================================================================
    # AGENT FEATURES (Provided to Agents)
    # ========================================================================
    
    def analyze_task(self, task: Any) -> Dict[str, Any]:
        """Analyze task characteristics (for agents)"""
        return self.task_analyzer.analyze_task(task)
    
    def recommend_task_type(self, task: Any) -> str:
        """Recommend task type (for agents)"""
        return self.task_recommender.recommend_type(task)
    
    def get_model_insights(self, model_id: str) -> List[Any]:
        """Get model insights from GitHub/Reddit (for agents)"""
        return self.insight_collector.get_model_insights(model_id)
    
    def get_fallback_models(self, primary_model: str) -> List[str]:
        """Get fallback models (for agents)"""
        return self.fallback_manager.get_fallback_models(primary_model)
    
    def find_fallback_model(self, primary_model: str, available_models: List[str]) -> Optional[str]:
        """Find available fallback model (for agents)"""
        return self.fallback_manager.find_available_model(primary_model, available_models)
    
    # ========================================================================
    # SYSTEM STATUS
    # ========================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "orchestrator": self.name,
            "agents": len(self.agents),
            "features": self.features.get_status(),
            "execution_stats": self.get_execution_statistics(),
            "models_available": len(self.model_checker.models),
            "workflows": len(self.workflow_manager.workflows),
            "task_history_entries": len(self.history_tracker.history),
        }
    
    def shutdown(self):
        """Shutdown orchestrator"""
        self.logger.info(f"Orchestrator {self.name} shutting down")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s'
    )
    
    # Create enhanced orchestrator
    orchestrator = DiveOrchestratorEnhanced("DiveOrchestratorEnhanced", num_agents=8)
    
    print("✅ Dive Orchestrator v16 - Enhanced with All 12 Features")
    print(f"   Orchestrator: {orchestrator.name}")
    print(f"   Agents: {len(orchestrator.agents)}")
    print()
    
    # Test YAML Workflow
    print("1. Testing YAML Workflow Definition...")
    yaml_workflow = """
workflow_id: workflow_001
name: Sample Workflow
description: Test workflow
steps:
  - step_id: step_01
    name: Planning
    description: Plan the work
    task_type: planning
    model_type: sonnet
    priority: 5
  - step_id: step_02
    name: Coding
    description: Implement the code
    task_type: coding
    model_type: opus
    priority: 8
"""
    workflow = orchestrator.create_workflow_from_yaml(yaml_workflow)
    if workflow:
        print(f"   ✅ Workflow created: {workflow.workflow_id}")
        result = orchestrator.execute_workflow(workflow.workflow_id)
        print(f"   ✅ Workflow executed: {result['steps_executed']} steps")
    print()
    
    # Test Model Checking
    print("2. Testing Model Checker & Selection...")
    models_checked = orchestrator.check_models_daily()
    print(f"   ✅ Models checked: {len(models_checked)}")
    print()
    
    # Test Task History
    print("3. Testing Task History Tracking...")
    orchestrator.record_task_execution(
        task_id="task_001",
        agent_id="agent_01",
        status="completed",
        execution_time=0.5,
        result={"output": "success"}
    )
    history = orchestrator.get_task_history("task_001")
    print(f"   ✅ Task recorded: {len(history)} entries")
    print()
    
    # Get system status
    print("4. System Status...")
    status = orchestrator.get_system_status()
    print(f"   ✅ Orchestrator: {status['orchestrator']}")
    print(f"   ✅ Agents: {status['agents']}")
    print(f"   ✅ Features: {status['features']}")
    print()
    
    orchestrator.shutdown()
    print("✅ Enhanced Orchestrator test complete!")
